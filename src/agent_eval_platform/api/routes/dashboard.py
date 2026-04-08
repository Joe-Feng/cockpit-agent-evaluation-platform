from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from agent_eval_platform.api.dependencies import get_session
from agent_eval_platform.repositories.run import RunRepository
from agent_eval_platform.services.dashboard import DashboardService

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/targets/{target_id}")
def get_target_overview(target_id: str, session: Session = Depends(get_session)) -> dict:
    service = DashboardService(RunRepository(session))
    return service.get_target_overview(target_id)


@router.get("/runs/{run_id}")
def get_run_center(run_id: str, session: Session = Depends(get_session)) -> dict:
    service = DashboardService(RunRepository(session))
    return service.get_run_center(run_id)


@router.get("/cases/{case_id}")
def get_case_explorer(case_id: str, session: Session = Depends(get_session)) -> dict:
    service = DashboardService(RunRepository(session))
    return service.get_case_explorer(case_id)


@router.get("/trends/{scope_id}")
def get_trend_dashboard(scope_id: str, session: Session = Depends(get_session)) -> dict:
    service = DashboardService(RunRepository(session))
    return service.get_trend_dashboard(scope_id)


@router.get("/regressions")
def list_regression_signals(session: Session = Depends(get_session)) -> dict:
    service = DashboardService(RunRepository(session))
    return service.list_regression_signals()
