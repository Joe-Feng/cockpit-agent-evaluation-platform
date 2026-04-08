from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from agent_eval_platform.api.dependencies import get_session
from agent_eval_platform.repositories.run import RunRepository
from agent_eval_platform.schemas.run import RunCreate, RunRead
from agent_eval_platform.services.runs import RunService

router = APIRouter(prefix="/api/v1/runs", tags=["runs"])


@router.post("", response_model=RunRead, status_code=status.HTTP_201_CREATED)
def create_run(payload: RunCreate, session: Session = Depends(get_session)) -> RunRead:
    service = RunService(RunRepository(session))
    return service.create_run(payload)


@router.post("/{run_id}/rerun", response_model=RunRead, status_code=status.HTTP_201_CREATED)
def rerun_run(run_id: str, session: Session = Depends(get_session)) -> RunRead:
    service = RunService(RunRepository(session))
    return service.create_rerun(run_id)
