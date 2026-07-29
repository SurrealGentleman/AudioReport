from fastapi import FastAPI

from app.api.v2.router import router as api_v2_router
from app.core.config import settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.app_debug,
    )

    app.include_router(api_v2_router, prefix="/api/v2")

    return app


app = create_app()
