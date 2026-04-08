from fastapi.testclient import TestClient

from agent_eval_platform.api.app import create_app


def test_platform_smoke_flow() -> None:
    client = TestClient(create_app())

    assert client.get("/health").status_code == 200
    assert client.get("/api/v1/dashboard/targets/cockpit_agents").status_code == 200
    assert client.get("/api/v1/alerts/events").status_code == 200
