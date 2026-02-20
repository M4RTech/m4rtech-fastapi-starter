from alembic import op

# revision identifiers, used by Alembic.
revision = "8b59d0f865eb"
down_revision = "cdbe21570c3c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("scans") as batch_op:
        batch_op.create_unique_constraint(
            "uq_scans_day_route_gb", ["day", "route", "gb_number"]
        )


def downgrade() -> None:
    with op.batch_alter_table("scans") as batch_op:
        batch_op.drop_constraint(
            "uq_scans_day_route_gb", type_="unique"
        )
