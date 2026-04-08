from agent_eval_platform.adapters.python_sdk import PythonSdkAdapter


def test_python_sdk_adapter_calls_named_function(tmp_path) -> None:
    module_path = tmp_path / "fake_target.py"
    module_path.write_text(
        "def run_case(payload):\n    return {'status': 'succeeded', 'final_answer': payload['message']}\n",
        encoding="utf-8",
    )

    adapter = PythonSdkAdapter()
    result = adapter.execute(
        module_path=str(module_path),
        callable_name="run_case",
        payload={"message": "hello"},
    )

    assert result.status_code == 0
    assert result.body["final_answer"] == "hello"
