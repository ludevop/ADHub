# Samba Web Management Application - Comprehensive Implementation Plan

## Executive Summary

A modern web-based management interface for Samba Active Directory Domain Controllers and file servers. The application provides intuitive web UI for managing SMB shares, Active Directory users/groups, Group Policy Objects, DNS, and all other Samba features traditionally managed via command-line tools.

**Deployment**: Docker container with optional dedicated Linux system installation
**Target Users**: System administrators managing Samba infrastructure
**Core Value**: Replicate Windows "Active Directory Users and Computers" functionality with additional Samba-specific features through a modern web interface

---

## Technology Stack (Final Decision)

### Backend: **FastAPI (Python 3.11+)**

**Rationale:**
- **Superior Samba Integration**: Native `python-samba` library provides direct API access to Samba internals
- **Linux Administration Sweet Spot**: Python is the de facto standard for Linux system administration
- **Performance**: Async capabilities handle I/O-bound operations efficiently (sufficient for admin interface)
- **Type Safety**: Pydantic models provide runtime validation and automatic OpenAPI documentation
- **Development Velocity**: Concise syntax and rich ecosystem accelerate development

**Key Libraries:**
- `fastapi` - Web framework
- `python-samba` - Direct Samba API access (official Samba Python bindings)
- `ldap3` - LDAP client for AD authentication
- `pydantic` v2 - Data validation and settings management
- `sqlalchemy` v2 - Database ORM
- `alembic` - Database migrations
- `python-jose` - JWT token handling
- `uvicorn` - ASGI server
- `asyncio` - Async subprocess execution
- `watchfiles` - Configuration file monitoring
- `redis` - Caching and rate limiting

### Frontend: **Vue 3 + TypeScript**

**Rationale:**
- User preference for Vue
- Simpler learning curve than React
- Excellent TypeScript support
- Composition API provides clean code organization
- Strong ecosystem for admin interfaces

**Key Libraries:**
- `vue` v3 - Frontend framework
- `typescript` v5 - Type safety
- `pinia` - State management
- `vue-router` v4 - Routing
- `axios` - HTTP client
- `vueuse` - Composition utilities
- `vue-i18n` - Internationalization
- `socket.io-client` - Real-time updates

**UI Framework: Ant Design Vue**
- Comprehensive component library
- Enterprise-grade UI components
- Excellent table/form components for admin interfaces
- Good documentation and active maintenance
- Built-in themes and customization

### Database: **PostgreSQL 16**

