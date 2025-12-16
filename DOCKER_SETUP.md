# Docker Setup for ADHub

This document explains the Docker configuration for ADHub, including Samba installation and privilege management.

## Overview

ADHub runs in Docker containers with Samba Active Directory Domain Controller capabilities. The backend container includes a full Samba installation with all necessary tools for domain provisioning and verification.

## Container Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Host System                                             │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Docker Network (172.20.0.0/16)                    │ │
│  │                                                     │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │ │
│  │  │   Database   │  │   Backend    │  │ Frontend │ │ │
│  │  │  PostgreSQL  │  │   FastAPI    │  │  Vue 3   │ │ │
│  │  │              │  │   + Samba    │  │          │ │ │
│  │  │ 172.20.0.x   │  │ 172.20.0.10  │  │          │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────┘ │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Backend Container Configuration

### Installed Packages

The backend container includes:

**Samba Components:**
- `samba` - Main Samba server
- `samba-common-bin` - Common Samba binaries
- `samba-dsdb-modules` - Directory Service modules
- `winbind` - Windows integration service

**Verification Tools:**
- `ldap-utils` - LDAP client utilities (ldapsearch, ldapadd, etc.)
- `krb5-user` - Kerberos client tools (kinit, klist, etc.)
- `smbclient` - SMB client for testing
- `dnsutils` - DNS utilities (nslookup, dig, etc.)
- `host` - DNS lookup utility

**Additional Tools:**
- `net-tools` - Network utilities
- `procps` - Process management tools
- `lsof` - List open files

### Privileges and Capabilities

The backend container runs with **elevated privileges** required for Samba AD DC operations:

```yaml
privileged: true
cap_add:
  - NET_ADMIN       # Network administration
  - SYS_ADMIN       # System administration
  - DAC_OVERRIDE    # Bypass file permissions
  - DAC_READ_SEARCH # Read/search any file
  - CHOWN           # Change file ownership
  - FOWNER          # Bypass permission checks
  - SETUID          # Set user ID
  - SETGID          # Set group ID
```

**Why privileged mode?**
- Samba AD DC needs to bind to privileged ports (< 1024)
- DNS service requires port 53
- LDAP requires port 389
- Kerberos requires port 88
- File system operations require elevated permissions

**Is this safe?**
Yes, running as root in containers is acceptable because:
- Containers provide process isolation
- Filesystem is isolated from host
- Network is isolated via Docker networking
- This is a dedicated application container, not a general-purpose system

### Exposed Ports

The backend container exposes all necessary Samba AD DC ports:

| Port | Protocol | Service | Description |
|------|----------|---------|-------------|
| 8000 | TCP | FastAPI | Web API |
| 53 | TCP/UDP | DNS | Domain Name Service |
| 88 | TCP/UDP | Kerberos | Authentication |
| 135 | TCP | MS-RPC | Remote Procedure Call |
| 137 | UDP | NetBIOS-NS | NetBIOS Name Service |
| 138 | UDP | NetBIOS-DGM | NetBIOS Datagram |
| 139 | TCP | NetBIOS-SSN | NetBIOS Session |
| 389 | TCP | LDAP | Lightweight Directory Access |
| 445 | TCP | SMB | Server Message Block |
| 464 | TCP | Kerberos | Password Change |
| 636 | TCP | LDAPS | LDAP over SSL |
| 3268 | TCP | GC | Global Catalog |
| 3269 | TCP | GC-SSL | Global Catalog SSL |

### Persistent Volumes

Samba data is persisted across container restarts:

```yaml
volumes:
  - samba_lib:/var/lib/samba      # Domain database
  - samba_log:/var/log/samba      # Samba logs
  - samba_cache:/var/cache/samba  # Cache files
  - samba_config:/etc/samba       # Configuration
  - adhub_logs:/var/log/adhub     # Application logs
```

### Static IP Address

The backend container is assigned a static IP (`172.20.0.10`) for:
- Stable DNS server address
- Client machines can consistently point to this IP
- Kerberos requires stable hostname/IP mapping

## Entrypoint Script

The container uses a custom entrypoint script (`/entrypoint.sh`) that:

1. **Creates runtime directories**
   ```bash
   mkdir -p /var/run/samba
   mkdir -p /var/log/adhub
   ```

2. **Checks for existing Samba configuration**
   - Looks for `/etc/samba/smb.conf`
   - Detects AD DC configuration

3. **Starts Samba services (if provisioned)**
   ```bash
   samba -D  # Start in daemon mode
   ```

4. **Starts FastAPI application**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## Service Startup Flow

### First Time (No Domain Provisioned)

```
Container starts
  ↓
Entrypoint runs
  ↓
Check /etc/samba/smb.conf → Not found
  ↓
Skip Samba startup
  ↓
Start FastAPI only
  ↓
User accesses http://localhost:5173
  ↓
User runs Setup Wizard
  ↓
Domain provisioned via samba-tool
  ↓
Samba services started automatically
  ↓
Domain is ready!
```

### Subsequent Starts (Domain Already Provisioned)

```
Container starts
  ↓
Entrypoint runs
  ↓
Check /etc/samba/smb.conf → Found (AD DC config)
  ↓
Start Samba services (samba -D)
  ↓
Start FastAPI
  ↓
Both services running
  ↓
Domain is immediately available!
```

## Building the Container

