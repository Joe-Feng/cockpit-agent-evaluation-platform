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


def test_create_app_instances_have_isolated_runtime_state() -> None:
    first_client = TestClient(create_app())
    second_client = TestClient(create_app())

    first_create = first_client.post(
        "/api/v1/catalog/targets",
        json={
            "id": "shared_target",
            "name": "shared-target",
            "adapter_types": ["http"],
            "profile": {"supported_modes": ["contract"]},
        },
    )
    second_list = second_client.get("/api/v1/catalog/targets")
    second_create = second_client.post(
        "/api/v1/catalog/targets",
        json={
            "id": "shared_target",
            "name": "shared-target",
            "adapter_types": ["http"],
            "profile": {"supported_modes": ["contract"]},
        },
    )

    assert first_create.status_code == 201
    assert second_list.status_code == 200
    assert second_list.json() == []
    assert second_create.status_code == 201


def test_adapter_types_round_trip_is_lossless() -> None:
    client = TestClient(create_app())

    empty_adapter_response = client.post(
        "/api/v1/catalog/targets",
        json={
            "id": "target_empty",
            "name": "target-empty",
            "adapter_types": [],
            "profile": {},
        },
    )
    comma_adapter_response = client.post(
        "/api/v1/catalog/targets",
        json={
            "id": "target_comma",
            "name": "target-comma",
            "adapter_types": ["http,v2", "native_test"],
            "profile": {},
        },
    )
    list_response = client.get("/api/v1/catalog/targets")
    payload_by_id = {item["id"]: item for item in list_response.json()}

    assert empty_adapter_response.status_code == 201
    assert comma_adapter_response.status_code == 201
    assert payload_by_id["target_empty"]["adapter_types"] == []
    assert payload_by_id["target_comma"]["adapter_types"] == ["http,v2", "native_test"]


def test_create_case_rejects_orphan_suite() -> None:
    client = TestClient(create_app())

    create_case_response = client.post(
        "/api/v1/catalog/cases",
        json={
            "id": "orphan-case-001",
            "suite_id": "missing-suite",
            "definition": {"input": {"path": "/health"}},
        },
    )

    assert create_case_response.status_code == 404


def test_list_environments_and_suites_exposes_workbench_metadata() -> None:
    client = TestClient(create_app())
    client.post(
        "/api/v1/catalog/environments",
        json={
            "id": "local_mock",
            "name": "local-mock",
            "profile": {"execution_mode": "direct"},
        },
    )
    client.post(
        "/api/v1/catalog/suites",
        json={
            "id": "suite-a",
            "mode": "contract",
            "definition": {"name": "核心巡检", "case_ids": []},
        },
    )

    env_response = client.get("/api/v1/catalog/environments")
    suite_response = client.get("/api/v1/catalog/suites")

    assert env_response.status_code == 200
    assert env_response.json()[0]["id"] == "local_mock"
    assert suite_response.status_code == 200
    assert suite_response.json()[0]["asset_status"] == "draft"
    assert suite_response.json()[0]["name"] == "核心巡检"


def test_used_suite_must_be_copied_before_editing() -> None:
    client = TestClient(create_app())
    _seed_target_env_suite_case(client, suite_id="suite-a", case_id="case-a")
    client.post(
        "/api/v1/runs",
        json={
            "run_id": "run-001",
            "target_id": "cockpit_agents",
            "env_id": "local_mock",
            "suite_ids": ["suite-a"],
            "execution_topology": "direct",
        },
    )

    patch_response = client.patch(
        "/api/v1/catalog/suites/suite-a",
        json={"definition": {"name": "不能原地改"}},
    )
    copy_response = client.post(
        "/api/v1/catalog/suites/suite-a/copy",
        json={"id": "suite-a-v2"},
    )

    assert patch_response.status_code == 409
    assert copy_response.status_code == 201
    assert copy_response.json()["asset_status"] == "draft"
    assert client.get("/api/v1/catalog/suites/suite-a").json()["asset_status"] == "superseded"


def _seed_target_env_suite_case(client: TestClient, *, suite_id: str, case_id: str) -> None:
    client.post(
        "/api/v1/catalog/targets",
        json={
            "id": "cockpit_agents",
            "name": "cockpit-agents",
            "adapter_types": ["http"],
            "profile": {
                "supported_modes": ["contract"],
                "invoke_contract": {"endpoint_template": "/invoke{path}"},
            },
        },
    )
    client.post(
        "/api/v1/catalog/environments",
        json={
            "id": "local_mock",
            "name": "local-mock",
            "profile": {"execution_mode": "direct"},
        },
    )
    client.post(
        "/api/v1/catalog/suites",
        json={
            "id": suite_id,
            "mode": "contract",
            "definition": {"name": "核心巡检", "case_ids": [case_id]},
        },
    )
    client.post(
        "/api/v1/catalog/cases",
        json={
            "id": case_id,
            "suite_id": suite_id,
            "definition": {"input": {"method": "GET", "path": f"/{case_id}"}},
        },
    )
