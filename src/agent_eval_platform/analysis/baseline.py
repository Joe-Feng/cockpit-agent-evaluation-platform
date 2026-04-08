def diff_against_baseline(
    current_value: float,
    baseline_value: float,
    metric_id: str,
) -> dict[str, float | bool | str]:
    delta = current_value - baseline_value
    return {
        "metric_id": metric_id,
        "current_value": current_value,
        "baseline_value": baseline_value,
        "delta": delta,
        "is_regression": delta < 0,
    }
