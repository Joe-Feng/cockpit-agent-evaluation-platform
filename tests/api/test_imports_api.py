from fastapi.testclient import TestClient
from sqlalchemy import select

from agent_eval_platform.api.app import create_app
from agent_eval_platform.models.catalog import CaseRecord, SuiteRecord


PACKAGE = {
    "schema_version": "benchmark-agent-export/v1",
    "export_id": "exp_20260411_001",
    "export_profile": "cockpit_agents_http_v1",
    "target_binding": {
        "target_id": "cockpit_agents",
        "adapter_type": "http",
        "mode": "e2e_mock",
    },
    "source": {"library_ids": ["lib-001"], "document_ids": ["doc-001"]},
    "filters": {"qc_status": ["passed"]},
    "suite": {
        "id": "cockpit.generated.e2e_mock.vehicle_control.20260411.batch_001",
        "name": "cockpit.generated.e2e_mock.vehicle_control.20260411.batch_001",
        "mode": "e2e_mock",
        "description": "Generated from benchmark",
        "case_count": 1,
        "source_summary": {"scenario_categories": ["车控"]},
    },
    "cases": [
        {
            "id": "ca_http_000001",
            "source_test_case_id": "11111111-1111-1111-1111-111111111111",
            "definition": {
                "input": {
                    "method": "POST",
                    "path": "/api/v1/chat",
                    "body": {
                        "message": "把空调调到24度",
                        "session_id": None,
                        "context": {"driving_mode": "parked", "user_role": "owner"},
                    },
                    "headers": {"X-Eval-Mode": "e2e_mock"},
                },
                "expectations": {
                    "intent": "vehicle_control",
                    "blocked": False,
                    "status": "succeeded",
                    "reply": {"non_empty": True, "contains_any": [], "forbidden_contains": []},
                    "trace": {"required": True, "min_events": 1},
                },
                "metadata": {
                    "scenario_category": "车控",
                    "complexity": "low",
                    "risk_level": "P3",
                    "expected_behavior": "execute",
                    "required_capabilities": ["intent_classification", "trace_output"],
                    "review_policy": "auto_pass",
                },
            },
        }
    ],
}


def test_import_benchmark_package_creates_suite_and_case_records() -> None:
    client = TestClient(create_app())

    client.post(
        "/api/v1/catalog/targets",
        json={
            "id": "cockpit_agents",
            "name": "cockpit-agents",
            "adapter_types": ["http"],
            "profile": {"supported_modes": ["e2e_mock"]},
        },
    )
    client.post(
        "/api/v1/catalog/environments",
        json={"id": "local_mock", "name": "local-mock", "profile": {"execution_mode": "direct"}},
    )

    response = client.post(
        "/api/v1/imports/benchmark-agent-package",
        json={"env_id": "local_mock", "package": PACKAGE},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["suite_id"] == PACKAGE["suite"]["id"]
    assert payload["case_count"] == 1

    runtime = client.app.state.runtime
    with runtime.session_factory() as session:
        suite = session.scalar(select(SuiteRecord).where(SuiteRecord.id == PACKAGE["suite"]["id"]))
        case = session.scalar(select(CaseRecord).where(CaseRecord.id == PACKAGE["cases"][0]["id"]))

    assert suite is not None
    assert case is not None


def test_import_benchmark_package_rolls_back_on_duplicate_case() -> None:
    client = TestClient(create_app())

    client.post(
        "/api/v1/catalog/targets",
        json={
            "id": "cockpit_agents",
            "name": "cockpit-agents",
            "adapter_types": ["http"],
            "profile": {"supported_modes": ["e2e_mock"]},
        },
    )
    client.post(
        "/api/v1/catalog/environments",
        json={"id": "local_mock", "name": "local-mock", "profile": {"execution_mode": "direct"}},
    )
    client.post(
        "/api/v1/catalog/suites",
        json={"id": "existing-suite", "mode": "contract", "definition": {"case_ids": []}},
    )
    client.post(
        "/api/v1/catalog/cases",
        json={"id": "ca_http_000001", "suite_id": "existing-suite", "definition": {"input": {}}},
    )

    response = client.post(
        "/api/v1/imports/benchmark-agent-package",
        json={"env_id": "local_mock", "package": PACKAGE},
    )

    assert response.status_code == 409

    runtime = client.app.state.runtime
    with runtime.session_factory() as session:
        imported_suite = session.scalar(select(SuiteRecord).where(SuiteRecord.id == PACKAGE["suite"]["id"]))

    assert imported_suite is None
