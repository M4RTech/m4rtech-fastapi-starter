"""create scan indexes

Revision ID: deb6a3041bd3
Revises: 263b6e101a12
Create Date: 2026-02-20 20:46:48.411592

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'deb6a3041bd3'
down_revision: Union[str, Sequence[str], None] = '263b6e101a12'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "ix_scans_day_route",
        "scans",
        ["day", "route"],
        unique=False,
    )

    op.create_index(
        "ix_scans_day_route_ts",
        "scans",
        ["day", "route", "ts"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_scans_day_route_ts", table_name="scans")
    op.drop_index("ix_scans_day_route", table_name="scans")