**Rationale:**
- **Cached user data** from Samba AD (for performance and audit trail)
- User session management
- Audit logging
- Application preferences
- Scheduled task tracking
- **NOT for authentication** (users authenticate against Samba AD via LDAP)
- **NOT for Samba data** (uses Samba's native LDB/TDB databases)

### Real-Time Communication: **Server-Sent Events (SSE)**

**Rationale:**
- Unidirectional server-to-client updates (sufficient for monitoring)
- Simpler than WebSockets
- Automatic reconnection
- Works over HTTP (easier firewall traversal)
- Use cases: Log streaming, connection monitoring, service status

### Caching/Session: **Redis 7**

**Use Cases:**
- Session storage
- Rate limiting
- Caching expensive Samba queries (user lists, group memberships)
- Real-time data aggregation

### Deployment: **Docker + Docker Compose**

**Container Architecture:**
- Multi-stage build for optimized image size
- Alpine Linux base (minimal footprint)
- Separate containers for: web app, PostgreSQL, Redis
- Optional: Dedicated Samba container or host integration

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
│                     (Vue 3 + TypeScript)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS (REST API + SSE)
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    Nginx Reverse Proxy                       │
│              (TLS Termination, Rate Limiting)                │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   FastAPI Application                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              API Layer (REST Endpoints)                 │ │
│  └────────────┬───────────────────────────────────────────┘ │
│               │                                              │
│  ┌────────────▼───────────────────────────────────────────┐ │
│  │         Service Layer (Business Logic)                  │ │
│  │  - AuthService (LDAP authentication)                   │ │
│  │  - SambaService (python-samba integration)             │ │
│  │  - ShareService (share management)                      │ │
│  │  - UserService (AD user/group management)              │ │
│  │  - GPOService (Group Policy)                            │ │
│  │  - DNSService (DNS management)                          │ │
│  │  - MonitoringService (logs, connections)               │ │
│  └────────────┬───────────────────────────────────────────┘ │
│               │                                              │
│  ┌────────────▼───────────────────────────────────────────┐ │
│  │    Samba Integration Layer                              │ │
│  │  - LDAP client (ldap3) for authentication              │ │
│  │  - Python-samba bindings (SamDB, LDB operations)       │ │
│  │  - CLI wrapper (samba-tool, smbcontrol, testparm)      │ │
│  │  - Config parser (smb.conf management)                 │ │
│  └────────────┬───────────────────────────────────────────┘ │
└───────────────┼──────────────────────────────────────────────┘
                │
         ┌──────┴──────┬────────────────┐
         │             │                │
┌────────▼────┐   ┌────▼──────────┐   ┌▼──────────────────┐
│  PostgreSQL │   │ Samba System  │   │  Samba AD LDAP    │
│  (Cache/    │   │ - smb.conf    │   │  (Port 389/636)   │
│   Audit)    │   │ - LDB DBs     │   │  - Authentication │
└─────────────┘   │ - TDB DBs     │   │  - User lookups   │
                  │ - sysvol/     │   │  - Group queries  │
┌─────────────┐   │ - Daemons     │   └───────────────────┘
│    Redis    │   └───────────────┘
│  (Cache)    │
└─────────────┘
```

### Directory Structure

```
adhub/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application entry
│   │   ├── config.py                  # Configuration management
│   │   ├── dependencies.py            # Dependency injection
│   │   │
│   │   ├── api/                       # API layer
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── auth.py
│   │   │   │   │   ├── shares.py
│   │   │   │   │   ├── users.py
│   │   │   │   │   ├── groups.py
│   │   │   │   │   ├── dns.py
│   │   │   │   │   ├── gpo.py
│   │   │   │   │   ├── monitoring.py
│   │   │   │   │   └── system.py
│   │   │   │   └── router.py
│   │   │
│   │   ├── core/                      # Core functionality
│   │   │   ├── __init__.py
│   │   │   ├── security.py            # Auth, JWT, RBAC
│   │   │   ├── exceptions.py          # Custom exceptions
│   │   │   ├── logging.py             # Logging configuration
│   │   │   └── events.py              # SSE event system
│   │   │
│   │   ├── services/                  # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── samba/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── samdb.py           # SamDB operations
│   │   │   │   ├── cli.py             # samba-tool wrapper
│   │   │   │   ├── config.py          # smb.conf management
│   │   │   │   └── validation.py      # Input validation
│   │   │   ├── share_service.py
│   │   │   ├── user_service.py
│   │   │   ├── group_service.py
│   │   │   ├── dns_service.py
│   │   │   ├── gpo_service.py
│   │   │   └── monitoring_service.py
│   │   │
│   │   ├── models/                    # Database models
│   │   │   ├── __init__.py
│   │   │   ├── user.py                # App users (not Samba)
│   │   │   ├── audit.py               # Audit logs
│   │   │   ├── session.py             # User sessions
│   │   │   └── config.py              # App configuration
│   │   │
│   │   ├── schemas/                   # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── share.py
│   │   │   ├── user.py
│   │   │   ├── group.py
│   │   │   ├── dns.py
│   │   │   ├── gpo.py
│   │   │   └── common.py
│   │   │
│   │   └── utils/                     # Utilities
│   │       ├── __init__.py
│   │       ├── validators.py
│   │       ├── formatters.py
│   │       └── cache.py
│   │
│   ├── alembic/                       # Database migrations
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   │
│   │   ├── router/
│   │   │   └── index.ts
│   │   │
│   │   ├── stores/                    # Pinia stores
│   │   │   ├── auth.ts
│   │   │   ├── shares.ts
│   │   │   ├── users.ts
│   │   │   └── monitoring.ts
│   │   │
│   │   ├── views/                     # Page components
│   │   │   ├── Dashboard.vue
│   │   │   ├── Shares/
│   │   │   │   ├── ShareList.vue
│   │   │   │   ├── ShareCreate.vue
│   │   │   │   └── ShareEdit.vue
│   │   │   ├── Users/
│   │   │   │   ├── UserList.vue
│   │   │   │   ├── UserCreate.vue
│   │   │   │   └── UserEdit.vue
│   │   │   ├── Groups/
│   │   │   ├── DNS/
│   │   │   ├── GPO/
│   │   │   ├── Monitoring/
│   │   │   └── Settings/
│   │   │
│   │   ├── components/                # Reusable components
│   │   │   ├── layout/
│   │   │   │   ├── AppLayout.vue
│   │   │   │   ├── Sidebar.vue
│   │   │   │   └── Header.vue
│   │   │   ├── common/
│   │   │   │   ├── DataTable.vue
│   │   │   │   ├── FormField.vue
│   │   │   │   └── PermissionEditor.vue
│   │   │   └── samba/
│   │   │       ├── SharePermissions.vue
│   │   │       ├── UserSelector.vue
│   │   │       └── GroupSelector.vue
│   │   │
│   │   ├── api/                       # API client
│   │   │   ├── client.ts
│   │   │   ├── shares.ts
│   │   │   ├── users.ts
│   │   │   └── ...
│   │   │
│   │   ├── types/                     # TypeScript types
│   │   ├── composables/               # Vue composables
│   │   ├── utils/
│   │   └── assets/
│   │
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── Dockerfile
│
├── docker-compose.yml
├── docker-compose.dev.yml
├── nginx/
│   ├── nginx.conf
│   └── ssl/                           # SSL certificates
├── docs/
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── USER_GUIDE.md
└── README.md
```

---

## Core Features Implementation Plan

### Phase 1: Foundation & Authentication (Weeks 1-2)

#### 1.1 Project Setup
- Initialize FastAPI backend with project structure
- Initialize Vue 3 frontend with Vite
- Configure Docker Compose with PostgreSQL and Redis
- Set up development environment
- Configure linting (Ruff for Python, ESLint for TypeScript)
- Set up pre-commit hooks

#### 1.2 Database & Models
- Design database schema for:
  - **Cached AD users** (no passwords - source of truth is Samba AD)
  - User sessions (JWT token tracking)
  - Audit logs
  - Application configuration
  - User preferences
- Create Alembic migrations
- Implement SQLAlchemy models

#### 1.3 Authentication & Authorization
- **LDAP Authentication Integration**:
  - Configure LDAP connection to Samba AD (ldap3 library)
  - Implement user authentication via LDAP bind
  - Query user attributes (displayName, mail, memberOf)
  - Extract group memberships from LDAP
- **Group-to-Role Mapping**:
  - Map AD security groups to application roles
  - Design role hierarchy:
    - **Super Admin**: Domain Admins, Enterprise Admins
    - **Domain Admin**: IT Staff, Samba Admins
    - **Share Admin**: File Server Admins
    - **Auditor**: Security Auditors
  - Store role mappings in configuration
- **JWT Token Management**:
  - Generate JWT tokens after successful LDAP authentication
  - Include username, email, and mapped roles in token
  - Short-lived access tokens (15 min)
  - Refresh tokens (7 days)
- **Session Management**:
  - Store active sessions in Redis
  - Token revocation support
  - Session timeout handling
- Create middleware for authentication
- Implement CSRF protection
- **Sync AD users to local cache** for audit trail and preferences

#### 1.4 Samba Integration Foundation
- Create Python wrapper around samba-tool CLI
- Implement SamDB connection management
- Create configuration parser for smb.conf
- Implement validation utilities for Samba-specific inputs
- Test connectivity to Samba services

#### 1.5 Frontend Foundation
- Create layout components (sidebar, header, footer)
- Implement router with route guards
- Create Pinia stores for auth state
- Implement API client with axios interceptors
- Create login page
- Set up Ant Design Vue theme

### Phase 2: Share Management (Weeks 3-4)

#### 2.1 Backend - Share Service
- Implement share CRUD operations:
  - List all shares (parse smb.conf + net conf list)
  - Get share details
  - Create new share
  - Update share configuration
  - Delete share
- Implement share validation:
  - Path existence checks
  - Permission validation
  - Name uniqueness
- Configuration management:
  - Backup smb.conf before changes
  - Use testparm for validation
  - Reload Samba services gracefully

#### 2.2 Backend - Share Permissions
- Implement user/group permission assignment
- Windows ACL support (via smbcacls)
- Permission visualization endpoint
- Host-based access control (hosts allow/deny)
- Guest access configuration

#### 2.3 Frontend - Share Management UI
- Share list view with data table:
  - Columns: Name, Path, Users, Status, Actions
  - Sorting and filtering
  - Pagination (server-side)
  - Search functionality
- Share create form:
  - Basic info (name, path, comment)
  - Access control (users, groups, hosts)
  - Advanced options (guest access, browseable, etc.)
  - Directory picker
- Share edit form (similar to create)
- Share delete confirmation dialog
- Permission editor component
- Bulk operations (enable/disable multiple shares)

#### 2.4 Configuration Validation
- Real-time testparm validation
- Display warnings/errors before applying
- Configuration diff viewer (show changes)
- Rollback capability

### Phase 3: User & Group Management (Weeks 5-7)

#### 3.1 Backend - User Service
- Using python-samba SamDB:
  - List users with pagination and filtering
  - Create user with attributes (givenName, sn, mail, etc.)
  - Update user attributes
  - Delete user
  - Enable/disable user account
  - Password operations (set, change, reset)
  - Unlock account
  - Password policy enforcement
  - User search (by name, email, sAMAccountName)
- Group membership management:
  - List user's groups
  - Add user to groups
  - Remove user from groups

#### 3.2 Backend - Group Service
- Group CRUD operations:
  - List groups
  - Create group (with optional GID)
  - Update group (name, description)
  - Delete group
- Group membership:
  - List group members
  - Add members (bulk support)
  - Remove members (bulk support)
- Nested group support

#### 3.3 Backend - OU Management
- OU CRUD operations:
  - List OUs in tree structure
  - Create OU
  - Delete OU (with recursive option)
  - Move objects between OUs
- OU object listing

#### 3.4 Frontend - User Management UI
- User list view:
  - Data table with: Username, Full Name, Email, Status, Groups, Last Login
  - Advanced filtering (by OU, group, status)
  - Bulk operations (enable/disable, delete)
  - Export to CSV
- User create form:
  - Basic info (username, password, name, email)
  - Password generator
  - Password strength meter
  - OU selection
  - Group membership
  - Account options (must change password, cannot change password, etc.)
- User edit form
- Password reset dialog
- Group assignment modal

#### 3.5 Frontend - Group Management UI
- Group list view with hierarchy
- Group create/edit forms
- Member management interface:
  - Current members list
  - Add members dialog (search users)
  - Remove members
- Nested group visualization

#### 3.6 Frontend - OU Management UI
- OU tree view component
- Create OU dialog
- Move objects between OUs (drag & drop)
- Delete OU with confirmation

### Phase 4: DNS Management (Week 8)

#### 4.1 Backend - DNS Service
- Zone management:
  - List zones
  - Create zone
  - Delete zone
  - Zone details
- Record management:
  - List records in zone
  - Add record (A, AAAA, CNAME, MX, TXT, SRV, PTR)
  - Update record
  - Delete record
  - Query record
- Validation:
  - DNS name validation
  - IP address validation
  - Record type-specific validation

#### 4.2 Frontend - DNS Management UI
- Zone list view
- Zone create/delete dialogs
- Record list view (grouped by type)
- Record create/edit forms (type-specific)
- DNS query tool (troubleshooting)
- Bulk record import (CSV/zone file)

### Phase 5: Group Policy Management (Week 9-10)

#### 5.1 Backend - GPO Service
- GPO operations:
  - List GPOs
  - Create empty GPO
  - Delete GPO
  - Get GPO details
  - Fetch GPO from domain
- GPO linking:
  - Link GPO to container (OU, domain)
  - Unlink GPO
  - List GPO links
- Specific policy management:
  - MOTD (Message of the Day)
  - Issue file
  - Access policies
  - OpenSSH settings

#### 5.2 Frontend - GPO Management UI
- GPO list view
- GPO create dialog
- GPO editor (basic policies)
- GPO link management
- Policy templates

### Phase 6: Monitoring & Diagnostics (Week 11-12)

#### 6.1 Backend - Monitoring Service
- Real-time monitoring:
  - Service status (smbd, nmbd, winbindd)
  - Active connections (smbstatus parsing)
  - File locks
  - Resource usage (CPU, memory, disk, network)
- Log management:
  - Stream logs via SSE
  - Log filtering and search
  - Log level configuration
- Health checks:
  - Database integrity (dbcheck)
  - Configuration validation (testparm)
  - Sysvol ACL check (ntacl sysvolcheck)
- Connection management:
  - List active sessions
  - Kill connection

#### 6.2 Backend - Audit Logging
- Log all administrative actions:
  - User: who performed action
  - Action: what was done
  - Target: what was affected
  - Timestamp
  - Result: success/failure
  - IP address
- Audit log API:
  - List logs with filtering
  - Export logs
  - Log retention policy

#### 6.3 Frontend - Dashboard
- Overview cards:
  - Service status indicators
  - Active connection count
  - Total users/groups/shares
  - Disk usage
- Charts:
  - Connection history (line chart)
  - Top active users (bar chart)
  - Share usage (pie chart)
- Recent activity feed
- Quick actions (create user, create share, etc.)
- System alerts

#### 6.4 Frontend - Monitoring UI
- Real-time connection list:
  - User, IP, Connected Since, Open Files
  - Kill connection button
  - Auto-refresh
- Log viewer:
  - Log streaming (SSE)
  - Filtering by level, service, date
  - Search
  - Download logs
- Health check results
- Performance metrics (charts)

### Phase 7: Advanced Features (Week 13-14)

#### 7.1 Configuration Backup & Restore
- Backend:
  - Create backup (full domain backup)
  - List backups
  - Restore from backup
  - Schedule automated backups
- Frontend:
  - Backup management UI
  - Backup/restore wizards
  - Backup scheduling

#### 7.2 Bulk Operations
- Backend:
  - Bulk user import (CSV)
  - Bulk user operations (enable/disable/delete)
  - Bulk share creation
  - Template-based provisioning
- Frontend:
  - CSV upload interface
  - Bulk operation wizard
  - Operation preview
  - Progress tracking

#### 7.3 Search & Advanced Filtering
- Backend:
  - Global search across users, groups, shares
  - LDAP query builder
  - Saved searches
- Frontend:
  - Global search bar
  - Advanced filter builder
  - Search history
  - Saved searches management

#### 7.4 Notification System
- Backend:
  - Email notifications for critical events
  - Webhook support
  - Notification rules engine
- Frontend:
  - In-app notifications
  - Notification preferences
  - Alert configuration

### Phase 8: Security Hardening & Testing (Week 15-16)

#### 8.1 Security Enhancements
- Implement rate limiting (per endpoint)
- Input sanitization review
- SQL injection prevention audit
- XSS prevention audit
- CSRF token validation
- Security headers (HSTS, CSP, X-Frame-Options)
- Secret management (environment variables)
- Privilege separation (run with minimal permissions)

#### 8.2 Testing
- Backend unit tests (pytest):
  - Service layer tests
  - API endpoint tests
  - Samba integration tests (mocked)
  - Authentication/authorization tests
- Frontend unit tests (Vitest):
  - Component tests
  - Store tests
  - Composable tests
- Integration tests:
  - End-to-end API tests
  - Database migration tests
- E2E tests (Playwright):
  - Critical user workflows
  - Cross-browser testing

#### 8.3 Performance Optimization
- Database query optimization
- Implement caching strategy
- Frontend code splitting
- Lazy loading for large datasets
- API response compression
- Image optimization

### Phase 9: Documentation & Deployment (Week 17-18)

#### 9.1 Documentation
- API documentation (OpenAPI/Swagger - auto-generated)
- User guide with screenshots
- Administrator guide:
  - Installation instructions
  - Configuration guide
  - Backup/restore procedures
  - Troubleshooting
- Developer guide:
  - Architecture overview
  - Development setup
  - Contributing guidelines
  - Code style guide

#### 9.2 Docker Optimization
- Multi-stage build optimization
- Image size reduction
- Security scanning (Trivy)
- Non-root user execution
- Health check endpoints
- Graceful shutdown handling

#### 9.3 Deployment Preparation
- Environment variable configuration
- Production Docker Compose file
- Nginx configuration for production
- SSL/TLS certificate setup (Let's Encrypt)
- Systemd service files (for dedicated Linux)
- Logging configuration (log rotation)
- Monitoring integration (Prometheus metrics)

#### 9.4 CI/CD Pipeline
- GitHub Actions workflow:
  - Linting and formatting
  - Unit tests
  - Integration tests
  - Security scanning
  - Docker image build
  - Docker image push to registry
  - Automated deployment (optional)

---

## Database Schema

### Application Tables (PostgreSQL)

```sql
-- Cached AD users (NO PASSWORDS - auth via LDAP)
CREATE TABLE cached_ad_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,  -- sAMAccountName from AD
    email VARCHAR(255),
    display_name VARCHAR(255),
    ad_dn VARCHAR(500),  -- Distinguished Name from AD
    ad_guid VARCHAR(100),  -- objectGUID from AD
    last_login TIMESTAMP,
    last_ad_sync TIMESTAMP,  -- Last time we synced from AD
    preferences JSONB DEFAULT '{}',  -- User UI preferences
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User sessions
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES cached_ad_users(id) ON DELETE CASCADE,
    token_jti VARCHAR(255) UNIQUE NOT NULL, -- JWT ID
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN DEFAULT false
);

