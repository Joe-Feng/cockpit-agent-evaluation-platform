import { dashboardApi, type AlertEvent, type RegressionSignal } from "../api/client";
import { MetricCard } from "../components/MetricCard";
import { useResource } from "../hooks/useResource";

type RegressionCenterData = {
  regressions: RegressionSignal[];
  alerts: AlertEvent[];
};

const EMPTY_REGRESSION_CENTER: RegressionCenterData = {
  regressions: [],
  alerts: [],
};

export function RegressionCenterPage() {
  const { data, error, loading } = useResource(
    async () => {
      const [regressions, alerts] = await Promise.all([
        dashboardApi.getRegressionCenter(),
        dashboardApi.getAlertEvents(),
      ]);
      return {
        regressions: regressions.items,
        alerts: alerts.items,
      };
    },
    EMPTY_REGRESSION_CENTER,
    [],
  );

  return (
    <section className="stack">
      <div className="section-header">
        <div>
          <p className="eyebrow">Regression Center</p>
          <h3>Severity queue and alert feed for recent baseline regressions</h3>
        </div>
        {loading ? <span className="badge">Refreshing</span> : null}
      </div>
      <div className="metric-grid">
        <MetricCard
          detail="Regression signals emitted by report snapshots"
          label="Regression Signals"
          tone={data.regressions.length > 0 ? "warm" : "good"}
          value={String(data.regressions.length)}
        />
        <MetricCard
          detail="Alert events eligible for notification delivery"
          label="Alert Events"
          tone={data.alerts.length > 0 ? "danger" : "good"}
          value={String(data.alerts.length)}
        />
      </div>
      {error ? <p className="callout">{error}</p> : null}
      <div className="panel-grid">
        <section className="panel">
          <div className="panel-heading">
            <h4>Regression queue</h4>
          </div>
          <ul className="list-card">
            {data.regressions.map((signal) => (
              <li key={`${signal.run_id}-${signal.metric_id}`}>
                <div>
                  <strong>{signal.metric_id}</strong>
                  <p>{signal.run_id} • {signal.target_id ?? "unknown target"}</p>
                </div>
                <div className="list-card__meta">
                  <span className="badge badge--warm">{signal.severity}</span>
                </div>
              </li>
            ))}
            {data.regressions.length === 0 ? (
              <li className="list-card__empty">No regression signals are currently open.</li>
            ) : null}
          </ul>
        </section>
        <section className="panel">
          <div className="panel-heading">
            <h4>Alert feed</h4>
          </div>
          <ul className="list-card">
            {data.alerts.map((alert) => (
              <li key={`${alert.run_id}-${alert.metric_id}`}>
                <div>
                  <strong>{alert.metric_id}</strong>
                  <p>{alert.target_id ?? "unknown target"} via {alert.run_id}</p>
                </div>
                <div className="list-card__meta">
                  <span className="badge badge--warm">{alert.severity}</span>
                </div>
              </li>
            ))}
            {data.alerts.length === 0 ? (
              <li className="list-card__empty">The alert feed is quiet right now.</li>
            ) : null}
          </ul>
        </section>
      </div>
    </section>
  );
}
