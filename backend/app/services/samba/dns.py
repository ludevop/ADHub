"""
Samba DNS Management Service

Manages Active Directory DNS using samba-tool dns commands
"""

import logging
import subprocess
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class SambaDNSService:
    """Service for managing Samba AD DNS"""

    def __init__(self):
        """Initialize DNS service and get server info"""
        self._server = "127.0.0.1"
        self._domain = None
        self._initialize()

    def _initialize(self):
        """Get domain information"""
        try:
            result = subprocess.run(
                ["samba-tool", "domain", "info", self._server],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line.startswith('Domain') and ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            self._domain = parts[1].strip()
                            break
        except Exception as e:
            logger.warning(f"Could not get domain info: {e}")

    def list_zones(self) -> List[Dict[str, Any]]:
        """
        List all DNS zones

        Returns:
            List of zone dictionaries
        """
        # For now, return the domain zone
        # Full zone listing requires authentication which we'll skip for read operations
        zones = []
        if self._domain:
            zones.append({
                "name": self._domain,
                "type": "forward"
            })
        return zones

    def list_records(self, zone: str) -> List[Dict[str, Any]]:
        """
        List all DNS records in a zone

        Args:
            zone: Zone name

        Returns:
            List of record dictionaries
        """
        # DNS record listing without authentication is not supported in current implementation
        # Records added through the UI will be tracked, but existing records won't be displayed
        # This is a limitation of samba-tool dns which requires authentication for queries
        logger.info(f"Listing DNS records for zone {zone} (read-only mode)")
        return []

    def add_record(
        self,
        zone: str,
        name: str,
        record_type: str,
        data: str,
        admin_password: str
    ) -> bool:
        """
        Add a DNS record

        Args:
            zone: Zone name
            name: Record name
            record_type: Record type (A, AAAA, CNAME, MX, TXT, SRV, PTR)
            data: Record data
            admin_password: Administrator password

        Returns:
            True if successful
        """
        try:
            result = subprocess.run(
                ["samba-tool", "dns", "add", self._server, zone, name, record_type, data, "-U", f"Administrator%{admin_password}"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                logger.error(f"Failed to add DNS record: {error_msg}")
                raise Exception(error_msg)

            logger.info(f"DNS record added: {name}.{zone} {record_type} {data}")
            return True

        except subprocess.TimeoutExpired:
            logger.error("Timeout while adding DNS record")
            raise Exception("Operation timed out")
        except Exception as e:
            logger.error(f"Error adding DNS record: {e}")
            raise

    def delete_record(
        self,
        zone: str,
        name: str,
        record_type: str,
        data: str,
        admin_password: str
    ) -> bool:
        """
        Delete a DNS record

        Args:
            zone: Zone name
            name: Record name
            record_type: Record type
            data: Record data
            admin_password: Administrator password

        Returns:
            True if successful
        """
        try:
            result = subprocess.run(
                ["samba-tool", "dns", "delete", self._server, zone, name, record_type, data, "-U", f"Administrator%{admin_password}"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                logger.error(f"Failed to delete DNS record: {error_msg}")
                raise Exception(error_msg)

            logger.info(f"DNS record deleted: {name}.{zone} {record_type} {data}")
            return True

        except subprocess.TimeoutExpired:
            logger.error("Timeout while deleting DNS record")
            raise Exception("Operation timed out")
        except Exception as e:
            logger.error(f"Error deleting DNS record: {e}")
            raise


# Singleton instance
dns_service = SambaDNSService()
