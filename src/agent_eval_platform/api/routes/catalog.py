from fastapi import APIRouter, Depends, status

from agent_eval_platform.api.dependencies import get_catalog_service
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
from agent_eval_platform.services.catalog import CatalogService

router = APIRouter(prefix="/api/v1/catalog", tags=["catalog"])


@router.post("/targets", response_model=TargetRead, status_code=status.HTTP_201_CREATED)
def create_target(
    payload: TargetCreate,
    service: CatalogService = Depends(get_catalog_service),
) -> TargetRead:
    return service.create_target(payload)


@router.get("/targets", response_model=list[TargetRead])
def list_targets(
    service: CatalogService = Depends(get_catalog_service),
) -> list[TargetRead]:
    return service.list_targets()


@router.post(
    "/environments",
    response_model=EnvironmentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_environment(
    payload: EnvironmentCreate,
    service: CatalogService = Depends(get_catalog_service),
) -> EnvironmentRead:
    return service.create_environment(payload)


@router.post("/suites", response_model=SuiteRead, status_code=status.HTTP_201_CREATED)
def create_suite(
    payload: SuiteCreate,
    service: CatalogService = Depends(get_catalog_service),
) -> SuiteRead:
    return service.create_suite(payload)


@router.post("/cases", response_model=CaseRead, status_code=status.HTTP_201_CREATED)
def create_case(
    payload: CaseCreate,
    service: CatalogService = Depends(get_catalog_service),
) -> CaseRead:
    return service.create_case(payload)
