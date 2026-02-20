#models.py
from datetime import datetime, timezone, date
from sqlalchemy import Date, DateTime, Integer, String, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


from app.db.base import Base

class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    gb_number: Mapped[str] = mapped_column(String(64), nullable=False)
    route: Mapped[int] = mapped_column(Integer, nullable=False)
    day: Mapped[date] = mapped_column(Date, nullable=False)
    user: Mapped[str | None] = mapped_column(String(64), nullable=True)
    drop_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        # 🔐 unikalność biznesowa
        UniqueConstraint("day", "route", "gb_number", name="uq_scans_day_route_gb"),

        # 📊 pod summary
        Index("ix_scans_day_route", "day", "route"),

        # ⚡ pod listę skanów (sortowanie po czasie)
        Index("ix_scans_day_route_ts", "day", "route", "ts"),
    )
class ExpectedItem(Base):
    __tablename__ = "expected_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    day: Mapped[date] = mapped_column(Date, nullable=False)
    route: Mapped[int] = mapped_column(Integer, nullable=False)
    gb_number: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        UniqueConstraint("day", "route", "gb_number", name="uq_expected_day_route_gb"),
        Index("ix_expected_day_route", "day", "route"),
    )