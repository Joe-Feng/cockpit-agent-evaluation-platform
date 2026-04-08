from pathlib import Path

from agent_eval_platform.models.analysis import ArtifactRecord
from agent_eval_platform.orchestration_ids import build_orchestration_id


def persist_execution_artifact(
    session,
    artifact_storage,
    *,
    task_id: str,
    attempt_id: str,
    body: dict,
) -> str:
    try:
        storage_uri = artifact_storage.write_json(attempt_id, body)
        session.add(
            ArtifactRecord(
                id=build_orchestration_id("artifact", task_id, attempt_id),
                owner_type="execution_task",
                owner_id=task_id,
                artifact_type="execution_result",
                storage_uri=storage_uri,
                size_bytes=Path(storage_uri).stat().st_size,
            )
        )
        session.commit()
        return "stored"
    except Exception:
        session.rollback()
        return "failed"
