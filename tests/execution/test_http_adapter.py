import httpx

from agent_eval_platform.adapters.http import HttpAdapter


def test_http_adapter_posts_payload_and_returns_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/chat"
        return httpx.Response(
            200,
            json={"reply": "ok", "intent": "fallback", "status": "succeeded"},
        )

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="http://target")
    adapter = HttpAdapter(client)

    result = adapter.execute(
        endpoint="/api/v1/chat",
        method="POST",
        payload={"message": "hello"},
        headers={"X-Eval-Run-Id": "run-001"},
    )

    assert result.status_code == 200
    assert result.body["reply"] == "ok"
