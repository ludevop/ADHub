# Quick Start Guide

Since Docker is encountering build issues with PrimeVue dependencies, here's how to run ADHub locally for development:

## Prerequisites

1. **Python 3.11+**
2. **Node.js 20+**
3. **PostgreSQL 15** (running on localhost:5432)
4. **Redis 7** (running on localhost:6379)

## Setup Steps

### 1. Database Setup

```bash
# Start PostgreSQL (if using Windows with PostgreSQL service)
# Or on Linux: sudo systemctl start postgresql

# Create database
psql -U postgres
CREATE DATABASE adhub;
CREATE USER adhub WITH PASSWORD 'adhub_dev_password';
GRANT ALL PRIVILEGES ON DATABASE adhub TO adhub;
\c adhub
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
\q

# Initialize schema
psql -U adhub -d adhub -f database/init.sql
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
# source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies (skip python-samba for now if not on Linux)
pip install fastapi uvicorn[standard] pydantic pydantic-settings ldap3 sqlalchemy asyncpg psycopg2-binary python-jose[cryptography] passlib[bcrypt] python-multipart cryptography redis aioredis hiredis slowapi python-dotenv prometheus-client python-json-logger celery flower python-dateutil pytz tenacity httpx pytest pytest-asyncio pytest-cov pytest-mock faker

# Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will be available at: http://localhost:8000**
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### 3. Frontend Setup (in a new terminal)

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

**Frontend will be available at: http://localhost:5173**

## Testing the Application

1. **Health Check:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Access Frontend:**
   - Open browser: http://localhost:5173
   - You'll see the login page

3. **Login:**
   - The backend expects LDAP authentication
   - You'll need a running Samba AD DC
   - Configure connection in `backend/.env`:
     ```env
     LDAP_SERVER=ldap://your-samba-dc
     LDAP_BASE_DN=DC=yourdomain,DC=com
     ```

## Current Limitations

### Without Samba AD

The application requires a Samba Active Directory Domain Controller for authentication. Without it:

- You can access the API documentation at http://localhost:8000/docs
- You can view the frontend UI at http://localhost:5173
- Login will fail unless connected to a real Samba AD

###To bypass LDAP for development, you can temporarily modify the backend code:

**Option 1: Mock Authentication (for development only)**

Edit `backend/app/api/v1/endpoints/auth.py` and add a development bypass:

```python
@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    # DEVELOPMENT ONLY - Remove in production!
    if credentials.username == "admin" and credentials.password == "admin":
        # Create mock user
        user = CachedADUser(
            username="admin",
            email="admin@example.com",
            display_name="Administrator",
            ad_dn="CN=Administrator,CN=Users,DC=example,DC=com"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        roles = ["super_admin"]

        access_token = jwt_service.create_access_token(
            username="admin",
            roles=roles
        )

        refresh_token = jwt_service.create_refresh_token(
            username="admin"
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(
                id=str(user.id),
                username="admin",
                email="admin@example.com",
                display_name="Administrator",
                roles=roles
            )
        )

    # Original LDAP auth code follows...
    success, ldap_user = await ldap_auth_service.authenticate(...)
```

Then you can login with:
- Username: `admin`
- Password: `admin`

## Troubleshooting

### Backend Issues

**"Module 'samba' not found":**
- On Windows, python-samba is not easily available
- Comment out samba imports temporarily
- Or use WSL/Linux for full Samba support

**Database connection failed:**
```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT 1;"

# Verify connection string in backend/.env
DATABASE_URL=postgresql+asyncpg://adhub:adhub_dev_password@localhost:5432/adhub
```

**Redis connection failed:**
```bash
# Install Redis (Windows - use Memurai or WSL)
# Linux: sudo systemctl start redis

# Test connection
redis-cli ping
```

### Frontend Issues

**Build errors with PrimeVue:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Module not found errors:**
- Check all imports in Vue files
- Ensure all PrimeVue components are imported correctly

## Docker (When Issues Are Resolved)

For Docker deployment:

```bash
# Create .env from example
cp .env.example .env

# Edit .env with your configuration
# Then:
docker-compose up -d
```

## Next Steps

1. **Configure Samba Connection:**
   - Update `backend/.env` with your Samba AD details
   - Test LDAP connectivity

2. **Explore the Code:**
   - Backend: `backend/app/`
   - Frontend: `frontend/src/`
   - Documentation: `TECHNICAL_SPEC.md`

3. **Start Development:**
   - Follow `TECHNICAL_SPEC.md` for feature implementation
   - Check `PLAN.md` for project roadmap

## Development Workflow

1. **Make changes** to backend or frontend
2. **Test locally** with hot reload
3. **Run tests:**
   ```bash
   # Backend
   cd backend
   pytest

   # Frontend
   cd frontend
   npm run test
   ```
4. **Commit** your changes
5. **Deploy** when ready (Docker or manual)

For full production deployment, see [SETUP_GUIDE.md](SETUP_GUIDE.md).
