import json
from pathlib import Path

import pytest
from sqlalchemy import select

from agent_eval_platform.adapters.base import AdapterResult
from agent_eval_platform.models.analysis import ArtifactRecord
from agent_eval_platform.models.run import (
    ExecutionAttemptRecord,
    ExecutionTaskRecord,
)
from agent_eval_platform.storage.artifacts import LocalArtifactStorage
from workers.executor.main import ExecutorWorker, main


class _RecordingExecutor:
    def __init__(self, result: AdapterResult) -> None:
        self.result = result
        self.called_payload: dict | None = None

    def execute(self, payload: dict) -> AdapterResult:
        self.called_payload = payload
        return self.result


class _ExplodingExecutor:
    def __init__(self, error: Exception) -> None:
        self.error = error

    def execute(self, payload: dict) -> AdapterResult:
        raise self.error


def test_executor_worker_processes_leased_task_with_persisted_payload(session, tmp_path) -> None:
    session.add(
        ExecutionTaskRecord(
            id="task:case-001",
            run_case_id="case-001",
            executor_type="direct",
            adapter_type="native_test",
            dispatch_payload=json.dumps(
                {"command": ["python", "-m", "pytest", "-q", "tests/native/test_health.py"]}
            ),
            status="queued",
            priority=100,
        )
    )
    session.commit()

    executor = _RecordingExecutor(
        AdapterResult(
            status_code=0,
            body={"stdout": "1 passed", "stderr": ""},
            raw_text="1 passed",
        )
    )
    worker = ExecutorWorker(
        session=session,
        artifact_storage=LocalArtifactStorage(tmp_path),
    )
    worker.executor = executor
    worker.process_once(worker_id="executor-1")

    task = session.get(ExecutionTaskRecord, "task:case-001")
    attempt = session.scalar(
        select(ExecutionAttemptRecord).where(ExecutionAttemptRecord.task_id == "task:case-001")
    )
    artifact = session.scalar(select(ArtifactRecord).where(ArtifactRecord.owner_id == "task:case-001"))

    assert executor.called_payload == {
        "adapter_type": "native_test",
        "command": ["python", "-m", "pytest", "-q", "tests/native/test_health.py"],
    }
    assert task is not None
    assert task.status == "succeeded"
    assert attempt is not None
    assert attempt.status == "succeeded"
    assert artifact is not None
    assert artifact.owner_type == "execution_task"
    assert artifact.artifact_type == "execution_result"
    assert artifact.size_bytes > 0
    assert Path(artifact.storage_uri).read_text(encoding="utf-8")


def test_executor_worker_marks_task_failed_when_executor_cannot_start(session, tmp_path) -> None:
    session.add(
        ExecutionTaskRecord(
            id="task:case-002",
            run_case_id="case-002",
            executor_type="direct",
            adapter_type="native_test",
            dispatch_payload=json.dumps({"command": ["missing-binary", "--version"]}),
            status="queued",
            priority=100,
        )
    )
    session.commit()

    worker = ExecutorWorker(
        session=session,
        artifact_storage=LocalArtifactStorage(tmp_path),
    )
    worker.executor = _ExplodingExecutor(FileNotFoundError("missing-binary"))

    worker.process_once(worker_id="executor-1")

    task = session.get(ExecutionTaskRecord, "task:case-002")
    attempt = session.scalar(
        select(ExecutionAttemptRecord).where(ExecutionAttemptRecord.task_id == "task:case-002")
    )
    artifact = session.scalar(select(ArtifactRecord).where(ArtifactRecord.owner_id == "task:case-002"))

    assert task is not None
    assert task.status == "failed"
    assert attempt is not None
    assert attempt.status == "failed"
    assert artifact is not None
    assert "missing-binary" in Path(artifact.storage_uri).read_text(encoding="utf-8")


def test_executor_worker_main_requires_process_manager() -> None:
    with pytest.raises(
        SystemExit,
        match="Use uvicorn or a process manager to launch the executor worker",
    ):
        main()
