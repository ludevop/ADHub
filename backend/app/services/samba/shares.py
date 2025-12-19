"""
Samba Share Management Service

Manages Samba shares using net conf commands
"""

import logging
import subprocess
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class SambaShareService:
    """Service for managing Samba shares"""

    def list_shares(self) -> List[Dict[str, Any]]:
        """
        List all shares

        Returns:
            List of share dictionaries with share name and details
        """
        try:
            result = subprocess.run(
                ["net", "conf", "list"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                logger.error(f"Failed to list shares: {result.stderr}")
                raise Exception(f"Failed to list shares: {result.stderr}")

            shares = []
            current_share = None
            current_config = {}

            for line in result.stdout.strip().split('\n'):
                line = line.strip()

                # Share section header [sharename]
                if line.startswith('[') and line.endswith(']'):
                    # Save previous share if exists
                    if current_share:
                        shares.append({
                            "name": current_share,
                            **current_config
                        })

                    # Start new share
                    current_share = line[1:-1]  # Remove [ ]
                    current_config = {
                        "path": None,
                        "comment": None,
                        "read_only": False,
                        "guest_ok": False,
                        "browseable": True
                    }

                # Configuration key = value
                elif '=' in line and current_share:
                    key, value = line.split('=', 1)
                    key = key.strip().lower()
                    value = value.strip()

                    if key == 'path':
                        current_config['path'] = value
                    elif key == 'comment':
                        current_config['comment'] = value
                    elif key == 'read only':
                        current_config['read_only'] = value.lower() in ('yes', 'true', '1')
                    elif key == 'guest ok':
                        current_config['guest_ok'] = value.lower() in ('yes', 'true', '1')
                    elif key == 'browseable' or key == 'browsable':
                        current_config['browseable'] = value.lower() in ('yes', 'true', '1')

            # Don't forget the last share
            if current_share:
                shares.append({
                    "name": current_share,
                    **current_config
                })

            # Filter out special shares (global, printers, etc.)
            shares = [s for s in shares if s['name'] not in ['global', 'printers', 'print$']]

            return shares

        except subprocess.TimeoutExpired:
            logger.error("Timeout while listing shares")
            raise Exception("Operation timed out")
        except Exception as e:
            logger.error(f"Error listing shares: {e}")
            raise

    def get_share(self, sharename: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific share's details

        Args:
            sharename: Share name to query

        Returns:
            Share details or None if not found
        """
        try:
            result = subprocess.run(
                ["net", "conf", "showshare", sharename],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                logger.warning(f"Share {sharename} not found")
                return None

            share_config = {
                "name": sharename,
                "path": None,
                "comment": None,
                "read_only": False,
                "guest_ok": False,
                "browseable": True
            }

            for line in result.stdout.strip().split('\n'):
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip().lower()
                    value = value.strip()

                    if key == 'path':
                        share_config['path'] = value
                    elif key == 'comment':
                        share_config['comment'] = value
                    elif key == 'read only':
                        share_config['read_only'] = value.lower() in ('yes', 'true', '1')
                    elif key == 'guest ok':
                        share_config['guest_ok'] = value.lower() in ('yes', 'true', '1')
                    elif key == 'browseable' or key == 'browsable':
                        share_config['browseable'] = value.lower() in ('yes', 'true', '1')

            return share_config

        except Exception as e:
            logger.error(f"Error getting share {sharename}: {e}")
            return None

    def create_share(
        self,
        sharename: str,
        path: str,
        comment: Optional[str] = None,
        read_only: bool = False,
        guest_ok: bool = False,
        browseable: bool = True
    ) -> bool:
        """
        Create a new share

        Args:
            sharename: Name for the new share
            path: Filesystem path to share
            comment: Share description/comment
            read_only: Whether share is read-only
            guest_ok: Whether guest access is allowed
            browseable: Whether share is browseable

        Returns:
            True if successful
        """
        try:
            # Create the share with basic config
            commands = [
                ["net", "conf", "addshare", sharename, path, "writeable=yes", "guest_ok=no"],
            ]

            # Set additional parameters
            if comment:
                commands.append(["net", "conf", "setparm", sharename, "comment", comment])

            if read_only:
                commands.append(["net", "conf", "setparm", sharename, "read only", "yes"])
            else:
                commands.append(["net", "conf", "setparm", sharename, "read only", "no"])

            if guest_ok:
                commands.append(["net", "conf", "setparm", sharename, "guest ok", "yes"])
            else:
                commands.append(["net", "conf", "setparm", sharename, "guest ok", "no"])

            if browseable:
                commands.append(["net", "conf", "setparm", sharename, "browseable", "yes"])
            else:
                commands.append(["net", "conf", "setparm", sharename, "browseable", "no"])

            # Execute all commands
            for cmd in commands:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode != 0:
                    error_msg = result.stderr.strip()
                    logger.error(f"Failed to configure share {sharename}: {error_msg}")
                    # Try to clean up by deleting the share
                    subprocess.run(["net", "conf", "delshare", sharename], capture_output=True)
                    raise Exception(error_msg)

            logger.info(f"Share {sharename} created successfully")
            return True

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout while creating share {sharename}")
            raise Exception("Operation timed out")
        except Exception as e:
            logger.error(f"Error creating share {sharename}: {e}")
            raise

    def delete_share(self, sharename: str) -> bool:
        """
        Delete a share

        Args:
            sharename: Share name to delete

        Returns:
            True if successful
        """
        try:
            result = subprocess.run(
                ["net", "conf", "delshare", sharename],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                logger.error(f"Failed to delete share {sharename}: {error_msg}")
                raise Exception(error_msg)

            logger.info(f"Share {sharename} deleted successfully")
            return True

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout while deleting share {sharename}")
            raise Exception("Operation timed out")
        except Exception as e:
            logger.error(f"Error deleting share {sharename}: {e}")
            raise

    def update_share(
        self,
        sharename: str,
        path: Optional[str] = None,
        comment: Optional[str] = None,
        read_only: Optional[bool] = None,
        guest_ok: Optional[bool] = None,
        browseable: Optional[bool] = None
    ) -> bool:
        """
        Update share attributes

        Args:
            sharename: Share name to update
            path: New filesystem path
            comment: New comment
            read_only: Whether share is read-only
            guest_ok: Whether guest access is allowed
            browseable: Whether share is browseable

        Returns:
            True if successful
        """
        try:
            commands = []

            if path is not None:
                commands.append(["net", "conf", "setparm", sharename, "path", path])

            if comment is not None:
                if comment:
                    commands.append(["net", "conf", "setparm", sharename, "comment", comment])
                else:
                    # Delete the comment parameter
                    commands.append(["net", "conf", "delparm", sharename, "comment"])

            if read_only is not None:
                commands.append(["net", "conf", "setparm", sharename, "read only", "yes" if read_only else "no"])

            if guest_ok is not None:
                commands.append(["net", "conf", "setparm", sharename, "guest ok", "yes" if guest_ok else "no"])

            if browseable is not None:
                commands.append(["net", "conf", "setparm", sharename, "browseable", "yes" if browseable else "no"])

            if not commands:
                logger.warning(f"No changes to apply for share {sharename}")
                return True

            # Execute all commands
            for cmd in commands:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode != 0:
                    error_msg = result.stderr.strip()
                    logger.error(f"Failed to update share {sharename}: {error_msg}")
                    raise Exception(error_msg)

            logger.info(f"Share {sharename} updated successfully")
            return True

        except Exception as e:
            logger.error(f"Error updating share {sharename}: {e}")
            raise


# Singleton instance
share_service = SambaShareService()
