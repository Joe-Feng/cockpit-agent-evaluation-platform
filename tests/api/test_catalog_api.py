from fastapi.testclient import TestClient

from agent_eval_platform.api.app import create_app


def test_create_and_list_targets() -> None:
    client = TestClient(create_app())

    create_response = client.post(
        "/api/v1/catalog/targets",
        json={
            "id": "cockpit_agents",
            "name": "cockpit-agents",
            "adapter_types": ["http", "native_test"],
            "profile": {"supported_modes": ["contract", "unit_native"]},
        },
    )
    list_response = client.get("/api/v1/catalog/targets")

    assert create_response.status_code == 201
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == "cockpit_agents"
