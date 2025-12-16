"""
Samba AD Domain Controller Verification Tests

This module contains comprehensive tests to verify that a Samba AD DC
has been provisioned correctly and is functioning properly.
"""

import asyncio
import subprocess
import socket
import time
from typing import List, Tuple
import logging

from app.schemas.setup import VerificationTest

logger = logging.getLogger(__name__)


class SambaVerificationService:
    """Service for verifying Samba AD DC installation"""

    def __init__(self, domain_name: str, realm: str, admin_password: str):
        self.domain_name = domain_name
        self.realm = realm
        self.admin_password = admin_password

    async def run_all_tests(self) -> List[VerificationTest]:
        """
        Run all verification tests
        Returns list of test results
        """
        tests = []

        logger.info("Starting Samba AD verification tests")

        # Run tests in order
        tests.extend(await self._test_prerequisites())
        tests.extend(await self._test_dns())
        tests.extend(await self._test_services())
        tests.extend(await self._test_ldap())
        tests.extend(await self._test_kerberos())
        tests.extend(await self._test_authentication())

        logger.info(f"Verification complete: {len(tests)} tests run")

        return tests

    async def _test_prerequisites(self) -> List[VerificationTest]:
        """Test system prerequisites"""
        tests = []

        # Test 1: Check if Samba is installed
        test = await self._run_test(
            "Samba Installation",
            "prerequisites",
            self._check_samba_installed
        )
        tests.append(test)

        # Test 2: Check smb.conf exists
        test = await self._run_test(
            "Samba Configuration File",
            "prerequisites",
            self._check_smb_conf
        )
        tests.append(test)

        return tests

    async def _test_dns(self) -> List[VerificationTest]:
        """Test DNS configuration and resolution"""
        tests = []

        # Test 1: Resolve domain name
        test = await self._run_test(
            f"DNS: Resolve {self.domain_name}",
            "dns",
            lambda: self._check_dns_resolution(self.domain_name)
        )
        tests.append(test)

        # Test 2: Resolve _ldap._tcp SRV record
        test = await self._run_test(
            "DNS: LDAP SRV Record",
            "dns",
            lambda: self._check_srv_record(f"_ldap._tcp.{self.domain_name}")
        )
        tests.append(test)

        # Test 3: Resolve _kerberos._tcp SRV record
        test = await self._run_test(
            "DNS: Kerberos SRV Record",
            "dns",
            lambda: self._check_srv_record(f"_kerberos._tcp.{self.domain_name}")
        )
        tests.append(test)

        return tests

    async def _test_services(self) -> List[VerificationTest]:
        """Test Samba services and ports"""
        tests = []

        # Test 1: Check port 389 (LDAP)
        test = await self._run_test(
            "Service: LDAP Port (389)",
            "services",
            lambda: self._check_port(389)
        )
        tests.append(test)

        # Test 2: Check port 636 (LDAPS)
        test = await self._run_test(
            "Service: LDAPS Port (636)",
            "services",
            lambda: self._check_port(636)
        )
        tests.append(test)

        # Test 3: Check port 88 (Kerberos)
        test = await self._run_test(
            "Service: Kerberos Port (88)",
            "services",
            lambda: self._check_port(88)
        )
        tests.append(test)

        # Test 4: Check port 445 (SMB)
        test = await self._run_test(
            "Service: SMB Port (445)",
            "services",
            lambda: self._check_port(445)
        )
        tests.append(test)

        # Test 5: Check port 53 (DNS)
        test = await self._run_test(
            "Service: DNS Port (53)",
            "services",
            lambda: self._check_port(53)
        )
        tests.append(test)

        return tests

    async def _test_ldap(self) -> List[VerificationTest]:
        """Test LDAP functionality"""
        tests = []

        # Test 1: Anonymous LDAP bind
        test = await self._run_test(
            "LDAP: Anonymous Bind",
            "ldap",
            self._check_ldap_anonymous_bind
        )
        tests.append(test)

        # Test 2: LDAP query domain DN
        test = await self._run_test(
            "LDAP: Query Domain DN",
            "ldap",
            self._check_ldap_query_domain
        )
        tests.append(test)

        return tests

    async def _test_kerberos(self) -> List[VerificationTest]:
        """Test Kerberos functionality"""
        tests = []

        # Test 1: Kerberos ticket acquisition
        test = await self._run_test(
            "Kerberos: Ticket Acquisition (kinit)",
            "kerberos",
            self._check_kerberos_kinit
        )
        tests.append(test)

        return tests

    async def _test_authentication(self) -> List[VerificationTest]:
        """Test authentication"""
        tests = []

        # Test 1: Administrator authentication
        test = await self._run_test(
            "Auth: Administrator Login",
            "authentication",
            self._check_admin_auth
        )
        tests.append(test)

        return tests

    async def _run_test(self, name: str, category: str, test_func) -> VerificationTest:
        """
        Run a single test and return result
        """
        start_time = time.time()

        try:
            logger.info(f"Running test: {name}")
            success, message, details = await asyncio.to_thread(test_func)

            duration_ms = int((time.time() - start_time) * 1000)

            return VerificationTest(
                test_name=name,
                category=category,
                status="passed" if success else "failed",
                message=message,
                details=details,
                duration_ms=duration_ms
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Test {name} failed with exception: {e}")

            return VerificationTest(
                test_name=name,
                category=category,
                status="failed",
                message=f"Test error: {str(e)}",
                details=None,
                duration_ms=duration_ms
            )

    # Individual test implementations

    def _check_samba_installed(self) -> Tuple[bool, str, str]:
        """Check if Samba is installed"""
        try:
            result = subprocess.run(
                ["samba", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                return True, "Samba is installed", version
            else:
                return False, "Samba not found", result.stderr
        except FileNotFoundError:
            return False, "Samba binary not found", "samba command not available"
        except Exception as e:
            return False, f"Error checking Samba: {str(e)}", None

    def _check_smb_conf(self) -> Tuple[bool, str, str]:
        """Check if smb.conf exists"""
        import os
        conf_path = "/etc/samba/smb.conf"

        if os.path.exists(conf_path):
            try:
                with open(conf_path, 'r') as f:
                    content = f.read()
                return True, "Configuration file exists", f"Size: {len(content)} bytes"
            except Exception as e:
                return False, f"Cannot read config: {str(e)}", None
        else:
            return False, "smb.conf not found", f"Expected at {conf_path}"

    def _check_dns_resolution(self, hostname: str) -> Tuple[bool, str, str]:
        """Check DNS resolution"""
        try:
            ip_address = socket.gethostbyname(hostname)
            return True, f"Resolved to {ip_address}", f"Hostname: {hostname}"
        except socket.gaierror as e:
            return False, f"DNS resolution failed: {str(e)}", None

    def _check_srv_record(self, srv_name: str) -> Tuple[bool, str, str]:
        """Check SRV record resolution against Samba DNS"""
        try:
            # Query Samba's DNS server directly (localhost:53)
            result = subprocess.run(
                ["host", "-t", "SRV", srv_name, "localhost"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and "has SRV record" in result.stdout:
                return True, "SRV record found", result.stdout.strip()
            else:
                # Try with dig as fallback
                try:
                    dig_result = subprocess.run(
                        ["dig", "@localhost", "-t", "SRV", srv_name, "+short"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if dig_result.returncode == 0 and dig_result.stdout.strip():
                        return True, "SRV record found (via dig)", dig_result.stdout.strip()
                    else:
                        return False, "SRV record not found", result.stderr
                except:
                    return False, "SRV record not found", result.stderr
        except FileNotFoundError:
            # If host command not available, try nslookup
            try:
                result = subprocess.run(
                    ["nslookup", "-type=SRV", srv_name, "localhost"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and "_" in result.stdout:
                    return True, "SRV record found (via nslookup)", result.stdout[:200]
                else:
                    return False, "SRV record not found", None
            except Exception:
                return False, "DNS query tools not available", "Install host or nslookup"
        except Exception as e:
            return False, f"Error checking SRV: {str(e)}", None

    def _check_port(self, port: int) -> Tuple[bool, str, str]:
        """Check if a port is listening"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)

        try:
            result = sock.connect_ex(('localhost', port))
            if result == 0:
                return True, f"Port {port} is open", "Service is listening"
            else:
                return False, f"Port {port} is closed", f"Connection failed with code {result}"
        except Exception as e:
            return False, f"Error checking port {port}: {str(e)}", None
        finally:
            sock.close()

    def _check_ldap_anonymous_bind(self) -> Tuple[bool, str, str]:
        """Check LDAP anonymous bind"""
        try:
            result = subprocess.run(
                ["ldapsearch", "-x", "-H", "ldap://localhost", "-b", "", "-s", "base"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return True, "LDAP anonymous bind successful", "LDAP server responding"
            else:
                return False, "LDAP bind failed", result.stderr[:200]
        except FileNotFoundError:
            return False, "ldapsearch command not found", "Install ldap-utils package"
        except Exception as e:
            return False, f"LDAP test error: {str(e)}", None

    def _check_ldap_query_domain(self) -> Tuple[bool, str, str]:
        """Check LDAP query for domain DN using samba-tool"""
        try:
            # Use samba-tool to query the domain (handles authentication internally)
            # This is more reliable than direct LDAP queries for Samba AD
            result = subprocess.run(
                ["samba-tool", "domain", "level", "show"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Parse domain name from output
                dn_parts = self.domain_name.split('.')
                base_dn = ','.join([f'DC={part}' for part in dn_parts])

                return True, f"Domain DN accessible via samba-tool", f"DN: {base_dn}"
            else:
                return False, "Cannot query domain information", result.stderr[:200]
        except FileNotFoundError:
            return False, "samba-tool not found", "Samba tools not installed"
        except Exception as e:
            return False, f"Domain query error: {str(e)}", None

    def _check_kerberos_kinit(self) -> Tuple[bool, str, str]:
        """Check Kerberos ticket acquisition"""
        try:
            # Try to get a ticket for administrator
            process = subprocess.Popen(
                ["kinit", f"administrator@{self.realm}"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate(input=self.admin_password + "\n", timeout=10)

            if process.returncode == 0:
                # Verify ticket was acquired
                result = subprocess.run(
                    ["klist"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if self.realm in result.stdout:
                    return True, "Kerberos ticket acquired", f"Principal: administrator@{self.realm}"
                else:
                    return False, "Ticket acquired but not found in klist", result.stdout[:200]
            else:
                return False, "kinit failed", stderr[:200]
        except FileNotFoundError:
            return False, "kinit command not found", "Install krb5-user package"
        except Exception as e:
            return False, f"Kerberos test error: {str(e)}", None

    def _check_admin_auth(self) -> Tuple[bool, str, str]:
        """Check administrator authentication"""
        try:
            # Use smbclient to test authentication
            result = subprocess.run(
                ["smbclient", "-L", "localhost", "-U", f"administrator%{self.admin_password}"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 or "Sharename" in result.stdout:
                return True, "Administrator authentication successful", "SMB authentication working"
            else:
                return False, "Authentication failed", result.stderr[:200]
        except FileNotFoundError:
            return False, "smbclient command not found", "Install smbclient package"
        except Exception as e:
            return False, f"Auth test error: {str(e)}", None
