from sqlalchemy.orm import Session

from agent_eval_platform.execution.artifacts import persist_execution_artifact
from agent_eval_platform.execution.queue import lease_tasks
from agent_eval_platform.execution.runner_protocol import RunnerClaimResponse, RunnerCompleteRequest
from agent_eval_platform.models.run import ExecutionAttemptRecord, ExecutionTaskRecord


class RunnerManager:
    def __init__(self, session: Session, artifact_storage=None) -> None:
        self.session = session
        self.artifact_storage = artifact_storage

    def claim_next_task(self, runner_id: str) -> RunnerClaimResponse | None:
        leased = lease_tasks(
            self.session,
            worker_id=runner_id,
            limit=1,
            executor_type="runner",
        )
        if not leased:
            return None

        task = leased[0]
        return RunnerClaimResponse(
            task_id=task.task_id,
            attempt_id=task.attempt_id,
            run_case_id=task.run_case_id,
            adapter_type=task.adapter_type,
            dispatch_payload=task.dispatch_payload,
        )

    def complete_task(self, payload: RunnerCompleteRequest) -> None:
        task = self.session.get(ExecutionTaskRecord, payload.task_id)
        attempt = self.session.get(ExecutionAttemptRecord, payload.attempt_id)
        if task is None:
            raise ValueError(f"execution task '{payload.task_id}' not found")
        if attempt is None:
            raise ValueError(f"execution attempt '{payload.attempt_id}' not found")

        final_status = payload.status
        if self.artifact_storage is not None:
            artifact_status = persist_execution_artifact(
                self.session,
                self.artifact_storage,
                task_id=payload.task_id,
                attempt_id=payload.attempt_id,
                body=payload.raw_result,
            )
            if artifact_status == "failed":
                final_status = "failed"

        task.status = final_status
        attempt.status = final_status
        self.session.commit()

    def get_task(self, task_id: str) -> ExecutionTaskRecord | None:
        return self.session.get(ExecutionTaskRecord, task_id)

    def get_attempt(self, attempt_id: str) -> ExecutionAttemptRecord | None:
        return self.session.get(ExecutionAttemptRecord, attempt_id)
