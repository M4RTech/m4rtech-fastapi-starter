from __future__ import annotations
from datetime import date

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.v1.endpoints.routes import routes_status
from app.db.session import get_session

router = APIRouter(tags=["ui"])
templates = Jinja2Templates(directory="app/ui/templates")


@router.get("/ui")
def ui_home(
    request: Request,
    day: date = date.today(),
    session: Session = Depends(get_session),
):
    status = routes_status(day=day, db=session)
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "day": day, "status": status},
    )

