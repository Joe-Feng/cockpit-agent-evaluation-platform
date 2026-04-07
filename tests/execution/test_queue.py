from agent_eval_platform.execution.queue import lease_tasks
from agent_eval_platform.models.run import ExecutionTaskRecord


def test_lease_tasks_marks_rows_as_leased(session) -> None:
    session.add(
        ExecutionTaskRecord(
            id="task:case-001",
            run_case_id="case-001",
            executor_type="direct",
            status="queued",
            priority=100,
        )
    )
    session.commit()

    leased = lease_tasks(session, worker_id="executor-1")

    assert leased[0].task_id == "task:case-001"
    assert session.get(ExecutionTaskRecord, "task:case-001").status == "leased"
