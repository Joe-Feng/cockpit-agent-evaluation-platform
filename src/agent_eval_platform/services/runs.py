import json
import shlex
from typing import Any

from fastapi import HTTPException, status

from agent_eval_platform.models.catalog import CaseRecord
from agent_eval_platform.orchestration_ids import build_orchestration_id
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

    def create_rerun(self, source_run_id: str) -> RunRead:
        source_run = self.repository.get_run(source_run_id)
        if source_run is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"run '{source_run_id}' not found",
            )

        rerun_id = self._build_rerun_id(source_run_id)
        self.repository.create_run(rerun_id, source_run.target_id, source_run.env_id)

        suite_id_map: dict[str, str] = {}
        for source_suite in self.repository.list_run_suites(source_run_id):
            rerun_suite = self.repository.add_suite_instance(rerun_id, source_suite.suite_id)
            suite_id_map[source_suite.id] = rerun_suite.id

        case_id_map: dict[str, str] = {}
        for source_case in self.repository.list_run_cases_for_run(source_run_id):
            rerun_case = self.repository.add_case_instance(
                suite_id_map[source_case.run_suite_id],
                source_case.case_id,
            )
            case_id_map[source_case.id] = rerun_case.id

        task_count = 0
        for source_task in self.repository.list_execution_tasks_for_run(source_run_id):
            self.repository.add_execution_task(
                case_id_map[source_task.run_case_id],
                source_task.executor_type,
                source_task.adapter_type,
                source_task.dispatch_payload,
                priority=source_task.priority,
            )
            task_count += 1

        self.repository.session.commit()
        return RunRead(run_id=rerun_id, status="queued", task_count=task_count)

    def _build_dispatch_payload(
        self,
        *,
        case: CaseRecord,
        target_profile: dict,
        target_adapter_types: list[str],
    ) -> tuple[str, dict]:
        case_definition = json.loads(case.raw_definition_json)
        case_input = case_definition.get("input", {})
        if not isinstance(case_input, dict):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"case '{case.id}' input must be an object",
            )

        native_contract = target_profile.get("native_test_contract")
        suite_mapping = self._resolve_suite_mapping(
            target_profile=target_profile,
            native_contract=native_contract,
        )
        suite_config = suite_mapping.get(case.suite_id, {})
        if suite_config and not isinstance(suite_config, dict):
            raise self._invalid_native_test_contract(
                f"suite_mapping.{case.suite_id} must be an object"
            )

        selected_adapter = self._select_adapter_type(
            target_adapter_types=target_adapter_types,
            suite_config=suite_config if isinstance(suite_config, dict) else {},
        )

        if selected_adapter == "native_test":
            if not isinstance(native_contract, dict):
                raise self._invalid_native_test_contract("native_test_contract must be an object")
            suite_adapter = suite_config.get("adapter", "native_test")
            if suite_adapter != "native_test":
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail=f"suite '{case.suite_id}' is mapped to unsupported adapter '{suite_adapter}'",
                )
            command = self._normalize_native_test_command(native_contract.get("command"))
            default_args = self._normalize_native_test_args(
                native_contract.get("default_args", []),
                field_name="native_test_contract.default_args",
            )
            suite_args = self._normalize_native_test_args(
                suite_config.get("args", []),
                field_name=f"suite_mapping.{case.suite_id}.args",
            )
            return "native_test", {
                "command": [
                    *command,
                    *default_args,
                    *suite_args,
                ]
            }

        if selected_adapter == "cli":
            cli_contract = target_profile.get("cli_contract")
            if not isinstance(cli_contract, dict):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="cli_contract must be an object",
                )

            command = self._normalize_cli_command(cli_contract.get("command"))
            default_args = self._normalize_cli_args(
                cli_contract.get("default_args", []),
                field_name="cli_contract.default_args",
            )
            suite_args = self._normalize_cli_args(
                suite_config.get("args", []),
                field_name=f"suite_mapping.{case.suite_id}.args",
            )
            return "cli", {"command": [*command, *default_args, *suite_args]}

        if selected_adapter == "python_sdk":
            sdk_contract = target_profile.get("python_sdk_contract")
            if not isinstance(sdk_contract, dict):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="python_sdk_contract must be an object",
                )

            module_path = sdk_contract.get("module_path")
            callable_name = sdk_contract.get("callable_name")
            if not isinstance(module_path, str) or not module_path:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="python_sdk_contract.module_path must be a non-empty string",
                )
            if not isinstance(callable_name, str) or not callable_name:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="python_sdk_contract.callable_name must be a non-empty string",
                )

            return "python_sdk", {
                "module_path": module_path,
                "callable_name": callable_name,
                "payload": case_input,
            }

        invoke_contract = target_profile.get("invoke_contract", {})
        if selected_adapter == "http" and isinstance(invoke_contract, dict):
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

    def _build_rerun_id(self, source_run_id: str) -> str:
        base_run_id = f"{source_run_id}-rerun"
        if len(base_run_id) <= 64 and not self.repository.run_exists(base_run_id):
            return base_run_id

        suffix = 2
        while len(f"{base_run_id}-{suffix}") <= 64:
            candidate = f"{base_run_id}-{suffix}"
            if not self.repository.run_exists(candidate):
                return candidate
            suffix += 1

        attempt = 1
        while True:
            candidate = build_orchestration_id("run", source_run_id, "rerun", str(attempt))
            if not self.repository.run_exists(candidate):
                return candidate
            attempt += 1

    @staticmethod
    def _resolve_suite_mapping(*, target_profile: dict, native_contract: Any) -> dict[str, Any]:
        suite_mapping = target_profile.get("suite_mapping", {})
        if isinstance(suite_mapping, dict) and suite_mapping:
            return suite_mapping
        if isinstance(native_contract, dict):
            fallback_mapping = native_contract.get("suite_mapping", {})
            if isinstance(fallback_mapping, dict):
                return fallback_mapping
        return {}

    @staticmethod
    def _select_adapter_type(*, target_adapter_types: list[str], suite_config: dict[str, Any]) -> str | None:
        mapped_adapter = suite_config.get("adapter")
        if isinstance(mapped_adapter, str):
            return mapped_adapter
        if len(target_adapter_types) == 1:
            return target_adapter_types[0]
        return "http" if "http" in target_adapter_types else None

    def _normalize_native_test_command(self, raw_command: Any) -> list[str]:
        if isinstance(raw_command, str):
            command = shlex.split(raw_command)
        elif isinstance(raw_command, list) and all(isinstance(item, str) for item in raw_command):
            command = raw_command
        else:
            raise self._invalid_native_test_contract(
                "native_test_contract.command must be a shell string or list[str]"
            )
        if not command:
            raise self._invalid_native_test_contract("native_test_contract.command must not be empty")
        return command

    def _normalize_native_test_args(self, raw_args: Any, *, field_name: str) -> list[str]:
        if not isinstance(raw_args, list) or not all(isinstance(item, str) for item in raw_args):
            raise self._invalid_native_test_contract(f"{field_name} must be list[str]")
        return raw_args

    def _normalize_cli_command(self, raw_command: Any) -> list[str]:
        if isinstance(raw_command, str):
            command = shlex.split(raw_command)
        elif isinstance(raw_command, list) and all(isinstance(item, str) for item in raw_command):
            command = raw_command
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="cli_contract.command must be a shell string or list[str]",
            )
        if not command:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="cli_contract.command must not be empty",
            )
        return command

    def _normalize_cli_args(self, raw_args: Any, *, field_name: str) -> list[str]:
        if not isinstance(raw_args, list) or not all(isinstance(item, str) for item in raw_args):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"{field_name} must be list[str]",
            )
        return raw_args

    @staticmethod
    def _invalid_native_test_contract(detail: str) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=detail,
        )
