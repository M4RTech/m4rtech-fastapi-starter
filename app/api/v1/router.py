from fastapi import APIRouter
from app.api.v1.endpoints import health, scan, routes, reconcile, expected

api_router = APIRouter()

api_router.include_router(reconcile.router)
api_router.include_router(health.router)
api_router.include_router(scan.router)
api_router.include_router(routes.router)
api_router.include_router(expected.router)