-- Audit logs
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES cached_ad_users(id) ON DELETE SET NULL,
    username VARCHAR(255), -- Denormalized for historical records (AD username)
    action VARCHAR(100) NOT NULL, -- create_user, delete_share, etc.
    resource_type VARCHAR(50), -- user, group, share, dns, gpo
    resource_id VARCHAR(255), -- Samba object identifier
    details JSONB, -- Additional context
    ip_address INET,
    result VARCHAR(20), -- success, failure, partial
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AD group to role mappings
CREATE TABLE role_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_name VARCHAR(50) NOT NULL,  -- super_admin, domain_admin, etc.
    ad_group_dn VARCHAR(500) NOT NULL,  -- Full DN of AD group
    ad_group_name VARCHAR(255),  -- Friendly name (CN)
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_name, ad_group_dn)
);

-- Backup records
CREATE TABLE backups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backup_type VARCHAR(50), -- full, configuration_only
    file_path VARCHAR(500),
    file_size BIGINT,
    created_by UUID REFERENCES cached_ad_users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50), -- completed, failed, in_progress
    error_message TEXT
);

-- Scheduled tasks
CREATE TABLE scheduled_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_type VARCHAR(50), -- backup, cleanup, report
    schedule VARCHAR(100), -- cron expression
    is_active BOOLEAN DEFAULT true,
    last_run TIMESTAMP,
    next_run TIMESTAMP,
    config JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Application configuration
