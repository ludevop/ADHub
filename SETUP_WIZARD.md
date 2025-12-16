# Samba AD Domain Controller Setup Wizard

## Overview

The ADHub Setup Wizard provides a comprehensive, step-by-step interface for provisioning a new Samba Active Directory Domain Controller with built-in verification tests.

## Wizard Steps

### 1. Welcome (Step 0)
- Introduction to the setup process
- Prerequisites overview
- System requirements
- Important warnings

### 2. Prerequisites Check (Step 1)
- **Automatic system validation:**
  - Samba installation check
  - System privileges verification
  - Existing domain detection
  - Disk space validation
  - Network connectivity test

- **Pass/Fail/Warning indicators** for each check
- **Re-run capability** to verify fixes
- **Blocks progression** if critical prerequisites fail

### 3. Domain Configuration (Step 2)
- **DNS Domain Name**: e.g., `example.com`
- **Kerberos Realm**: e.g., `EXAMPLE.COM` (auto-filled from domain)
- **NetBIOS Domain**: e.g., `EXAMPLE` (max 15 chars, auto-filled)
- **Domain Functional Level**: 2008 R2, 2012, or 2012 R2
- **Administrator Password**: With strength validation
- **Password Confirmation**: Must match

**Validation:**
- Password minimum 8 characters
- Must contain uppercase, lowercase, and numbers
- Real-time password match checking

### 4. DNS Configuration (Step 3)
- **DNS Backend Options:**
  - `SAMBA_INTERNAL` (recommended)
  - `BIND9_DLZ` (advanced)
  - `NONE` (external DNS)

- **DNS Forwarder**: External DNS server (e.g., 8.8.8.8)
- **Host IP**: Optional static IP specification

### 5. Review Configuration (Step 4)
- **Complete configuration review** before provisioning
- Organized display of all settings:
  - Domain settings
  - Administrator account
  - DNS configuration

- **Edit capability**: Jump back to configuration steps
- **Warning about irreversibility** of provisioning

### 6. Provision Domain (Step 5)
- **Automatic provisioning** using `samba-tool domain provision`
- **Real-time progress** indication
- **Output capture** (stdout/stderr)
- **Success/Failure** detection
- **Retry capability** on failure
- **Auto-advance** to verification on success

### 7. Verification Tests (Step 6) ⭐ **THE KEY FEATURE**

Comprehensive automated testing to ensure everything is working correctly.

#### Test Categories

**📋 Prerequisites Tests:**
- Samba installation verification
- Configuration file existence

**🌍 DNS Tests:**
- Domain name resolution
- LDAP SRV record (`_ldap._tcp.domain`)
- Kerberos SRV record (`_kerberos._tcp.domain`)

**⚙️ Service Port Tests:**
- Port 389 (LDAP)
- Port 636 (LDAPS)
- Port 88 (Kerberos)
- Port 445 (SMB)
- Port 53 (DNS)

**📂 LDAP Tests:**
- Anonymous LDAP bind
- Domain DN query
- Users container access

**🔐 Kerberos Tests:**
- Ticket acquisition (kinit)
- Ticket verification (klist)

**✅ Authentication Tests:**
- Administrator authentication
- SMB client connection

#### Test Results Display

- **Overall status**: Passed / Partial / Failed
- **Statistics**: Total, Passed, Failed, Skipped counts
- **Categorized tests** with expandable details
- **Individual test status** with icons (✓/✗/⚠)
- **Duration tracking** for each test
- **Detailed error messages** for failed tests
- **Troubleshooting tips** for common issues
- **Re-run capability** to verify fixes

#### Test Output Format

```
Category: DNS Services
├─ ✓ DNS: Resolve example.com (45ms)
│  └─ Resolved to 192.168.1.10
├─ ✓ DNS: LDAP SRV Record (52ms)
│  └─ SRV record found
└─ ✗ DNS: Kerberos SRV Record (2103ms)
   └─ DNS resolution failed: timeout
   Details: [Expandable technical details]
```

### 8. Complete (Step 7)
- **Success animation** with checkmark
- **Domain information summary**
- **Next steps** guidance
- **Quick tips** for domain management
- **Security reminders**
- **Navigate to dashboard** or re-run setup

## Backend Architecture

### API Endpoints

```python
# Setup status
GET /api/v1/setup/status

# Prerequisites check
POST /api/v1/setup/check-prerequisites

# Validate configuration
POST /api/v1/setup/validate-config
{
  "realm": "EXAMPLE.COM",
  "domain": "EXAMPLE",
  "domain_name": "example.com",
  ...
}

# Provision domain
POST /api/v1/setup/provision
{
  "realm": "EXAMPLE.COM",
  "domain": "EXAMPLE",
  "domain_name": "example.com",
  "admin_password": "SecurePass123!",
  "dns_backend": "SAMBA_INTERNAL",
  "dns_forwarder": "8.8.8.8",
  ...
}

# Run verification tests
POST /api/v1/setup/verify
{
  "domain_name": "example.com",
  "realm": "EXAMPLE.COM",
  "admin_password": "SecurePass123!"
}

# Get domain info
GET /api/v1/setup/domain-info
```

### Services

**`SambaProvisionService`** (`backend/app/services/samba/provision.py`):
- System prerequisites checking
- Domain provisioning via `samba-tool`
- Provision status tracking
- Output logging

**`SambaVerificationService`** (`backend/app/services/samba/verification.py`):
- Comprehensive test suite
- DNS resolution tests
- Port availability checks
- LDAP connectivity tests
- Kerberos ticket tests
- Authentication tests
- Test result aggregation

### Schemas

