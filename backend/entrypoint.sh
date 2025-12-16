#!/bin/bash
set -e

echo "==========================================="
echo "ADHub Backend Container Starting"
echo "==========================================="

# Create runtime directories if they don't exist
mkdir -p /var/run/samba
mkdir -p /var/log/adhub

# Check if Samba is provisioned by looking for smb.conf with AD DC configuration
if [ -f /etc/samba/smb.conf ]; then
    if grep -q "server role.*active directory domain controller" /etc/samba/smb.conf 2>/dev/null; then
        echo "✓ Samba AD DC configuration detected"
        echo "  Starting Samba services..."

        # Start Samba AD DC service
        if ! pgrep -x "samba" > /dev/null; then
            samba -D
            echo "  ✓ Samba AD DC started"
        else
            echo "  ✓ Samba AD DC already running"
        fi
    else
        echo "ℹ Samba configuration exists but not configured as AD DC"
    fi
else
    echo "ℹ No Samba configuration found - will be created during setup wizard"
fi

# Display Samba version
SAMBA_VERSION=$(samba --version 2>/dev/null || echo "Unknown")
echo "  Samba version: $SAMBA_VERSION"

echo "==========================================="
echo "Starting FastAPI application..."
echo "==========================================="

# Start the application
exec "$@"
