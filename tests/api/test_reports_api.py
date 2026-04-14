import json

from fastapi.testclient import TestClient
from sqlalchemy import select

from agent_eval_platform.api.app import create_app
from agent_eval_platform.models.analysis import ArtifactRecord
from agent_eval_platform.models.run import ExecutionTaskRecord, RunCaseRecord, RunSuiteRecord

RESULT_MAPPING = {
    "reply": "response_text",
    "intent": "intent_name",
    "status": {
        "field": "result",
        "values": {
            "ok": "passed",
            "error": "failed",
        },
    },
}


def test_get_run_report_returns_normalized_results_without_baseline(tmp_path) -> None:
    client = TestClient(create_app())
    _seed_catalog(client, result_mapping=RESULT_MAPPING)
    _create_run(client, run_id="run-001")

    runtime = client.app.state.runtime
    with runtime.session_factory() as session:
        tasks = _list_tasks_for_run(session, "run-001")
        assert len(tasks) == 1
        task_id = tasks[0].id
        tasks[0].status = "succeeded"
        _add_artifact(
            session=session,
            tmp_path=tmp_path,
            task=tasks[0],
            artifact_id="artifact-run-001-1",
            payload={
                "status_code": 200,
                "body": {
                    "response_text": "pong",
                    "intent_name": "health_check",
                    "result": "ok",
                },
                "raw_text": '{"response_text":"pong"}',
            },
        )
        session.commit()

    response = client.get("/api/v1/reports/runs/run-001")

    assert response.status_code == 200
    assert response.json() == {
        "run_id": "run-001",
        "status": "succeeded",
        "target_id": "cockpit_agents",
        "env_id": "local_mock",
        "suite_ids": ["cockpit.contract.api"],
        "suite_count": 1,
        "case_count": 1,
        "task_count": 1,
        "passed_count": 1,
        "normalized_results": [
            {
                "reply": "pong",
                "intent": "health_check",
                "status": "passed",
                "error_type": None,
                "error_message": None,
            }
        ],
        "task_items": [
            {
                "task_id": task_id,
                "status": "succeeded",
                "adapter_type": "http",
                "artifact_excerpt": '{"response_text":"pong"}',
            }
        ],
        "regression_signals": [],
    }


def test_get_run_report_returns_high_severity_regression_signal_when_pass_rate_drops() -> None:
    client = TestClient(create_app())
    _seed_catalog(client, case_ids=("health-001", "health-002"))
    _create_run(client, run_id="run-001")
    _create_run(client, run_id="run-002")

    runtime = client.app.state.runtime
    with runtime.session_factory() as session:
        baseline_tasks = _list_tasks_for_run(session, "run-001")
        current_tasks = _list_tasks_for_run(session, "run-002")
        assert len(baseline_tasks) == 2
        assert len(current_tasks) == 2
        current_task_ids = [task.id for task in current_tasks]
        for task in baseline_tasks:
            task.status = "succeeded"
        current_tasks[0].status = "succeeded"
        current_tasks[1].status = "failed"
        session.commit()

    response = client.get("/api/v1/reports/runs/run-002")

    assert response.status_code == 200
    assert response.json() == {
        "run_id": "run-002",
        "status": "failed",
        "target_id": "cockpit_agents",
        "env_id": "local_mock",
        "suite_ids": ["cockpit.contract.api"],
        "suite_count": 1,
        "case_count": 2,
        "task_count": 2,
        "passed_count": 1,
        "normalized_results": [],
        "task_items": [
            {
                "task_id": current_task_ids[0],
                "status": "succeeded",
                "adapter_type": "http",
                "artifact_excerpt": None,
            },
            {
                "task_id": current_task_ids[1],
                "status": "failed",
                "adapter_type": "http",
                "artifact_excerpt": None,
            },
        ],
        "regression_signals": [
            {
                "metric_id": "pass_rate",
                "is_regression": True,
                "severity": "high",
            }
        ],
    }


def test_get_run_report_skips_regression_signals_for_in_progress_run() -> None:
    client = TestClient(create_app())
    _seed_catalog(client, case_ids=("health-001", "health-002"))
    _create_run(client, run_id="run-001")
    _create_run(client, run_id="run-002")

    runtime = client.app.state.runtime
    with runtime.session_factory() as session:
        baseline_tasks = _list_tasks_for_run(session, "run-001")
        current_tasks = _list_tasks_for_run(session, "run-002")
        current_task_ids = [task.id for task in current_tasks]
        for task in baseline_tasks:
            task.status = "succeeded"
        current_tasks[0].status = "succeeded"
        session.commit()

    response = client.get("/api/v1/reports/runs/run-002")

    assert response.status_code == 200
    assert response.json()["status"] == "running"
    assert response.json()["task_items"] == [
        {
            "task_id": current_task_ids[0],
            "status": "succeeded",
            "adapter_type": "http",
            "artifact_excerpt": None,
        },
        {
            "task_id": current_task_ids[1],
            "status": "queued",
            "adapter_type": "http",
            "artifact_excerpt": None,
        },
    ]
    assert response.json()["regression_signals"] == []


def test_get_run_report_ignores_incomplete_baseline_run_for_regression() -> None:
    client = TestClient(create_app())
    _seed_catalog(client, case_ids=("health-001", "health-002"))
    _create_run(client, run_id="run-001")
    _create_run(client, run_id="run-002")

    runtime = client.app.state.runtime
    with runtime.session_factory() as session:
        baseline_tasks = _list_tasks_for_run(session, "run-001")
        current_tasks = _list_tasks_for_run(session, "run-002")
        current_task_ids = [task.id for task in current_tasks]
        baseline_tasks[0].status = "succeeded"
        current_tasks[0].status = "failed"
        current_tasks[1].status = "failed"
        session.commit()

    response = client.get("/api/v1/reports/runs/run-002")

    assert response.status_code == 200
    assert response.json()["status"] == "failed"
    assert response.json()["task_items"] == [
        {
            "task_id": current_task_ids[0],
            "status": "failed",
            "adapter_type": "http",
            "artifact_excerpt": None,
        },
        {
            "task_id": current_task_ids[1],
            "status": "failed",
            "adapter_type": "http",
            "artifact_excerpt": None,
        },
    ]
    assert response.json()["regression_signals"] == []


