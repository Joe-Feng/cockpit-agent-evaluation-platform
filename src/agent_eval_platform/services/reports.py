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
        return {
            "run_id": run.id,
            "status": run.status,
            "target_id": run.target_id,
            "env_id": run.env_id,
            "suite_ids": suite_ids,
            "suite_count": len(suite_ids),
            "case_count": self.repository.count_cases_for_run(run_id),
            "task_count": self.repository.count_tasks_for_run(run_id),
            "passed_count": self.repository.count_cases_for_run_with_status(run_id, "passed"),
            "regression_signals": [],
        }
