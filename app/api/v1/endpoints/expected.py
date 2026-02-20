from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import delete, select, func
from sqlalchemy.orm import Session

from app.api.v1.schemas.expected import ExpectedBulkIn, ExpectedBulkOut
from app.db.models import ExpectedItem
from app.db.session import get_session

router = APIRouter(tags=["expected"])


@router.post("/expected/bulk", response_model=ExpectedBulkOut)
def expected_bulk(payload: ExpectedBulkIn, db: Session = Depends(get_session)):
    # REPLACE = reset listy dla day+route
    db.execute(
        delete(ExpectedItem).where(
            ExpectedItem.day == payload.day,
            ExpectedItem.route == payload.route,
        )
    )

    # bulk insert
    rows = [
        ExpectedItem(day=payload.day, route=payload.route, gb_number=gb)
        for gb in payload.items
    ]
    db.add_all(rows)
    db.commit()

    expected_count = db.scalar(
        select(func.count()).select_from(ExpectedItem).where(
            ExpectedItem.day == payload.day,
            ExpectedItem.route == payload.route,
        )
    ) or 0

    return ExpectedBulkOut(
        day=payload.day,
        route=payload.route,
        expected_count=expected_count,
        inserted=len(rows),
        skipped_duplicates=0,  # bo w validate_items już deduplikujemy
    )
