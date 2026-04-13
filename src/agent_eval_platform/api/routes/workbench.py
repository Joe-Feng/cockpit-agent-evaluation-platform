from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from agent_eval_platform.api.dependencies import get_session
from agent_eval_platform.repositories.run import RunRepository
from agent_eval_platform.schemas.workbench import RunListRead, WorkbenchHomeRead
from agent_eval_platform.services.workbench import WorkbenchService

router = APIRouter(prefix="/api/v1/workbench", tags=["workbench"])


@router.get("/home", response_model=WorkbenchHomeRead)
def get_workbench_home(
    target_id: str,
    session: Session = Depends(get_session),
) -> WorkbenchHomeRead:
    service = WorkbenchService(RunRepository(session))
    return service.get_home(target_id)


@router.get("/runs", response_model=RunListRead)
def list_workbench_runs(session: Session = Depends(get_session)) -> RunListRead:
    service = WorkbenchService(RunRepository(session))
    return service.list_runs()
