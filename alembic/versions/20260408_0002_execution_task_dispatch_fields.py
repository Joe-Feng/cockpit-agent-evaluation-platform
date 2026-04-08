from alembic import op
import sqlalchemy as sa


revision = "20260408_0002"
down_revision = "20260407_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "execution_tasks",
        sa.Column("adapter_type", sa.String(length=32), nullable=False, server_default=""),
    )
    op.add_column(
        "execution_tasks",
        sa.Column("dispatch_payload", sa.Text(), nullable=False, server_default="{}"),
    )


def downgrade() -> None:
    op.drop_column("execution_tasks", "dispatch_payload")
    op.drop_column("execution_tasks", "adapter_type")
