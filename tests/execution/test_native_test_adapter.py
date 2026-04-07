from agent_eval_platform.adapters.native_test import NativeTestAdapter


def test_native_test_adapter_returns_exit_code(monkeypatch) -> None:
    class Completed:
        returncode = 0
        stdout = "1 passed"
        stderr = ""

    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: Completed())

    adapter = NativeTestAdapter()
    result = adapter.execute(command=["pytest", "tests/test_api.py"])

    assert result.status_code == 0
    assert result.body["stdout"] == "1 passed"
