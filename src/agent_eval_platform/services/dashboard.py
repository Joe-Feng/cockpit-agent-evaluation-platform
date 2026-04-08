from typing import Any

from agent_eval_platform.analysis.trends import build_trend_point
from agent_eval_platform.read_models.builders import (
    build_case_explorer,
    build_case_history_item,
    build_open_alert_item,
    build_regression_center,
    build_regression_item,
    build_run_center,
    build_run_summary,
    build_target_overview,
    build_trend_dashboard,
)
from agent_eval_platform.repositories.run import RunRepository
from agent_eval_platform.services.alerts import AlertService
from agent_eval_platform.services.reports import ReportService


class DashboardService:
    def __init__(self, repository: RunRepository) -> None:
        self.repository = repository
        self.report_service = ReportService(repository)
        self.alert_service = AlertService(repository)

    def get_target_overview(self, target_id: str) -> dict[str, Any]:
        reports = [
            self.report_service.build_run_report(run.id)
            for run in self.repository.list_runs_for_target(target_id, limit=5)
        ]
        return build_target_overview(
            target_id=target_id,
            latest_runs=[build_run_summary(report=report) for report in reports],
            open_alerts=[
                build_open_alert_item(event=event)
                for event in self.alert_service.list_events(target_id=target_id)["items"]
            ],
        )

    def get_run_center(self, run_id: str) -> dict[str, Any]:
        report = self.report_service.build_run_report(run_id)
        return build_run_center(
            report=report,
            execution_topology=self.repository.get_execution_topology_for_run(run_id),
        )

    def get_case_explorer(self, case_id: str) -> dict[str, Any]:
        history = []
        for run in self.repository.list_runs_for_case(case_id, limit=20):
            report = self.report_service.build_run_report(run.id)
            history.append(
                build_case_history_item(
                    run_id=run.id,
                    target_id=run.target_id,
                    env_id=run.env_id,
                    status=str(report["status"]),
                    created_at=run.created_at,
                )
            )
        return build_case_explorer(case_id=case_id, history=history)

    def get_trend_dashboard(self, scope_id: str) -> dict[str, Any]:
        series: list[dict[str, Any]] = []
        for run in self.repository.list_runs_for_suite(scope_id):
            report = self.report_service.build_run_report(run.id)
            task_count = int(report["task_count"])
            if task_count == 0 or str(report["status"]) not in {"succeeded", "failed"}:
                continue
            series.append(
                build_trend_point(
                    scope_type="suite",
                    scope_id=scope_id,
                    metric_id="pass_rate",
                    dimension_key=f"env={report['env_id']}",
                    value=round(int(report["passed_count"]) / task_count, 4),
                    captured_at=run.created_at,
                )
            )
        return build_trend_dashboard(scope_id=scope_id, series=series)

    def list_regression_signals(self) -> dict[str, Any]:
        items: list[dict[str, Any]] = []
        for run in self.repository.list_recent_runs(limit=20):
            report = self.report_service.build_run_report(run.id)
            for signal in report["regression_signals"]:
                items.append(
                    build_regression_item(
                        run_id=run.id,
                        target_id=run.target_id,
                        env_id=run.env_id,
                        signal=signal,
                        created_at=run.created_at,
                    )
                )
        return build_regression_center(items=items)
