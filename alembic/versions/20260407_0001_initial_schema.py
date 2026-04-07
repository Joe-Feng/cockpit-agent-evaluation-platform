from alembic import op
import sqlalchemy as sa


revision = "20260407_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "targets",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("adapter_types", sa.String(length=256), nullable=False),
        sa.Column("raw_profile_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "environments",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("raw_profile_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "suites",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("mode", sa.String(length=64), nullable=False),
        sa.Column("raw_definition_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "cases",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("suite_id", sa.String(length=64), nullable=False),
        sa.Column("raw_definition_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_cases_suite_id", "cases", ["suite_id"])
    op.create_table(
        "runs",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("target_id", sa.String(length=64), nullable=False),
        sa.Column("env_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_runs_target_id", "runs", ["target_id"])
    op.create_table(
        "run_suites",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("suite_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
    )
    op.create_index("ix_run_suites_run_id", "run_suites", ["run_id"])
    op.create_table(
        "run_cases",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("run_suite_id", sa.String(length=64), nullable=False),
        sa.Column("case_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
    )
    op.create_index("ix_run_cases_run_suite_id", "run_cases", ["run_suite_id"])
    op.create_table(
        "execution_tasks",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("run_case_id", sa.String(length=64), nullable=False),
        sa.Column("executor_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
    )
    op.create_index("ix_execution_tasks_run_case_id", "execution_tasks", ["run_case_id"])
    op.create_table(
        "execution_attempts",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("task_id", sa.String(length=64), nullable=False),
        sa.Column("attempt_no", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
    )
    op.create_index("ix_execution_attempts_task_id", "execution_attempts", ["task_id"])
    op.create_table(
        "artifacts",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("owner_type", sa.String(length=32), nullable=False),
        sa.Column("owner_id", sa.String(length=64), nullable=False),
        sa.Column("artifact_type", sa.String(length=64), nullable=False),
        sa.Column("storage_uri", sa.String(length=512), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
    )
    op.create_index("ix_artifacts_owner_id", "artifacts", ["owner_id"])


def downgrade() -> None:
    op.drop_index("ix_artifacts_owner_id", table_name="artifacts")
    op.drop_table("artifacts")
    op.drop_index("ix_execution_attempts_task_id", table_name="execution_attempts")
    op.drop_table("execution_attempts")
    op.drop_index("ix_execution_tasks_run_case_id", table_name="execution_tasks")
    op.drop_table("execution_tasks")
    op.drop_index("ix_run_cases_run_suite_id", table_name="run_cases")
    op.drop_table("run_cases")
    op.drop_index("ix_run_suites_run_id", table_name="run_suites")
    op.drop_table("run_suites")
    op.drop_index("ix_runs_target_id", table_name="runs")
    op.drop_table("runs")
    op.drop_index("ix_cases_suite_id", table_name="cases")
    op.drop_table("cases")
    op.drop_table("suites")
    op.drop_table("environments")
    op.drop_table("targets")
