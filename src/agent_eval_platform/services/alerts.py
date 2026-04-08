from typing import Any

from agent_eval_platform.analysis.alerts import default_alert_rules, evaluate_alert_rule
from agent_eval_platform.read_models.builders import build_alert_event
from agent_eval_platform.repositories.run import RunRepository
from agent_eval_platform.services.reports import ReportService


class AlertService:
    def __init__(self, repository: RunRepository) -> None:
        self.repository = repository
        self.report_service = ReportService(repository)

    def list_rules(self) -> dict[str, list[dict[str, Any]]]:
        return {"items": default_alert_rules()}

    def list_events(self, *, target_id: str | None = None) -> dict[str, list[dict[str, Any]]]:
        runs = (
            self.repository.list_runs_for_target(target_id, limit=20)
            if target_id is not None
            else self.repository.list_recent_runs(limit=20)
        )
        items: list[dict[str, Any]] = []
        for run in runs:
            diff = self.report_service.build_pass_rate_diff(run.id)
            if diff is None:
                continue
            for rule in default_alert_rules():
                event = evaluate_alert_rule(rule=rule, diff=diff)
                if event["should_fire"]:
                    items.append(
                        build_alert_event(
                            run_id=run.id,
                            target_id=run.target_id,
                            event=event,
                        )
                    )
        return {"items": items}