CREATE TABLE app_config (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES cached_ad_users(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_cached_ad_users_username ON cached_ad_users(username);
CREATE INDEX idx_cached_ad_users_ad_dn ON cached_ad_users(ad_dn);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_sessions_user ON sessions(user_id);
CREATE INDEX idx_sessions_expires ON sessions(expires_at);
CREATE INDEX idx_role_mappings_role ON role_mappings(role_name);
```

---

## API Design

### RESTful API Structure

**Base URL**: `/api/v1`

**Authentication**: Bearer token (JWT) in `Authorization` header

**Response Format**:
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful",
  "timestamp": "2025-12-14T10:30:00Z"
}
```

**Error Format**:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "username",
      "issue": "Username already exists"
    }
  },
  "timestamp": "2025-12-14T10:30:00Z"
}
```

### API Endpoints

#### Authentication
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/logout` - Logout
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

#### Shares
- `GET /api/v1/shares` - List shares (paginated, filterable)
- `GET /api/v1/shares/{name}` - Get share details
- `POST /api/v1/shares` - Create share
- `PUT /api/v1/shares/{name}` - Update share
- `DELETE /api/v1/shares/{name}` - Delete share
- `POST /api/v1/shares/{name}/validate` - Validate share configuration
- `GET /api/v1/shares/{name}/permissions` - Get share permissions
- `PUT /api/v1/shares/{name}/permissions` - Update share permissions

