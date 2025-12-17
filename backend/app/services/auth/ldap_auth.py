"""
LDAP Authentication Service for Samba Active Directory

Authenticates users against Samba AD using LDAP bind and retrieves user information
"""

import logging
from typing import Optional, Tuple, List
from ldap3 import Server, Connection, ALL, NTLM, SIMPLE, AUTO_BIND_NO_TLS
from ldap3.core.exceptions import LDAPException, LDAPBindError

from app.schemas.auth import User

logger = logging.getLogger(__name__)


class LDAPAuthService:
    """Service for LDAP authentication against Samba AD"""

    def __init__(self, server_uri: str = "ldap://localhost", use_ssl: bool = False):
        """
        Initialize LDAP authentication service

        Args:
            server_uri: LDAP server URI (default: ldap://localhost)
            use_ssl: Whether to use LDAPS (default: False for internal use)
        """
        self.server_uri = server_uri
        self.use_ssl = use_ssl
        self.server = Server(server_uri, get_info=ALL, use_ssl=use_ssl)

    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        Authenticate a user against Samba AD via LDAP bind

        Args:
            username: Username (can be sAMAccountName, UPN, or DN)
            password: User password

        Returns:
            Tuple of (success, user_info, error_message)
        """
        try:
            # Determine the bind DN format based on username format
            if "@" in username:
                # UPN format: user@domain.com
                bind_dn = username
            elif "\\" in username:
                # DOMAIN\\username format
                bind_dn = username
            else:
                # Simple username - try to get domain from server
                domain_info = self._get_domain_info()
                if domain_info:
                    # Try DOMAIN\\username format
                    bind_dn = f"{domain_info['netbios']}\\{username}"
                else:
                    # Fallback to simple username
                    bind_dn = username

            # Attempt LDAP bind - try multiple authentication methods
            conn = None
            auth_methods = [
                ('SIMPLE', SIMPLE),
                ('NTLM', NTLM)
            ]

            last_error = None
            for method_name, auth_type in auth_methods:
                try:
                    logger.info(f"Trying {method_name} authentication for {username}")

                    # For NTLM, format the username properly
                    if auth_type == NTLM and not ("\\" in bind_dn or "@" in bind_dn):
                        domain_info = self._get_domain_info()
                        if domain_info and domain_info.get('netbios'):
                            bind_user = f"{domain_info['netbios']}\\{username}"
                        else:
                            bind_user = bind_dn
                    else:
                        bind_user = bind_dn

                    conn = Connection(
                        self.server,
                        user=bind_user,
                        password=password,
                        authentication=auth_type,
                        raise_exceptions=False
                    )

                    if conn.bind():
                        logger.info(f"Successfully authenticated with {method_name}")
                        break
                    else:
                        last_error = conn.last_error
                        logger.debug(f"{method_name} authentication failed: {last_error}")
                        conn = None
                except Exception as e:
                    logger.debug(f"{method_name} authentication error: {e}")
                    last_error = str(e)
                    conn = None

            if not conn:
                error_msg = f"Authentication failed: {last_error}"
                logger.warning(f"All LDAP bind methods failed for user {username}: {error_msg}")
                return False, None, "Invalid credentials"

            # Authentication successful - get user information
            user_info = self._get_user_info(conn, username)

            conn.unbind()

            if user_info:
                return True, user_info, None
            else:
                return True, None, "Could not retrieve user information"

        except LDAPBindError as e:
            logger.error(f"LDAP bind error for {username}: {e}")
            return False, None, "Invalid credentials"
        except LDAPException as e:
            logger.error(f"LDAP error during authentication: {e}")
            return False, None, f"LDAP error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {e}")
            return False, None, f"Authentication error: {str(e)}"

    def _get_user_info(self, conn: Connection, username: str) -> Optional[User]:
        """
        Get user information from AD

        Args:
            conn: Authenticated LDAP connection
            username: Username to look up

        Returns:
            User object with user information
        """
        try:
            # Get base DN from connection
            if not conn.server.info or not conn.server.info.other:
                logger.warning("Could not get server info")
                return None

            # Try to get default naming context
            base_dn = None
            if 'defaultNamingContext' in conn.server.info.other:
                base_dn = conn.server.info.other['defaultNamingContext'][0]

            if not base_dn:
                logger.warning("Could not determine base DN")
                return None

            # Search for user
            search_filter = f"(&(objectClass=user)(sAMAccountName={username}))"

            conn.search(
                search_base=base_dn,
                search_filter=search_filter,
                attributes=['sAMAccountName', 'displayName', 'mail', 'memberOf']
            )

            if not conn.entries:
                logger.warning(f"User {username} not found in directory")
                return None

            entry = conn.entries[0]

            # Log the raw entry for debugging
            logger.info(f"Raw LDAP entry: {entry}")
            logger.info(f"Entry attributes: {entry.entry_attributes_as_dict}")

            # Extract user information - LDAP attributes are returned as lists
            # Get the actual value from the attribute, handling various return types
            def get_ldap_attr(entry, attr_name):
                """Safely extract LDAP attribute value"""
                if not hasattr(entry, attr_name):
                    return None
                attr = getattr(entry, attr_name)
                if attr is None:
                    return None
                # Get the value
                value = attr.value if hasattr(attr, 'value') else attr
                # If it's a list with one item, extract it
                if isinstance(value, list):
                    if len(value) == 0:
                        return None
                    elif len(value) == 1:
                        return str(value[0]) if value[0] else None
                    else:
                        return value  # Return list for multi-valued attributes
                return str(value) if value else None

            sam_account_name = get_ldap_attr(entry, 'sAMAccountName') or username
            display_name = get_ldap_attr(entry, 'displayName')
            email = get_ldap_attr(entry, 'mail')

            logger.info(f"Extracted - sAMAccountName: {sam_account_name}, displayName: {display_name}, email: {email}")

            # Get groups
            groups = []
            member_of_attr = get_ldap_attr(entry, 'memberOf')
            if member_of_attr:
                member_of_list = member_of_attr if isinstance(member_of_attr, list) else [member_of_attr]
                for group_dn in member_of_list:
                    if group_dn:
                        # Extract CN from DN (e.g., "CN=Domain Admins,CN=Users,DC=example,DC=com")
                        cn_part = str(group_dn).split(',')[0]
                        if cn_part.startswith('CN='):
                            groups.append(cn_part[3:])  # Remove "CN=" prefix

            logger.info(f"Extracted groups: {groups}")

            # Determine if user is admin (member of Domain Admins or Administrators)
            is_admin = any(
                group.lower() in ['domain admins', 'administrators', 'enterprise admins']
                for group in groups
            )

            # Extract domain from base DN
            domain_parts = base_dn.split(',')
            domain = '.'.join([part.split('=')[1] for part in domain_parts if part.startswith('DC=')])

            return User(
                username=sam_account_name,
                display_name=display_name,
                email=email,
                domain=domain,
                groups=groups,
                is_admin=is_admin
            )

        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None

    def _get_domain_info(self) -> Optional[dict]:
        """
        Get domain information from Samba

        Returns:
            Dictionary with domain info or None
        """
        try:
            import subprocess
            result = subprocess.run(
                ["samba-tool", "domain", "info", "127.0.0.1"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                info = {}
                for line in result.stdout.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower().replace(' ', '_')
                        info[key] = value.strip()

                # Map to expected fields
                return {
                    'netbios': info.get('netbios_domain', '').upper(),
                    'domain': info.get('domain', ''),
                    'forest': info.get('forest', '')
                }
            return None
        except Exception as e:
            logger.warning(f"Could not get domain info: {e}")
            return None
