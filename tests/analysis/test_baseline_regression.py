from agent_eval_platform.analysis.baseline import diff_against_baseline
from agent_eval_platform.analysis.regression import build_regression_signal


def test_diff_against_baseline_and_build_regression_signal_for_pass_rate_drop() -> None:
    diff = diff_against_baseline(
        current_value=0.70,
        baseline_value=0.95,
        metric_id="pass_rate",
    )

    assert diff == {
        "metric_id": "pass_rate",
        "current_value": 0.70,
        "baseline_value": 0.95,
        "delta": -0.25,
        "is_regression": True,
    }

    signal = build_regression_signal("pass_rate", diff)

    assert signal == {
        "metric_id": "pass_rate",
        "is_regression": True,
        "severity": "high",
    }
