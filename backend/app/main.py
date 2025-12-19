from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.api.v1 import health, setup, auth, stats, users, groups

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting ADHub API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'Not configured'}")
    yield
    logger.info("Shutting down ADHub API...")


# Initialize FastAPI app
app = FastAPI(
    title="ADHub API",
    description="Samba Active Directory Management API",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(setup.router, prefix="/api/v1", tags=["setup"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(stats.router, prefix="/api/v1", tags=["stats"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(groups.router, prefix="/api/v1", tags=["groups"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ADHub API",
        "version": "0.1.0",
        "docs": "/docs"
    }
