from pydantic import BaseModel


class RunCreate(BaseModel):
    run_id: str
    target_id: str
    env_id: str
    suite_ids: list[str]
    execution_topology: str


class RunRead(BaseModel):
    run_id: str
    status: str
    task_count: int
