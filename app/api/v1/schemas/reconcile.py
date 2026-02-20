from datetime import date
from pydantic import BaseModel


class ReconcileResponse(BaseModel):
    day: date
    route: int
    expected_count: int
    scanned_count: int
    missing: list[str]
    extra: list[str]
