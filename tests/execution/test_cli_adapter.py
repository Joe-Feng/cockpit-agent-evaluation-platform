from agent_eval_platform.adapters.cli import CliAdapter


def test_cli_adapter_runs_command(monkeypatch) -> None:
    class Completed:
        returncode = 0
        stdout = '{"status":"succeeded"}'
        stderr = ""

    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: Completed())

    adapter = CliAdapter()
    result = adapter.execute(command=["target-cli", "--json"])

    assert result.status_code == 0
    assert result.body["status"] == "succeeded"
    assert result.raw_text == '{"status":"succeeded"}'
