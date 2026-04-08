import json

from agent_eval_platform.execution.runner_manager import RunnerManager
from agent_eval_platform.execution.runner_protocol import RunnerCompleteRequest
from agent_eval_platform.models.run import ExecutionAttemptRecord, ExecutionTaskRecord


def test_runner_can_claim_and_complete_a_task(session) -> None:
    session.add(
        ExecutionTaskRecord(
            id="task:runner-001",
            run_case_id="case-001",
            executor_type="runner",
            adapter_type="cli",
            dispatch_payload=json.dumps({"command": ["target-cli", "--json"]}),
            status="queued",
            priority=100,
        )
    )
    session.commit()

    manager = RunnerManager(session)
    task = manager.claim_next_task(runner_id="runner-a")

    assert task is not None
    assert task.task_id == "task:runner-001"
    assert task.adapter_type == "cli"
    assert task.dispatch_payload == {"command": ["target-cli", "--json"]}

    attempt = session.get(ExecutionAttemptRecord, task.attempt_id)
    assert attempt is not None
    assert attempt.status == "leased"

    completion = RunnerCompleteRequest(
        task_id=task.task_id,
        attempt_id=task.attempt_id,
        status="succeeded",
        raw_result={"status": "succeeded"},
    )
    manager.complete_task(completion)

    stored_task = manager.get_task(task.task_id)
    stored_attempt = manager.get_attempt(task.attempt_id)
    assert stored_task is not None
    assert stored_attempt is not None
    assert stored_task.status == "succeeded"
    assert stored_attempt.status == "succeeded"


def test_runner_claim_only_leases_runner_tasks(session) -> None:
    session.add_all(
        [
            ExecutionTaskRecord(
                id="task:direct-001",
                run_case_id="case-direct-001",
                executor_type="direct",
                adapter_type="http",
                dispatch_payload=json.dumps({"endpoint": "/invoke", "method": "POST", "body": {}}),
                status="queued",
                priority=200,
            ),
            ExecutionTaskRecord(
                id="task:runner-002",
                run_case_id="case-runner-002",
                executor_type="runner",
                adapter_type="python_sdk",
                dispatch_payload=json.dumps(
                    {
                        "module_path": "/tmp/target.py",
                        "callable_name": "run_case",
                        "payload": {"message": "hello"},
                    }
                ),
                status="queued",
                priority=100,
            ),
        ]
    )
    session.commit()

    task = RunnerManager(session).claim_next_task(runner_id="runner-b")

    assert task is not None
    assert task.task_id == "task:runner-002"
    assert session.get(ExecutionTaskRecord, "task:direct-001").status == "queued"
    assert session.get(ExecutionTaskRecord, "task:runner-002").status == "leased"
