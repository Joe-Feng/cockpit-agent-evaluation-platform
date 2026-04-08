from datetime import datetime

from agent_eval_platform.analysis.alerts import evaluate_alert_rule
from agent_eval_platform.analysis.trends import build_trend_point


def test_build_trend_point_keeps_metric_dimensions() -> None:
    point = build_trend_point(
        scope_type="suite",
        scope_id="cockpit.contract.api",
        metric_id="pass_rate",
        dimension_key="env=local_mock",
        value=1.0,
        captured_at=datetime(2026, 4, 8, 12, 0, 0),
    )

    assert point == {
        "scope_type": "suite",
        "scope_id": "cockpit.contract.api",
        "metric_id": "pass_rate",
        "dimension_key": "env=local_mock",
        "value": 1.0,
        "captured_at": "2026-04-08T12:00:00",
    }


def test_evaluate_alert_rule_triggers_on_regression() -> None:
    event = evaluate_alert_rule(
        rule={"metric_id": "pass_rate", "threshold": -0.1, "severity": "high"},
        diff={"metric_id": "pass_rate", "delta": -0.2, "is_regression": True},
    )

    assert event == {
        "metric_id": "pass_rate",
        "threshold": -0.1,
        "delta": -0.2,
        "should_fire": True,
        "severity": "high",
    }


def test_evaluate_alert_rule_stays_quiet_when_metric_does_not_match() -> None:
    event = evaluate_alert_rule(
        rule={"metric_id": "latency_p95", "threshold": 50, "severity": "medium"},
        diff={"metric_id": "pass_rate", "delta": -0.2, "is_regression": True},
    )

    assert event["should_fire"] is False
    assert event["severity"] == "none"