### Build Command

```bash
docker-compose build backend
```

### Build Time

- **First build**: ~5-10 minutes (downloads and installs all packages)
- **Subsequent builds**: ~30 seconds (uses Docker cache)

### Image Size

- **Approximate size**: 800MB - 1GB
  - Python 3.11 base: ~150MB
  - Samba + tools: ~400MB
  - Python packages: ~200MB
  - Application code: ~50MB

## Managing Samba Services

### Check Samba Status

```bash
# Enter container
docker exec -it adhub-backend bash

# Check if Samba is running
pgrep samba

# View Samba processes
ps aux | grep samba

# Check service status
samba --show-build
```

### View Logs

```bash
# Samba logs
docker exec -it adhub-backend tail -f /var/log/samba/log.samba

# Provision logs
docker exec -it adhub-backend tail -f /var/log/adhub/provision.log

# FastAPI logs
docker-compose logs -f backend
```

### Manual Samba Control

```bash
# Start Samba
docker exec -it adhub-backend samba -D

# Stop Samba
docker exec -it adhub-backend killall samba

# Restart Samba
docker exec -it adhub-backend bash -c "killall samba; samba -D"
```

### Run samba-tool Commands

```bash
# List users
docker exec -it adhub-backend samba-tool user list

# List groups
docker exec -it adhub-backend samba-tool group list

# Domain info
docker exec -it adhub-backend samba-tool domain info localhost

# DNS queries
docker exec -it adhub-backend samba-tool dns query localhost example.com @ ALL
```

## Troubleshooting

### Port Conflicts

If you get port binding errors:

```bash
# Check what's using the ports
# Windows:
netstat -ano | findstr :389
netstat -ano | findstr :445

# Linux/Mac:
lsof -i :389
lsof -i :445

# Solution: Stop conflicting services or change ports in docker-compose.yml
```

### Permission Issues

If Samba operations fail with permission errors:

```bash
# Verify container is running privileged
docker inspect adhub-backend | grep Privileged

# Should show: "Privileged": true

# Check capabilities
docker inspect adhub-backend | grep CapAdd
```

### Samba Won't Start

```bash
# Check logs
docker exec -it adhub-backend tail -100 /var/log/samba/log.samba

# Verify configuration
docker exec -it adhub-backend testparm -s

# Check for port conflicts inside container
docker exec -it adhub-backend netstat -tulpn | grep -E '(389|445|88)'
```

### Container Crashes on Startup

```bash
# Check container logs
docker-compose logs backend

# Run container interactively
docker-compose run --rm backend bash

# Check entrypoint script
docker exec -it adhub-backend cat /entrypoint.sh
```

## Security Considerations

### Running as Root

**Q: Is it safe to run as root in the container?**

**A:** Yes, for this use case:
- ✅ Containers provide process isolation
- ✅ Limited to container filesystem
- ✅ Network isolation via Docker
- ✅ Samba requires elevated privileges
- ✅ Not exposing SSH or shell access to users
- ✅ Application validates all inputs

**Q: Can we run as non-root?**

**A:** Not practically for Samba AD DC:
- ❌ Cannot bind to privileged ports (53, 88, 389, 445)
- ❌ Cannot modify system files
- ❌ Cannot perform domain operations
- Alternative would require complex sudo configuration

### Network Exposure

**Important:** Only expose necessary ports to the host:
- Port 8000 (API) - Required for web UI
- Port 5173 (Frontend) - Required for development

**Samba ports** are exposed but should be:
- Protected by firewall on host
- Only accessible from trusted networks
- Not exposed to public internet

### Firewall Configuration

Recommended host firewall rules:

```bash
# Allow from local network only (example: 192.168.1.0/24)
# Adjust to your network

# LDAP
iptables -A INPUT -p tcp --dport 389 -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 389 -j DROP

# Kerberos
iptables -A INPUT -p tcp --dport 88 -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 88 -j DROP

# DNS
iptables -A INPUT -p udp --dport 53 -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -p udp --dport 53 -j DROP

# SMB
iptables -A INPUT -p tcp --dport 445 -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 445 -j DROP
```

## Production Deployment

### Recommendations

1. **Use host networking for production** (optional):
   ```yaml
   network_mode: host
   ```
   Benefits: Better performance, easier DNS setup
   Drawbacks: Less isolation

2. **Use volumes for backups**:
   ```bash
   # Backup Samba data
   docker run --rm -v adhub_samba_lib:/data -v $(pwd):/backup \
     alpine tar czf /backup/samba-backup.tar.gz /data
   ```

3. **Monitor logs**:
   - Set up log aggregation (ELK, Splunk, etc.)
   - Monitor Samba service health
   - Alert on authentication failures

4. **Regular updates**:
   ```bash
   # Rebuild with latest packages
   docker-compose build --no-cache backend
   ```

5. **Use secrets for passwords**:
   - Don't commit passwords to git
   - Use environment variables
   - Consider Docker secrets in production

## Summary

✅ **Complete Samba installation** in backend container
✅ **All verification tools** included
✅ **Privileged access** properly configured
✅ **Persistent storage** for domain data
✅ **Automatic service startup** after provisioning
✅ **Static IP** for DNS stability
✅ **All necessary ports** exposed

The Docker setup provides a **complete, production-ready** Samba AD DC environment with web-based management through ADHub!
