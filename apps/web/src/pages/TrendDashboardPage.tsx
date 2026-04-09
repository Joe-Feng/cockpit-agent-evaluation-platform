import { dashboardApi, type TrendDashboard } from "../api/client";
import { MetricCard } from "../components/MetricCard";
import { TrendChart } from "../components/TrendChart";
import { useResource } from "../hooks/useResource";

const SCOPE_ID = "cockpit.contract.api";

const EMPTY_TREND_DASHBOARD: TrendDashboard = {
  scope_id: SCOPE_ID,
  series: [],
};

export function TrendDashboardPage() {
  const { data, error, loading } = useResource(
    () => dashboardApi.getTrendDashboard(SCOPE_ID),
    EMPTY_TREND_DASHBOARD,
    [],
  );
  const latestPoint = data.series.length > 0 ? data.series[data.series.length - 1] : undefined;

  return (
    <section className="stack">
      <div className="section-header">
        <div>
          <p className="eyebrow">趋势看板</p>
          <h3>当前套件范围的基线感知通过率趋势</h3>
        </div>
        {loading ? <span className="badge">刷新中</span> : null}
      </div>
      <div className="metric-grid metric-grid--trend">
        <MetricCard
          detail="趋势中已采集的完成运行数"
          label="点位数"
          tone="neutral"
          value={String(data.series.length)}
        />
        <MetricCard
          detail="最近一次通过率"
          label="最新通过率"
          tone={latestPoint && latestPoint.value < 0.8 ? "danger" : "good"}
          value={latestPoint ? `${Math.round(latestPoint.value * 100)}%` : "N/A"}
          variant="primary"
        />
        <MetricCard
          detail="趋势序列携带的观测维度"
          label="观测维度"
          tone="warm"
          value={latestPoint?.dimension_key ?? "环境：未知"}
        />
      </div>
      {error ? <p className="callout">{error}</p> : null}
      <TrendChart series={data.series} title="通过率趋势" />
    </section>
  );
}
