from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class AdapterResult:
    status_code: int
    body: Any | None
    raw_text: str


class TargetAdapter(Protocol):
    def execute(self, **kwargs) -> AdapterResult:
        ...


ADAPTER_REGISTRY = {
    "http": "agent_eval_platform.adapters.http.HttpAdapter",
    "native_test": "agent_eval_platform.adapters.native_test.NativeTestAdapter",
    "cli": "agent_eval_platform.adapters.cli.CliAdapter",
    "python_sdk": "agent_eval_platform.adapters.python_sdk.PythonSdkAdapter",
}
