from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/v1",
    tags=["scan"]
)

class ScanIn(BaseModel):
    gb_number: str

@router.post("/scan")
def scan(payload: ScanIn):
    gb = payload.gb_number.strip().upper()

    if not gb.startswith("GB"):
        raise HTTPException(status_code=400, detail="Invalid GB number")

    return {
        "received": gb,
        "status": "ok",
        "length": len(gb),
    }
