from __future__ import annotations

from datetime import date
from pydantic import BaseModel, Field


class RouteStatusItem(BaseModel):
    route: int = Field(..., ge=300, le=360)

    expected_count: int = Field(..., ge=0)
    scanned_count: int = Field(..., ge=0)

    missing_count: int = Field(..., ge=0)
    extra_count: int = Field(..., ge=0)

    coverage_pct: float = Field(..., ge=0.0)
    complete: bool


class RoutesStatusOut(BaseModel):
    day: date
    routes: list[RouteStatusItem]