#### Users
- `GET /api/v1/users` - List users
- `GET /api/v1/users/{username}` - Get user details
- `POST /api/v1/users` - Create user
- `PUT /api/v1/users/{username}` - Update user
- `DELETE /api/v1/users/{username}` - Delete user
- `POST /api/v1/users/{username}/password` - Set password
- `POST /api/v1/users/{username}/enable` - Enable user
- `POST /api/v1/users/{username}/disable` - Disable user
- `POST /api/v1/users/{username}/unlock` - Unlock account
- `GET /api/v1/users/{username}/groups` - Get user groups
- `POST /api/v1/users/{username}/groups` - Add user to groups
- `DELETE /api/v1/users/{username}/groups/{groupname}` - Remove from group
- `POST /api/v1/users/bulk` - Bulk user operations

#### Groups
- `GET /api/v1/groups` - List groups
- `GET /api/v1/groups/{name}` - Get group details
- `POST /api/v1/groups` - Create group
- `PUT /api/v1/groups/{name}` - Update group
- `DELETE /api/v1/groups/{name}` - Delete group
- `GET /api/v1/groups/{name}/members` - List group members
- `POST /api/v1/groups/{name}/members` - Add members
- `DELETE /api/v1/groups/{name}/members` - Remove members

#### OUs
- `GET /api/v1/ous` - List OUs (tree structure)
- `GET /api/v1/ous/{dn}` - Get OU details
- `POST /api/v1/ous` - Create OU
- `DELETE /api/v1/ous/{dn}` - Delete OU
- `GET /api/v1/ous/{dn}/objects` - List objects in OU

#### DNS
- `GET /api/v1/dns/zones` - List zones
- `POST /api/v1/dns/zones` - Create zone
- `DELETE /api/v1/dns/zones/{zone}` - Delete zone
- `GET /api/v1/dns/zones/{zone}/records` - List records
- `POST /api/v1/dns/zones/{zone}/records` - Add record
- `PUT /api/v1/dns/zones/{zone}/records/{name}` - Update record
- `DELETE /api/v1/dns/zones/{zone}/records/{name}` - Delete record
- `POST /api/v1/dns/query` - Query DNS

#### GPO
- `GET /api/v1/gpo` - List GPOs
- `GET /api/v1/gpo/{gpo}` - Get GPO details
- `POST /api/v1/gpo` - Create GPO
- `DELETE /api/v1/gpo/{gpo}` - Delete GPO
- `POST /api/v1/gpo/{gpo}/link` - Link GPO to container
- `DELETE /api/v1/gpo/{gpo}/link` - Unlink GPO
- `GET /api/v1/gpo/{gpo}/policies` - Get policies
- `PUT /api/v1/gpo/{gpo}/policies` - Update policies

#### Monitoring
- `GET /api/v1/monitoring/status` - Service status
- `GET /api/v1/monitoring/connections` - Active connections
- `DELETE /api/v1/monitoring/connections/{id}` - Kill connection
- `GET /api/v1/monitoring/locks` - File locks
- `GET /api/v1/monitoring/health` - Health check
- `GET /api/v1/monitoring/logs/stream` - Stream logs (SSE)
- `GET /api/v1/monitoring/metrics` - System metrics

#### System
- `GET /api/v1/system/config` - Get Samba configuration
- `PUT /api/v1/system/config` - Update configuration
- `POST /api/v1/system/config/validate` - Validate configuration
- `POST /api/v1/system/reload` - Reload Samba services
- `POST /api/v1/system/restart` - Restart Samba services
- `GET /api/v1/system/backup` - List backups
- `POST /api/v1/system/backup` - Create backup
- `POST /api/v1/system/restore` - Restore from backup

#### Audit
- `GET /api/v1/audit/logs` - Get audit logs
- `GET /api/v1/audit/export` - Export audit logs

---

## Security Implementation Details

### Authentication Flow (LDAP-Based)

1. **Login**:
   - User submits credentials (username + password)
   - Backend connects to Samba AD LDAP (port 636 for LDAPS)
   - Perform LDAP bind with user credentials using NTLM or Simple auth
   - If bind succeeds, authentication is valid
   - Query user attributes via LDAP:
     - displayName, mail, memberOf (group list)
   - Map AD groups to application roles
   - Generate JWT access token (15 min expiry) with roles
   - Generate refresh token (7 days)
   - Cache user info in PostgreSQL (username, email, display name, AD DN)
   - Store session in Redis with token JTI
   - Return tokens to client

