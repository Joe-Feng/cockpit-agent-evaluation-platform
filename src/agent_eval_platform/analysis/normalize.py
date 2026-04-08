from collections.abc import Mapping
from typing import Any


def normalize_http_result(
    raw_body: Mapping[str, Any],
    result_mapping: Mapping[str, Any],
) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for normalized_key, rule in result_mapping.items():
        normalized[normalized_key] = _resolve_rule(raw_body, rule)

    normalized.setdefault("error_type", None)
    normalized.setdefault("error_message", None)
    return normalized


def _resolve_rule(raw_body: Mapping[str, Any], rule: Any) -> Any:
    if isinstance(rule, str):
        return raw_body.get(rule)

    if not isinstance(rule, Mapping):
        return None

    field_name = rule.get("field")
    raw_value = raw_body.get(field_name) if isinstance(field_name, str) else None
    values = rule.get("values")
    if isinstance(values, Mapping):
        return values.get(raw_value, raw_value)
    return raw_value