def test_get_run_report_returns_empty_regression_signals_without_comparable_baseline() -> None:
    client = TestClient(create_app())
    _seed_catalog(client)
    _create_run(client, run_id="run-001")

    runtime = client.app.state.runtime
    with runtime.session_factory() as session:
        tasks = _list_tasks_for_run(session, "run-001")
        assert len(tasks) == 1
        task_id = tasks[0].id
        tasks[0].status = "succeeded"
        session.commit()

    response = client.get("/api/v1/reports/runs/run-001")

    assert response.status_code == 200
    assert response.json() == {
        "run_id": "run-001",
        "status": "succeeded",
        "target_id": "cockpit_agents",
        "env_id": "local_mock",
        "suite_ids": ["cockpit.contract.api"],
        "suite_count": 1,
        "case_count": 1,
        "task_count": 1,
        "passed_count": 1,
        "normalized_results": [],
        "task_items": [
            {
                "task_id": task_id,
                "status": "succeeded",
                "adapter_type": "http",
                "artifact_excerpt": None,
            }
        ],
        "regression_signals": [],
    }


def test_rerun_endpoint_clones_existing_run() -> None:
    client = TestClient(create_app())
    _seed_catalog(client)
    _create_run(client, run_id="run-001")

    assert (
        client.post(
            "/api/v1/catalog/cases",
            json={
                "id": "health-002",
                "suite_id": "cockpit.contract.api",
                "definition": {"input": {"method": "GET", "path": "/health-002"}},
            },
        ).status_code
        == 201
    )

    rerun_response = client.post("/api/v1/runs/run-001/rerun")

    assert rerun_response.status_code == 201
    rerun_run_id = rerun_response.json()["run_id"]
    assert rerun_response.json()["task_count"] == 1

    runtime = client.app.state.runtime
    with runtime.session_factory() as session:
        source_task = session.scalar(
            select(ExecutionTaskRecord)
            .join(RunCaseRecord, ExecutionTaskRecord.run_case_id == RunCaseRecord.id)
            .join(RunSuiteRecord, RunCaseRecord.run_suite_id == RunSuiteRecord.id)
            .where(RunSuiteRecord.run_id == "run-001")
        )
        rerun_task = session.scalar(
            select(ExecutionTaskRecord)
            .join(RunCaseRecord, ExecutionTaskRecord.run_case_id == RunCaseRecord.id)
            .join(RunSuiteRecord, RunCaseRecord.run_suite_id == RunSuiteRecord.id)
            .where(RunSuiteRecord.run_id == rerun_run_id)
        )

    assert source_task is not None
    assert rerun_task is not None
    assert rerun_task.adapter_type == source_task.adapter_type
    assert rerun_task.dispatch_payload == source_task.dispatch_payload
    assert rerun_task.executor_type == source_task.executor_type


def test_rerun_endpoint_keeps_long_rerun_id_within_64_chars() -> None:
    client = TestClient(create_app())
    run_id = "run-" + ("r" * 60)
    _seed_catalog(client)
    _create_run(client, run_id=run_id)

    rerun_response = client.post(f"/api/v1/runs/{run_id}/rerun")

    assert rerun_response.status_code == 201
    assert len(rerun_response.json()["run_id"]) <= 64


def _seed_catalog(
    client: TestClient,
    *,
    case_ids: tuple[str, ...] = ("health-001",),
    result_mapping: dict | None = None,
) -> None:
    profile = {"supported_modes": ["contract"]}
    if result_mapping is not None:
        profile["result_mapping"] = result_mapping

    assert (
        client.post(
            "/api/v1/catalog/targets",
            json={
                "id": "cockpit_agents",
                "name": "cockpit-agents",
                "adapter_types": ["http"],
                "profile": profile,
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
            json={
                "id": "cockpit.contract.api",
                "mode": "contract",
                "definition": {"case_ids": list(case_ids)},
            },
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
    response = client.post(
        "/api/v1/runs",
        json={
            "run_id": run_id,
            "target_id": "cockpit_agents",
            "env_id": "local_mock",
            "suite_ids": ["cockpit.contract.api"],
            "execution_topology": "direct",
        },
    )
    assert response.status_code == 201


def _list_tasks_for_run(session, run_id: str) -> list[ExecutionTaskRecord]:
    stmt = (
        select(ExecutionTaskRecord)
        .join(RunCaseRecord, ExecutionTaskRecord.run_case_id == RunCaseRecord.id)
        .join(RunSuiteRecord, RunCaseRecord.run_suite_id == RunSuiteRecord.id)
        .where(RunSuiteRecord.run_id == run_id)
        .order_by(ExecutionTaskRecord.id)
    )
    return list(session.scalars(stmt))


def _add_artifact(session, *, tmp_path, task: ExecutionTaskRecord, artifact_id: str, payload: dict) -> None:
    artifact_path = tmp_path / f"{artifact_id}.json"
    artifact_path.write_text(json.dumps(payload), encoding="utf-8")
    session.add(
        ArtifactRecord(
            id=artifact_id,
            owner_type="execution_task",
            owner_id=task.id,
            artifact_type="execution_result",
            storage_uri=str(artifact_path),
            size_bytes=artifact_path.stat().st_size,
        )
    )
