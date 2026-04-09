import { dashboardApi, type TargetOverview } from "../api/client";
import { MetricCard } from "../components/MetricCard";
import { useResource } from "../hooks/useResource";
import { labelForSeverity, labelForStatus } from "../utils/labels";
import { toneForSeverity, toneForStatus } from "../utils/tone";

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
          <p className="eyebrow">目标总览</p>
          <h3>当前目标的运行健康一览</h3>
        </div>
        <span className={`status-pill status-pill--${toneForStatus(data.latest_status)}`}>
          {labelForStatus(data.latest_status)}
        </span>
      </div>
      <div className="metric-grid metric-grid--overview">
        <MetricCard
          detail="最新汇总健康信号"
          label="最新状态"
          tone={toneForStatus(data.latest_status)}
          value={labelForStatus(data.latest_status)}
          variant="primary"
        />
        <MetricCard
          detail="总览中纳入的最近运行数"
          label="近次运行"
          tone="neutral"
          value={String(data.latest_runs.length)}
        />
        <MetricCard
          detail="仍待处理的回归告警数"
          label="打开告警"
          tone={data.open_alerts.length > 0 ? "danger" : "good"}
          value={String(data.open_alerts.length)}
        />
      </div>
      <div className="panel-grid panel-grid--overview">
        <section className="panel panel--feed">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">最近运行流</p>
              <h4>{data.target_id} 的最近运行</h4>
            </div>
            {loading ? <span className="badge badge--warm">刷新中</span> : null}
          </div>
          {error ? <p className="callout">{error}</p> : null}
          <ul className="list-card">
            {data.latest_runs.map((run) => (
              <li key={run.run_id}>
                <div>
                  <strong>{run.run_id}</strong>
                  <p>{run.suite_ids.join("、") || "未关联套件"}</p>
                </div>
                <div className="list-card__meta">
                  <span>{run.passed_count}/{run.task_count} 通过</span>
                  <span className={`status-pill status-pill--${toneForStatus(run.status)}`}>
                    {labelForStatus(run.status)}
                  </span>
                </div>
              </li>
            ))}
            {data.latest_runs.length === 0 ? (
              <li className="list-card__empty">暂无运行数据。</li>
            ) : null}
          </ul>
        </section>
        <section className="panel panel--risk">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">告警态势</p>
              <h4>当前打开的告警事件</h4>
            </div>
          </div>
          <ul className="list-card">
            {data.open_alerts.map((alert) => (
              <li key={`${alert.run_id}-${alert.metric_id}`}>
                <div>
                  <strong>{alert.metric_id}</strong>
                  <p>由 {alert.run_id} 触发</p>
                </div>
                <div className="list-card__meta">
                  <span className={`badge badge--${toneForSeverity(alert.severity)}`}>
                    {labelForSeverity(alert.severity)}
                  </span>
                </div>
              </li>
            ))}
            {data.open_alerts.length === 0 ? (
              <li className="list-card__empty">当前无活动告警，回归队列已清空。</li>
            ) : null}
          </ul>
        </section>
      </div>
    </section>
  );
}
