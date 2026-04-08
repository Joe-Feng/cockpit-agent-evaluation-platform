from typing import Any

from pydantic import BaseModel


class RunnerClaimResponse(BaseModel):
    task_id: str
    attempt_id: str
    run_case_id: str
    adapter_type: str
    dispatch_payload: dict[str, Any]


class RunnerCompleteRequest(BaseModel):
    task_id: str
    attempt_id: str
    status: str
    raw_result: dict[str, Any]
