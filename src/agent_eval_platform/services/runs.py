from agent_eval_platform.repositories.run import RunRepository
from agent_eval_platform.schemas.run import RunCreate, RunRead


class RunService:
    def __init__(self, repository: RunRepository) -> None:
        self.repository = repository

    def create_run(self, payload: RunCreate) -> RunRead:
        self.repository.create_run(payload.run_id, payload.target_id, payload.env_id)

        task_count = 0
        for suite_id in payload.suite_ids:
            run_suite = self.repository.add_suite_instance(payload.run_id, suite_id)
            for case in self.repository.get_cases_for_suite(suite_id):
                run_case = self.repository.add_case_instance(run_suite.id, case.id)
                self.repository.add_execution_task(run_case.id, payload.execution_topology)
                task_count += 1

        self.repository.session.commit()
        return RunRead(run_id=payload.run_id, status="queued", task_count=task_count)
