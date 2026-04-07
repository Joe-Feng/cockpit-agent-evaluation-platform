from fastapi.testclient import TestClient

from agent_eval_platform.api.app import create_app


def test_create_run_enqueues_one_task_per_case() -> None:
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

    response = client.post(
        "/api/v1/runs",
        json={
            "run_id": "run-001",
            "target_id": "cockpit_agents",
            "env_id": "local_mock",
            "suite_ids": ["cockpit.contract.api"],
            "execution_topology": "direct",
        },
    )

    payload = response.json()
    assert response.status_code == 201
    assert payload["task_count"] == 1
    assert payload["status"] == "queued"
