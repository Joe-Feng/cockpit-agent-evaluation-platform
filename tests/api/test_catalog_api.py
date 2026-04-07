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
