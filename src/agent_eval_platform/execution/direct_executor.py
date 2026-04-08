from typing import Any

from agent_eval_platform.adapters.base import AdapterResult
from agent_eval_platform.adapters.http import HttpAdapter


class DirectExecutor:
    def __init__(
        self,
        http_adapter: HttpAdapter,
        native_test_adapter=None,
        cli_adapter=None,
        python_sdk_adapter=None,
    ) -> None:
        self.http_adapter = http_adapter
        self.native_test_adapter = native_test_adapter
        self.cli_adapter = cli_adapter
        self.python_sdk_adapter = python_sdk_adapter

    def execute(self, payload: dict[str, Any]) -> AdapterResult:
        adapter_type = payload.get("adapter_type")
        if adapter_type is None:
            raise ValueError("Missing required field: adapter_type")

        if adapter_type == "http":
            missing = [field for field in ("endpoint", "method", "body") if field not in payload]
            if missing:
                raise ValueError(
                    f"Missing required fields for http adapter: {', '.join(missing)}"
                )
            return self.http_adapter.execute(
                endpoint=payload["endpoint"],
                method=payload["method"],
                payload=payload["body"],
                headers=payload.get("headers"),
            )
        if adapter_type == "native_test":
            if self.native_test_adapter is None:
                raise ValueError("Unsupported adapter_type: native_test")
            command = self._get_command_payload(payload, adapter_type="native_test")
            return self.native_test_adapter.execute(command=command)
        if adapter_type == "cli":
            if self.cli_adapter is None:
                raise ValueError("Unsupported adapter_type: cli")
            command = self._get_command_payload(payload, adapter_type="cli")
            return self.cli_adapter.execute(command=command)
        if adapter_type == "python_sdk":
            if self.python_sdk_adapter is None:
                raise ValueError("Unsupported adapter_type: python_sdk")
            required_fields = [field for field in ("module_path", "callable_name", "payload") if field not in payload]
            if required_fields:
                raise ValueError(
                    f"Missing required fields for python_sdk adapter: {', '.join(required_fields)}"
                )
            module_path = payload["module_path"]
            callable_name = payload["callable_name"]
            adapter_payload = payload["payload"]
            if not isinstance(module_path, str) or not module_path:
                raise ValueError("python_sdk adapter requires module_path to be non-empty str")
            if not isinstance(callable_name, str) or not callable_name:
                raise ValueError("python_sdk adapter requires callable_name to be non-empty str")
            if not isinstance(adapter_payload, dict):
                raise ValueError("python_sdk adapter requires payload to be dict")
            return self.python_sdk_adapter.execute(
                module_path=module_path,
                callable_name=callable_name,
                payload=adapter_payload,
            )
        raise ValueError(f"Unsupported adapter_type: {adapter_type}")

    @staticmethod
    def _get_command_payload(payload: dict[str, Any], *, adapter_type: str) -> list[str]:
        if "command" not in payload:
            raise ValueError(f"Missing required fields for {adapter_type} adapter: command")
        command = payload["command"]
        if not isinstance(command, list) or not all(isinstance(item, str) for item in command):
            raise ValueError(f"{adapter_type} adapter requires command to be list[str]")
        return command
