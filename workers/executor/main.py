from pathlib import Path

import httpx

from agent_eval_platform.adapters.http import HttpAdapter
from agent_eval_platform.adapters.native_test import NativeTestAdapter
from agent_eval_platform.execution.direct_executor import DirectExecutor
from agent_eval_platform.execution.queue import lease_tasks
from agent_eval_platform.models.analysis import ArtifactRecord
from agent_eval_platform.models.run import ExecutionAttemptRecord, ExecutionTaskRecord
from agent_eval_platform.orchestration_ids import build_orchestration_id


class ExecutorWorker:
    def __init__(self, session, artifact_storage) -> None:
        self.session = session
        self.artifact_storage = artifact_storage
        self.executor = DirectExecutor(
            http_adapter=HttpAdapter(httpx.Client(base_url="http://127.0.0.1:8000")),
            native_test_adapter=NativeTestAdapter(),
        )

    def process_once(self, worker_id: str) -> None:
        leased = lease_tasks(self.session, worker_id=worker_id)
        for task in leased:
            task_record = self.session.get(ExecutionTaskRecord, task.task_id)
            attempt_record = self.session.get(ExecutionAttemptRecord, task.attempt_id)
            try:
                result = self.executor.execute(
                    {
                        "adapter_type": task.adapter_type,
                        **task.dispatch_payload,
                    }
                )
                task_status = (
                    "succeeded"
                    if self._is_success(adapter_type=task.adapter_type, status_code=result.status_code)
                    else "failed"
                )
                artifact_body = {
                    "status_code": result.status_code,
                    "body": result.body,
                    "raw_text": result.raw_text,
                }
            except Exception as exc:
                task_status = "failed"
                artifact_body = {
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }

            storage_uri = self.artifact_storage.write_json(task.attempt_id, artifact_body)
            self.session.add(
                ArtifactRecord(
                    id=build_orchestration_id("artifact", task.task_id, task.attempt_id),
                    owner_type="execution_task",
                    owner_id=task.task_id,
                    artifact_type="execution_result",
                    storage_uri=storage_uri,
                    size_bytes=Path(storage_uri).stat().st_size,
                )
            )
            if task_record is not None:
                task_record.status = task_status
            if attempt_record is not None:
                attempt_record.status = task_status
            self.session.commit()

    @staticmethod
    def _is_success(*, adapter_type: str, status_code: int) -> bool:
        if adapter_type == "native_test":
            return status_code == 0
        return 200 <= status_code < 400


def main() -> None:
    raise SystemExit("Use uvicorn or a process manager to launch the executor worker")
