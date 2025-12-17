"""Statistics API endpoints"""

from fastapi import APIRouter, Depends
from app.schemas.stats import DashboardStats
from app.services.samba.stats import stats_service
from app.api.dependencies.auth import get_current_user
from app.schemas.auth import User

router = APIRouter()


@router.get("/stats/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    """
    Get dashboard statistics

    Requires authentication.
    """
    stats = stats_service.get_dashboard_stats()
    return stats
