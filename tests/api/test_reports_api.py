from fastapi.testclient import TestClient
from sqlalchemy import select

from agent_eval_platform.api.app import create_app
from agent_eval_platform.models.run import ExecutionTaskRecord, RunCaseRecord, RunSuiteRecord


def test_get_run_report_returns_report_payload() -> None:
    client = TestClient(create_app())

    client.post(
        "/api/v1/catalog/targets",
        json={
            "id": "cockpit_agents",
            "name": "cockpit-agents",
            "adapter_types": ["http"],
            "profile": {"supported_modes": ["contract"]},
        },
    )
    client.post(
        "/api/v1/catalog/environments",
        json={"id": "local_mock", "name": "local-mock", "profile": {"execution_mode": "direct"}},
    )
    client.post(
        "/api/v1/catalog/suites",
        json={"id": "cockpit.contract.api", "mode": "contract", "definition": {"case_ids": ["health-001"]}},
    )
    client.post(
        "/api/v1/catalog/cases",
        json={
            "id": "health-001",
            "suite_id": "cockpit.contract.api",
            "definition": {"input": {"method": "GET", "path": "/health"}},
        },
    )
    create_response = client.post(
        "/api/v1/runs",
        json={
            "run_id": "run-001",
            "target_id": "cockpit_agents",
            "env_id": "local_mock",
            "suite_ids": ["cockpit.contract.api"],
            "execution_topology": "direct",
        },
    )

    assert create_response.status_code == 201

    runtime = client.app.state.runtime
    with runtime.session_factory() as session:
        task = session.scalar(select(ExecutionTaskRecord))
        assert task is not None
        task.status = "succeeded"
        session.commit()

    response = client.get("/api/v1/reports/runs/run-001")

    assert response.status_code == 200
    assert response.json() == {
        "run_id": "run-001",
        "status": "succeeded",
        "target_id": "cockpit_agents",
        "env_id": "local_mock",
        "suite_ids": ["cockpit.contract.api"],
        "suite_count": 1,
        "case_count": 1,
        "task_count": 1,
        "passed_count": 1,
        "regression_signals": [],
    }


def test_rerun_endpoint_clones_existing_run() -> None:
    client = TestClient(create_app())

    client.post(
        "/api/v1/catalog/targets",
        json={
            "id": "cockpit_agents",
            "name": "cockpit-agents",
            "adapter_types": ["http"],
            "profile": {"supported_modes": ["contract"]},
        },
    )
    client.post(
        "/api/v1/catalog/environments",
        json={"id": "local_mock", "name": "local-mock", "profile": {"execution_mode": "direct"}},
    )
    client.post(
        "/api/v1/catalog/suites",
        json={"id": "cockpit.contract.api", "mode": "contract", "definition": {"case_ids": ["health-001"]}},
    )
    client.post(
        "/api/v1/catalog/cases",
        json={
            "id": "health-001",
            "suite_id": "cockpit.contract.api",
            "definition": {"input": {"method": "GET", "path": "/health"}},
        },
    )

    create_response = client.post(
        "/api/v1/runs",
        json={
            "run_id": "run-001",
            "target_id": "cockpit_agents",
            "env_id": "local_mock",
            "suite_ids": ["cockpit.contract.api"],
            "execution_topology": "direct",
        },
    )

    assert create_response.status_code == 201

    client.post(
        "/api/v1/catalog/cases",
        json={
            "id": "health-002",
            "suite_id": "cockpit.contract.api",
            "definition": {"input": {"method": "GET", "path": "/health-2"}},
        },
    )

    rerun_response = client.post("/api/v1/runs/run-001/rerun")

    assert rerun_response.status_code == 201
    rerun_run_id = rerun_response.json()["run_id"]
    assert rerun_response.json()["task_count"] == 1

    runtime = client.app.state.runtime
    with runtime.session_factory() as session:
        source_task = session.scalar(
            select(ExecutionTaskRecord)
            .join(RunCaseRecord, ExecutionTaskRecord.run_case_id == RunCaseRecord.id)
            .join(RunSuiteRecord, RunCaseRecord.run_suite_id == RunSuiteRecord.id)
            .where(RunSuiteRecord.run_id == "run-001")
        )
        rerun_task = session.scalar(
            select(ExecutionTaskRecord)
            .join(RunCaseRecord, ExecutionTaskRecord.run_case_id == RunCaseRecord.id)
            .join(RunSuiteRecord, RunCaseRecord.run_suite_id == RunSuiteRecord.id)
            .where(RunSuiteRecord.run_id == rerun_run_id)
        )

    assert source_task is not None
    assert rerun_task is not None
    assert rerun_task.adapter_type == source_task.adapter_type
    assert rerun_task.dispatch_payload == source_task.dispatch_payload
    assert rerun_task.executor_type == source_task.executor_type


def test_rerun_endpoint_keeps_long_rerun_id_within_64_chars() -> None:
    client = TestClient(create_app())
    run_id = "run-" + ("r" * 60)

    client.post(
        "/api/v1/catalog/targets",
        json={
            "id": "cockpit_agents",
            "name": "cockpit-agents",
            "adapter_types": ["http"],
            "profile": {"supported_modes": ["contract"]},
        },
    )
    client.post(
        "/api/v1/catalog/environments",
        json={"id": "local_mock", "name": "local-mock", "profile": {"execution_mode": "direct"}},
    )
    client.post(
        "/api/v1/catalog/suites",
        json={"id": "cockpit.contract.api", "mode": "contract", "definition": {"case_ids": ["health-001"]}},
    )
    client.post(
        "/api/v1/catalog/cases",
        json={
            "id": "health-001",
            "suite_id": "cockpit.contract.api",
            "definition": {"input": {"method": "GET", "path": "/health"}},
        },
    )

    create_response = client.post(
        "/api/v1/runs",
        json={
            "run_id": run_id,
            "target_id": "cockpit_agents",
            "env_id": "local_mock",
            "suite_ids": ["cockpit.contract.api"],
            "execution_topology": "direct",
        },
    )

    assert create_response.status_code == 201

    rerun_response = client.post(f"/api/v1/runs/{run_id}/rerun")

    assert rerun_response.status_code == 201
    assert len(rerun_response.json()["run_id"]) <= 64
