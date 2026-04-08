import json
import shlex

from fastapi import HTTPException, status

from agent_eval_platform.models.catalog import CaseRecord
from agent_eval_platform.repositories.run import RunRepository
from agent_eval_platform.schemas.run import RunCreate, RunRead


class RunService:
    def __init__(self, repository: RunRepository) -> None:
        self.repository = repository

    def create_run(self, payload: RunCreate) -> RunRead:
        for suite_id in payload.suite_ids:
            if not self.repository.suite_exists(suite_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"suite '{suite_id}' not found",
                )

        self.repository.create_run(payload.run_id, payload.target_id, payload.env_id)
        target_profile = self.repository.get_target_profile(payload.target_id)
        target_adapter_types = self.repository.get_target_adapter_types(payload.target_id)

        task_count = 0
        for suite_id in payload.suite_ids:
            run_suite = self.repository.add_suite_instance(payload.run_id, suite_id)
            for case in self.repository.get_cases_for_suite(suite_id):
                run_case = self.repository.add_case_instance(run_suite.id, case.id)
                adapter_type, dispatch_payload = self._build_dispatch_payload(
                    case=case,
                    target_profile=target_profile,
                    target_adapter_types=target_adapter_types,
                )
                self.repository.add_execution_task(
                    run_case.id,
                    payload.execution_topology,
                    adapter_type,
                    json.dumps(dispatch_payload, ensure_ascii=False),
                )
                task_count += 1

        self.repository.session.commit()
        return RunRead(run_id=payload.run_id, status="queued", task_count=task_count)

    def _build_dispatch_payload(
        self,
        *,
        case: CaseRecord,
        target_profile: dict,
        target_adapter_types: list[str],
    ) -> tuple[str, dict]:
        native_contract = target_profile.get("native_test_contract")
        native_suite_mapping = target_profile.get("suite_mapping", {})
        if not isinstance(native_suite_mapping, dict):
            native_suite_mapping = {}
        if not native_suite_mapping and isinstance(native_contract, dict):
            fallback_mapping = native_contract.get("suite_mapping", {})
            if isinstance(fallback_mapping, dict):
                native_suite_mapping = fallback_mapping
        if "native_test" in target_adapter_types and case.suite_id in native_suite_mapping:
            suite_config = native_suite_mapping.get(case.suite_id, {})
            suite_adapter = suite_config.get("adapter", "native_test") if isinstance(
                suite_config, dict
            ) else "native_test"
            if suite_adapter != "native_test":
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail=f"suite '{case.suite_id}' is mapped to unsupported adapter '{suite_adapter}'",
                )
            default_args = native_contract.get("default_args", [])
            suite_args = suite_config.get("args", []) if isinstance(suite_config, dict) else []
            return "native_test", {
                "command": [
                    *shlex.split(native_contract["command"]),
                    *default_args,
                    *suite_args,
                ]
            }

        invoke_contract = target_profile.get("invoke_contract", {})
        if "http" in target_adapter_types and isinstance(invoke_contract, dict):
            case_definition = json.loads(case.raw_definition_json)
            case_input = case_definition.get("input", {})
            headers = {}
            if isinstance(invoke_contract.get("headers"), dict):
                headers.update(invoke_contract["headers"])
            if isinstance(case_input.get("headers"), dict):
                headers.update(case_input["headers"])

            endpoint_template = invoke_contract.get("endpoint_template")
            if isinstance(endpoint_template, str):
                endpoint = endpoint_template.format(path=case_input.get("path", ""))
            else:
                endpoint = case_input.get("path", invoke_contract.get("endpoint", ""))
            payload = {
                "endpoint": endpoint,
                "method": case_input.get("method", invoke_contract.get("method", "POST")),
                "body": case_input.get("body", {}),
            }
            if headers:
                payload["headers"] = headers
            return "http", payload

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"suite '{case.suite_id}' could not be mapped to a dispatch contract",
        )
