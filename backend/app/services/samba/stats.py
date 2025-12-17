"""
Samba Statistics Service

Retrieves statistics about users, groups, shares, and DNS from Samba AD
"""

import logging
import subprocess
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class SambaStatsService:
    """Service for retrieving Samba AD statistics"""

    def get_dashboard_stats(self) -> Dict[str, int]:
        """
        Get dashboard statistics

        Returns:
            Dictionary with total_users, total_groups, total_shares, total_dns_records
        """
        return {
            "total_users": self._count_users(),
            "total_groups": self._count_groups(),
            "total_shares": self._count_shares(),
            "total_dns_records": self._count_dns_records()
        }

    def _count_users(self) -> int:
        """Count total users in AD"""
        try:
            result = subprocess.run(
                ["samba-tool", "user", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Count non-empty lines
                users = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                return len(users)
            else:
                logger.error(f"Failed to list users: {result.stderr}")
                return 0

        except Exception as e:
            logger.error(f"Error counting users: {e}")
            return 0

    def _count_groups(self) -> int:
        """Count total groups in AD"""
        try:
            result = subprocess.run(
                ["samba-tool", "group", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Count non-empty lines
                groups = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                return len(groups)
            else:
                logger.error(f"Failed to list groups: {result.stderr}")
                return 0

        except Exception as e:
            logger.error(f"Error counting groups: {e}")
            return 0

    def _count_shares(self) -> int:
        """Count total shares in smb.conf (excluding default shares)"""
        try:
            result = subprocess.run(
                ["net", "conf", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Count share sections, excluding default ones
                default_shares = {'global', 'sysvol', 'netlogon', 'printers', 'print$'}
                shares = []

                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line.startswith('[') and line.endswith(']'):
                        share_name = line[1:-1].lower()
                        if share_name not in default_shares:
                            shares.append(share_name)

                return len(shares)
            else:
                logger.debug(f"net conf list not available, trying smb.conf")
                # Fallback: parse smb.conf
                return self._count_shares_from_config()

        except Exception as e:
            logger.error(f"Error counting shares: {e}")
            return 0

    def _count_shares_from_config(self) -> int:
        """Fallback: Count shares from smb.conf"""
        try:
            with open('/etc/samba/smb.conf', 'r') as f:
                content = f.read()

            default_shares = {'global', 'sysvol', 'netlogon', 'printers', 'print$'}
            shares = []

            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('[') and line.endswith(']'):
                    share_name = line[1:-1].lower()
                    if share_name not in default_shares:
                        shares.append(share_name)

            return len(shares)

        except Exception as e:
            logger.error(f"Error reading smb.conf: {e}")
            return 0

    def _count_dns_records(self) -> int:
        """Count total DNS records in Samba DNS"""
        try:
            # Get domain info first
            domain_result = subprocess.run(
                ["samba-tool", "domain", "info", "127.0.0.1"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if domain_result.returncode != 0:
                logger.error("Could not get domain info")
                return 0

            # Extract domain name
            domain_name = None
            for line in domain_result.stdout.split('\n'):
                if line.strip().startswith('Domain'):
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        domain_name = parts[1].strip().lower()
                        break

            if not domain_name:
                logger.error("Could not determine domain name")
                return 0

            # List DNS records
            result = subprocess.run(
                ["samba-tool", "dns", "query", "localhost", domain_name, "@", "ALL"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Count lines that contain DNS records
                # Each record typically has "Name=" in it
                record_count = 0
                for line in result.stdout.split('\n'):
                    if 'Name=' in line or 'name=' in line:
                        record_count += 1
                return record_count
            else:
                logger.debug(f"Could not query DNS records: {result.stderr}")
                return 0

        except Exception as e:
            logger.error(f"Error counting DNS records: {e}")
            return 0


# Singleton instance
stats_service = SambaStatsService()
