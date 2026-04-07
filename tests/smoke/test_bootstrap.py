from pathlib import Path
from runpy import run_path

from fastapi.testclient import TestClient

from agent_eval_platform.api.app import create_app


def test_health_endpoint_returns_ok() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_runtime_entrypoint_exposes_health_endpoint() -> None:
    module = run_path(str(Path("apps/api/main.py")))
    client = TestClient(module["app"])

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
