import json

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from agent_eval_platform.models.catalog import CaseRecord, SuiteRecord, TargetRecord
from agent_eval_platform.models.run import (
    ExecutionTaskRecord,
    RunCaseRecord,
    RunRecord,
    RunSuiteRecord,
)
from agent_eval_platform.orchestration_ids import build_orchestration_id


class RunRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_run(self, run_id: str, target_id: str, env_id: str) -> RunRecord:
        record = RunRecord(id=run_id, target_id=target_id, env_id=env_id, status="queued")
        self.session.add(record)
        return record

    def get_run(self, run_id: str) -> RunRecord | None:
        stmt = select(RunRecord).where(RunRecord.id == run_id)
        return self.session.scalar(stmt)

    def run_exists(self, run_id: str) -> bool:
        stmt = select(RunRecord.id).where(RunRecord.id == run_id)
        return self.session.scalar(stmt) is not None

    def get_cases_for_suite(self, suite_id: str) -> list[CaseRecord]:
        stmt = select(CaseRecord).where(CaseRecord.suite_id == suite_id).order_by(CaseRecord.id)
        return list(self.session.scalars(stmt))

    def get_target_profile(self, target_id: str) -> dict:
        stmt = select(TargetRecord).where(TargetRecord.id == target_id)
        record = self.session.scalar(stmt)
        if record is None:
            return {}
        return json.loads(record.raw_profile_json)

    def get_target_adapter_types(self, target_id: str) -> list[str]:
        stmt = select(TargetRecord.adapter_types).where(TargetRecord.id == target_id)
        raw_value = self.session.scalar(stmt)
        if raw_value is None:
            return []
        try:
            decoded = json.loads(raw_value)
        except json.JSONDecodeError:
            return []
        return decoded if isinstance(decoded, list) else []

    def suite_exists(self, suite_id: str) -> bool:
        stmt = select(SuiteRecord.id).where(SuiteRecord.id == suite_id)
        return self.session.scalar(stmt) is not None

    def add_suite_instance(self, run_id: str, suite_id: str) -> RunSuiteRecord:
        record = RunSuiteRecord(
            id=build_orchestration_id("rs", run_id, suite_id),
            run_id=run_id,
            suite_id=suite_id,
            status="queued",
        )
        self.session.add(record)
        return record

    def list_suite_ids_for_run(self, run_id: str) -> list[str]:
        stmt = select(RunSuiteRecord.suite_id).where(RunSuiteRecord.run_id == run_id).order_by(
            RunSuiteRecord.id
        )
        return list(self.session.scalars(stmt))

    def list_run_suites(self, run_id: str) -> list[RunSuiteRecord]:
        stmt = select(RunSuiteRecord).where(RunSuiteRecord.run_id == run_id).order_by(RunSuiteRecord.id)
        return list(self.session.scalars(stmt))

    def list_run_cases_for_run(self, run_id: str) -> list[RunCaseRecord]:
        stmt = (
            select(RunCaseRecord)
            .join(RunSuiteRecord, RunCaseRecord.run_suite_id == RunSuiteRecord.id)
            .where(RunSuiteRecord.run_id == run_id)
            .order_by(RunCaseRecord.run_suite_id, RunCaseRecord.id)
        )
        return list(self.session.scalars(stmt))

    def count_cases_for_run(self, run_id: str) -> int:
        stmt = (
            select(func.count())
            .select_from(RunCaseRecord)
            .join(RunSuiteRecord, RunCaseRecord.run_suite_id == RunSuiteRecord.id)
            .where(RunSuiteRecord.run_id == run_id)
        )
        return int(self.session.scalar(stmt) or 0)

    def count_cases_for_run_with_status(self, run_id: str, status: str) -> int:
        stmt = (
            select(func.count())
            .select_from(RunCaseRecord)
            .join(RunSuiteRecord, RunCaseRecord.run_suite_id == RunSuiteRecord.id)
            .where(RunSuiteRecord.run_id == run_id, RunCaseRecord.status == status)
        )
        return int(self.session.scalar(stmt) or 0)

    def count_tasks_for_run(self, run_id: str) -> int:
        stmt = (
            select(func.count())
            .select_from(ExecutionTaskRecord)
            .join(RunCaseRecord, ExecutionTaskRecord.run_case_id == RunCaseRecord.id)
            .join(RunSuiteRecord, RunCaseRecord.run_suite_id == RunSuiteRecord.id)
            .where(RunSuiteRecord.run_id == run_id)
        )
        return int(self.session.scalar(stmt) or 0)

    def count_tasks_for_run_with_status(self, run_id: str, status: str) -> int:
        stmt = (
            select(func.count())
            .select_from(ExecutionTaskRecord)
            .join(RunCaseRecord, ExecutionTaskRecord.run_case_id == RunCaseRecord.id)
            .join(RunSuiteRecord, RunCaseRecord.run_suite_id == RunSuiteRecord.id)
            .where(
                RunSuiteRecord.run_id == run_id,
                ExecutionTaskRecord.status == status,
            )
        )
        return int(self.session.scalar(stmt) or 0)

    def list_execution_tasks_for_run(self, run_id: str) -> list[ExecutionTaskRecord]:
        stmt = (
            select(ExecutionTaskRecord)
            .join(RunCaseRecord, ExecutionTaskRecord.run_case_id == RunCaseRecord.id)
            .join(RunSuiteRecord, RunCaseRecord.run_suite_id == RunSuiteRecord.id)
            .where(RunSuiteRecord.run_id == run_id)
            .order_by(ExecutionTaskRecord.run_case_id, ExecutionTaskRecord.id)
        )
        return list(self.session.scalars(stmt))

    def get_execution_topology_for_run(self, run_id: str) -> str | None:
        stmt = (
            select(ExecutionTaskRecord.executor_type)
            .join(RunCaseRecord, ExecutionTaskRecord.run_case_id == RunCaseRecord.id)
            .join(RunSuiteRecord, RunCaseRecord.run_suite_id == RunSuiteRecord.id)
            .where(RunSuiteRecord.run_id == run_id)
            .order_by(ExecutionTaskRecord.id)
            .limit(1)
        )
        return self.session.scalar(stmt)

    def add_case_instance(self, run_suite_id: str, case_id: str) -> RunCaseRecord:
        record = RunCaseRecord(
            id=build_orchestration_id("rc", run_suite_id, case_id),
            run_suite_id=run_suite_id,
            case_id=case_id,
            status="queued",
        )
        self.session.add(record)
        return record

    def add_execution_task(
        self,
        run_case_id: str,
        executor_type: str,
        adapter_type: str,
        dispatch_payload: str,
        priority: int = 100,
    ) -> ExecutionTaskRecord:
        record = ExecutionTaskRecord(
            id=build_orchestration_id("task", run_case_id, executor_type),
            run_case_id=run_case_id,
            executor_type=executor_type,
            adapter_type=adapter_type,
            dispatch_payload=dispatch_payload,
            status="queued",
            priority=priority,
        )
        self.session.add(record)
        return record
