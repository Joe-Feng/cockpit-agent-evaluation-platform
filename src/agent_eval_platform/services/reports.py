from fastapi import HTTPException, status

from agent_eval_platform.repositories.run import RunRepository


class ReportService:
    def __init__(self, repository: RunRepository) -> None:
        self.repository = repository

    def build_run_report(self, run_id: str) -> dict[str, object]:
        run = self.repository.get_run(run_id)
        if run is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"run '{run_id}' not found",
            )

        suite_ids = self.repository.list_suite_ids_for_run(run_id)
        task_count = self.repository.count_tasks_for_run(run_id)
        passed_count = self.repository.count_tasks_for_run_with_status(run_id, "succeeded")
        failed_count = self.repository.count_tasks_for_run_with_status(run_id, "failed")
        leased_count = self.repository.count_tasks_for_run_with_status(run_id, "leased")
        queued_count = self.repository.count_tasks_for_run_with_status(run_id, "queued")
        return {
            "run_id": run.id,
            "status": self._derive_status(
                persisted_status=run.status,
                task_count=task_count,
                passed_count=passed_count,
                failed_count=failed_count,
                leased_count=leased_count,
                queued_count=queued_count,
            ),
            "target_id": run.target_id,
            "env_id": run.env_id,
            "suite_ids": suite_ids,
            "suite_count": len(suite_ids),
            "case_count": self.repository.count_cases_for_run(run_id),
            "task_count": task_count,
            "passed_count": passed_count,
            "regression_signals": [],
        }

    @staticmethod
    def _derive_status(
        *,
        persisted_status: str,
        task_count: int,
        passed_count: int,
        failed_count: int,
        leased_count: int,
        queued_count: int,
    ) -> str:
        if task_count == 0:
            return persisted_status
        if passed_count == task_count:
            return "succeeded"
        if failed_count > 0 and passed_count + failed_count == task_count:
            return "failed"
        if queued_count == task_count:
            return "queued"
        if leased_count > 0 or queued_count > 0 or passed_count > 0 or failed_count > 0:
            return "running"
        return persisted_status
