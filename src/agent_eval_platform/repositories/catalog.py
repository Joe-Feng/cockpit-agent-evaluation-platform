import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_eval_platform.models.catalog import (
    CaseRecord,
    EnvironmentRecord,
    SuiteRecord,
    TargetRecord,
)
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

    def create_suite(self, payload: SuiteCreate, *, commit: bool = True) -> SuiteRecord:
        record = SuiteRecord(
            id=payload.id,
            mode=payload.mode,
            raw_definition_json=json.dumps(payload.definition),
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

    def target_exists(self, target_id: str) -> bool:
        stmt = select(TargetRecord.id).where(TargetRecord.id == target_id)
        return self.session.scalar(stmt) is not None

    def environment_exists(self, env_id: str) -> bool:
        stmt = select(EnvironmentRecord.id).where(EnvironmentRecord.id == env_id)
        return self.session.scalar(stmt) is not None

    def case_exists(self, case_id: str) -> bool:
        stmt = select(CaseRecord.id).where(CaseRecord.id == case_id)
        return self.session.scalar(stmt) is not None
