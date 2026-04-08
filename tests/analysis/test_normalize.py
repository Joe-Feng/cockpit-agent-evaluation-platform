from agent_eval_platform.analysis.normalize import normalize_http_result


def test_normalize_http_result_maps_reply_intent_and_status() -> None:
    raw_body = {
        "response_text": "pong",
        "intent_name": "health_check",
        "result": "ok",
    }
    result_mapping = {
        "reply": "response_text",
        "intent": "intent_name",
        "status": {
            "field": "result",
            "values": {
                "ok": "passed",
                "error": "failed",
            },
        },
    }

    normalized = normalize_http_result(raw_body, result_mapping)

    assert normalized == {
        "reply": "pong",
        "intent": "health_check",
        "status": "passed",
        "error_type": None,
        "error_message": None,
    }
