import { useDeferredValue, useState } from "react";

import { dashboardApi, type CaseExplorer } from "../api/client";
import { useResource } from "../hooks/useResource";
import { labelForStatus } from "../utils/labels";
import { toneForStatus } from "../utils/tone";

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
  const latestTone = toneForStatus(data.latest_status);

  return (
    <section className="stack stack--workbench">
      <div className="section-header">
        <div>
          <p className="eyebrow">用例回看</p>
          <h3>回看单个用例的执行轨迹</h3>
        </div>
        <span className={`badge badge--${latestTone}`}>{labelForStatus(data.latest_status)}</span>
      </div>

      <label className="input-panel input-panel--command">
        <span className="eyebrow">用例查询</span>
        <span className="input-panel__label">用例 ID</span>
        <input onChange={(event) => setCaseId(event.target.value)} value={caseId} />
      </label>

      <section className="panel panel--timeline">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">执行历史</p>
            <h4>{data.case_id || deferredCaseId} 的回放窗口</h4>
          </div>
          {loading ? <span className="badge badge--warm">加载中</span> : null}
        </div>
        {error ? <p className="callout">{error}</p> : null}
        <ul className="list-card">
          {data.history.map((item) => (
            <li key={`${item.run_id}-${item.created_at}`}>
              <div>
                <strong>{item.run_id}</strong>
                <p>
                  {item.target_id} • {item.env_id}
                </p>
              </div>
              <div className="list-card__meta">
                <span>{item.created_at.replace("T", " ")}</span>
                <span className={`badge badge--${toneForStatus(item.status)}`}>
                  {labelForStatus(item.status)}
                </span>
              </div>
            </li>
          ))}
          {data.history.length === 0 ? (
            <li className="list-card__empty">暂无该用例的执行历史。</li>
          ) : null}
        </ul>
      </section>
    </section>
  );
}
