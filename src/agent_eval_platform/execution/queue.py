from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_eval_platform.execution.contracts import LeasedTask
from agent_eval_platform.models.run import ExecutionAttemptRecord, ExecutionTaskRecord


def lease_tasks(session: Session, worker_id: str, limit: int = 1) -> list[LeasedTask]:
    del worker_id
    queued = list(
        session.scalars(
            select(ExecutionTaskRecord)
            .where(ExecutionTaskRecord.status == "queued")
            .order_by(ExecutionTaskRecord.priority.desc(), ExecutionTaskRecord.id)
            .limit(limit)
        )
    )
    leased: list[LeasedTask] = []
    for task in queued:
        task.status = "leased"
        session.add(
            ExecutionAttemptRecord(
                id=f"attempt:{task.id}:1",
                task_id=task.id,
                attempt_no=1,
                status="leased",
            )
        )
        leased.append(
            LeasedTask(
                task_id=task.id,
                run_case_id=task.run_case_id,
                executor_type=task.executor_type,
            )
        )

    session.commit()
    return leased
