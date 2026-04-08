from sqlalchemy import inspect

from agent_eval_platform.db import Base


def test_metadata_contains_initial_tables() -> None:
    expected = {
        "targets",
        "environments",
        "suites",
        "cases",
        "runs",
        "run_suites",
        "run_cases",
        "execution_tasks",
        "execution_attempts",
        "artifacts",
    }
    assert expected.issubset(Base.metadata.tables.keys())


def test_execution_tasks_schema_includes_dispatch_columns(engine) -> None:
    columns = {column["name"] for column in inspect(engine).get_columns("execution_tasks")}

    assert {"adapter_type", "dispatch_payload"}.issubset(columns)
