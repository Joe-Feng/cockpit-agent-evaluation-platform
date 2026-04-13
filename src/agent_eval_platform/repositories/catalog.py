import json

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from agent_eval_platform.models.catalog import (
    CaseRecord,
    EnvironmentRecord,
    SuiteRecord,
    TargetRecord,
)
from agent_eval_platform.models.run import RunSuiteRecord
from agent_eval_platform.schemas.catalog import (
    CaseCreate,
    EnvironmentCreate,
    SuiteCreate,
    TargetCreate,
)


class CatalogRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_target(self, payload: TargetCreate) -> TargetRecord:
        record = TargetRecord(
            id=payload.id,
            name=payload.name,
            adapter_types=json.dumps(payload.adapter_types),
            raw_profile_json=json.dumps(payload.profile),
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def list_targets(self) -> list[TargetRecord]:
        return list(self.session.scalars(select(TargetRecord).order_by(TargetRecord.id)))

    def create_environment(self, payload: EnvironmentCreate) -> EnvironmentRecord:
        record = EnvironmentRecord(
            id=payload.id,
            name=payload.name,
            raw_profile_json=json.dumps(payload.profile),
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def list_environments(self) -> list[EnvironmentRecord]:
        return list(
            self.session.scalars(select(EnvironmentRecord).order_by(EnvironmentRecord.id))
        )

    def create_suite(self, payload: SuiteCreate, *, commit: bool = True) -> SuiteRecord:
        record = SuiteRecord(
            id=payload.id,
            mode=payload.mode,
            raw_definition_json=json.dumps(payload.definition),
            asset_status="draft",
            version_group_id=payload.id,
            superseded_by_id=None,
        )
        self.session.add(record)
        if commit:
            self.session.commit()
            self.session.refresh(record)
        else:
            self.session.flush()
        return record

    def create_case(self, payload: CaseCreate, *, commit: bool = True) -> CaseRecord:
        record = CaseRecord(
            id=payload.id,
            suite_id=payload.suite_id,
            raw_definition_json=json.dumps(payload.definition),
            asset_status="draft",
            version_group_id=payload.id,
            superseded_by_id=None,
        )
        self.session.add(record)
        if commit:
            self.session.commit()
            self.session.refresh(record)
        else:
            self.session.flush()
        return record

    def suite_exists(self, suite_id: str) -> bool:
        stmt = select(SuiteRecord.id).where(SuiteRecord.id == suite_id)
        return self.session.scalar(stmt) is not None

    def list_suites(self) -> list[SuiteRecord]:
        return list(self.session.scalars(select(SuiteRecord).order_by(SuiteRecord.id)))

    def get_suite(self, suite_id: str) -> SuiteRecord | None:
        return self.session.get(SuiteRecord, suite_id)

    def count_cases_for_suite(self, suite_id: str) -> int:
        stmt = select(func.count()).select_from(CaseRecord).where(CaseRecord.suite_id == suite_id)
        return int(self.session.scalar(stmt) or 0)

    def suite_has_run_usage(self, suite_id: str) -> bool:
        stmt = select(RunSuiteRecord.id).where(RunSuiteRecord.suite_id == suite_id).limit(1)
        return self.session.scalar(stmt) is not None

    def update_suite(self, record: SuiteRecord, *, definition: dict) -> SuiteRecord:
        record.raw_definition_json = json.dumps(definition)
        self.session.flush()
        return record

    def copy_suite(self, source: SuiteRecord, *, new_id: str) -> SuiteRecord:
        copied = SuiteRecord(
            id=new_id,
            mode=source.mode,
            raw_definition_json=source.raw_definition_json,
            asset_status="draft",
            version_group_id=source.version_group_id or source.id,
            superseded_by_id=None,
        )
        self.session.add(copied)
        source.asset_status = "superseded"
        source.superseded_by_id = copied.id
        self.session.flush()
        return copied

    def target_exists(self, target_id: str) -> bool:
        stmt = select(TargetRecord.id).where(TargetRecord.id == target_id)
        return self.session.scalar(stmt) is not None

    def environment_exists(self, env_id: str) -> bool:
        stmt = select(EnvironmentRecord.id).where(EnvironmentRecord.id == env_id)
        return self.session.scalar(stmt) is not None

    def case_exists(self, case_id: str) -> bool:
        stmt = select(CaseRecord.id).where(CaseRecord.id == case_id)
        return self.session.scalar(stmt) is not None
