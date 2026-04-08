import json
import subprocess

from agent_eval_platform.adapters.base import AdapterResult


class CliAdapter:
    def execute(self, *, command: list[str]) -> AdapterResult:
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        body = self._parse_body(stdout=completed.stdout, stderr=completed.stderr)
        return AdapterResult(
            status_code=completed.returncode,
            body=body,
            raw_text=completed.stdout,
        )

    @staticmethod
    def _parse_body(*, stdout: str, stderr: str) -> dict:
        if stdout.strip():
            try:
                parsed = json.loads(stdout)
            except json.JSONDecodeError:
                parsed = None
            if isinstance(parsed, dict):
                return parsed
        return {"stdout": stdout, "stderr": stderr}
