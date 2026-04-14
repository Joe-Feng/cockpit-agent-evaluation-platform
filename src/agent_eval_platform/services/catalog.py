import json

from fastapi import HTTPException, status

from agent_eval_platform.repositories.catalog import CatalogRepository
from agent_eval_platform.schemas.catalog import (
    AssetStatus,
    CaseCreate,
    CaseRead,
    EnvironmentCreate,
    EnvironmentRead,
    SuiteCopyRequest,
    SuiteCreate,
    SuitePatch,
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
            adapter_types=self._parse_adapter_types(record.adapter_types),
            profile=json.loads(record.raw_profile_json),
        )

    def list_targets(self) -> list[TargetRead]:
        records = self.repository.list_targets()
        return [
            TargetRead(
                id=record.id,
                name=record.name,
                adapter_types=self._parse_adapter_types(record.adapter_types),
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

    def list_environments(self) -> list[EnvironmentRead]:
        records = self.repository.list_environments()
        return [
            EnvironmentRead(
                id=record.id,
                name=record.name,
                profile=json.loads(record.raw_profile_json),
            )
            for record in records
        ]

    def create_suite(self, payload: SuiteCreate) -> SuiteRead:
        record = self.repository.create_suite(payload, commit=False)
        self.repository.session.commit()
        self.repository.session.refresh(record)
        return self._build_suite_read(record)

    def list_suites(self) -> list[SuiteRead]:
        return [self._build_suite_read(record) for record in self.repository.list_suites()]

    def get_suite(self, suite_id: str) -> SuiteRead:
        record = self.repository.get_suite(suite_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"suite '{suite_id}' not found",
            )
        return self._build_suite_read(record)

    def update_suite(self, suite_id: str, payload: SuitePatch) -> SuiteRead:
        record = self.repository.get_suite(suite_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"suite '{suite_id}' not found",
            )
        if record.asset_status != AssetStatus.DRAFT.value or self.repository.suite_has_run_usage(
            suite_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"suite '{suite_id}' must be copied before editing",
            )

        self.repository.update_suite(record, definition=payload.definition)
        self.repository.session.commit()
        self.repository.session.refresh(record)
        return self._build_suite_read(record)

    def copy_suite(self, suite_id: str, payload: SuiteCopyRequest) -> SuiteRead:
        source = self.repository.get_suite(suite_id)
        if source is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"suite '{suite_id}' not found",
            )
        if self.repository.suite_exists(payload.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"suite '{payload.id}' already exists",
            )
        if source.asset_status == AssetStatus.SUPERSEDED.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"suite '{suite_id}' has already been superseded",
            )

        copied = self.repository.copy_suite(source, new_id=payload.id)
        self.repository.session.commit()
        self.repository.session.refresh(copied)
        return self._build_suite_read(copied)

    def create_case(self, payload: CaseCreate) -> CaseRead:
        if not self.repository.suite_exists(payload.suite_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"suite '{payload.suite_id}' not found",
            )
        record = self.repository.create_case(payload, commit=False)
        self.repository.session.commit()
        self.repository.session.refresh(record)
        return CaseRead(
            id=record.id,
            suite_id=record.suite_id,
            definition=json.loads(record.raw_definition_json),
        )

    @staticmethod
    def _parse_adapter_types(raw_value: str) -> list[str]:
        try:
            decoded = json.loads(raw_value)
        except json.JSONDecodeError:
            return [] if raw_value == "" else raw_value.split(",")

        if isinstance(decoded, list) and all(isinstance(item, str) for item in decoded):
            return decoded
        return [] if raw_value == "" else raw_value.split(",")

    def _build_suite_read(self, record) -> SuiteRead:
        definition = json.loads(record.raw_definition_json)
        name = record.id
        if isinstance(definition, dict):
            raw_name = definition.get("name")
            if isinstance(raw_name, str) and raw_name:
                name = raw_name
        return SuiteRead(
            id=record.id,
            mode=record.mode,
            name=name,
            definition=definition,
            asset_status=AssetStatus(record.asset_status),
            version_group_id=record.version_group_id,
            superseded_by_id=record.superseded_by_id,
            case_count=self.repository.count_cases_for_suite(record.id),
            updated_at=record.updated_at,
        )
