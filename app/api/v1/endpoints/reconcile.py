from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.schemas.expected import ReconcileOut
from app.db.models import ExpectedItem, Scan
from app.db.session import get_session

router = APIRouter(tags=["reconcile"])


@router.get("/reconcile", response_model=ReconcileOut)
def reconcile(
    day: date = Query(..., description="e.g. 2026-02-19"),
    route: int = Query(..., ge=300, le=360, description="e.g. 320"),
    db: Session = Depends(get_session),
):
    expected = db.execute(
        select(ExpectedItem.gb_number).where(
            ExpectedItem.day == day,
            ExpectedItem.route == route,
        )
    ).scalars().all()

    scanned = db.execute(
        select(Scan.gb_number).where(
            Scan.day == day,
            Scan.route == route,
        )
    ).scalars().all()

    expected_set = set(expected)
    scanned_set = set(scanned)

    missing = sorted(expected_set - scanned_set)
    extra = sorted(scanned_set - expected_set)

    expected_count = len(expected_set)
    scanned_count = len(scanned_set)

    coverage = 0.0
    if expected_count > 0:
        coverage = round((scanned_count / expected_count) * 100.0, 2)

    return ReconcileOut(
        day=day,
        route=route,
        expected_count=expected_count,
        scanned_count=scanned_count,
        missing_count=len(missing),
        extra_count=len(extra),
        missing=missing,
        extra=extra,
        coverage_pct=coverage,
    )
