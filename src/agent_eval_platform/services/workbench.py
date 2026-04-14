from agent_eval_platform.models.run import RunRecord
from agent_eval_platform.repositories.run import RunRepository
from agent_eval_platform.schemas.workbench import (
    QuickActionRead,
    RunListItemRead,
    RunListRead,
    SummaryCardRead,
    WorkbenchHomeRead,
)
from agent_eval_platform.services.alerts import AlertService
from agent_eval_platform.services.reports import ReportService


class WorkbenchService:
    def __init__(self, repository: RunRepository) -> None:
        self.repository = repository
        self.alert_service = AlertService(repository)
        self.report_service = ReportService(repository)

    def get_home(self, target_id: str) -> WorkbenchHomeRead:
        recent_runs = [
            self._build_run_list_item(run)
            for run in self.repository.list_runs_for_target(target_id, limit=5)
        ]
        risk_items = self.alert_service.list_events(target_id=target_id)["items"]
        summary_cards = [
            SummaryCardRead(
                id="recent-runs",
                label="最近运行",
                value=str(len(recent_runs)),
                detail="当前 target 最近 5 次运行",
                tone="neutral",
            ),
            SummaryCardRead(
                id="open-risks",
                label="打开风险",
                value=str(len(risk_items)),
                detail="当前 target 的回归/告警信号",
                tone="warning" if risk_items else "neutral",
            ),
            SummaryCardRead(
                id="latest-status",
                label="最新状态",
                value=recent_runs[0].status if recent_runs else "unknown",
                detail="最近一次运行的聚合状态",
                tone=self._status_tone(recent_runs[0].status) if recent_runs else "neutral",
            ),
        ]
        quick_actions = [
            QuickActionRead(label="导入 Benchmark", href="/imports/benchmark", tone="primary"),
            QuickActionRead(label="查看测试集", href="/suites", tone="neutral"),
            QuickActionRead(label="创建 Run", href="/runs/new", tone="neutral"),
            QuickActionRead(label="处理风险", href="/risks", tone="warning"),
        ]
        return WorkbenchHomeRead(
            target_id=target_id,
            summary_cards=summary_cards,
            quick_actions=quick_actions,
            recent_runs=recent_runs,
            risk_items=risk_items,
        )

    def list_runs(self) -> RunListRead:
        return RunListRead(
            items=[self._build_run_list_item(run) for run in self.repository.list_recent_runs(limit=20)]
        )

    def _build_run_list_item(self, run: RunRecord) -> RunListItemRead:
        report = self.report_service.build_run_report(run.id)
        return RunListItemRead(
            run_id=run.id,
            status=str(report["status"]),
            target_id=run.target_id,
            env_id=run.env_id,
            suite_ids=[str(suite_id) for suite_id in report["suite_ids"]],
            task_count=int(report["task_count"]),
            passed_count=int(report["passed_count"]),
            created_at=run.created_at,
        )

    @staticmethod
    def _status_tone(status: str) -> str:
        tones: dict[str, str] = {
            "queued": "neutral",
            "running": "warning",
            "succeeded": "positive",
            "failed": "danger",
            "unknown": "neutral",
        }
        return tones.get(status, "neutral")