2. **Request Authentication**:
   - Client includes access token in Authorization header
   - Middleware validates token signature and expiry
   - Check if token is revoked (Redis lookup)
   - Extract username and roles from token
   - Inject user context into request

3. **Token Refresh**:
   - Client sends refresh token
   - Backend validates refresh token
   - Re-query AD for latest group memberships (roles may have changed)
   - Issue new access token with updated roles
   - Optionally rotate refresh token

4. **Logout**:
   - Revoke tokens (add JTI to Redis blacklist)
   - Clear client-side tokens
   - Update last_login timestamp in cache

### Authorization (RBAC with AD Group Mapping)

**Role Hierarchy**:
```
Super Admin
  ├── Full system access
  ├── Mapped from: Domain Admins, Enterprise Admins
  └── All permissions below

Domain Admin
  ├── Manage AD users/groups
  ├── Manage OUs
  ├── Manage GPOs
  ├── Manage DNS
  ├── View shares
  └── Mapped from: IT Staff, Samba Admins, etc.

Share Admin
  ├── Manage shares
  ├── Manage share permissions
  ├── View users/groups
  └── Mapped from: File Server Admins, Storage Team

Auditor
  ├── Read-only access
  ├── View all resources
  ├── Export audit logs
  ├── Cannot modify anything
  └── Mapped from: Security Auditors, Compliance Team
```

**Group-to-Role Mapping** (stored in `role_mappings` table):
```python
DEFAULT_ROLE_MAPPINGS = {
    'super_admin': [
        'CN=Domain Admins,CN=Users,DC=example,DC=com',
        'CN=Enterprise Admins,CN=Users,DC=example,DC=com'
    ],
    'domain_admin': [
        'CN=IT Staff,OU=Groups,DC=example,DC=com',
        'CN=Samba Administrators,OU=Groups,DC=example,DC=com'
    ],
    'share_admin': [
        'CN=File Server Admins,OU=Groups,DC=example,DC=com'
    ],
    'auditor': [
        'CN=Security Auditors,OU=Groups,DC=example,DC=com'
    ]
}
```

**Implementation**:
- LDAP query retrieves `memberOf` attribute during login
- Map AD group DNs to application roles
- Include roles in JWT token payload
- Decorator-based permission checks: `@require_role("domain_admin")`
- Resource-level permissions for fine-grained control
- Audit all permission checks (failed attempts)
- **Configurable mappings** via admin UI

### CSRF Protection

- Generate CSRF token on login
- Include in custom header (`X-CSRF-Token`)
- Validate on all state-changing requests (POST, PUT, DELETE)
- Token rotation on critical operations

### Input Validation

**Pydantic Models** for all inputs:
```python
class ShareCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=80, pattern=r'^[a-zA-Z0-9_-]+$')
    path: str = Field(..., min_length=1, max_length=255)
    comment: Optional[str] = Field(None, max_length=255)
    read_only: bool = False
    browseable: bool = True
    guest_ok: bool = False
    valid_users: List[str] = []

    @validator('path')
    def validate_path(cls, v):
        # Check path exists and is absolute
        path = Path(v)
        if not path.is_absolute():
            raise ValueError("Path must be absolute")
        if not path.exists():
            raise ValueError("Path does not exist")
        return str(path)
```

**Samba-Specific Validation**:
- Username format (alphanumeric, max 20 chars)
- DN format validation
- IP address validation
- DNS name validation
- Share name validation (NetBIOS restrictions)

### Rate Limiting

Using `slowapi` (FastAPI rate limiting library):
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Global: 100 requests per minute per IP
# Auth endpoints: 5 login attempts per minute
# Bulk operations: 10 per hour
```

### Secrets Management

- All secrets in environment variables (never in code)
- Use Docker secrets in production
- Secrets:
  - `SECRET_KEY` - JWT signing key
  - `DATABASE_URL` - PostgreSQL connection
  - `REDIS_URL` - Redis connection
  - `LDAP_SERVER` - Samba LDAP server URI
  - `LDAP_BASE_DN` - Base DN for LDAP searches
  - `LDAP_DOMAIN` - NetBIOS domain name
  - `LDAP_SERVICE_ACCOUNT_DN` - Service account for user lookups (optional)
  - `LDAP_SERVICE_PASSWORD` - Service account password (optional)
  - `LDAP_USE_SSL` - Whether to use LDAPS (recommended: true)

### Logging & Monitoring

**Security Event Logging**:
- Failed login attempts
- Permission denied errors
- Invalid token usage
- Configuration changes
- Critical operations (user deletion, share deletion)

**Log Format** (structured JSON):
```json
{
  "timestamp": "2025-12-14T10:30:00Z",
  "level": "WARNING",
  "event": "failed_login",
  "user": "admin",
  "ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "details": {
    "reason": "invalid_password",
    "attempt_count": 3
  }
}
```

---

## Deployment Architecture

### Docker Compose Structure

```yaml
version: '3.8'

services:
  # Reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - frontend-dist:/usr/share/nginx/html:ro
    depends_on:
      - backend
    networks:
      - adhub-network

  # FastAPI backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://adhub:${DB_PASSWORD}@postgres:5432/adhub
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - SAMBA_CONFIG_PATH=/etc/samba/smb.conf
      - LDAP_SERVER=ldap://${SAMBA_DC_HOST}:389
      - LDAP_BASE_DN=${LDAP_BASE_DN}
      - LDAP_DOMAIN=${DOMAIN}
      - LDAP_USE_SSL=true
    volumes:
      - /etc/samba:/etc/samba:ro  # Read-only Samba config
      - /var/lib/samba:/var/lib/samba:ro  # Read-only Samba data
      - /var/log/samba:/var/log/samba:ro  # Read-only logs
      - ./backend/backups:/app/backups  # Backup storage
    depends_on:
      - postgres
      - redis
    networks:
      - adhub-network
    # Run with capabilities to execute samba-tool
    cap_add:
      - DAC_OVERRIDE  # Read any file
      - DAC_READ_SEARCH

  # PostgreSQL database
  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=adhub
      - POSTGRES_USER=adhub
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - adhub-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U adhub"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis cache
  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    networks:
      - adhub-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Optional: Samba container (if not using host Samba)
  samba:
    image: dperson/samba
    environment:
      - WORKGROUP=${WORKGROUP}
    volumes:
      - samba-config:/etc/samba
      - samba-data:/var/lib/samba
    networks:
      - adhub-network
    # Only if running Samba in container

