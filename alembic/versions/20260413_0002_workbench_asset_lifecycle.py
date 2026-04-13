from alembic import op
import sqlalchemy as sa


revision = "20260413_0002"
down_revision = "20260408_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "suites",
        sa.Column("asset_status", sa.String(length=32), nullable=False, server_default="draft"),
    )
    op.add_column(
        "suites",
        sa.Column("version_group_id", sa.String(length=64), nullable=False, server_default=""),
    )
    op.add_column("suites", sa.Column("superseded_by_id", sa.String(length=64), nullable=True))
    op.create_index("ix_suites_asset_status", "suites", ["asset_status"])
    op.create_index("ix_suites_version_group_id", "suites", ["version_group_id"])
    op.create_index("ix_suites_superseded_by_id", "suites", ["superseded_by_id"])

    op.add_column(
        "cases",
        sa.Column("asset_status", sa.String(length=32), nullable=False, server_default="draft"),
    )
    op.add_column(
        "cases",
        sa.Column("version_group_id", sa.String(length=64), nullable=False, server_default=""),
    )
    op.add_column("cases", sa.Column("superseded_by_id", sa.String(length=64), nullable=True))
    op.create_index("ix_cases_asset_status", "cases", ["asset_status"])
    op.create_index("ix_cases_version_group_id", "cases", ["version_group_id"])
    op.create_index("ix_cases_superseded_by_id", "cases", ["superseded_by_id"])


def downgrade() -> None:
    op.drop_index("ix_cases_superseded_by_id", table_name="cases")
    op.drop_index("ix_cases_version_group_id", table_name="cases")
    op.drop_index("ix_cases_asset_status", table_name="cases")
    op.drop_column("cases", "superseded_by_id")
    op.drop_column("cases", "version_group_id")
    op.drop_column("cases", "asset_status")

    op.drop_index("ix_suites_superseded_by_id", table_name="suites")
    op.drop_index("ix_suites_version_group_id", table_name="suites")
    op.drop_index("ix_suites_asset_status", table_name="suites")
    op.drop_column("suites", "superseded_by_id")
    op.drop_column("suites", "version_group_id")
    op.drop_column("suites", "asset_status")
