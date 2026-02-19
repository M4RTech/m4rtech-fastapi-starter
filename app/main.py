from fastapi import FastAPI
from app.core.config import settings
from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(title=settings.app_name, version=settings.version)

app.include_router(api_router)