from datetime import UTC, datetime


def build_trend_point(
    *,
    scope_type: str,
    scope_id: str,
    metric_id: str,
    dimension_key: str,
    value: float,
    captured_at: datetime | None = None,
) -> dict[str, str | float]:
    timestamp = captured_at or datetime.now(UTC).replace(tzinfo=None)
    return {
        "scope_type": scope_type,
        "scope_id": scope_id,
        "metric_id": metric_id,
        "dimension_key": dimension_key,
        "value": value,
        "captured_at": timestamp.replace(microsecond=0).isoformat(),
    }
