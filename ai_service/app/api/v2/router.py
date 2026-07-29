from fastapi import APIRouter

from app.api.v2.endpoints.health import router as health_router
from app.api.v2.endpoints.reports import router as reports_router

router = APIRouter()

router.include_router(health_router, tags=["Health"])
router.include_router(reports_router, tags=["Reports"])
