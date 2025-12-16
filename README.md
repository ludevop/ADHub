# ADHub - Samba Active Directory Management

A modern web-based management interface for Samba Active Directory, built with FastAPI and Vue 3.

## ✨ Features

### 🧙 Setup Wizard
Complete **8-step guided wizard** for provisioning a new Samba AD Domain Controller:
- **Prerequisites checking** - Validates system requirements
- **Domain configuration** - Easy setup with auto-fill
- **DNS configuration** - Multiple backend options
- **Review & provision** - Safe deployment with confirmation
- **🔬 Comprehensive verification tests** - Automated testing suite with 15+ tests covering DNS, LDAP, Kerberos, services, and authentication

**See [SETUP_WIZARD.md](SETUP_WIZARD.md) for complete documentation.**

### 📊 Verification Tests
The wizard includes a comprehensive test suite that verifies:
- ✅ DNS resolution and SRV records
- ✅ Service ports (LDAP, Kerberos, SMB, DNS)
- ✅ LDAP connectivity and queries
- ✅ Kerberos ticket acquisition
- ✅ Administrator authentication
- ✅ System prerequisites

All tests run automatically after provisioning with detailed results, error messages, and troubleshooting tips.

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Git
- **Note**: The backend container runs with elevated privileges for Samba operations (this is safe in containerized environments)
- **Windows Users**: See [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for port conflict information (TL;DR: default config works fine, Samba ports not exposed to avoid Windows conflicts)

### Running the Application

1. **Clone the repository** (if not already done)
   ```bash
   git clone <repository-url>
   cd ADHub
   ```

2. **Start all services**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Database: localhost:5432

### Stopping the Application

```bash
docker-compose down
```

To also remove volumes (database data):
```bash
docker-compose down -v
```

## 📁 Project Structure

```
ADHub/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   │   └── v1/
│   │   │       └── health.py
│   │   ├── config.py       # Configuration
│   │   ├── database.py     # Database setup
│   │   └── main.py         # FastAPI app
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # Vue 3 frontend
│   ├── src/
│   │   ├── App.vue        # Main component
│   │   └── main.ts
│   ├── Dockerfile.dev
│   └── vite.config.ts     # Vite config with proxy
├── docker-compose.yml
└── README.md
```

## 🔧 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy 2.0** - Async ORM
- **PostgreSQL** - Database
- **asyncpg** - Async PostgreSQL driver
- **Pydantic** - Data validation

### Frontend
- **Vue 3** - Progressive JavaScript framework
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **Composition API** - Modern Vue development

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Production web server (planned)

## 🏥 Health Checks

The application includes comprehensive health checks:

### Basic Health Check
```bash
curl http://localhost:8000/api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-16T19:00:00.000000",
  "service": "ADHub API"
}
```

### Detailed Health Check (with database)
```bash
curl http://localhost:8000/api/v1/health/detailed
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-16T19:00:00.000000",
  "service": "ADHub API",
  "checks": {
    "api": "healthy",
    "database": "healthy"
  }
}
```

## 🛠️ Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Environment Variables

Backend (`.env`):
```env
APP_NAME=ADHub
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql://adhub:adhub_password@localhost:5432/adhub
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

Frontend (`.env`):
```env
VITE_API_URL=http://localhost:8000
```

## 🐳 Docker Services

### Database Service
- **Image**: postgres:15-alpine
- **Port**: 5432
- **Credentials**:
  - User: `adhub`
  - Password: `adhub_password`
  - Database: `adhub`

### Backend Service
- **Port**: 8000 (API exposed to host)
- **Samba Ports**: Available inside container and Docker network (NOT exposed to host by default to avoid Windows conflicts)
- **Container IP**: 172.20.0.10 (access Samba services via this IP from other containers)
- **Hot Reload**: Enabled (volume mounted)
- **Health Check**: Every 30s
- **Includes**: Full Samba AD DC installation
- **Privileges**: Runs with elevated privileges (required for Samba)

### Frontend Service
- **Port**: 5173
- **Hot Reload**: Enabled (volume mounted)
- **Proxy**: `/api/*` → `http://backend:8000`

## 📝 API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔍 Vite Proxy Configuration

The frontend is configured to proxy API requests to the backend:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://backend:8000',
      changeOrigin: true,
    }
  }
}
```

This allows the frontend to call `/api/v1/health` which gets proxied to `http://backend:8000/api/v1/health`.

## 🧪 Testing the Setup

1. **Start the stack**:
   ```bash
   docker-compose up --build
   ```

2. **Check logs**:
   ```bash
   docker-compose logs -f backend
   docker-compose logs -f frontend
   docker-compose logs -f db
   ```

3. **Test backend directly**:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

4. **Test frontend**:
   Open http://localhost:5173 in your browser

5. **Check Docker health**:
   ```bash
   docker ps
   ```
   All services should show "healthy" status.

## 🚨 Troubleshooting

### Backend won't start
```bash
# Check backend logs
docker-compose logs backend

# Rebuild backend
docker-compose up --build backend
```

### Database connection issues
```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Connect to database
docker-compose exec db psql -U adhub -d adhub
```

### Frontend can't reach backend
1. Check Vite proxy configuration in `vite.config.ts`
2. Verify backend is healthy: `curl http://localhost:8000/api/v1/health`
3. Check browser console for errors
4. Verify CORS settings in `backend/app/config.py`

### Port already in use
```bash
# Find process using port
# Windows:
netstat -ano | findstr :8000
# Linux/Mac:
lsof -i :8000

# Kill the process or change port in docker-compose.yml
```

## 📚 Next Steps

Now that your stack is working, you can start building features:

1. **Authentication**: Implement LDAP authentication against Samba AD
2. **User Management**: CRUD operations for AD users
3. **Group Management**: Manage AD groups and memberships
4. **Share Management**: Create and manage Samba shares
5. **DNS Management**: Manage DNS records
6. **Group Policy**: GPO management interface

Refer to `CLAUDE.md`, `TECHNICAL_SPEC.md`, and `SETUP_WIZARD.md` for detailed planning and architecture.

## 🐳 Docker Configuration

The backend container includes:
- **Full Samba installation** (samba, samba-tool, etc.)
- **Verification tools** (ldap-utils, krb5-user, smbclient, dnsutils)
- **Privileged mode** (required for Samba AD DC operations)
- **Persistent volumes** for Samba data
- **Static IP address** for DNS stability

**See [DOCKER_SETUP.md](DOCKER_SETUP.md) for complete Docker configuration documentation.**

### Installed in Backend Container

```bash
# Samba components
samba, samba-common-bin, samba-dsdb-modules, winbind

# Verification utilities
ldap-utils, krb5-user, smbclient, dnsutils, host

# Network tools
net-tools, iputils-ping, procps
```

### Security Note

The backend container runs with **privileged mode** and elevated capabilities. This is:
- ✅ **Required** for Samba AD DC operations (port binding, file permissions)
- ✅ **Safe** in containerized environments (process and filesystem isolation)
- ✅ **Standard** for Samba DC containers
- ⚠️ **Only expose** necessary ports to trusted networks

## 📄 License

[Your License Here]

## 🤝 Contributing

Contributions are welcome! Please read the contributing guidelines first.

---

Built with ❤️ using FastAPI and Vue 3
