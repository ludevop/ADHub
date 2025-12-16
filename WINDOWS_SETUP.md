# Running ADHub on Windows

This guide covers Windows-specific setup considerations and how to handle port conflicts.

## Port Conflicts on Windows

### The Issue

Windows uses several ports that Samba AD DC also needs:

| Port | Windows Service | Samba Service |
|------|----------------|---------------|
| 135 | RPC Endpoint Mapper | MS-RPC |
| 139 | NetBIOS Session | NetBIOS Session |
| 445 | SMB/CIFS File Sharing | SMB |
| 53* | DNS Client (sometimes) | DNS |

**This causes Docker port binding errors** when trying to expose these ports from the container to the host.

### The Solution

**ADHub's default configuration does NOT expose Samba ports to the host.** This avoids conflicts while keeping full functionality:

✅ **Setup wizard works** - All operations happen inside the container
✅ **Verification tests work** - Tests run inside the container
✅ **Domain provisioning works** - Samba services run on container's localhost
✅ **No port conflicts** - Windows services and Samba coexist peacefully

## How It Works

### Container vs Host

```
┌─────────────────────────────────────────────────┐
│  Windows Host (Your PC)                         │
│  Ports: 135, 139, 445 (Used by Windows)        │
│                                                  │
│  ┌───────────────────────────────────────────┐ │
│  │  Docker Container (adhub-backend)         │ │
│  │  IP: 172.20.0.10                          │ │
│  │  Ports: 53, 88, 135, 139, 389, 445       │ │
│  │                                            │ │
│  │  ✓ Samba running on container localhost  │ │
│  │  ✓ FastAPI can access Samba             │ │
│  │  ✓ Tests run against container localhost │ │
│  └───────────────────────────────────────────┘ │
│                                                  │
│  Only Port 8000 exposed to host ✓              │
└─────────────────────────────────────────────────┘
```

### What You Can Access

**From Windows Host:**
- ✅ Web UI: http://localhost:5173
- ✅ API: http://localhost:8000
- ❌ Samba services (not exposed, by design)

**Inside Container:**
- ✅ All Samba services on localhost
- ✅ All Samba services on 172.20.0.10 (container IP)

**From Other Docker Containers:**
- ✅ All Samba services via 172.20.0.10

## Use Cases

### Use Case 1: Just Running the Setup Wizard (Default)

**Scenario:** You want to use the web UI to provision and manage a Samba domain.

**Configuration:** Use default docker-compose.yml (no changes needed)

**What works:**
- ✅ Web UI access
- ✅ Domain provisioning
- ✅ Verification tests
- ✅ User/group management (via API)
- ✅ Share management (via API)

**Limitations:**
- ❌ Cannot join Windows host to the domain
- ❌ Cannot access LDAP from host
- ❌ Cannot access file shares from host

**Is this enough?**
**YES**, for development and testing the wizard!

### Use Case 2: Joining Windows Clients to Domain

**Scenario:** You want Windows machines (including the host) to join this domain.

**Configuration:** Expose Samba ports to host (on different ports)

**Steps:**

1. Edit `docker-compose.yml`
2. Uncomment and modify port mappings:

```yaml
ports:
  - "8000:8000"
  # Map to ports NOT used by Windows
  - "10053:53"       # DNS (use 10053 on host)
  - "10053:53/udp"   # DNS UDP
  - "10088:88"       # Kerberos
  - "10088:88/udp"   # Kerberos UDP
  - "10389:389"      # LDAP
  - "10445:445"      # SMB
  - "10636:636"      # LDAPS
```

3. Restart: `docker-compose down && docker-compose up`

4. Configure Windows to use these ports (see below)

### Use Case 3: Production Deployment (Linux Server)

**Scenario:** Deploy to a Linux server (no Windows port conflicts).

**Configuration:** Can expose standard Samba ports

**Steps:**

1. On Linux server, edit `docker-compose.yml`:

```yaml
ports:
  - "8000:8000"
  - "53:53"      # No conflict on Linux
  - "53:53/udp"
  - "88:88"
  - "88:88/udp"
  - "389:389"
  - "445:445"    # No conflict on Linux
  - "636:636"
```

2. Clients can join domain normally using server's IP

## Joining Windows to Domain (Advanced)

If you've exposed Samba ports to non-standard ports, here's how to join Windows:

### Option A: Using Mapped Ports (Complex)

This is **not straightforward** because Windows expects standard ports. You'd need:

1. **Hosts file entry** pointing domain to localhost
2. **Port forwarding rules** to redirect standard ports to mapped ports
3. **NAT/firewall configuration**

**Recommendation:** Don't do this on Windows host. Use Linux server instead.

### Option B: VM or Separate Windows Machine

1. **Create a VM** (VirtualBox, VMware, Hyper-V)
2. **Bridge network** to access host
3. **Point DNS** to host IP (where container runs)
4. **Join domain** using host's IP address

