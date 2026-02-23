from __future__ import annotations
#/app/api/v1/endpoints/scan.py
from datetime import datetime, timezone, date
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session

from app.api.v1.schemas.scan import ScanIn, ScanOut, ScanCreateResponse, ScanListResponse, ClearResponse
from app.db.models import Scan
from app.db.session import get_session


from datetime import date
from typing import Optional

from sqlalchemy import Select, Delete
from sqlalchemy.sql import and_

from app.db.models import Scan
router = APIRouter(tags=["scan"])




def apply_scan_filters(stmt, route: int | None, day: date | None, user: str | None):
    """
    Działa dla:
    - select(Scan) ...
    - select(func.count()).select_from(Scan)
    - delete(Scan)

    Zwraca stmt z dołożonymi .where(...)
    """
    if route is not None:
        stmt = stmt.where(Scan.route == route)
    if day is not None:
        stmt = stmt.where(Scan.day == day)
    if user:
        stmt = stmt.where(Scan.user == user.strip())
    return stmt


@router.post("/scan", response_model=ScanCreateResponse)
def scan(payload: ScanIn, db: Session = Depends(get_session)):
    # 🔒 check route status
    from app.db.models import RouteStatus

    status_row = db.scalar(
        select(RouteStatus).where(
            RouteStatus.day == payload.day,
            RouteStatus.route == payload.route,
        )
    )

    if status_row and status_row.status == "CLOSED":
        raise HTTPException(
            status_code=403,
            detail="Route is CLOSED",
        )

    item = Scan(
        gb_number=payload.gb_number,
        route=payload.route,
        day=payload.day,
        user=payload.user,
        drop_number=getattr(payload, "drop_number", None),
        ts=datetime.now(timezone.utc),
    )
    db.add(item)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Duplicate scan for this route/day",
        )

    db.refresh(item)

    return ScanCreateResponse(
        id=item.id,
        received=item.gb_number,
        length=len(item.gb_number),   # <-- DODAJ
        route=item.route,
        day=item.day,
        user=item.user,
    )



@router.get("/scans", response_model=ScanListResponse)
def get_scans(
    route: int | None = Query(None, ge=300, le=360, description="Filter by route, e.g. 320"),
    day: date | None = Query(None, description="Filter by day, e.g. 2026-02-19"),
    user: str | None = Query(None, description="Filter by user"),
    limit: int = Query(50, ge=1, le=500, description="How many scans to return"),
    db: Session = Depends(get_session),
):
    stmt = select(Scan).order_by(Scan.id.desc()).limit(limit)
    stmt = apply_scan_filters(stmt, route, day, user)

    rows = db.execute(stmt).scalars().all()

    return ScanListResponse(
        count=len(rows),
        items=[ScanOut.model_validate(r) for r in rows],
    )


@router.delete("/scans", response_model=ClearResponse)
def clear_scans(
    route: int | None = Query(None, ge=300, le=360),
    day: date | None = Query(None),
    user: str | None = Query(None),
    db: Session = Depends(get_session),
):
    count_stmt = select(func.count()).select_from(Scan)
    del_stmt = delete(Scan)

    count_stmt = apply_scan_filters(count_stmt, route, day, user)
    del_stmt = apply_scan_filters(del_stmt, route, day, user)

    count = db.scalar(count_stmt) or 0
    db.execute(del_stmt)
    db.commit()

    return ClearResponse(removed_count=count)

