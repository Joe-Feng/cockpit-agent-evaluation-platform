from typing import Any

from agent_eval_platform.adapters.base import AdapterResult
from agent_eval_platform.adapters.http import HttpAdapter


class DirectExecutor:
    def __init__(self, http_adapter: HttpAdapter, native_test_adapter=None) -> None:
        self.http_adapter = http_adapter
        self.native_test_adapter = native_test_adapter

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
            if "command" not in payload:
                raise ValueError("Missing required fields for native_test adapter: command")
            return self.native_test_adapter.execute(command=payload["command"])
        raise ValueError(f"Unsupported adapter_type: {adapter_type}")
