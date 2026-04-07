from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_eval_platform.models.catalog import CaseRecord, SuiteRecord
from agent_eval_platform.models.run import (
    ExecutionTaskRecord,
    RunCaseRecord,
    RunRecord,
    RunSuiteRecord,
)


class RunRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_run(self, run_id: str, target_id: str, env_id: str) -> RunRecord:
        record = RunRecord(id=run_id, target_id=target_id, env_id=env_id, status="queued")
        self.session.add(record)
        return record

    def get_cases_for_suite(self, suite_id: str) -> list[CaseRecord]:
        stmt = select(CaseRecord).where(CaseRecord.suite_id == suite_id).order_by(CaseRecord.id)
        return list(self.session.scalars(stmt))

    def suite_exists(self, suite_id: str) -> bool:
        stmt = select(SuiteRecord.id).where(SuiteRecord.id == suite_id)
        return self.session.scalar(stmt) is not None

    def add_suite_instance(self, run_id: str, suite_id: str) -> RunSuiteRecord:
        record = RunSuiteRecord(
            id=f"{run_id}:{suite_id}",
            run_id=run_id,
            suite_id=suite_id,
            status="queued",
        )
        self.session.add(record)
        return record

    def add_case_instance(self, run_suite_id: str, case_id: str) -> RunCaseRecord:
        record = RunCaseRecord(
            id=f"{run_suite_id}:{case_id}",
            run_suite_id=run_suite_id,
            case_id=case_id,
            status="queued",
        )
        self.session.add(record)
        return record

    def add_execution_task(self, run_case_id: str, executor_type: str) -> ExecutionTaskRecord:
        record = ExecutionTaskRecord(
            id=f"task:{run_case_id}",
            run_case_id=run_case_id,
            executor_type=executor_type,
            status="queued",
            priority=100,
        )
        self.session.add(record)
        return record
