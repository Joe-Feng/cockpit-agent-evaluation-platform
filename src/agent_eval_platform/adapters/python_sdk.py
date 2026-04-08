import importlib.util
from pathlib import Path
from typing import Any

from agent_eval_platform.adapters.base import AdapterResult


class PythonSdkAdapter:
    def execute(
        self,
        *,
        module_path: str,
        callable_name: str,
        payload: dict[str, Any],
    ) -> AdapterResult:
        module = self._load_module(module_path)
        callable_obj = getattr(module, callable_name, None)
        if not callable(callable_obj):
            raise ValueError(f"callable '{callable_name}' not found in module '{module_path}'")

        result = callable_obj(payload)
        body = result if isinstance(result, dict) else {"result": result}
        return AdapterResult(status_code=0, body=body, raw_text=str(body))

    @staticmethod
    def _load_module(module_path: str):
        path = Path(module_path)
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            raise ValueError(f"could not load python sdk module from '{module_path}'")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
