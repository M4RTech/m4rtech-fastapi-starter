"""add route day user

Revision ID: cdbe21570c3c
Revises: 6772525eae41
Create Date: 2026-02-19 07:55:15.673097

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cdbe21570c3c'
down_revision: Union[str, Sequence[str], None] = '6772525eae41'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("scans") as batch_op:
        batch_op.add_column(sa.Column("route", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("day", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("user", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("drop_number", sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("scans") as batch_op:
        batch_op.drop_column("drop_number")
        batch_op.drop_column("user")
        batch_op.drop_column("day")
        batch_op.drop_column("route")
