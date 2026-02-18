from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(
    prefix="/api/v1",
    tags=["meta"]
)

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/version")
def version():
    return {"version": settings.version}
