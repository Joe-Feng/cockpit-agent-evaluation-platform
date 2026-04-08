import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from fastapi import HTTPException, status

from agent_eval_platform.analysis.baseline import diff_against_baseline
from agent_eval_platform.analysis.normalize import normalize_http_result
from agent_eval_platform.analysis.regression import build_regression_signal
from agent_eval_platform.models.run import RunRecord
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
        report_status = self._derive_status(
            persisted_status=run.status,
            task_count=task_count,
            passed_count=passed_count,
            failed_count=failed_count,
            leased_count=leased_count,
            queued_count=queued_count,
        )
        normalized_results = self._build_normalized_results(run_id=run.id, target_id=run.target_id)
        regression_signals = self._build_regression_signals(
            run=run,
            run_status=report_status,
            suite_ids=suite_ids,
            task_count=task_count,
            passed_count=passed_count,
        )
        return {
            "run_id": run.id,
            "status": report_status,
            "target_id": run.target_id,
            "env_id": run.env_id,
            "suite_ids": suite_ids,
            "suite_count": len(suite_ids),
            "case_count": self.repository.count_cases_for_run(run_id),
            "task_count": task_count,
            "passed_count": passed_count,
            "normalized_results": normalized_results,
            "regression_signals": regression_signals,
        }

    def build_pass_rate_diff(self, run_id: str) -> dict[str, Any] | None:
        run = self.repository.get_run(run_id)
        if run is None:
            return None

        suite_ids = self.repository.list_suite_ids_for_run(run_id)
        task_count = self.repository.count_tasks_for_run(run_id)
        passed_count = self.repository.count_tasks_for_run_with_status(run_id, "succeeded")
        failed_count = self.repository.count_tasks_for_run_with_status(run_id, "failed")
        leased_count = self.repository.count_tasks_for_run_with_status(run_id, "leased")
        queued_count = self.repository.count_tasks_for_run_with_status(run_id, "queued")
        run_status = self._derive_status(
            persisted_status=run.status,
            task_count=task_count,
            passed_count=passed_count,
            failed_count=failed_count,
            leased_count=leased_count,
            queued_count=queued_count,
        )
        return self._build_pass_rate_diff(
            run=run,
            run_status=run_status,
            suite_ids=suite_ids,
            task_count=task_count,
            passed_count=passed_count,
        )

    def _build_normalized_results(self, *, run_id: str, target_id: str) -> list[dict[str, Any]]:
        target_profile = self.repository.get_target_profile(target_id)
        result_mapping = target_profile.get("result_mapping")
        if not isinstance(result_mapping, Mapping) or not result_mapping:
            return []

        tasks = self.repository.list_execution_tasks_for_run(run_id)
        artifacts = self.repository.list_execution_result_artifacts([task.id for task in tasks])
        artifacts_by_task_id = {artifact.owner_id: artifact for artifact in artifacts}

        normalized_results: list[dict[str, Any]] = []
        for task in tasks:
            if task.adapter_type != "http":
                continue
            body = self._read_artifact_body(artifacts_by_task_id.get(task.id))
            if isinstance(body, Mapping):
                normalized_results.append(normalize_http_result(body, result_mapping))
        return normalized_results

    def _build_regression_signals(
        self,
        *,
        run: RunRecord,
        run_status: str,
        suite_ids: list[str],
        task_count: int,
        passed_count: int,
    ) -> list[dict[str, Any]]:
        diff = self._build_pass_rate_diff(
            run=run,
            run_status=run_status,
            suite_ids=suite_ids,
            task_count=task_count,
            passed_count=passed_count,
        )
        if diff is None:
            return []
        signal = build_regression_signal("pass_rate", diff)
        return [signal] if bool(signal.get("is_regression")) else []

    def _build_pass_rate_diff(
        self,
        *,
        run: RunRecord,
        run_status: str,
        suite_ids: list[str],
        task_count: int,
        passed_count: int,
    ) -> dict[str, Any] | None:
        if task_count == 0 or run_status not in {"succeeded", "failed"}:
            return None

        baseline_run = self._find_comparable_baseline_run(run=run, suite_ids=suite_ids)
        if baseline_run is None:
            return None

        baseline_task_count = self.repository.count_tasks_for_run(baseline_run.id)
        if baseline_task_count == 0:
            return None

        baseline_passed_count = self.repository.count_tasks_for_run_with_status(
            baseline_run.id,
            "succeeded",
        )
        return diff_against_baseline(
            current_value=passed_count / task_count,
            baseline_value=baseline_passed_count / baseline_task_count,
            metric_id="pass_rate",
        )

    def _find_comparable_baseline_run(
        self,
        *,
        run: RunRecord,
        suite_ids: list[str],
    ) -> RunRecord | None:
        suite_key = tuple(sorted(suite_ids))
        candidates = self.repository.list_candidate_baseline_runs(
            current_run_id=run.id,
            target_id=run.target_id,
            env_id=run.env_id,
            created_at=run.created_at,
        )
        for candidate in candidates:
            candidate_suite_ids = self.repository.list_suite_ids_for_run(candidate.id)
            if tuple(sorted(candidate_suite_ids)) == suite_key and self._is_completed_run(candidate):
                return candidate
        return None

    @staticmethod
    def _read_artifact_body(artifact: Any | None) -> Mapping[str, Any] | None:
        if artifact is None:
            return None
        try:
            payload = json.loads(Path(artifact.storage_uri).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(payload, Mapping):
            return None
        body = payload.get("body")
        return body if isinstance(body, Mapping) else None

    def _is_completed_run(self, run: RunRecord) -> bool:
        task_count = self.repository.count_tasks_for_run(run.id)
        passed_count = self.repository.count_tasks_for_run_with_status(run.id, "succeeded")
        failed_count = self.repository.count_tasks_for_run_with_status(run.id, "failed")
        leased_count = self.repository.count_tasks_for_run_with_status(run.id, "leased")
        queued_count = self.repository.count_tasks_for_run_with_status(run.id, "queued")
        run_status = self._derive_status(
            persisted_status=run.status,
            task_count=task_count,
            passed_count=passed_count,
            failed_count=failed_count,
            leased_count=leased_count,
            queued_count=queued_count,
        )
        return run_status in {"succeeded", "failed"}

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
