from __future__ import annotations

from datetime import date
from sqlalchemy import func, select, desc
from sqlalchemy.orm import Session

from app.db.models import Scan


def scans_summary(session: Session, route: int, day: date):
    q = (
        select(
            func.count(Scan.id).label("count"),
            func.count(func.distinct(Scan.gb_number)).label("unique_gb"),
            func.min(Scan.ts).label("first_ts"),
            func.max(Scan.ts).label("last_ts"),
        )
        .where(Scan.route == route, Scan.day == day)
    )
    row = session.execute(q).one()

    return {
        "day": str(day),
        "route": route,
        "count": int(row.count or 0),
        "unique_gb": int(row.unique_gb or 0),
        "first_ts": row.first_ts.isoformat() if row.first_ts else None,
        "last_ts": row.last_ts.isoformat() if row.last_ts else None,
    }


def scans_list(session: Session, route: int, day: date, limit: int = 200):
    q = (
        select(Scan)
        .where(Scan.route == route, Scan.day == day)
        .order_by(desc(Scan.ts))
        .limit(limit)
    )
    items = session.execute(q).scalars().all()

    return [
        {
            "id": s.id,
            "gb_number": s.gb_number,
            "route": s.route,
            "day": str(s.day),
            "user": s.user,
            "drop_number": s.drop_number,
            "ts": s.ts.isoformat() if s.ts else None,
        }
        for s in items
    ]

