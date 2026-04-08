from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from agent_eval_platform.api.dependencies import get_runtime, get_session
from agent_eval_platform.execution.runner_manager import RunnerManager
from agent_eval_platform.execution.runner_protocol import RunnerCompleteRequest
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


@router.get("/leases")
def claim_runner_task(
    runner_id: str = "remote-runner",
    session: Session = Depends(get_session),
) -> dict:
    task = RunnerManager(session).claim_next_task(runner_id=runner_id)
    return {} if task is None else task.model_dump()


@router.post("/completions")
def complete_runner_task(
    payload: RunnerCompleteRequest,
    runtime=Depends(get_runtime),
    session: Session = Depends(get_session),
) -> dict:
    RunnerManager(session, artifact_storage=runtime.artifact_storage).complete_task(payload)
    return {"status": "accepted", "task_id": payload.task_id}
