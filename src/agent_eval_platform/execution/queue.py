import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_eval_platform.execution.contracts import LeasedTask
from agent_eval_platform.models.run import ExecutionAttemptRecord, ExecutionTaskRecord
from agent_eval_platform.orchestration_ids import build_orchestration_id


def _build_queued_tasks_query(*, dialect_name: str, limit: int):
    stmt = (
        select(ExecutionTaskRecord)
        .where(ExecutionTaskRecord.status == "queued")
        .order_by(ExecutionTaskRecord.priority.desc(), ExecutionTaskRecord.id)
        .limit(limit)
    )
    if dialect_name == "postgresql":
        stmt = stmt.with_for_update(skip_locked=True)
    return stmt


def lease_tasks(session: Session, worker_id: str, limit: int = 1) -> list[LeasedTask]:
    del worker_id
    bind = session.get_bind()
    dialect_name = bind.dialect.name if bind is not None else ""
    queued = list(
        session.scalars(_build_queued_tasks_query(dialect_name=dialect_name, limit=limit))
    )
    leased: list[LeasedTask] = []
    for task in queued:
        task.status = "leased"
        attempt_no = 1
        attempt_id = build_orchestration_id("attempt", task.id, str(attempt_no))
        session.add(
            ExecutionAttemptRecord(
                id=attempt_id,
                task_id=task.id,
                attempt_no=attempt_no,
                status="leased",
            )
        )
        leased.append(
            LeasedTask(
                task_id=task.id,
                attempt_id=attempt_id,
                run_case_id=task.run_case_id,
                executor_type=task.executor_type,
                adapter_type=task.adapter_type,
                dispatch_payload=json.loads(task.dispatch_payload),
            )
        )

    session.commit()
    return leased
