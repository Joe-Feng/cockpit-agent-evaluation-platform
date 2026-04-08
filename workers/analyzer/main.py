from agent_eval_platform.repositories.run import RunRepository
from agent_eval_platform.services.alerts import AlertService
from agent_eval_platform.services.dashboard import DashboardService


class AnalyzerWorker:
    def __init__(self, session) -> None:
        repository = RunRepository(session)
        self.dashboard_service = DashboardService(repository)
        self.alert_service = AlertService(repository)

    def rebuild_once(self) -> dict:
        regressions = self.dashboard_service.list_regression_signals()
        alerts = self.alert_service.list_events()
        return {
            "status": "ok",
            "recomputed": ["trend_series", "regression_signals", "target_overview"],
            "regression_count": len(regressions["items"]),
            "alert_count": len(alerts["items"]),
        }


def main() -> None:
    raise SystemExit("Use a process manager to launch the analyzer worker")
