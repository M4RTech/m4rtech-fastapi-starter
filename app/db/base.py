from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models so that Alembic can discover them.
# Must be after Base definition to avoid circular import.
from app.db import models  # noqa: F401, E402
