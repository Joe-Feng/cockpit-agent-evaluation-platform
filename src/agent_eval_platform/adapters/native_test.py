import subprocess

from agent_eval_platform.adapters.base import AdapterResult


class NativeTestAdapter:
    def execute(self, *, command: list[str]) -> AdapterResult:
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        return AdapterResult(
            status_code=completed.returncode,
            body={"stdout": completed.stdout, "stderr": completed.stderr},
            raw_text=completed.stdout,
        )
