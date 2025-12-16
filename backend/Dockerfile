FROM python:3.11-slim

WORKDIR /app

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies, Samba, and verification tools
RUN apt-get update && apt-get install -y \
    # Build essentials
    gcc \
    g++ \
    make \
    # Database client
    postgresql-client \
    # Samba and related packages
    samba \
    samba-common-bin \
    samba-dsdb-modules \
    winbind \
    # LDAP utilities for verification tests
    ldap-utils \
    # Kerberos client for verification tests
    krb5-user \
    # SMB client for verification tests
    smbclient \
    # DNS utilities for verification tests
    dnsutils \
    host \
    # Network utilities
    net-tools \
    iputils-ping \
    # Process management
    procps \
    # Text processing
    vim \
    nano \
    # Debugging tools
    lsof \
    && rm -rf /var/lib/apt/lists/*

# Create necessary Samba directories with proper permissions
RUN mkdir -p /var/lib/samba \
    && mkdir -p /var/log/samba \
    && mkdir -p /var/cache/samba \
    && mkdir -p /run/samba \
    && mkdir -p /etc/samba \
    && mkdir -p /var/log/adhub \
    && chmod 755 /var/lib/samba \
    && chmod 755 /var/log/samba \
    && chmod 755 /var/log/adhub

# Remove default smb.conf created by Samba installation
# This prevents conflicts during AD DC provisioning
RUN if [ -f /etc/samba/smb.conf ]; then \
        mv /etc/samba/smb.conf /etc/samba/smb.conf.original; \
        echo "Removed default smb.conf"; \
    fi

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy and set up entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose ports
# 8000 - FastAPI application
# 53 - DNS (if running Samba DNS)
# 88 - Kerberos
# 135 - MS-RPC
# 139 - NetBIOS
# 389 - LDAP
# 445 - SMB
# 464 - Kerberos password change
# 636 - LDAPS
# 3268 - Global Catalog
# 3269 - Global Catalog SSL
EXPOSE 8000 53 88 135 139 389 445 464 636 3268 3269

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health', timeout=5)" || exit 1

# Run the application as root (required for Samba operations)
# Note: Running as root in containers is acceptable since containers provide isolation
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
