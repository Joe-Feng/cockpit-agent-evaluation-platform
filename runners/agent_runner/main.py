import os

import httpx

from agent_eval_platform.adapters.cli import CliAdapter
from agent_eval_platform.adapters.http import HttpAdapter
from agent_eval_platform.adapters.native_test import NativeTestAdapter
from agent_eval_platform.adapters.python_sdk import PythonSdkAdapter
from agent_eval_platform.execution.direct_executor import DirectExecutor
from agent_eval_platform.execution.runner_protocol import RunnerCompleteRequest


def main() -> None:
    api_base_url = os.getenv("AGENT_EVAL_API_BASE_URL", "http://127.0.0.1:8000")
    target_base_url = os.getenv("AGENT_EVAL_TARGET_BASE_URL", "http://127.0.0.1:8000")
    runner_id = os.getenv("AGENT_EVAL_RUNNER_ID", "remote-runner")

    with httpx.Client(base_url=api_base_url) as api_client:
        claim_response = api_client.get("/api/v1/runs/leases", params={"runner_id": runner_id})
        claim_response.raise_for_status()
        lease = claim_response.json()
        if not lease:
            print("no-task")
            return

        executor = DirectExecutor(
            http_adapter=HttpAdapter(httpx.Client(base_url=target_base_url)),
            native_test_adapter=NativeTestAdapter(),
            cli_adapter=CliAdapter(),
            python_sdk_adapter=PythonSdkAdapter(),
        )
        try:
            result = executor.execute(
                {
                    "adapter_type": lease["adapter_type"],
                    **lease["dispatch_payload"],
                }
            )
            task_status = (
                "succeeded"
                if _is_success(adapter_type=lease["adapter_type"], status_code=result.status_code)
                else "failed"
            )
            raw_result = {
                "status_code": result.status_code,
                "body": result.body,
                "raw_text": result.raw_text,
            }
        except Exception as exc:
            task_status = "failed"
            raw_result = {
                "error_type": type(exc).__name__,
                "error": str(exc),
            }

        completion = RunnerCompleteRequest(
            task_id=lease["task_id"],
            attempt_id=lease["attempt_id"],
            status=task_status,
            raw_result=raw_result,
        )
        completion_response = api_client.post(
            "/api/v1/runs/completions",
            json=completion.model_dump(),
        )
        completion_response.raise_for_status()
        print(f"completed:{completion.task_id}")


def _is_success(*, adapter_type: str, status_code: int) -> bool:
    if adapter_type in {"native_test", "cli", "python_sdk"}:
        return status_code == 0
    return 200 <= status_code < 400


if __name__ == "__main__":
    main()
