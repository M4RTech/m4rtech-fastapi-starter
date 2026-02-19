from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["scan"])

NEXT_ID = 1

# Prosta "baza" w pamięci (na start)
SCANS: list[dict] = []

class ScanIn(BaseModel):
    gb_number: str

@router.post("/scan")
def scan(payload: ScanIn):
    global NEXT_ID

    gb = payload.gb_number.strip().upper()

    if not gb.startswith("GB"):
        raise HTTPException(status_code=400, detail="Invalid GB number")
    if len(gb) < 3:
        raise HTTPException(status_code=400, detail="GB number too short")

    scan_id = NEXT_ID
    NEXT_ID += 1

    item = {
        "id": scan_id,
        "gb_number": gb,
        "ts": datetime.now(timezone.utc).isoformat(),
    }

    SCANS.append(item)

    # limit pamięci: trzymaj tylko ostatnie 5000
    if len(SCANS) > 5000:
        del SCANS[:-5000]

    return {
        "id": scan_id,
        "received": gb,
        "status": "ok",
        "length": len(gb),
        "saved": True,
    }

@router.get("/scans")
def get_scans(limit: int = 50):
    if limit < 1:
        raise HTTPException(status_code=400, detail="limit must be >= 1")
    if limit > 500:
        raise HTTPException(status_code=400, detail="limit must be <= 500")

    return {
        "count": min(limit, len(SCANS)),
        "items": list(reversed(SCANS[-limit:])),
    }
@router.delete("/scans")
def clear_scans():
    global NEXT_ID

    count = len(SCANS)
    SCANS.clear()
    NEXT_ID = 1

    return {
        "cleared": True,
        "removed_count": count
    }