**Example:**
```powershell
# On VM, set DNS to host IP
Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses "192.168.1.100"

# Join domain
Add-Computer -DomainName "example.com" -Credential (Get-Credential)
```

### Option C: Use Linux for Production

**Best practice:**
- Develop/test on Windows (using wizard only)
- Deploy to Linux server for production
- Join Windows clients to Linux server

## Checking Port Conflicts

### See What's Using Ports on Windows

```powershell
# Check if port 445 is in use
netstat -ano | findstr :445

# Check port 135
netstat -ano | findstr :135

# Check port 139
netstat -ano | findstr :139

# List all listening ports
netstat -ano | findstr LISTENING
```

**Expected output:**
```
TCP    0.0.0.0:135            0.0.0.0:0              LISTENING       1234
TCP    0.0.0.0:445            0.0.0.0:0              LISTENING       4
```

These are Windows services - **do not disable them!**

### Windows Services Using These Ports

```powershell
# Get service info
Get-Service -Name Server    # Port 445 (SMB)
Get-Service -Name RpcSs     # Port 135 (RPC)
Get-Service -Name LanmanServer  # Port 139
```

**Do NOT stop these services** - Windows needs them!

## Troubleshooting

### Error: "Ports are not available"

**Full error:**
```
Error response from daemon: ports are not available:
exposing port TCP 0.0.0.0:445 -> 127.0.0.1:0:
listen tcp 0.0.0.0:445: bind: Only one usage of each socket address
```

**Solution:**
✅ Use default configuration (ports NOT exposed)
✅ This is expected and correct on Windows

### Can't Access Samba from Host

**Issue:** Trying to connect to `localhost:389` (LDAP) from Windows host fails.

**Why:** Samba ports are not exposed to host by default.

**Solutions:**
1. **If just testing wizard:** This is expected, use the web UI
2. **If need access:** Expose ports on different numbers (see Use Case 2)
3. **If production:** Deploy to Linux server

### Verification Tests Fail

**Issue:** Tests report ports not listening.

**Check:**
```bash
# Enter container
docker exec -it adhub-backend bash

# Check ports INSIDE container
netstat -tulpn | grep -E '(389|445|88|53)'

# Should see Samba listening
```

**If ports not listening inside container:**
- Check Samba is running: `pgrep samba`
- Check logs: `tail /var/log/samba/log.samba`
- Start manually: `samba -D`

### Container Won't Start

**Error:** Port binding error even with default config.

**Solution:**
```bash
# Stop all containers
docker-compose down

# Remove any orphaned containers
docker container prune

# Rebuild
docker-compose build --no-cache

# Start fresh
docker-compose up
```

## Development Workflow on Windows

### Recommended Workflow

1. **Develop on Windows** ✅
   - Use web UI to test wizard
   - Samba runs in container
   - No port conflicts
   - Fast iteration

2. **Test joining clients on Linux VM** ✅
   - Spin up Linux VM or server
   - Deploy ADHub to Linux
   - Join Windows clients to Linux server
   - Test full AD functionality

3. **Deploy to Linux production** ✅
   - Use Linux server
   - Expose standard Samba ports
   - Production-ready setup

### What NOT to Do

❌ **Don't disable Windows services** to free ports
❌ **Don't try to join Windows host** to domain in container
❌ **Don't expose Samba ports** on Windows (causes conflicts)

## WSL2 Considerations

If you're using Docker with WSL2:

### Advantages
- ✅ Better Linux compatibility
- ✅ Faster Docker performance
- ✅ True Linux environment

### Port Behavior
- Ports exposed from containers go through WSL2 → Windows
- Same port conflicts apply
- Default configuration still works best

### WSL2 Access

You can access Samba services from WSL2:

```bash
# From WSL2 shell
ldapsearch -x -H ldap://172.20.0.10 -b "" -s base

# Test SMB
smbclient -L 172.20.0.10 -U administrator
```

## Summary

### For Windows Development (Recommended)

```yaml
# docker-compose.yml - Default configuration
ports:
  - "8000:8000"  # Only expose API
  # Samba ports NOT exposed (avoid conflicts)
```

**What this gives you:**
- ✅ Full web UI functionality
- ✅ Complete setup wizard
- ✅ All verification tests pass
- ✅ No port conflicts
- ✅ Fast development

**What you CAN'T do:**
- ❌ Join Windows host to domain
- ❌ Access Samba from host directly

**Solution for full testing:**
- Deploy to Linux server or VM
- OR run in WSL2 and access from there

### For Production (Linux Server)

```yaml
# docker-compose.yml - Production on Linux
ports:
  - "8000:8000"
  - "53:53"      # Can expose standard ports
  - "88:88"      # No conflicts on Linux
  - "389:389"
  - "445:445"
  - "636:636"
```

**Perfect for:**
- ✅ Production deployment
- ✅ Joining Windows clients
- ✅ Full AD DC functionality

---

**Bottom line:** The default configuration is **perfect for Windows development**. For production or client testing, use a Linux server.
