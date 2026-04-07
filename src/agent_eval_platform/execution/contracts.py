from pydantic import BaseModel


class LeasedTask(BaseModel):
    task_id: str
    run_case_id: str
    executor_type: str
