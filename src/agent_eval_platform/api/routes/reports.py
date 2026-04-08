from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from agent_eval_platform.api.dependencies import get_session
from agent_eval_platform.repositories.run import RunRepository
from agent_eval_platform.services.reports import ReportService

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("/runs/{run_id}")
def get_run_report(run_id: str, session: Session = Depends(get_session)) -> dict[str, object]:
    service = ReportService(RunRepository(session))
    return service.build_run_report(run_id)
