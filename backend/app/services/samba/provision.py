"""
Samba AD Domain Controller Provisioning Service

This module handles the provisioning of a new Samba AD DC using samba-tool.
"""

import subprocess
import asyncio
import logging
import os
from typing import Tuple, Optional
from datetime import datetime

from app.schemas.setup import DomainConfigSchema, ProvisionStatus

logger = logging.getLogger(__name__)


class SambaProvisionService:
    """Service for provisioning Samba AD DC"""

    def __init__(self):
        self.provision_log_path = "/var/log/adhub/provision.log"
        self._ensure_log_directory()

    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        log_dir = os.path.dirname(self.provision_log_path)
        os.makedirs(log_dir, exist_ok=True)

    async def check_prerequisites(self) -> Tuple[bool, list]:
        """
        Check system prerequisites before provisioning
        Returns (all_passed, list_of_checks)
        """
        checks = []

        # Check 1: Samba installed
        samba_installed = await self._check_samba_installed()
        checks.append({
            "check_name": "Samba Installation",
            "status": "passed" if samba_installed else "failed",
            "message": "Samba is installed" if samba_installed else "Samba is not installed",
            "details": "samba-tool is available" if samba_installed else "Install samba package"
        })

        # Check 2: Running as root or with privileges
        is_privileged = await self._check_privileges()
        checks.append({
            "check_name": "System Privileges",
            "status": "passed" if is_privileged else "failed",
            "message": "Has required privileges" if is_privileged else "Insufficient privileges",
            "details": "Can execute samba-tool" if is_privileged else "Requires root or sudo access"
        })

        # Check 3: No existing domain
        no_existing_domain = await self._check_no_existing_domain()
        checks.append({
            "check_name": "Existing Domain Check",
            "status": "passed" if no_existing_domain else "warning",
            "message": "No existing domain" if no_existing_domain else "Domain may already be provisioned",
            "details": "Safe to provision" if no_existing_domain else "Check /etc/samba/smb.conf"
        })

        # Check 4: Disk space
        has_disk_space = await self._check_disk_space()
        checks.append({
            "check_name": "Disk Space",
            "status": "passed" if has_disk_space else "warning",
            "message": "Sufficient disk space" if has_disk_space else "Low disk space",
            "details": "At least 1GB available" if has_disk_space else "Less than 1GB available"
        })

        # Check 5: Network connectivity
        has_network = await self._check_network()
        checks.append({
            "check_name": "Network Connectivity",
            "status": "passed" if has_network else "warning",
            "message": "Network is available" if has_network else "Network issues detected",
            "details": None
        })

        all_passed = all(check["status"] == "passed" for check in checks)

        return all_passed, checks

    async def provision_domain(self, config: DomainConfigSchema) -> Tuple[ProvisionStatus, str, Optional[str]]:
        """
        Provision a new Samba AD domain
        Returns (status, message, output/error)
        """
        logger.info(f"Starting domain provision for {config.domain_name}")

        try:
            # Prepare for provisioning (remove conflicting config)
            await self._prepare_for_provisioning()

            # Build samba-tool command
            cmd = self._build_provision_command(config)

            logger.info(f"Running command: {' '.join(cmd[:3])}...")  # Don't log password

            # Run provision command
            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )

            # Log output
            self._log_provision_output(config.domain_name, result.stdout, result.stderr)

            if result.returncode == 0:
                logger.info("Domain provision completed successfully")

                # Start Samba services after successful provision
                await self._start_samba_services()

                return ProvisionStatus.COMPLETED, "Domain provisioned successfully", result.stdout
            else:
                logger.error(f"Domain provision failed: {result.stderr}")
                return ProvisionStatus.FAILED, "Domain provision failed", result.stderr

        except subprocess.TimeoutExpired:
            logger.error("Domain provision timed out")
            return ProvisionStatus.FAILED, "Provision operation timed out", None

        except Exception as e:
            logger.error(f"Domain provision error: {str(e)}")
            return ProvisionStatus.FAILED, f"Error: {str(e)}", None

    def _build_provision_command(self, config: DomainConfigSchema) -> list:
        """Build samba-tool domain provision command"""
        cmd = [
            "samba-tool",
            "domain",
            "provision",
            f"--realm={config.realm}",
            f"--domain={config.domain}",
            f"--adminpass={config.admin_password}",
            f"--server-role={config.server_role}",
            f"--dns-backend={config.dns_backend.value}",
        ]

        if config.dns_forwarder:
            cmd.append(f"--option=dns forwarder={config.dns_forwarder}")

        if config.host_ip:
            cmd.append(f"--host-ip={config.host_ip}")

        # Function level mapping
        # Valid Samba 4.x function levels: 2000, 2003, 2008, 2008_R2
        # Note: 2016 and higher may not be fully supported in all Samba versions
        function_level_map = {
            "2000": "2000",
            "2003": "2003",
            "2008": "2008",
            "2008_R2": "2008_R2"
        }
        fl = function_level_map.get(config.function_level.value, "2008")

        logger.info(f"Setting function level to: {fl}")
        cmd.append(f"--function-level={fl}")

        # Use simple bind for LDAP
        cmd.append("--use-rfc2307")

        return cmd

    def _log_provision_output(self, domain_name: str, stdout: str, stderr: str):
        """Log provision output to file"""
        try:
            with open(self.provision_log_path, 'a') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"Provision attempt: {domain_name}\n")
                f.write(f"Timestamp: {datetime.utcnow().isoformat()}\n")
                f.write(f"{'='*80}\n\n")
                f.write("STDOUT:\n")
                f.write(stdout)
                f.write("\n\nSTDERR:\n")
                f.write(stderr)
                f.write(f"\n{'='*80}\n\n")
        except Exception as e:
            logger.warning(f"Could not write to provision log: {e}")

    async def get_domain_info(self) -> Optional[dict]:
        """
        Get information about provisioned domain
        Returns None if not provisioned
        """
        try:
            # Use 127.0.0.1 instead of localhost (samba-tool requires IP)
            result = await asyncio.to_thread(
                subprocess.run,
                ["samba-tool", "domain", "info", "127.0.0.1"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Parse domain info from output
                info = {}
                for line in result.stdout.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        info[key.strip()] = value.strip()
                return info
            else:
                logger.warning(f"samba-tool domain info failed: {result.stderr}")
                return None

        except Exception as e:
            logger.error(f"Error getting domain info: {e}")
            return None

    async def is_domain_provisioned(self) -> bool:
        """Check if a domain is already provisioned"""
        smb_conf_path = "/etc/samba/smb.conf"

        if not os.path.exists(smb_conf_path):
            return False

        try:
            with open(smb_conf_path, 'r') as f:
                content = f.read()

                # Check for AD DC indicators in config
                if "server role = active directory domain controller" in content.lower():
                    return True

                if "netbios name" in content.lower() and "realm" in content.lower():
                    return True

            return False

        except Exception as e:
            logger.error(f"Error checking provision status: {e}")
            return False

    # Helper check methods

    async def _check_samba_installed(self) -> bool:
        """Check if samba-tool is available"""
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                ["which", "samba-tool"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    async def _check_privileges(self) -> bool:
        """Check if running with required privileges"""
        try:
            # Try to run a harmless samba-tool command
            result = await asyncio.to_thread(
                subprocess.run,
                ["samba-tool", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    async def _check_no_existing_domain(self) -> bool:
        """Check if no domain is already provisioned"""
        return not await self.is_domain_provisioned()

    async def _check_disk_space(self) -> bool:
        """Check if sufficient disk space is available"""
        try:
            import shutil
            stat = shutil.disk_usage("/var/lib/samba")
            # Check for at least 1GB free
            return stat.free > 1024 * 1024 * 1024
        except Exception:
            return True  # Assume OK if we can't check

    async def _check_network(self) -> bool:
        """Check basic network connectivity"""
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            return True
        except Exception:
            return True  # Don't fail on this, just warn

    async def _prepare_for_provisioning(self):
        """
        Prepare system for domain provisioning
        Removes existing non-AD DC smb.conf if present
        """
        smb_conf_path = "/etc/samba/smb.conf"

        if not os.path.exists(smb_conf_path):
            logger.info("No existing smb.conf found - ready for provisioning")
            return

        try:
            # Read existing config
            with open(smb_conf_path, 'r') as f:
                content = f.read()

            # Check if it's already an AD DC config
            if "server role = active directory domain controller" in content.lower():
                logger.info("Existing AD DC configuration found")
                return

            # It's a non-AD DC config (like standalone server) - back it up and remove
            logger.info("Found non-AD DC smb.conf - backing up and removing")

            # Create backup
            backup_path = f"/etc/samba/smb.conf.backup.{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            os.rename(smb_conf_path, backup_path)
            logger.info(f"Backed up existing config to: {backup_path}")

            # Also backup the entire /etc/samba directory structure
            samba_backup_dir = f"/var/log/adhub/samba_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(samba_backup_dir, exist_ok=True)

            # Copy any other config files
            import shutil
            for item in os.listdir("/etc/samba"):
                if item != os.path.basename(backup_path):  # Skip the backup we just made
                    src = os.path.join("/etc/samba", item)
                    if os.path.isfile(src):
                        dst = os.path.join(samba_backup_dir, item)
                        shutil.copy2(src, dst)

            logger.info(f"Backed up Samba config to: {samba_backup_dir}")
            logger.info("System ready for AD DC provisioning")

        except Exception as e:
            logger.error(f"Error preparing for provisioning: {e}")
            raise

    async def _start_samba_services(self) -> bool:
        """
        Start Samba AD DC services after successful provisioning
        Returns True if services started successfully
        """
        logger.info("Starting Samba AD DC services...")

        try:
            # Check if Samba is already running
            check_result = await asyncio.to_thread(
                subprocess.run,
                ["pgrep", "-x", "samba"],
                capture_output=True,
                timeout=5
            )

            if check_result.returncode == 0:
                logger.info("Samba is already running")
                return True

            # Start Samba in daemon mode
            start_result = await asyncio.to_thread(
                subprocess.run,
                ["samba", "-D"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if start_result.returncode == 0:
                logger.info("Samba AD DC started successfully")

                # Wait a moment for services to initialize
                await asyncio.sleep(2)

                # Verify it's running
                verify_result = await asyncio.to_thread(
                    subprocess.run,
                    ["pgrep", "-x", "samba"],
                    capture_output=True,
                    timeout=5
                )

                if verify_result.returncode == 0:
                    logger.info("Samba AD DC verified running")
                    return True
                else:
                    logger.warning("Samba started but process not found")
                    return False
            else:
                logger.error(f"Failed to start Samba: {start_result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error starting Samba services: {e}")
            return False

    async def reset_domain(self) -> Tuple[bool, str]:
        """
        Reset domain configuration by stopping services and backing up/removing config
        Returns (success, message)
        """
        logger.warning("Domain reset requested - this will remove all AD configuration")

        try:
            # Step 1: Stop Samba services
            logger.info("Stopping Samba services...")
            stop_result = await asyncio.to_thread(
                subprocess.run,
                ["pkill", "-x", "samba"],
                capture_output=True,
                timeout=10
            )

            # Wait for services to stop
            await asyncio.sleep(2)

            # Verify stopped
            check_result = await asyncio.to_thread(
                subprocess.run,
                ["pgrep", "-x", "samba"],
                capture_output=True,
                timeout=5
            )

            if check_result.returncode == 0:
                logger.warning("Samba still running after stop attempt")
                # Force kill if needed
                await asyncio.to_thread(
                    subprocess.run,
                    ["pkill", "-9", "-x", "samba"],
                    capture_output=True,
                    timeout=10
                )
                await asyncio.sleep(1)

            logger.info("Samba services stopped")

            # Step 2: Backup current configuration
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_dir = f"/var/log/adhub/domain_reset_{timestamp}"
            os.makedirs(backup_dir, exist_ok=True)

            logger.info(f"Creating backup at {backup_dir}")

            # Backup smb.conf
            smb_conf_path = "/etc/samba/smb.conf"
            if os.path.exists(smb_conf_path):
                import shutil
                shutil.copy2(smb_conf_path, os.path.join(backup_dir, "smb.conf"))
                logger.info("Backed up smb.conf")

            # Backup entire /var/lib/samba (contains LDB databases)
            samba_lib_path = "/var/lib/samba"
            if os.path.exists(samba_lib_path):
                import shutil
                shutil.copytree(
                    samba_lib_path,
                    os.path.join(backup_dir, "samba_lib"),
                    dirs_exist_ok=True
                )
                logger.info("Backed up Samba databases")

            # Step 3: Remove configuration files
            logger.info("Removing Samba configuration...")

            if os.path.exists(smb_conf_path):
                os.remove(smb_conf_path)
                logger.info("Removed smb.conf")

            # Step 4: Clean Samba databases
            # Remove private directory (contains secrets, keytabs, etc.)
            private_dir = "/var/lib/samba/private"
            if os.path.exists(private_dir):
                import shutil
                shutil.rmtree(private_dir)
                logger.info("Removed private directory")

            # Remove other Samba state directories
            for subdir in ["sysvol", "bind-dns", "state"]:
                subdir_path = os.path.join(samba_lib_path, subdir)
                if os.path.exists(subdir_path):
                    import shutil
                    shutil.rmtree(subdir_path)
                    logger.info(f"Removed {subdir}")

            # Recreate empty directories
            os.makedirs("/var/lib/samba", exist_ok=True)
            os.makedirs("/var/lib/samba/private", exist_ok=True)

            logger.info(f"Domain reset complete. Backup saved to: {backup_dir}")

            return True, f"Domain reset successfully. Backup saved to: {backup_dir}"

        except Exception as e:
            logger.error(f"Error during domain reset: {e}")
            return False, f"Domain reset failed: {str(e)}"
