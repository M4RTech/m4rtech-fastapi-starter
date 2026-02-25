from __future__ import annotations
from datetime import date, datetime
from fastapi import APIRouter, Depends, Request, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from app.api.v1.endpoints.routes import routes_status
from app.db.session import get_session

templates = Jinja2Templates(directory="app/ui/templates")
ui_router = APIRouter(prefix="/ui", tags=["ui"])

def parse_day(day_str: str | None) -> date:
    if not day_str:
        return datetime.utcnow().date()
    return date.fromisoformat(day_str)  # expects YYYY-MM-DD

@ui_router.get("", response_class=HTMLResponse)
def ui_index(
    request: Request,
    day: str | None = Query(default=None),
):
    day_date = parse_day(day)

    return templates.TemplateResponse(
        "ui/index.html",
        {
            "request": request,
            "day": day_date.isoformat(),
        },
    )

@ui_router.get("/partials/routes-table", response_class=HTMLResponse)
def routes_table_partial(
    request: Request,
    session: Session = Depends(get_session),
    day: str | None = Query(default=None),
):
    day_date = parse_day(day)

    # TODO: podmień na Twoją logikę / queries:
    # routes_status = get_routes_status(session, day_date)
    routes_status = [
        {"route": 301, "expected": 120, "scanned": 115, "missing": 5, "extra": 0, "status": "IN_PROGRESS"},
        {"route": 302, "expected": 98, "scanned": 98, "missing": 0, "extra": 0, "status": "OK"},
    ]

    return templates.TemplateResponse(
        "ui/partials/routes_table.html",
        {
            "request": request,
            "day": day_date.isoformat(),
            "rows": routes_status,
        },
    )
