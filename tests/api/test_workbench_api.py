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


def test_workbench_home_and_run_list_return_p0_read_models() -> None:
    client = TestClient(create_app())
    _seed_catalog(client, case_ids=("health-001", "health-002"))
    _create_run(client, run_id="run-001")

    home_response = client.get("/api/v1/workbench/home?target_id=cockpit_agents")
    runs_response = client.get("/api/v1/workbench/runs")

    assert home_response.status_code == 200
    assert home_response.json()["quick_actions"][0]["href"] == "/imports/benchmark"
    assert runs_response.status_code == 200
    assert runs_response.json()["items"][0]["run_id"] == "run-001"


def test_run_report_exposes_task_items_and_evidence_summary(tmp_path) -> None:
    client = TestClient(create_app())
    _seed_catalog(client, result_mapping=RESULT_MAPPING)
    _create_run(client, run_id="run-001")

    runtime = client.app.state.runtime
    with runtime.session_factory() as session:
        tasks = _list_tasks_for_run(session, "run-001")
        tasks[0].status = "failed"
        _add_artifact(
            session=session,
            tmp_path=tmp_path,
            task=tasks[0],
            artifact_id="artifact-run-001-1",
            payload={"body": {"result": "error"}, "raw_text": '{"result":"error"}'},
        )
        session.commit()

    response = client.get("/api/v1/reports/runs/run-001")

    assert response.status_code == 200
    assert response.json()["task_items"][0]["status"] == "failed"
    assert response.json()["task_items"][0]["artifact_excerpt"] == '{"result":"error"}'


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
