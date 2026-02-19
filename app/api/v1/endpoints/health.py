from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["meta"])


@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/version")
def version():
    return {"version": settings.version}