All request/response models defined in `backend/app/schemas/setup.py`:
- `DomainConfigSchema` - Domain configuration
- `PrerequisitesResponse` - Prerequisites check results
- `ProvisionResponse` - Provisioning status and output
- `VerificationResponse` - Test results
- `VerificationTest` - Individual test result

## Frontend Architecture

### Components

```
frontend/src/
├── views/
│   └── SetupWizard.vue          # Main wizard container
├── components/setup/
│   ├── WelcomeStep.vue          # Step 0
│   ├── PrerequisitesStep.vue    # Step 1
│   ├── DomainConfigStep.vue     # Step 2
│   ├── DNSConfigStep.vue        # Step 3
│   ├── ReviewStep.vue           # Step 4
│   ├── ProvisionStep.vue        # Step 5
│   ├── VerificationStep.vue     # Step 6 ⭐
│   └── CompleteStep.vue         # Step 7
├── stores/
│   └── setup.ts                 # Pinia state management
├── api/
│   └── setup.ts                 # API client
└── types/
    └── setup.ts                 # TypeScript types
```

### State Management

Pinia store (`useSetupStore`) manages:
- Current wizard step
- Domain configuration
- Prerequisites results
- Verification test results
- Provisioning status
- Loading states
- Error states

### Key Features

✅ **Progressive wizard** with step indicators
✅ **Form validation** with real-time feedback
✅ **Auto-fill** from domain name
✅ **Comprehensive error handling**
✅ **Retry mechanisms** for failed operations
✅ **Responsive design** for mobile/desktop
✅ **Accessibility** considerations

## Verification Tests - Deep Dive

### Test Execution Flow

1. **User triggers verification** (auto or manual)
2. **Backend instantiates** `SambaVerificationService`
3. **Tests run sequentially** by category
4. **Each test**:
   - Executes system command or connection attempt
   - Captures stdout/stderr
   - Measures duration
   - Returns structured result
5. **Results aggregated** and returned to frontend
6. **Frontend displays** categorized results with details

### Test Implementation Example

```python
async def _test_dns(self) -> List[VerificationTest]:
    """Test DNS configuration and resolution"""
    tests = []

    # Test 1: Resolve domain name
    test = await self._run_test(
        "DNS: Resolve example.com",
        "dns",
        lambda: self._check_dns_resolution(self.domain_name)
    )
    tests.append(test)

    return tests

def _check_dns_resolution(self, hostname: str) -> Tuple[bool, str, str]:
    """Check DNS resolution"""
    try:
        ip_address = socket.gethostbyname(hostname)
        return True, f"Resolved to {ip_address}", f"Hostname: {hostname}"
    except socket.gaierror as e:
        return False, f"DNS resolution failed: {str(e)}", None
```

### Adding Custom Tests

To add a new verification test:

1. **Add test method** to `SambaVerificationService`
2. **Call from** `run_all_tests()`
3. **Return** `VerificationTest` object
4. **Frontend automatically** displays the result

Example:
```python
async def _test_custom_feature(self) -> List[VerificationTest]:
    """Test custom feature"""
    tests = []

    test = await self._run_test(
        "Custom: My Feature Test",
        "custom",  # Category
        self._check_my_feature
    )
    tests.append(test)

    return tests

def _check_my_feature(self) -> Tuple[bool, str, str]:
    """Check if custom feature works"""
    try:
        # Your test logic here
        return True, "Feature works!", "Details about the test"
    except Exception as e:
        return False, f"Feature failed: {str(e)}", None
```

## Security Considerations

### Password Handling
- Passwords **never logged** or stored in plain text
- Passed securely to `samba-tool` via stdin
- Masked in UI with password inputs
- Confirmation required to prevent typos

### Privilege Requirements
- Setup requires **root/administrator** privileges
- Samba provisioning modifies system files
- Port binding requires elevated permissions

### Validation
- **Backend validation** of all inputs
- **Pydantic schemas** ensure type safety
- **Domain name validation** (RFC compliance)
- **Password strength** requirements enforced

## Troubleshooting

### Common Issues

**Prerequisites Fail:**
- Install Samba: `apt-get install samba`
- Ensure running as root: `sudo -i`
- Check disk space: `df -h`

**Provision Fails:**
- Check logs: `/var/log/adhub/provision.log`
- Verify no existing config: `/etc/samba/smb.conf`
- Ensure ports are free: `netstat -tulpn | grep -E '(389|445|88)'`

**Verification Tests Fail:**
- **DNS tests**: Check `/etc/resolv.conf`, ensure DNS forwarder is reachable
- **Port tests**: Check firewall rules, ensure services started
- **LDAP tests**: Install `ldap-utils`, verify Samba is running
- **Kerberos tests**: Install `krb5-user`, check time sync
- **Auth tests**: Install `smbclient`, verify password is correct

### Re-running Tests

Tests can be re-run **multiple times**:
1. After fixing issues
2. After service restarts
3. To verify stability

## Future Enhancements

- [ ] Multi-DC support (additional domain controllers)
- [ ] Domain join verification
- [ ] Group Policy verification tests
- [ ] Replication status checks
- [ ] Performance benchmarks
- [ ] Automated backups during provision
- [ ] Rollback capability
- [ ] Email notifications for test results
- [ ] Export test results as PDF/JSON

## Summary

The ADHub Setup Wizard with verification tests provides:

✅ **Complete automation** of Samba AD DC provisioning
✅ **Safety checks** at every step
✅ **Comprehensive testing** to ensure correctness
✅ **User-friendly interface** for complex operations
✅ **Detailed feedback** for troubleshooting
✅ **Production-ready** domain controllers

The **verification tests** are the standout feature, providing confidence that your Samba AD DC is fully functional before putting it into production use.
