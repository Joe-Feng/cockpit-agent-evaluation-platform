import { useDeferredValue, useState } from "react";

import { dashboardApi, type RunCenter } from "../api/client";
import { MetricCard } from "../components/MetricCard";
import { useResource } from "../hooks/useResource";
import { labelForSeverity, labelForStatus, labelForTopology } from "../utils/labels";
import { toneForStatus } from "../utils/tone";

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
    <section className="stack stack--workbench">
      <div className="section-header">
        <div>
          <p className="eyebrow">运行中心</p>
          <h3>在驾驶舱内查看单次运行报告</h3>
        </div>
        {loading ? <span className="badge badge--warm">刷新中</span> : null}
      </div>

      <label className="input-panel input-panel--command">
        <span className="eyebrow">运行查询</span>
        <span className="input-panel__label">运行 ID</span>
        <input onChange={(event) => setRunId(event.target.value)} value={runId} />
      </label>

      <div className="metric-grid">
        <MetricCard
          detail="根据执行任务状态汇总"
          label="运行状态"
          tone={toneForStatus(data.status)}
          value={labelForStatus(data.status)}
          variant="primary"
        />
        <MetricCard
          detail="任务分发采用的执行路径"
          label="执行拓扑"
          tone="neutral"
          value={labelForTopology(data.execution_topology)}
        />
        <MetricCard
          detail="当前报告中的回归信号数"
          label="回归信号"
          tone={data.regression_signals.length > 0 ? "warm" : "good"}
          value={String(data.regression_signals.length)}
        />
      </div>
      <div className="panel-grid">
        <section className="panel">
          <div className="panel-heading">
            <h4>套件清单</h4>
          </div>
          {error ? <p className="callout">{error}</p> : null}
          <ul className="list-card">
            {data.suite_ids.map((suiteId) => (
              <li key={suiteId}>
                <div>
                  <strong>{suiteId}</strong>
                  <p>附属于运行 {data.run_id || deferredRunId}</p>
                </div>
              </li>
            ))}
            {data.suite_ids.length === 0 ? (
              <li className="list-card__empty">当前运行未加载到套件数据。</li>
            ) : null}
          </ul>
        </section>
        <section className="panel">
          <div className="panel-heading">
            <h4>回归信号</h4>
          </div>
          <ul className="list-card">
            {data.regression_signals.map((signal) => (
              <li key={`${signal.metric_id}-${signal.severity}`}>
                <div>
                  <strong>{signal.metric_id}</strong>
                  <p>级别 {labelForSeverity(signal.severity)}</p>
                </div>
              </li>
            ))}
            {data.regression_signals.length === 0 ? (
              <li className="list-card__empty">当前运行尚未被标记为回归。</li>
            ) : null}
          </ul>
        </section>
      </div>
    </section>
  );
}
