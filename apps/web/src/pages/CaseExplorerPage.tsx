import { useDeferredValue, useState } from "react";

import { dashboardApi, type CaseExplorer } from "../api/client";
import { useResource } from "../hooks/useResource";

const EMPTY_CASE_EXPLORER: CaseExplorer = {
  case_id: "",
  latest_status: "unknown",
  history: [],
};

export function CaseExplorerPage() {
  const [caseId, setCaseId] = useState("health-001");
  const deferredCaseId = useDeferredValue(caseId);
  const { data, error, loading } = useResource(
    () => dashboardApi.getCaseExplorer(deferredCaseId),
    EMPTY_CASE_EXPLORER,
    [deferredCaseId],
  );

  return (
    <section className="stack">
      <div className="section-header">
        <div>
          <p className="eyebrow">Case Explorer</p>
          <h3>Replay the exact case trajectory across recent runs</h3>
        </div>
        <span className="badge">{data.latest_status}</span>
      </div>
      <label className="panel input-panel">
        <span>Case ID</span>
        <input onChange={(event) => setCaseId(event.target.value)} value={caseId} />
      </label>
      <section className="panel">
        <div className="panel-heading">
          <h4>Execution History</h4>
          {loading ? <span className="badge">Loading</span> : null}
        </div>
        {error ? <p className="callout">{error}</p> : null}
        <ul className="list-card">
          {data.history.map((item) => (
            <li key={`${item.run_id}-${item.created_at}`}>
              <div>
                <strong>{item.run_id}</strong>
                <p>{item.target_id} • {item.env_id}</p>
              </div>
              <div className="list-card__meta">
                <span>{item.created_at.replace("T", " ")}</span>
                <span className="badge">{item.status}</span>
              </div>
            </li>
          ))}
          {data.history.length === 0 ? (
            <li className="list-card__empty">No case history was found yet.</li>
          ) : null}
        </ul>
      </section>
    </section>
  );
}
