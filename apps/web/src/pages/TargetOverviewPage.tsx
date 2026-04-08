import { dashboardApi, type TargetOverview } from "../api/client";
import { MetricCard } from "../components/MetricCard";
import { useResource } from "../hooks/useResource";

const TARGET_ID = "cockpit_agents";

const EMPTY_TARGET_OVERVIEW: TargetOverview = {
  target_id: TARGET_ID,
  latest_status: "unknown",
  latest_runs: [],
  open_alerts: [],
};

export function TargetOverviewPage() {
  const { data, error, loading } = useResource(
    () => dashboardApi.getTargetOverview(TARGET_ID),
    EMPTY_TARGET_OVERVIEW,
    [],
  );

  return (
    <section className="stack">
      <div className="section-header">
        <div>
          <p className="eyebrow">Target Overview</p>
          <h3>How the active target is behaving right now</h3>
        </div>
        <span className={`status-pill status-pill--${toneForStatus(data.latest_status)}`}>
          {data.latest_status}
        </span>
      </div>
      <div className="metric-grid">
        <MetricCard
          detail="Latest aggregated health signal"
          label="Latest Status"
          tone={toneForStatus(data.latest_status)}
          value={data.latest_status.toUpperCase()}
        />
        <MetricCard
          detail="Recent runs included in the overview"
          label="Recent Runs"
          tone="neutral"
          value={String(data.latest_runs.length)}
        />
        <MetricCard
          detail="Regression alerts still open"
          label="Open Alerts"
          tone={data.open_alerts.length > 0 ? "danger" : "good"}
          value={String(data.open_alerts.length)}
        />
      </div>
      <div className="panel-grid">
        <section className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Run Feed</p>
              <h4>Latest runs for {data.target_id}</h4>
            </div>
            {loading ? <span className="badge">Refreshing</span> : null}
          </div>
          {error ? <p className="callout">{error}</p> : null}
          <ul className="list-card">
            {data.latest_runs.map((run) => (
              <li key={run.run_id}>
                <div>
                  <strong>{run.run_id}</strong>
                  <p>{run.suite_ids.join(", ") || "No suites"}</p>
                </div>
                <div className="list-card__meta">
                  <span>{run.passed_count}/{run.task_count} passed</span>
                  <span className={`status-pill status-pill--${toneForStatus(run.status)}`}>
                    {run.status}
                  </span>
                </div>
              </li>
            ))}
            {data.latest_runs.length === 0 ? (
              <li className="list-card__empty">No run data has been produced yet.</li>
            ) : null}
          </ul>
        </section>
        <section className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Alert Posture</p>
              <h4>Open alert events</h4>
            </div>
          </div>
          <ul className="list-card">
            {data.open_alerts.map((alert) => (
              <li key={`${alert.run_id}-${alert.metric_id}`}>
                <div>
                  <strong>{alert.metric_id}</strong>
                  <p>Triggered by {alert.run_id}</p>
                </div>
                <div className="list-card__meta">
                  <span className="badge badge--warm">{alert.severity}</span>
                </div>
              </li>
            ))}
            {data.open_alerts.length === 0 ? (
              <li className="list-card__empty">No active alerts. Regression queue is clear.</li>
            ) : null}
          </ul>
        </section>
      </div>
    </section>
  );
}

function toneForStatus(status: string): "neutral" | "good" | "warm" | "danger" {
  if (status === "succeeded") {
    return "good";
  }
  if (status === "failed") {
    return "danger";
  }
  if (status === "running") {
    return "warm";
  }
  return "neutral";
}
