import json

from fastapi.testclient import TestClient
from sqlalchemy import select

from agent_eval_platform.api.app import create_app
from agent_eval_platform.models.run import ExecutionTaskRecord, RunCaseRecord, RunSuiteRecord


def test_create_run_enqueues_one_task_per_case() -> None:
    client = TestClient(create_app())

    client.post(
        "/api/v1/catalog/targets",
        json={
            "id": "cockpit_agents",
            "name": "cockpit-agents",
            "adapter_types": ["http"],
            "profile": {
                "supported_modes": ["contract"],
                "invoke_contract": {
                    "endpoint_template": "/invoke{path}",
                    "headers": {"X-Eval-Mode": "contract"},
                },
            },
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
            "definition": {
                "input": {
                    "method": "POST",
                    "path": "/health",
                    "body": {"message": "ping"},
                }
            },
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

    runtime = client.app.state.runtime
    with runtime.session_factory() as session:
        task = session.scalar(select(ExecutionTaskRecord))

    assert task is not None
    assert task.adapter_type == "http"
    assert json.loads(task.dispatch_payload) == {
        "endpoint": "/invoke/health",
        "method": "POST",
        "body": {"message": "ping"},
        "headers": {"X-Eval-Mode": "contract"},
    }


def test_create_run_persists_native_test_dispatch_payload() -> None:
    client = TestClient(create_app())

    client.post(
        "/api/v1/catalog/targets",
        json={
            "id": "native_target",
            "name": "native-target",
            "adapter_types": ["native_test"],
            "profile": {
                "supported_modes": ["unit_native"],
                "native_test_contract": {
                    "command": "python -m pytest",
                    "default_args": ["-q"],
                    "suite_mapping": {
                        "cockpit.native.smoke": {
                            "args": ["tests/native/test_health.py", "-k", "smoke"]
                        }
                    },
                },
            },
        },
    )
    client.post(
        "/api/v1/catalog/environments",
        json={"id": "local_mock", "name": "local-mock", "profile": {"execution_mode": "direct"}},
    )
    client.post(
        "/api/v1/catalog/suites",
        json={
            "id": "cockpit.native.smoke",
            "mode": "unit_native",
            "definition": {"case_ids": ["native-001"]},
        },
    )
    client.post(
        "/api/v1/catalog/cases",
        json={
            "id": "native-001",
            "suite_id": "cockpit.native.smoke",
            "definition": {"input": {}},
        },
    )

    response = client.post(
        "/api/v1/runs",
        json={
            "run_id": "run-native-001",
            "target_id": "native_target",
            "env_id": "local_mock",
            "suite_ids": ["cockpit.native.smoke"],
            "execution_topology": "direct",
        },
    )

    assert response.status_code == 201

    runtime = client.app.state.runtime
    with runtime.session_factory() as session:
        task = session.scalar(select(ExecutionTaskRecord))

    assert task is not None
    assert task.adapter_type == "native_test"
    assert json.loads(task.dispatch_payload) == {
        "command": [
            "python",
            "-m",
            "pytest",
            "-q",
            "tests/native/test_health.py",
            "-k",
            "smoke",
        ]
    }


def test_create_run_rejects_missing_suite() -> None:
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

    response = client.post(
        "/api/v1/runs",
        json={
            "run_id": "r-missing",
            "target_id": "cockpit_agents",
            "env_id": "local_mock",
            "suite_ids": ["missing-suite"],
            "execution_topology": "direct",
        },
    )

    payload = response.json()
    assert response.status_code == 404
    assert "missing-suite" in payload["detail"]


def test_create_run_with_long_ids_keeps_orchestration_ids_within_64_chars() -> None:
    client = TestClient(create_app())
    run_id = "run-" + ("r" * 40)
    suite_id = "suite-" + ("s" * 40)
    case_id = "case-" + ("c" * 40)

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
        json={"id": suite_id, "mode": "contract", "definition": {"case_ids": [case_id]}},
    )
    client.post(
        "/api/v1/catalog/cases",
        json={
            "id": case_id,
            "suite_id": suite_id,
            "definition": {"input": {"method": "GET", "path": "/health"}},
        },
    )

    response = client.post(
        "/api/v1/runs",
        json={
            "run_id": run_id,
            "target_id": "cockpit_agents",
            "env_id": "local_mock",
            "suite_ids": [suite_id],
            "execution_topology": "direct",
        },
    )

    assert response.status_code == 201

    runtime = client.app.state.runtime
    with runtime.session_factory() as session:
        run_suite_ids = list(session.scalars(select(RunSuiteRecord.id)))
        run_case_ids = list(session.scalars(select(RunCaseRecord.id)))
        task_ids = list(session.scalars(select(ExecutionTaskRecord.id)))

    assert len(run_suite_ids) == 1
    assert len(run_case_ids) == 1
    assert len(task_ids) == 1
    assert len(run_suite_ids[0]) <= 64
    assert len(run_case_ids[0]) <= 64
    assert len(task_ids[0]) <= 64
