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


def test_http_adapter_returns_json_array_body() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/chat"
        return httpx.Response(200, json=["ok", "fallback"])

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="http://target")
    adapter = HttpAdapter(client)

    result = adapter.execute(
        endpoint="/api/v1/chat",
        method="POST",
        payload={"message": "hello"},
    )

    assert result.status_code == 200
    assert result.body == ["ok", "fallback"]


def test_http_adapter_handles_text_plain_response_without_raising() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            500,
            text="upstream error",
            headers={"Content-Type": "text/plain"},
        )

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="http://target")
    adapter = HttpAdapter(client)

    result = adapter.execute(
        endpoint="/api/v1/chat",
        method="POST",
        payload={"message": "hello"},
    )

    assert result.status_code == 500
    assert result.body is None
    assert result.raw_text == "upstream error"


def test_http_adapter_handles_no_content_response_without_raising() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(204)

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="http://target")
    adapter = HttpAdapter(client)

    result = adapter.execute(
        endpoint="/api/v1/chat",
        method="POST",
        payload={"message": "hello"},
    )

    assert result.status_code == 204
    assert result.body is None
    assert result.raw_text == ""
