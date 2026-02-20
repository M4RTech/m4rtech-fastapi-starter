from __future__ import annotations

import re
from datetime import date, datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator

GB_PATTERN = re.compile(r"^GB\d{9}([A-Z]\d)?$")


class ExpectedBulkIn(BaseModel):
    day: date = Field(default_factory=lambda: datetime.now(timezone.utc).date())
    route: int = Field(..., ge=300, le=360)
    items: list[str] = Field(..., min_length=1)
    mode: Literal["replace"] = "replace"  # na razie tylko replace, jak chcesz dodamy append później

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: list[str]) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()

        for raw in v:
            gb = raw.strip().upper()
            if not gb:
                continue
            if not GB_PATTERN.match(gb):
                raise ValueError(f"Invalid GB number in items: {raw!r}")
            if gb not in seen:
                cleaned.append(gb)
                seen.add(gb)

        if not cleaned:
            raise ValueError("items cannot be empty after normalization")
        return cleaned


class ExpectedBulkOut(BaseModel):
    day: date
    route: int
    expected_count: int
    inserted: int
    skipped_duplicates: int
    mode: str = "replace"


class ReconcileOut(BaseModel):
    day: date
    route: int

    expected_count: int
    scanned_count: int

    missing_count: int
    extra_count: int

    missing: list[str]
    extra: list[str]

    coverage_pct: float
