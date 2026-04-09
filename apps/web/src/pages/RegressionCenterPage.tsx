import { dashboardApi, type AlertEvent, type RegressionSignal } from "../api/client";
import { MetricCard } from "../components/MetricCard";
import { useResource } from "../hooks/useResource";
import { labelForSeverity } from "../utils/labels";
import { toneForSeverity } from "../utils/tone";

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
          <p className="eyebrow">风险态势</p>
          <h3>最近基线回归的队列与告警流</h3>
        </div>
        {loading ? <span className="badge badge--warm">刷新中</span> : null}
      </div>

      <div className="metric-grid metric-grid--risk">
        <MetricCard
          detail="由报告快照产生的回归信号"
          label="回归信号"
          tone={data.regressions.length > 0 ? "warm" : "good"}
          value={String(data.regressions.length)}
          variant="primary"
        />
        <MetricCard
          detail="可进入通知流程的告警事件"
          label="告警事件"
          tone={data.alerts.length > 0 ? "danger" : "good"}
          value={String(data.alerts.length)}
          variant="primary"
        />
      </div>

      {error ? <p className="callout">{error}</p> : null}

      <div className="panel-grid panel-grid--risk">
        <section className="panel panel--risk">
          <div className="panel-heading">
            <h4>回归队列</h4>
          </div>
          <ul className="list-card">
            {data.regressions.map((signal) => (
              <li key={`${signal.run_id}-${signal.metric_id}`}>
                <div>
                  <strong>{signal.metric_id}</strong>
                  <p>{signal.run_id} • {signal.target_id ?? "未知目标"}</p>
                </div>
                <div className="list-card__meta">
                  <span className={`badge badge--${toneForSeverity(signal.severity)}`}>
                    {labelForSeverity(signal.severity)}
                  </span>
                </div>
              </li>
            ))}
            {data.regressions.length === 0 ? (
              <li className="list-card__empty">当前没有打开的回归信号。</li>
            ) : null}
          </ul>
        </section>

        <section className="panel panel--feed">
          <div className="panel-heading">
            <h4>告警流</h4>
          </div>
          <ul className="list-card">
            {data.alerts.map((alert) => (
              <li key={`${alert.run_id}-${alert.metric_id}`}>
                <div>
                  <strong>{alert.metric_id}</strong>
                  <p>{alert.target_id ?? "未知目标"} 来自 {alert.run_id}</p>
                </div>
                <div className="list-card__meta">
                  <span className={`badge badge--${toneForSeverity(alert.severity)}`}>
                    {labelForSeverity(alert.severity)}
                  </span>
                </div>
              </li>
            ))}
            {data.alerts.length === 0 ? (
              <li className="list-card__empty">当前告警流较为平静。</li>
            ) : null}
          </ul>
        </section>
      </div>
    </section>
  );
}
