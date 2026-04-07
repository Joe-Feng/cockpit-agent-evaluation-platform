from agent_eval_platform.execution.queue import lease_tasks
from agent_eval_platform.models.run import ExecutionTaskRecord
from agent_eval_platform.storage.artifacts import LocalArtifactStorage
from workers.executor.main import ExecutorWorker


def test_executor_worker_processes_leased_task(session, tmp_path) -> None:
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

    worker = ExecutorWorker(
        session=session,
        artifact_storage=LocalArtifactStorage(tmp_path),
    )
    worker.process_once(worker_id="executor-1")

    task = session.get(ExecutionTaskRecord, "task:case-001")
    assert task.status in {"succeeded", "failed"}
