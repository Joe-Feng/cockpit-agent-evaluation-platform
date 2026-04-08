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
          <p className="eyebrow">Trend Dashboard</p>
          <h3>Baseline-aware pass-rate drift for the active suite scope</h3>
        </div>
        {loading ? <span className="badge">Refreshing</span> : null}
      </div>
      <div className="metric-grid">
        <MetricCard
          detail="Completed runs captured in the series"
          label="Points"
          tone="neutral"
          value={String(data.series.length)}
        />
        <MetricCard
          detail="Most recent pass-rate value"
          label="Latest Pass Rate"
          tone={latestPoint && latestPoint.value < 0.8 ? "danger" : "good"}
          value={latestPoint ? `${Math.round(latestPoint.value * 100)}%` : "N/A"}
        />
        <MetricCard
          detail="Dimension carried into the trend series"
          label="Dimension"
          tone="warm"
          value={latestPoint?.dimension_key ?? "env=unknown"}
        />
      </div>
      {error ? <p className="callout">{error}</p> : null}
      <TrendChart series={data.series} title="Pass Rate Trend" />
    </section>
  );
}
