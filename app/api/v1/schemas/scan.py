#/app/api/v1/schemas/scan.py
import re
from datetime import datetime, date, timezone

from pydantic import BaseModel, Field, field_validator, ConfigDict

GB_PATTERN = re.compile(r"^GB\d{9}([A-Z]\d)?$")  # GB123456789 lub GB123456789A1


class ScanIn(BaseModel):
    gb_number: str
    route: int = Field(..., ge=300, le=360)
    day: date = Field(default_factory=lambda: datetime.now(timezone.utc).date())
    user: str | None = None
    drop_number: int | None = Field(default=None, ge=1, le=130)

    @field_validator("gb_number")
    @classmethod
    def validate_gb(cls, v: str) -> str:
        gb = v.strip().upper()
        if not GB_PATTERN.match(gb):
            raise ValueError("Invalid GB number")
        return gb


class ScanOut(BaseModel):
    id: int
    gb_number: str
    route: int
    day: date
    user: str | None
    drop_number: int | None = None
    ts: datetime

    model_config = ConfigDict(from_attributes=True)


class ScanCreateResponse(BaseModel):
    id: int
    received: str
    route: int
    length: int
    day: date
    user: str | None
    status: str = "ok"
    saved: bool = True


class ScanListResponse(BaseModel):
    count: int
    items: list[ScanOut]


class ClearResponse(BaseModel):
    cleared: bool = True
    removed_count: int
