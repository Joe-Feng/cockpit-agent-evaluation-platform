import pytest

from agent_eval_platform.adapters.base import AdapterResult
from agent_eval_platform.execution.direct_executor import DirectExecutor


class _RecordingHttpAdapter:
    def __init__(self) -> None:
        self.called_with: dict | None = None

    def execute(self, **kwargs) -> AdapterResult:
        self.called_with = kwargs
        return AdapterResult(status_code=200, body={"reply": "ok"}, raw_text='{"reply":"ok"}')


class _RecordingNativeTestAdapter:
    def __init__(self) -> None:
        self.called_command: list[str] | None = None

    def execute(self, *, command: list[str]) -> AdapterResult:
        self.called_command = command
        return AdapterResult(status_code=0, body={"status": "ok"}, raw_text="ok")


def test_direct_executor_dispatches_http_payload() -> None:
    http_adapter = _RecordingHttpAdapter()
    executor = DirectExecutor(http_adapter=http_adapter)

    result = executor.execute(
        {
            "adapter_type": "http",
            "endpoint": "/api/v1/chat",
            "method": "POST",
            "body": {"message": "hello"},
            "headers": {"X-Eval-Run-Id": "run-001"},
        }
    )

    assert result.status_code == 200
    assert http_adapter.called_with == {
        "endpoint": "/api/v1/chat",
        "method": "POST",
        "payload": {"message": "hello"},
        "headers": {"X-Eval-Run-Id": "run-001"},
    }


def test_direct_executor_dispatches_native_test_payload() -> None:
    http_adapter = _RecordingHttpAdapter()
    native_test_adapter = _RecordingNativeTestAdapter()
    executor = DirectExecutor(http_adapter=http_adapter, native_test_adapter=native_test_adapter)

    result = executor.execute(
        {
            "adapter_type": "native_test",
            "command": ["echo", "hello"],
        }
    )

    assert result.status_code == 0
    assert native_test_adapter.called_command == ["echo", "hello"]


def test_direct_executor_rejects_native_test_command_that_is_not_list_of_strings() -> None:
    http_adapter = _RecordingHttpAdapter()
    native_test_adapter = _RecordingNativeTestAdapter()
    executor = DirectExecutor(http_adapter=http_adapter, native_test_adapter=native_test_adapter)

    with pytest.raises(
        ValueError,
        match="native_test adapter requires command to be list\\[str\\]",
    ):
        executor.execute(
            {
                "adapter_type": "native_test",
                "command": "echo hello",
            }
        )


def test_direct_executor_rejects_unsupported_adapter_type() -> None:
    http_adapter = _RecordingHttpAdapter()
    executor = DirectExecutor(http_adapter=http_adapter)

    with pytest.raises(ValueError, match="Unsupported adapter_type: grpc"):
        executor.execute({"adapter_type": "grpc"})


def test_direct_executor_rejects_http_payload_with_missing_required_fields() -> None:
    http_adapter = _RecordingHttpAdapter()
    executor = DirectExecutor(http_adapter=http_adapter)

    with pytest.raises(ValueError, match="Missing required fields for http adapter: endpoint"):
        executor.execute(
            {
                "adapter_type": "http",
                "method": "POST",
                "body": {"message": "hello"},
            }
        )
