import json

from agent_eval_platform.repositories.catalog import CatalogRepository
from agent_eval_platform.schemas.catalog import (
    CaseCreate,
    CaseRead,
    EnvironmentCreate,
    EnvironmentRead,
    SuiteCreate,
    SuiteRead,
    TargetCreate,
    TargetRead,
)


class CatalogService:
    def __init__(self, repository: CatalogRepository) -> None:
        self.repository = repository

    def create_target(self, payload: TargetCreate) -> TargetRead:
        record = self.repository.create_target(payload)
        return TargetRead(
            id=record.id,
            name=record.name,
            adapter_types=record.adapter_types.split(","),
            profile=json.loads(record.raw_profile_json),
        )

    def list_targets(self) -> list[TargetRead]:
        records = self.repository.list_targets()
        return [
            TargetRead(
                id=record.id,
                name=record.name,
                adapter_types=record.adapter_types.split(","),
                profile=json.loads(record.raw_profile_json),
            )
            for record in records
        ]

    def create_environment(self, payload: EnvironmentCreate) -> EnvironmentRead:
        record = self.repository.create_environment(payload)
        return EnvironmentRead(
            id=record.id,
            name=record.name,
            profile=json.loads(record.raw_profile_json),
        )

    def create_suite(self, payload: SuiteCreate) -> SuiteRead:
        record = self.repository.create_suite(payload)
        return SuiteRead(
            id=record.id,
            mode=record.mode,
            definition=json.loads(record.raw_definition_json),
        )

    def create_case(self, payload: CaseCreate) -> CaseRead:
        record = self.repository.create_case(payload)
        return CaseRead(
            id=record.id,
            suite_id=record.suite_id,
            definition=json.loads(record.raw_definition_json),
        )
