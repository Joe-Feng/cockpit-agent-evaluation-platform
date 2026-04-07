import httpx

from agent_eval_platform.adapters.http import HttpAdapter
from agent_eval_platform.adapters.native_test import NativeTestAdapter
from agent_eval_platform.execution.direct_executor import DirectExecutor
from agent_eval_platform.execution.queue import lease_tasks
from agent_eval_platform.models.run import ExecutionTaskRecord


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
            result = self.executor.execute(
                {
                    "adapter_type": "native_test",
                    "command": ["python", "-c", "print('ok')"],
                }
            )
            self.artifact_storage.write_json(task.task_id, result.body)
            task_record = self.session.get(ExecutionTaskRecord, task.task_id)
            task_record.status = "succeeded" if result.status_code == 0 else "failed"
            self.session.commit()
