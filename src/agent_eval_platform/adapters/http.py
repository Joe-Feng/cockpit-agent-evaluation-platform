from typing import Any

import httpx

from agent_eval_platform.adapters.base import AdapterResult


class HttpAdapter:
    def __init__(self, client: httpx.Client) -> None:
        self.client = client

    def execute(
        self,
        *,
        endpoint: str,
        method: str,
        payload: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> AdapterResult:
        response = self.client.request(
            method=method,
            url=endpoint,
            json=payload,
            headers=headers,
        )
        return AdapterResult(
            status_code=response.status_code,
            body=response.json(),
            raw_text=response.text,
        )
