import json

from sqlalchemy.dialects import postgresql

from agent_eval_platform.execution.queue import _build_queued_tasks_query, lease_tasks
from sqlalchemy import select

from agent_eval_platform.models.run import ExecutionAttemptRecord, ExecutionTaskRecord


def test_lease_tasks_marks_rows_as_leased(session) -> None:
    session.add(
        ExecutionTaskRecord(
            id="task:case-001",
            run_case_id="case-001",
            executor_type="direct",
            adapter_type="http",
            dispatch_payload=json.dumps(
                {
                    "endpoint": "/invoke/health",
                    "method": "GET",
                    "body": {},
                    "headers": {"X-Eval-Mode": "contract"},
                }
            ),
            status="queued",
            priority=100,
        )
    )
    session.commit()

    leased = lease_tasks(session, worker_id="executor-1")

    assert leased[0].task_id == "task:case-001"
    assert leased[0].attempt_id
    assert leased[0].adapter_type == "http"
    assert leased[0].dispatch_payload == {
        "endpoint": "/invoke/health",
        "method": "GET",
        "body": {},
        "headers": {"X-Eval-Mode": "contract"},
    }
    assert session.get(ExecutionTaskRecord, "task:case-001").status == "leased"


def test_build_lease_query_uses_skip_locked_for_postgresql() -> None:
    stmt = _build_queued_tasks_query(dialect_name="postgresql", limit=1)
    compiled = str(stmt.compile(dialect=postgresql.dialect()))
    assert "FOR UPDATE SKIP LOCKED" in compiled.upper()


def test_lease_tasks_does_not_return_same_task_twice_sequentially(session) -> None:
    session.add_all(
        [
            ExecutionTaskRecord(
                id="task:case-001",
                run_case_id="case-001",
                executor_type="direct",
                adapter_type="http",
                dispatch_payload=json.dumps({"endpoint": "/one", "method": "GET", "body": {}}),
                status="queued",
                priority=100,
            ),
            ExecutionTaskRecord(
                id="task:case-002",
                run_case_id="case-002",
                executor_type="direct",
                adapter_type="http",
                dispatch_payload=json.dumps({"endpoint": "/two", "method": "GET", "body": {}}),
                status="queued",
                priority=90,
            ),
        ]
    )
    session.commit()

    first = lease_tasks(session, worker_id="executor-1")
    second = lease_tasks(session, worker_id="executor-2")

    assert first[0].task_id != second[0].task_id


def test_lease_tasks_generates_attempt_ids_within_64_chars(session) -> None:
    task_id = "task-" + ("x" * 59)
    session.add(
        ExecutionTaskRecord(
            id=task_id,
            run_case_id="case-003",
            executor_type="direct",
            adapter_type="native_test",
            dispatch_payload=json.dumps({"command": ["pytest", "-q"]}),
            status="queued",
            priority=100,
        )
    )
    session.commit()

    lease_tasks(session, worker_id="executor-1")
    attempt_ids = list(session.scalars(select(ExecutionAttemptRecord.id)))

    assert len(attempt_ids) == 1
    assert len(attempt_ids[0]) <= 64
