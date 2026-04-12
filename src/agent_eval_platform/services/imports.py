from fastapi import HTTPException, status

from agent_eval_platform.repositories.catalog import CatalogRepository
from agent_eval_platform.schemas.catalog import CaseCreate, SuiteCreate
from agent_eval_platform.schemas.imports import (
    BenchmarkPackageImportRequest,
    BenchmarkPackageImportSummary,
)


class BenchmarkPackageImportService:
    def __init__(self, repository: CatalogRepository) -> None:
        self.repository = repository

    def import_package(
        self,
        payload: BenchmarkPackageImportRequest,
    ) -> BenchmarkPackageImportSummary:
        package = payload.package
        target_id = package.target_binding.target_id

        if not self.repository.target_exists(target_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"target '{target_id}' not found",
            )
        if not self.repository.environment_exists(payload.env_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"environment '{payload.env_id}' not found",
            )
        if self.repository.suite_exists(package.suite.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"suite '{package.suite.id}' already exists",
            )

        duplicate_cases = [
            case.id for case in package.cases if self.repository.case_exists(case.id)
        ]
        if duplicate_cases:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"cases already exist: {', '.join(duplicate_cases)}",
            )

        try:
            self.repository.create_suite(
                SuiteCreate(
                    id=package.suite.id,
                    mode=package.suite.mode,
                    definition={
                        "name": package.suite.name,
                        "description": package.suite.description,
                        "source_summary": package.suite.source_summary,
                        "case_ids": [case.id for case in package.cases],
                        "benchmark_export": {
                            "schema_version": package.schema_version,
                            "export_id": package.export_id,
                            "export_profile": package.export_profile,
                        },
                    },
                ),
                commit=False,
            )
            for case in package.cases:
                self.repository.create_case(
                    CaseCreate(
                        id=case.id,
                        suite_id=package.suite.id,
                        definition=case.definition,
                    ),
                    commit=False,
                )
            self.repository.session.commit()
        except Exception:
            self.repository.session.rollback()
            raise

        return BenchmarkPackageImportSummary(
            target_id=target_id,
            env_id=payload.env_id,
            suite_id=package.suite.id,
            case_count=len(package.cases),
        )
