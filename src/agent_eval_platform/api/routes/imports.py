from fastapi import APIRouter, Depends, status

from agent_eval_platform.api.dependencies import get_benchmark_package_import_service
from agent_eval_platform.schemas.imports import (
    BenchmarkPackageImportRequest,
    BenchmarkPackageImportSummary,
)
from agent_eval_platform.services.imports import BenchmarkPackageImportService

router = APIRouter(prefix="/api/v1/imports", tags=["imports"])


@router.post(
    "/benchmark-agent-package",
    response_model=BenchmarkPackageImportSummary,
    status_code=status.HTTP_201_CREATED,
)
def import_benchmark_agent_package(
    payload: BenchmarkPackageImportRequest,
    service: BenchmarkPackageImportService = Depends(get_benchmark_package_import_service),
) -> BenchmarkPackageImportSummary:
    return service.import_package(payload)