volumes:
  postgres-data:
  redis-data:
  frontend-dist:
  samba-config:
  samba-data:

networks:
  adhub-network:
    driver: bridge
```

### Dockerfile (Backend)

```dockerfile
# Multi-stage build
FROM python:3.11-alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    python3-dev \
    samba-dev

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-alpine

# Install runtime dependencies
RUN apk add --no-cache \
    samba \
    samba-client \
    samba-common-tools \
    postgresql-libs \
    libstdc++

# Create non-root user
RUN addgroup -g 1000 adhub && \
    adduser -D -u 1000 -G adhub adhub

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY --chown=adhub:adhub ./app ./app

# Switch to non-root user (for most operations)
USER adhub

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health')"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile (Frontend)

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Nginx Configuration

```nginx
upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name _;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=general:10m rate=100r/m;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;

    # Frontend
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # API endpoints
    location /api/ {
        limit_req zone=general burst=20 nodelay;

        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (for SSE)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }

    # Auth endpoints (stricter rate limiting)
    location /api/v1/auth/ {
        limit_req zone=auth burst=3 nodelay;

        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Installation Methods

#### Method 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/adhub.git
cd adhub

# Create .env file
cp .env.example .env
# Edit .env with your settings

# Generate SSL certificates (self-signed for testing)
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/key.pem \
    -out nginx/ssl/cert.pem

# Start services
docker-compose up -d

# Initialize database
docker-compose exec backend alembic upgrade head

# Create admin user
docker-compose exec backend python -m app.cli create-admin

# Access at https://your-server-ip
```

#### Method 2: Dedicated Linux System

```bash
# Install dependencies
sudo apt update
sudo apt install -y python3.11 python3-pip python3-venv \
    postgresql postgresql-contrib redis-server \
    samba samba-common-bin samba-dsdb-modules \
    nginx

# Create application user
sudo useradd -r -s /bin/bash -d /opt/adhub adhub

# Clone repository
sudo git clone https://github.com/yourusername/adhub.git /opt/adhub
cd /opt/adhub

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database setup
sudo -u postgres createuser adhub
sudo -u postgres createdb adhub -O adhub
alembic upgrade head

# Frontend build
cd ../frontend
npm install
npm run build

# Configure systemd service
sudo cp systemd/adhub.service /etc/systemd/system/
sudo systemctl enable adhub
sudo systemctl start adhub

# Configure Nginx
sudo cp nginx/adhub.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/adhub.conf /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

---

## Testing Strategy

### Unit Tests

**Backend (pytest)**:
```python
# tests/test_user_service.py
import pytest
from app.services.user_service import UserService

def test_create_user_success(mock_samdb):
    service = UserService(mock_samdb)
    user = service.create_user(
        username="testuser",
        password="P@ssw0rd!",
        given_name="Test",
        surname="User"
    )
    assert user.username == "testuser"

def test_create_user_duplicate(mock_samdb):
    service = UserService(mock_samdb)
    with pytest.raises(UserExistsError):
        service.create_user(username="existinguser", password="P@ssw0rd!")
```

**Frontend (Vitest)**:
```typescript
// tests/stores/auth.spec.ts
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('logs in successfully', async () => {
    const auth = useAuthStore()
    await auth.login('admin', 'password')
    expect(auth.isAuthenticated).toBe(true)
  })
})
```

### Integration Tests

```python
# tests/integration/test_share_api.py
def test_share_lifecycle(client, auth_headers):
    # Create share
    response = client.post('/api/v1/shares', json={
        'name': 'testshare',
        'path': '/tmp/testshare',
        'comment': 'Test share'
    }, headers=auth_headers)
    assert response.status_code == 201

    # Get share
    response = client.get('/api/v1/shares/testshare', headers=auth_headers)
    assert response.status_code == 200
    assert response.json()['data']['name'] == 'testshare'

    # Delete share
    response = client.delete('/api/v1/shares/testshare', headers=auth_headers)
    assert response.status_code == 204
```

### E2E Tests (Playwright)

```typescript
// e2e/share-management.spec.ts
import { test, expect } from '@playwright/test'

test('create and delete share', async ({ page }) => {
  // Login
  await page.goto('https://localhost')
  await page.fill('[data-testid="username"]', 'admin')
  await page.fill('[data-testid="password"]', 'password')
  await page.click('[data-testid="login-button"]')

  // Navigate to shares
  await page.click('text=Shares')
  await page.click('[data-testid="create-share-button"]')

  // Fill form
  await page.fill('[data-testid="share-name"]', 'testshare')
  await page.fill('[data-testid="share-path"]', '/tmp/testshare')
  await page.click('[data-testid="submit-button"]')

  // Verify
  await expect(page.locator('text=testshare')).toBeVisible()

  // Delete
  await page.click('[data-testid="delete-testshare"]')
  await page.click('[data-testid="confirm-delete"]')
  await expect(page.locator('text=testshare')).not.toBeVisible()
})
```

---

## Monitoring & Observability

### Application Metrics (Prometheus)

```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

active_connections = Gauge(
    'samba_active_connections',
    'Number of active Samba connections'
)

