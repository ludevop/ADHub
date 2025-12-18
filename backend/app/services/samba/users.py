"""
Samba User Management Service

Manages Active Directory users using samba-tool
"""

import logging
import subprocess
import re
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class SambaUserService:
    """Service for managing Samba AD users"""

    def list_users(self) -> List[Dict[str, Any]]:
        """
        List all users in AD

        Returns:
            List of user dictionaries with username and basic info
        """
        try:
            result = subprocess.run(
                ["samba-tool", "user", "list"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                logger.error(f"Failed to list users: {result.stderr}")
                raise Exception(f"Failed to list users: {result.stderr}")

            users = []
            for line in result.stdout.strip().split('\n'):
                username = line.strip()
                if username:
                    # Get user details
                    user_details = self._get_user_details(username)
                    users.append(user_details)

            return users

        except subprocess.TimeoutExpired:
            logger.error("Timeout while listing users")
            raise Exception("Operation timed out")
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            raise

    def _get_user_details(self, username: str) -> Dict[str, Any]:
        """
        Get detailed information about a user

        Args:
            username: Username to query

        Returns:
            Dictionary with user details
        """
        try:
            result = subprocess.run(
                ["samba-tool", "user", "show", username],
                capture_output=True,
                text=True,
                timeout=10
            )

            user_info = {
                "username": username,
                "display_name": None,
                "email": None,
                "description": None,
                "account_disabled": False
            }

            if result.returncode == 0:
                # Parse the output
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()

                        if key == 'displayname':
                            user_info['display_name'] = value
                        elif key == 'mail':
                            user_info['email'] = value
                        elif key == 'description':
                            user_info['description'] = value
                        elif key == 'accountexpires' and value != 'never':
                            # Could parse expiration date
                            pass
                        elif 'disabled' in key.lower():
                            user_info['account_disabled'] = 'true' in value.lower()

            return user_info

        except Exception as e:
            logger.warning(f"Could not get details for user {username}: {e}")
            return {
                "username": username,
                "display_name": None,
                "email": None,
                "description": None,
                "account_disabled": False
            }

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific user's details

        Args:
            username: Username to query

        Returns:
            User details or None if not found
        """
        try:
            return self._get_user_details(username)
        except Exception as e:
            logger.error(f"Error getting user {username}: {e}")
            return None

    def create_user(
        self,
        username: str,
        password: str,
        given_name: Optional[str] = None,
        surname: Optional[str] = None,
        email: Optional[str] = None,
        description: Optional[str] = None,
        must_change_password: bool = True
    ) -> bool:
        """
        Create a new user

        Args:
            username: Username for the new user
            password: Initial password
            given_name: User's first name
            surname: User's last name
            email: User's email address
            description: User description
            must_change_password: Whether user must change password on first login

        Returns:
            True if successful, False otherwise
        """
        try:
            cmd = ["samba-tool", "user", "create", username, password]

            # Add optional parameters
            if given_name:
                cmd.extend(["--given-name", given_name])
            if surname:
                cmd.extend(["--surname", surname])
            if email:
                cmd.extend(["--mail-address", email])
            if description:
                cmd.extend(["--description", description])

            if must_change_password:
                cmd.append("--must-change-at-next-login")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                logger.error(f"Failed to create user {username}: {error_msg}")
                raise Exception(error_msg)

            logger.info(f"User {username} created successfully")
            return True

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout while creating user {username}")
            raise Exception("Operation timed out")
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            raise

    def delete_user(self, username: str) -> bool:
        """
        Delete a user

        Args:
            username: Username to delete

        Returns:
            True if successful
        """
        try:
            result = subprocess.run(
                ["samba-tool", "user", "delete", username],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                logger.error(f"Failed to delete user {username}: {error_msg}")
                raise Exception(error_msg)

            logger.info(f"User {username} deleted successfully")
            return True

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout while deleting user {username}")
            raise Exception("Operation timed out")
        except Exception as e:
            logger.error(f"Error deleting user {username}: {e}")
            raise

    def enable_user(self, username: str) -> bool:
        """
        Enable a user account

        Args:
            username: Username to enable

        Returns:
            True if successful
        """
        try:
            result = subprocess.run(
                ["samba-tool", "user", "enable", username],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                logger.error(f"Failed to enable user {username}: {error_msg}")
                raise Exception(error_msg)

            logger.info(f"User {username} enabled successfully")
            return True

        except Exception as e:
            logger.error(f"Error enabling user {username}: {e}")
            raise

    def disable_user(self, username: str) -> bool:
        """
        Disable a user account

        Args:
            username: Username to disable

        Returns:
            True if successful
        """
        try:
            result = subprocess.run(
                ["samba-tool", "user", "disable", username],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                logger.error(f"Failed to disable user {username}: {error_msg}")
                raise Exception(error_msg)

            logger.info(f"User {username} disabled successfully")
            return True

        except Exception as e:
            logger.error(f"Error disabling user {username}: {e}")
            raise

    def update_user(
        self,
        username: str,
        display_name: Optional[str] = None,
        email: Optional[str] = None,
        description: Optional[str] = None,
        admin_password: str = None
    ) -> bool:
        """
        Update user attributes using LDAP

        Args:
            username: Username to update
            display_name: New display name
            email: New email address
            description: New description
            admin_password: Administrator password for authentication

        Returns:
            True if successful
        """
        try:
            from ldap3 import Server, Connection, MODIFY_REPLACE, MODIFY_DELETE, SIMPLE, SUBTREE
            import subprocess

            # Get domain info to construct bind DN
            domain_result = subprocess.run(
                ["samba-tool", "domain", "info", "127.0.0.1"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if domain_result.returncode != 0:
                raise Exception("Could not get domain info")

            # Parse domain name and construct base DN
            domain_name = None
            netbios_domain = None
            for line in domain_result.stdout.split('\n'):
                line = line.strip()
                if line.startswith('Domain') and ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        domain_name = parts[1].strip()
                elif line.startswith('Netbios domain') and ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        netbios_domain = parts[1].strip()

            if not domain_name:
                raise Exception("Could not determine domain name")

            # Convert domain name to DN (e.g., "colarossi.local" -> "DC=colarossi,DC=local")
            base_dn = ','.join([f'DC={part}' for part in domain_name.split('.')])

            # Connect to LDAP with Administrator credentials
            server = Server('ldap://localhost')

            if not admin_password:
                raise Exception("Admin password is required to update user attributes")

            # Bind as Administrator with provided credentials
            admin_user = f"{netbios_domain}\\Administrator" if netbios_domain else "Administrator"

            # Try to connect with admin credentials
            try:
                conn = Connection(
                    server,
                    user=admin_user,
                    password=admin_password,
                    authentication=SIMPLE,
                    auto_bind=True,
                    raise_exceptions=True
                )
            except Exception as e:
                logger.error(f"Failed to connect to LDAP: {e}")
                # Check if it's an authentication error
                if "invalidCredentials" in str(e) or "bind" in str(e).lower():
                    raise Exception("Invalid administrator credentials")
                raise Exception(f"Cannot connect to LDAP to update user: {str(e)}")

            # Search for the user to get their actual DN
            logger.info(f"Searching for user {username} in {base_dn}")
            search_filter = f"(&(objectClass=user)(sAMAccountName={username}))"

            conn.search(
                search_base=base_dn,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['distinguishedName']
            )

            if not conn.entries:
                conn.unbind()
                raise Exception(f"User {username} not found in directory")

            # Get the actual DN from search results
            user_dn = str(conn.entries[0].distinguishedName)
            logger.info(f"Found user DN: {user_dn}")

            # Build modification dictionary
            changes = {}

            if display_name is not None:
                # Use MODIFY_REPLACE with empty list to clear, which works even if attribute doesn't exist
                changes['displayName'] = [(MODIFY_REPLACE, [display_name] if display_name else [])]

            if email is not None:
                changes['mail'] = [(MODIFY_REPLACE, [email] if email else [])]

            if description is not None:
                changes['description'] = [(MODIFY_REPLACE, [description] if description else [])]

            if not changes:
                logger.warning(f"No changes to apply for user {username}")
                conn.unbind()
                return True

            # Apply modifications
            success = conn.modify(user_dn, changes)

            if not success:
                error_msg = str(conn.result)
                logger.error(f"Failed to update user {username}: {error_msg}")
                conn.unbind()
                raise Exception(error_msg)

            conn.unbind()
            logger.info(f"User {username} updated successfully")
            return True

        except Exception as e:
            logger.error(f"Error updating user {username}: {e}")
            raise

    def set_password(self, username: str, new_password: str, must_change: bool = False) -> bool:
        """
        Set a user's password

        Args:
            username: Username
            new_password: New password
            must_change: Whether user must change password at next login

        Returns:
            True if successful
        """
        try:
            cmd = ["samba-tool", "user", "setpassword", username, "--newpassword", new_password]

            if must_change:
                cmd.append("--must-change-at-next-login")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                logger.error(f"Failed to set password for {username}: {error_msg}")
                raise Exception(error_msg)

            logger.info(f"Password set for user {username}")
            return True

        except Exception as e:
            logger.error(f"Error setting password for {username}: {e}")
            raise


# Singleton instance
user_service = SambaUserService()
