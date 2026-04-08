from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import select

from agent_eval_platform.api.app import create_app
from agent_eval_platform.models.run import ExecutionTaskRecord, RunCaseRecord, RunRecord, RunSuiteRecord


def test_target_overview_and_alerts_show_latest_regression() -> None:
    client = TestClient(create_app())
    _seed_catalog(client, case_ids=("health-001", "health-002"))
    _create_run(client, run_id="run-001")
    _create_run(client, run_id="run-002")

    runtime = client.app.state.runtime
    with runtime.session_factory() as session:
        _set_run_timestamp(session, "run-001", datetime(2026, 4, 8, 0, 0, 0))
        _set_run_timestamp(session, "run-002", datetime(2026, 4, 8, 0, 0, 1))
        baseline_tasks = _list_tasks_for_run(session, "run-001")
        current_tasks = _list_tasks_for_run(session, "run-002")
        for task in baseline_tasks:
            task.status = "succeeded"
        current_tasks[0].status = "succeeded"
        current_tasks[1].status = "failed"
        session.commit()

    overview_response = client.get("/api/v1/dashboard/targets/cockpit_agents")
    alert_response = client.get("/api/v1/alerts/events")

    assert overview_response.status_code == 200
    assert overview_response.json() == {
        "target_id": "cockpit_agents",
        "latest_status": "failed",
        "latest_runs": [
            {
                "run_id": "run-002",
                "status": "failed",
                "env_id": "local_mock",
                "suite_ids": ["cockpit.contract.api"],
                "task_count": 2,
                "passed_count": 1,
            },
            {
                "run_id": "run-001",
                "status": "succeeded",
                "env_id": "local_mock",
                "suite_ids": ["cockpit.contract.api"],
                "task_count": 2,
                "passed_count": 2,
            },
        ],
        "open_alerts": [
            {
                "run_id": "run-002",
                "metric_id": "pass_rate",
                "severity": "high",
                "should_fire": True,
            }
        ],
    }
    assert alert_response.status_code == 200
    assert alert_response.json()["items"] == [
        {
            "run_id": "run-002",
            "target_id": "cockpit_agents",
            "metric_id": "pass_rate",
            "severity": "high",
            "should_fire": True,
        }
    ]


def test_trend_dashboard_returns_pass_rate_series_for_suite_scope() -> None:
    client = TestClient(create_app())
    _seed_catalog(client, case_ids=("health-001", "health-002"))
    _create_run(client, run_id="run-001")
    _create_run(client, run_id="run-002")

    runtime = client.app.state.runtime
    with runtime.session_factory() as session:
        _set_run_timestamp(session, "run-001", datetime(2026, 4, 8, 0, 0, 0))
        _set_run_timestamp(session, "run-002", datetime(2026, 4, 8, 0, 0, 1))
        baseline_tasks = _list_tasks_for_run(session, "run-001")
        current_tasks = _list_tasks_for_run(session, "run-002")
        for task in baseline_tasks:
            task.status = "succeeded"
        current_tasks[0].status = "succeeded"
        current_tasks[1].status = "failed"
        session.commit()

    response = client.get("/api/v1/dashboard/trends/cockpit.contract.api")

    assert response.status_code == 200
    assert response.json() == {
        "scope_id": "cockpit.contract.api",
        "series": [
            {
                "scope_type": "suite",
                "scope_id": "cockpit.contract.api",
                "metric_id": "pass_rate",
                "dimension_key": "env=local_mock",
                "value": 1.0,
                "captured_at": "2026-04-08T00:00:00",
            },
            {
                "scope_type": "suite",
                "scope_id": "cockpit.contract.api",
                "metric_id": "pass_rate",
                "dimension_key": "env=local_mock",
                "value": 0.5,
                "captured_at": "2026-04-08T00:00:01",
            },
        ],
    }


def _seed_catalog(client: TestClient, *, case_ids: tuple[str, ...]) -> None:
    assert (
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
        ).status_code
        == 201
    )
    assert (
        client.post(
            "/api/v1/catalog/environments",
            json={"id": "local_mock", "name": "local-mock", "profile": {"execution_mode": "direct"}},
        ).status_code
        == 201
    )
    assert (
        client.post(
            "/api/v1/catalog/suites",
            json={"id": "cockpit.contract.api", "mode": "contract", "definition": {"case_ids": list(case_ids)}},
        ).status_code
        == 201
    )
    for case_id in case_ids:
        assert (
            client.post(
                "/api/v1/catalog/cases",
                json={
                    "id": case_id,
                    "suite_id": "cockpit.contract.api",
                    "definition": {"input": {"method": "GET", "path": f"/{case_id}"}},
                },
            ).status_code
            == 201
        )


def _create_run(client: TestClient, *, run_id: str) -> None:
    assert (
        client.post(
            "/api/v1/runs",
            json={
                "run_id": run_id,
                "target_id": "cockpit_agents",
                "env_id": "local_mock",
                "suite_ids": ["cockpit.contract.api"],
                "execution_topology": "direct",
            },
        ).status_code
        == 201
    )


def _list_tasks_for_run(session, run_id: str) -> list[ExecutionTaskRecord]:
    stmt = (
        select(ExecutionTaskRecord)
        .join(RunCaseRecord, ExecutionTaskRecord.run_case_id == RunCaseRecord.id)
        .join(RunSuiteRecord, RunCaseRecord.run_suite_id == RunSuiteRecord.id)
        .where(RunSuiteRecord.run_id == run_id)
        .order_by(ExecutionTaskRecord.id)
    )
    return list(session.scalars(stmt))


def _set_run_timestamp(session, run_id: str, created_at: datetime) -> None:
    record = session.get(RunRecord, run_id)
    assert record is not None
    record.created_at = created_at
