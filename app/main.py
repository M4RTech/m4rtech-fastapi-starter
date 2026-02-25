import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.ui.router import router as ui_router
from app.api.v1.router import api_router
from app.core.config import settings
from app.db.init_db import init_db
from app.core.logging import setup_logging

setup_logging()
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s v%s", settings.APP_NAME, settings.VERSION)

    if not settings.TESTING:
        init_db()

    yield

    logger.info("Shutting down %s", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

# UI
app.include_router(ui_router)

# API
app.include_router(api_router, prefix="/api/v1")
