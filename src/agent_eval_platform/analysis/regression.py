from collections.abc import Mapping
from typing import Any


def build_regression_signal(metric_id: str, diff: Mapping[str, Any]) -> dict[str, Any]:
    is_regression = bool(diff.get("is_regression", False))
    delta = float(diff.get("delta", 0.0))
    severity = "none"
    if is_regression:
        severity = "high" if delta <= -0.2 else "medium"

    return {
        "metric_id": metric_id,
        "is_regression": is_regression,
        "severity": severity,
    }
