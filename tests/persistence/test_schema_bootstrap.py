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
