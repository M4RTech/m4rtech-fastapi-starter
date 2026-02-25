from __future__ import annotations

from datetime import date
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Scan


def routes_status(session: Session, day: date, route_min: int = 300, route_max: int = 360):
    # zlicz skany per route dla dnia
    q = (
        select(Scan.route, func.count(Scan.id).label("scanned_count"))
        .where(Scan.day == day, Scan.route >= route_min, Scan.route <= route_max)
        .group_by(Scan.route)
        .order_by(Scan.route)
    )
    rows = session.execute(q).all()
    scanned_by_route = {int(r.route): int(r.scanned_count) for r in rows}

    routes = []
    for route in range(route_min, route_max + 1):
        scanned = scanned_by_route.get(route, 0)
        # Na razie expected/coverage nie liczymy (bo to zależy od expected table).
        # Dashboard pokaże chociaż "ile zeskanowano".
        routes.append(
            {
                "route": route,
                "scanned_count": scanned,
            }
        )

    return {"day": str(day), "routes": routes}
