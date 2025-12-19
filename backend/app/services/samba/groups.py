"""
Samba Group Management Service

Manages Active Directory groups using samba-tool and LDAP
"""

import logging
import subprocess
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class SambaGroupService:
    """Service for managing Samba AD groups"""

    def list_groups(self) -> List[Dict[str, Any]]:
        """
        List all groups in AD

        Returns:
            List of group dictionaries with group name and basic info
        """
        try:
            result = subprocess.run(
                ["samba-tool", "group", "list"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                logger.error(f"Failed to list groups: {result.stderr}")
                raise Exception(f"Failed to list groups: {result.stderr}")

            groups = []
            for line in result.stdout.strip().split('\n'):
                groupname = line.strip()
                if groupname:
                    # Get group details
                    group_details = self._get_group_details(groupname)
                    groups.append(group_details)

            return groups

        except subprocess.TimeoutExpired:
            logger.error("Timeout while listing groups")
            raise Exception("Operation timed out")
        except Exception as e:
            logger.error(f"Error listing groups: {e}")
            raise

    def _get_group_details(self, groupname: str) -> Dict[str, Any]:
        """
        Get detailed information about a group

        Args:
            groupname: Group name to query

        Returns:
            Dictionary with group details
        """
        try:
            result = subprocess.run(
                ["samba-tool", "group", "show", groupname],
                capture_output=True,
                text=True,
                timeout=10
            )

            group_info = {
                "name": groupname,
                "description": None,
                "members": []
            }

            if result.returncode == 0:
                # Parse the output
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()

                        if key == 'description':
                            group_info['description'] = value

            # Get group members
            group_info['members'] = self._get_group_members(groupname)

            return group_info

        except Exception as e:
            logger.warning(f"Could not get details for group {groupname}: {e}")
            return {
                "name": groupname,
                "description": None,
                "members": []
            }

    def _get_group_members(self, groupname: str) -> List[str]:
        """
        Get members of a group

        Args:
            groupname: Group name to query

        Returns:
            List of member usernames
        """
        try:
            result = subprocess.run(
                ["samba-tool", "group", "listmembers", groupname],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return []

            members = []
            for line in result.stdout.strip().split('\n'):
                member = line.strip()
                if member:
                    members.append(member)

            return members

        except Exception as e:
            logger.warning(f"Could not get members for group {groupname}: {e}")
            return []

    def get_group(self, groupname: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific group's details

        Args:
            groupname: Group name to query

        Returns:
            Group details or None if not found
        """
        try:
            return self._get_group_details(groupname)
        except Exception as e:
            logger.error(f"Error getting group {groupname}: {e}")
            return None

    def create_group(
        self,
        groupname: str,
        description: Optional[str] = None
    ) -> bool:
        """
        Create a new group

        Args:
            groupname: Name for the new group
            description: Group description

        Returns:
            True if successful
        """
        try:
            cmd = ["samba-tool", "group", "add", groupname]

            if description:
                cmd.extend(["--description", description])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                logger.error(f"Failed to create group {groupname}: {error_msg}")
                raise Exception(error_msg)

            logger.info(f"Group {groupname} created successfully")
            return True

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout while creating group {groupname}")
            raise Exception("Operation timed out")
        except Exception as e:
            logger.error(f"Error creating group {groupname}: {e}")
            raise

    def delete_group(self, groupname: str) -> bool:
        """
        Delete a group

        Args:
            groupname: Group name to delete

        Returns:
            True if successful
        """
        try:
            result = subprocess.run(
                ["samba-tool", "group", "delete", groupname],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                logger.error(f"Failed to delete group {groupname}: {error_msg}")
                raise Exception(error_msg)

            logger.info(f"Group {groupname} deleted successfully")
            return True

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout while deleting group {groupname}")
            raise Exception("Operation timed out")
        except Exception as e:
            logger.error(f"Error deleting group {groupname}: {e}")
            raise

    def update_group(
        self,
        groupname: str,
        description: Optional[str] = None,
        admin_password: str = None
    ) -> bool:
        """
        Update group attributes using LDAP

        Args:
            groupname: Group name to update
            description: New description
            admin_password: Administrator password for authentication

        Returns:
            True if successful
        """
        try:
            from ldap3 import Server, Connection, MODIFY_REPLACE, SIMPLE, SUBTREE
            import subprocess

            # Get domain info
            domain_result = subprocess.run(
                ["samba-tool", "domain", "info", "127.0.0.1"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if domain_result.returncode != 0:
                raise Exception("Could not get domain info")

            # Parse domain name
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

            # Convert domain name to DN
            base_dn = ','.join([f'DC={part}' for part in domain_name.split('.')])

            # Connect to LDAP
            server = Server('ldap://localhost')

            if not admin_password:
                raise Exception("Admin password is required to update group attributes")

            admin_user = f"{netbios_domain}\\Administrator" if netbios_domain else "Administrator"

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
                if "invalidCredentials" in str(e) or "bind" in str(e).lower():
                    raise Exception("Invalid administrator credentials")
                raise Exception(f"Cannot connect to LDAP to update group: {str(e)}")

            # Search for the group to get its DN
            logger.info(f"Searching for group {groupname} in {base_dn}")
            search_filter = f"(&(objectClass=group)(sAMAccountName={groupname}))"

            conn.search(
                search_base=base_dn,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['distinguishedName']
            )

            if not conn.entries:
                conn.unbind()
                raise Exception(f"Group {groupname} not found in directory")

            # Get the actual DN
            group_dn = str(conn.entries[0].distinguishedName)
            logger.info(f"Found group DN: {group_dn}")

            # Build modification dictionary
            changes = {}

            if description is not None:
                changes['description'] = [(MODIFY_REPLACE, [description] if description else [])]

            if not changes:
                logger.warning(f"No changes to apply for group {groupname}")
                conn.unbind()
                return True

            # Apply modifications
            success = conn.modify(group_dn, changes)

            if not success:
                error_msg = str(conn.result)
                logger.error(f"Failed to update group {groupname}: {error_msg}")
                conn.unbind()
                raise Exception(error_msg)

            conn.unbind()
            logger.info(f"Group {groupname} updated successfully")
            return True

        except Exception as e:
            logger.error(f"Error updating group {groupname}: {e}")
            raise

    def add_member(self, groupname: str, username: str) -> bool:
        """
        Add a user to a group

        Args:
            groupname: Group name
            username: Username to add

        Returns:
            True if successful
        """
        try:
            result = subprocess.run(
                ["samba-tool", "group", "addmembers", groupname, username],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                logger.error(f"Failed to add {username} to group {groupname}: {error_msg}")
                raise Exception(error_msg)

            logger.info(f"User {username} added to group {groupname}")
            return True

        except Exception as e:
            logger.error(f"Error adding member to group: {e}")
            raise

    def remove_member(self, groupname: str, username: str) -> bool:
        """
        Remove a user from a group

        Args:
            groupname: Group name
            username: Username to remove

        Returns:
            True if successful
        """
        try:
            result = subprocess.run(
                ["samba-tool", "group", "removemembers", groupname, username],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                logger.error(f"Failed to remove {username} from group {groupname}: {error_msg}")
                raise Exception(error_msg)

            logger.info(f"User {username} removed from group {groupname}")
            return True

        except Exception as e:
            logger.error(f"Error removing member from group: {e}")
            raise


# Singleton instance
group_service = SambaGroupService()
