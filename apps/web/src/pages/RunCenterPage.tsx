import { useDeferredValue, useState } from "react";

import { dashboardApi, type RunCenter } from "../api/client";
import { MetricCard } from "../components/MetricCard";
import { useResource } from "../hooks/useResource";

const EMPTY_RUN_CENTER: RunCenter = {
  run_id: "",
  status: "unknown",
  execution_topology: "unknown",
  suite_ids: [],
  normalized_results: [],
  regression_signals: [],
};

export function RunCenterPage() {
  const [runId, setRunId] = useState("run-002");
  const deferredRunId = useDeferredValue(runId);
  const { data, error, loading } = useResource(
    () => dashboardApi.getRunCenter(deferredRunId),
    EMPTY_RUN_CENTER,
    [deferredRunId],
  );

  return (
    <section className="stack">
      <div className="section-header">
        <div>
          <p className="eyebrow">Run Center</p>
          <h3>Inspect a run report without leaving the dashboard shell</h3>
        </div>
      </div>
      <label className="panel input-panel">
        <span>Run ID</span>
        <input onChange={(event) => setRunId(event.target.value)} value={runId} />
      </label>
      <div className="metric-grid">
        <MetricCard
          detail="Resolved from execution task state"
          label="Run Status"
          tone={data.status === "failed" ? "danger" : "neutral"}
          value={data.status.toUpperCase()}
        />
        <MetricCard
          detail="Executor path used to dispatch tasks"
          label="Topology"
          tone="neutral"
          value={data.execution_topology}
        />
        <MetricCard
          detail="Regression signals in the report"
          label="Signals"
          tone={data.regression_signals.length > 0 ? "warm" : "good"}
          value={String(data.regression_signals.length)}
        />
      </div>
      <div className="panel-grid">
        <section className="panel">
          <div className="panel-heading">
            <h4>Suites</h4>
            {loading ? <span className="badge">Loading</span> : null}
          </div>
          {error ? <p className="callout">{error}</p> : null}
          <ul className="list-card">
            {data.suite_ids.map((suiteId) => (
              <li key={suiteId}>
                <div>
                  <strong>{suiteId}</strong>
                  <p>Attached to run {data.run_id || deferredRunId}</p>
                </div>
              </li>
            ))}
            {data.suite_ids.length === 0 ? (
              <li className="list-card__empty">No suite data loaded for this run.</li>
            ) : null}
          </ul>
        </section>
        <section className="panel">
          <div className="panel-heading">
            <h4>Regression Signals</h4>
          </div>
          <ul className="list-card">
            {data.regression_signals.map((signal) => (
              <li key={`${signal.metric_id}-${signal.severity}`}>
                <div>
                  <strong>{signal.metric_id}</strong>
                  <p>Severity {signal.severity}</p>
                </div>
              </li>
            ))}
            {data.regression_signals.length === 0 ? (
              <li className="list-card__empty">This run is not currently marked as regressing.</li>
            ) : null}
          </ul>
        </section>
      </div>
    </section>
  );
}
