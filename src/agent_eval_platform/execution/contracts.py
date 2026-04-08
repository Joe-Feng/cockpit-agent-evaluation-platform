from typing import Any

from pydantic import BaseModel


class LeasedTask(BaseModel):
    task_id: str
    attempt_id: str
    run_case_id: str
    executor_type: str
    adapter_type: str
    dispatch_payload: dict[str, Any]
