from collections.abc import Mapping
from typing import Any


def default_alert_rules() -> list[dict[str, Any]]:
    return [
        {
            "metric_id": "pass_rate",
            "threshold": -0.1,
            "severity": "high",
        }
    ]


def evaluate_alert_rule(*, rule: Mapping[str, Any], diff: Mapping[str, Any]) -> dict[str, Any]:
    metric_id = str(diff.get("metric_id", ""))
    threshold = float(rule.get("threshold", 0.0))
    delta = float(diff.get("delta", 0.0))
    should_fire = (
        rule.get("metric_id") == metric_id
        and bool(diff.get("is_regression"))
        and delta <= threshold
    )
    return {
        "metric_id": metric_id,
        "threshold": threshold,
        "delta": delta,
        "should_fire": should_fire,
        "severity": str(rule.get("severity", "medium")) if should_fire else "none",
    }
