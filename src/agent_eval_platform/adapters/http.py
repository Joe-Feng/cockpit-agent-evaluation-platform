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
        raw_text = response.text
        body: Any | None = None
        if raw_text.strip():
            try:
                body = response.json()
            except ValueError:
                body = None
        return AdapterResult(
            status_code=response.status_code,
            body=body,
            raw_text=raw_text,
        )
