from fastapi.testclient import TestClient

from agent_eval_platform.api.app import create_app


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

    response = client.get("/api/v1/reports/runs/run-001")

    assert response.status_code == 200
    assert response.json()["run_id"] == "run-001"


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

    rerun_response = client.post("/api/v1/runs/run-001/rerun")

    assert rerun_response.status_code == 201
    assert rerun_response.json()["run_id"] == "run-001-rerun"
    assert rerun_response.json()["task_count"] == 1
