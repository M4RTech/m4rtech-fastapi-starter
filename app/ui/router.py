from __future__ import annotations

from datetime import date
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.api.v1.endpoints.routes import routes_status  # reuse logic if simple
from app.api.v1.endpoints.routes import route_summary, route_state, route_scans

router = APIRouter(tags=["ui"])
templates = Jinja2Templates(directory="app/ui/templates")


@router.get("/ui", response_class=HTMLResponse)
def ui_home(
    request: Request,
    day: date = Query(default_factory=date.today),
    session: Session = Depends(get_session),
):
    # korzystamy z istniejącej logiki endpointu API
    status = routes_status(day=day, session=session)  # type: ignore
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "day": day, "status": status},
    )


@router.get("/ui/partials/routes", response_class=HTMLResponse)
def ui_routes_partial(
    request: Request,
    day: date = Query(default_factory=date.today),
    session: Session = Depends(get_session),
):
    status = routes_status(day=day, session=session)  # type: ignore
    return templates.TemplateResponse(
        "partials/routes_table.html",
        {"request": request, "day": day, "status": status},
    )


@router.get("/ui/route/{route}", response_class=HTMLResponse)
def ui_route(
    request: Request,
    route: int,
    day: date = Query(default_factory=date.today),
    session: Session = Depends(get_session),
):
    summary = route_summary(route=route, day=day, session=session)  # type: ignore
    state = route_state(route=route, day=day, session=session)  # type: ignore
    scans = route_scans(route=route, day=day, limit=200, session=session)  # type: ignore

    return templates.TemplateResponse(
        "route.html",
        {"request": request, "day": day, "route": route, "summary": summary, "state": state, "scans": scans},
    )
