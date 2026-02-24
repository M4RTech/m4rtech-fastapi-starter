from __future__ import annotations
from app.db.models import ExpectedItem, Scan, RouteStatus
from app.api.v1.schemas.routes import RoutesStatusOut, RouteStatusItem
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session
from app.db.session import get_session

router = APIRouter(tags=["routes"])


@router.get("/routes/{route}/summary")
def route_summary(
    route: int,
    day: date = Query(..., description="YYYY-MM-DD"),
    db: Session = Depends(get_session),
):
    """
    Podsumowanie trasy na dany dzień:
    - ile skanów
    - pierwszy/ostatni timestamp
    - unikalne GB (na wypadek gdybyś kiedyś dopuścił duplikaty)
    """
    total = db.scalar(
        select(func.count()).select_from(Scan).where(Scan.day == day, Scan.route == route)
    ) or 0

    first_ts = db.scalar(
        select(func.min(Scan.ts)).where(Scan.day == day, Scan.route == route)
    )
    last_ts = db.scalar(
        select(func.max(Scan.ts)).where(Scan.day == day, Scan.route == route)
    )

    unique_gb = db.scalar(
        select(func.count(func.distinct(Scan.gb_number))).where(Scan.day == day, Scan.route == route)
    ) or 0

    return {
        "day": day.isoformat(),
        "route": route,
        "count": int(total),
        "unique_gb": int(unique_gb),
        "first_ts": first_ts.isoformat() if first_ts else None,
        "last_ts": last_ts.isoformat() if last_ts else None,
    }


@router.get("/routes/{route}/scans")
def route_scans(
    route: int,
    day: date = Query(..., description="YYYY-MM-DD"),
    limit: int = Query(200, ge=1, le=2000),
    db: Session = Depends(get_session),
):
    """
    Lista skanów dla trasy/dnia (najnowsze pierwsze).
    """
    rows = db.execute(
        select(Scan)
        .where(Scan.day == day, Scan.route == route)
        .order_by(desc(Scan.ts), desc(Scan.id))
        .limit(limit)
    ).scalars().all()

    return {
        "day": day.isoformat(),
        "route": route,
        "count": len(rows),
        "items": [
            {
                "id": r.id,
                "gb_number": r.gb_number,
                "route": r.route,
                "day": r.day.isoformat(),
                "user": r.user,
                "drop_number": r.drop_number,
                "ts": r.ts.isoformat(),
            }
            for r in rows
        ],
    }


@router.get("/routes/{route}/check")
def route_check_gb(
    route: int,
    day: date = Query(..., description="YYYY-MM-DD"),
    gb: str = Query(..., min_length=3, max_length=64, description="GB number (any case/spaces ok)"),
    db: Session = Depends(get_session),
):
    """
    Sprawdza czy dany GB jest już zeskanowany na tej trasie/dniu.
    """
    normalized = gb.strip().upper()

    exists_id = db.scalar(
        select(Scan.id).where(
            Scan.day == day,
            Scan.route == route,
            Scan.gb_number == normalized,
        )
    )

    return {
        "day": day.isoformat(),
        "route": route,
        "gb_number": normalized,
        "exists": exists_id is not None,
        "id": int(exists_id) if exists_id is not None else None,
    }
@router.get("/routes/status", response_model=RoutesStatusOut)
def routes_status(
    day: date = Query(..., description="YYYY-MM-DD"),
    db: Session = Depends(get_session),
):
    # expected per route
    expected_rows = db.execute(
        select(
            ExpectedItem.route,
            func.count(func.distinct(ExpectedItem.gb_number)),
        )
        .where(ExpectedItem.day == day)
        .group_by(ExpectedItem.route)
    ).all()
    expected_map = {r: c for r, c in expected_rows}

    # scanned per route
    scanned_rows = db.execute(
        select(
            Scan.route,
            func.count(func.distinct(Scan.gb_number)),
        )
        .where(Scan.day == day)
        .group_by(Scan.route)
    ).all()
    scanned_map = {r: c for r, c in scanned_rows}

    all_routes = sorted(set(expected_map.keys()) | set(scanned_map.keys()))
    result: list[RouteStatusItem] = []

    for route in all_routes:
        expected_count = int(expected_map.get(route, 0))
        scanned_count = int(scanned_map.get(route, 0))

        missing_count = max(expected_count - scanned_count, 0)
        extra_count = max(scanned_count - expected_count, 0)

        coverage_pct = round((scanned_count / expected_count) * 100.0, 2) if expected_count else 0.0
        complete = expected_count > 0 and missing_count == 0 and extra_count == 0

        result.append(
            RouteStatusItem(
                route=route,
                expected_count=expected_count,
                scanned_count=scanned_count,
                missing_count=missing_count,
                extra_count=extra_count,
                coverage_pct=coverage_pct,
                complete=complete,
            )
        )

    return RoutesStatusOut(day=day, routes=result)
@router.post("/routes/{route}/open")
def open_route(
    route: int,
    day: date = Query(..., description="YYYY-MM-DD"),
    db: Session = Depends(get_session),
):
    existing = db.scalar(
        select(RouteStatus).where(
            RouteStatus.day == day,
            RouteStatus.route == route,
        )
    )

    if existing:
        existing.status = "OPEN"
    else:
        existing = RouteStatus(day=day, route=route, status="OPEN")
        db.add(existing)

    db.commit()
    db.refresh(existing)

    return {
        "day": day.isoformat(),
        "route": route,
        "status": existing.status,
    }
@router.post("/routes/{route}/close")
def close_route(
    route: int,
    day: date = Query(..., description="YYYY-MM-DD"),
    db: Session = Depends(get_session),
):
    existing = db.scalar(
        select(RouteStatus).where(
            RouteStatus.day == day,
            RouteStatus.route == route,
        )
    )

    if existing:
        existing.status = "CLOSED"
    else:
        existing = RouteStatus(day=day, route=route, status="CLOSED")
        db.add(existing)

    db.commit()
    db.refresh(existing)

    return {
        "day": day.isoformat(),
        "route": route,
        "status": existing.status,
    }
@router.get("/routes/{route}/state")
def route_state(
    route: int,
    day: date = Query(..., description="YYYY-MM-DD"),
    db: Session = Depends(get_session),
):
    row = db.scalar(
        select(RouteStatus).where(
            RouteStatus.day == day,
            RouteStatus.route == route,
        )
    )

    if not row:
        return {"day": day.isoformat(), "route": route, "status": "NOT_FOUND"}

    return {"day": day.isoformat(), "route": route, "status": row.status}