# Expose metrics endpoint
@app.get('/metrics')
async def metrics():
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

### Logging Configuration

```python
import logging
import sys
from pythonjsonlogger import jsonlogger

# Configure structured logging
handler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter(
    '%(timestamp)s %(level)s %(name)s %(message)s'
)
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Health Checks

```python
@app.get('/api/v1/health')
async def health_check():
    checks = {
        'database': await check_database(),
        'redis': await check_redis(),
        'samba': await check_samba_services()
    }

    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503

    return JSONResponse(
        status_code=status_code,
        content={
            'status': 'healthy' if all_healthy else 'unhealthy',
            'checks': checks,
            'timestamp': datetime.utcnow().isoformat()
        }
    )
```

---

## Performance Targets

### Response Time Goals
- API endpoints: < 200ms (p95)
- Page load: < 2s (first contentful paint)
- Time to interactive: < 3s

### Throughput Goals
- Support 100 concurrent users
- Handle 1000 requests/minute
- Database queries: < 50ms (p95)

### Optimization Strategies
- Database connection pooling (SQLAlchemy)
- Redis caching for expensive queries (TTL: 5 minutes)
- Frontend code splitting and lazy loading
- API response pagination (default: 50 items)
- Debounced search inputs (300ms delay)
- Virtualized lists for large datasets (react-window)

---

## Future Enhancements (Post-MVP)

### Advanced Features
- **Multi-domain support**: Manage multiple Samba domains from single interface
- **LDAP sync**: Synchronize with external LDAP directories
- **Two-factor authentication**: TOTP support for app users
- **Advanced reporting**: Custom reports, scheduled exports
- **Mobile app**: Native iOS/Android apps
- **Role templates**: Pre-defined role configurations
- **Workflow automation**: Multi-step approval workflows for sensitive operations
- **Integration API**: Webhooks and external integrations
- **Backup scheduling**: Automated backup management
- **Disaster recovery**: Point-in-time recovery
- **Multi-language support**: i18n for global deployments

### Infrastructure Enhancements
- **High availability**: Multi-instance deployment with load balancing
- **Clustering**: Distributed Samba management
- **Kubernetes deployment**: Helm charts for K8s
- **Monitoring dashboard**: Grafana dashboards
- **Alerting**: PagerDuty, Slack integration
- **Compliance reports**: GDPR, HIPAA audit reports

---

## Success Criteria

### Functional Requirements
- ✅ All core Samba features accessible via web UI
- ✅ Feature parity with samba-tool CLI
- ✅ No data loss during operations
- ✅ Configuration validation before applying
- ✅ Comprehensive audit logging

### Non-Functional Requirements
- ✅ 99.9% uptime (excluding maintenance)
- ✅ < 200ms API response time (p95)
- ✅ Support 100 concurrent users
- ✅ OWASP Top 10 compliance
- ✅ < 5 minute deployment time
- ✅ Automated backup/restore

### User Experience
- ✅ Intuitive interface requiring minimal training
- ✅ Mobile-responsive design
- ✅ Real-time updates for monitoring
- ✅ Clear error messages with actionable guidance
- ✅ Context-sensitive help

---

## Risk Assessment & Mitigation

### Technical Risks

1. **Samba API Changes**
   - **Risk**: Python-samba API changes between Samba versions
   - **Mitigation**: Version pinning, comprehensive testing, abstract Samba layer

2. **Performance Bottlenecks**
   - **Risk**: Slow response times with large directories
   - **Mitigation**: Pagination, caching, async operations, database indexes

3. **Security Vulnerabilities**
   - **Risk**: Unauthorized access, privilege escalation
   - **Mitigation**: Security audits, penetration testing, regular updates

4. **Data Corruption**
   - **Risk**: Invalid configurations breaking Samba
   - **Mitigation**: Validation, testparm checks, configuration backups, rollback

### Operational Risks

1. **Deployment Complexity**
   - **Risk**: Difficult setup process
   - **Mitigation**: Docker Compose automation, comprehensive documentation, setup wizard

2. **Backup Failures**
   - **Risk**: Unable to restore after disaster
   - **Mitigation**: Automated backup testing, multiple backup locations, backup verification

3. **User Adoption**
   - **Risk**: Users prefer CLI tools
   - **Mitigation**: Superior UX, time-saving features, training materials

---

## Timeline Summary

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1: Foundation | 2 weeks | Auth, database, basic API |
| Phase 2: Share Management | 2 weeks | Full share CRUD, permissions |
| Phase 3: User/Group Management | 3 weeks | AD user/group/OU management |
| Phase 4: DNS Management | 1 week | DNS zone and record management |
| Phase 5: GPO Management | 2 weeks | Group Policy operations |
| Phase 6: Monitoring | 2 weeks | Dashboard, logs, health checks |
| Phase 7: Advanced Features | 2 weeks | Backups, bulk ops, search |
| Phase 8: Security & Testing | 2 weeks | Hardening, comprehensive tests |
| Phase 9: Documentation & Deploy | 2 weeks | Docs, optimization, CI/CD |
| **Total** | **18 weeks** | **Production-ready application** |

---

## Conclusion

This plan provides a comprehensive roadmap for building a production-ready Samba web management application. The chosen technology stack (FastAPI + Vue 3) offers the best balance of development velocity, maintainability, and Samba integration capabilities.

The phased approach ensures incremental delivery of value while maintaining high quality through comprehensive testing and security measures. The modular architecture allows for future extensibility and scalability.

Key differentiators:
- Native Python-samba integration (best-in-class Samba support)
- Modern, responsive UI built with Vue 3 and Ant Design
- Comprehensive security (RBAC, audit logging, input validation)
- Docker-first deployment with dedicated Linux support
- Real-time monitoring and diagnostics
- Enterprise-grade architecture

The estimated timeline of 18 weeks accounts for thorough implementation, testing, and documentation, resulting in a robust, production-ready solution for Samba administration.
