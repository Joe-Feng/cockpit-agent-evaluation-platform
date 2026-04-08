from collections.abc import Mapping
from datetime import datetime
from typing import Any


def build_run_summary(*, report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "run_id": report["run_id"],
        "status": report["status"],
        "env_id": report["env_id"],
        "suite_ids": list(report["suite_ids"]),
        "task_count": report["task_count"],
        "passed_count": report["passed_count"],
    }


def build_target_overview(
    *,
    target_id: str,
    latest_runs: list[dict[str, Any]],
    open_alerts: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "target_id": target_id,
        "latest_status": latest_runs[0]["status"] if latest_runs else "unknown",
        "latest_runs": latest_runs,
        "open_alerts": open_alerts,
    }


def build_open_alert_item(*, event: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "run_id": event["run_id"],
        "metric_id": event["metric_id"],
        "severity": event["severity"],
        "should_fire": event["should_fire"],
    }


def build_run_center(
    *,
    report: Mapping[str, Any],
    execution_topology: str | None,
) -> dict[str, Any]:
    return {
        "run_id": report["run_id"],
        "status": report["status"],
        "execution_topology": execution_topology or "unknown",
        "suite_ids": list(report["suite_ids"]),
        "normalized_results": list(report["normalized_results"]),
        "regression_signals": list(report["regression_signals"]),
    }


def build_case_history_item(
    *,
    run_id: str,
    target_id: str,
    env_id: str,
    status: str,
    created_at: datetime,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "target_id": target_id,
        "env_id": env_id,
        "status": status,
        "created_at": created_at.replace(microsecond=0).isoformat(),
    }


def build_case_explorer(*, case_id: str, history: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "history": history,
        "latest_status": history[0]["status"] if history else "unknown",
    }


def build_trend_dashboard(*, scope_id: str, series: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "scope_id": scope_id,
        "series": series,
    }


def build_regression_item(
    *,
    run_id: str,
    target_id: str,
    env_id: str,
    signal: Mapping[str, Any],
    created_at: datetime,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "target_id": target_id,
        "env_id": env_id,
        "metric_id": signal["metric_id"],
        "severity": signal["severity"],
        "is_regression": signal["is_regression"],
        "captured_at": created_at.replace(microsecond=0).isoformat(),
    }


def build_regression_center(*, items: list[dict[str, Any]]) -> dict[str, Any]:
    return {"items": items}


def build_alert_event(*, run_id: str, target_id: str, event: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "target_id": target_id,
        "metric_id": event["metric_id"],
        "severity": event["severity"],
        "should_fire": event["should_fire"],
    }
