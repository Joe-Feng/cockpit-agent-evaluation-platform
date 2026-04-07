from agent_eval_platform.adapters.base import AdapterResult
from agent_eval_platform.adapters.http import HttpAdapter


class DirectExecutor:
    def __init__(self, http_adapter: HttpAdapter, native_test_adapter=None) -> None:
        self.http_adapter = http_adapter
        self.native_test_adapter = native_test_adapter

    def execute(self, payload: dict) -> AdapterResult:
        if payload["adapter_type"] == "http":
            return self.http_adapter.execute(
                endpoint=payload["endpoint"],
                method=payload["method"],
                payload=payload["body"],
                headers=payload.get("headers"),
            )
        if payload["adapter_type"] == "native_test" and self.native_test_adapter is not None:
            return self.native_test_adapter.execute(command=payload["command"])
        raise ValueError(f"Unsupported adapter_type: {payload['adapter_type']}")
