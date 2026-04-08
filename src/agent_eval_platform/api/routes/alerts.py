from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from agent_eval_platform.api.dependencies import get_session
from agent_eval_platform.repositories.run import RunRepository
from agent_eval_platform.services.alerts import AlertService

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


@router.get("/rules")
def list_alert_rules(session: Session = Depends(get_session)) -> dict:
    service = AlertService(RunRepository(session))
    return service.list_rules()


@router.get("/events")
def list_alert_events(session: Session = Depends(get_session)) -> dict:
    service = AlertService(RunRepository(session))
    return service.list_events()
