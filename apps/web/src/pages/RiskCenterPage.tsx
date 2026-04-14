import { TrendChart } from "../components/TrendChart";
import { PageHeader } from "../components/workbench/PageHeader";
import { WorkbenchTable } from "../components/workbench/WorkbenchTable";

const REGRESSION_ROWS = [
  { id: "risk-1", metric_id: "检索成功率", severity: "high" },
];

const ALERT_ROWS = [
  { id: "alert-1", metric_id: "工具调用稳定性", severity: "warning" },
];

export function RiskCenterPage() {
  return (
    <section className="stack">
      <PageHeader
        description="先看打开的回归和告警，再看趋势视角。"
        eyebrow="风险"
        title="风险中心"
      />
      <section className="panel-grid">
        <section className="stack">
          <h4>当前打开的回归</h4>
          <WorkbenchTable
            ariaLabel="当前打开的回归"
            columns={[
              { key: "metric_id", label: "回归项", sticky: true },
              { key: "severity", label: "级别" },
            ]}
            rows={REGRESSION_ROWS}
          />
        </section>
        <section className="stack">
          <h4>当前打开的告警</h4>
          <WorkbenchTable
            ariaLabel="当前打开的告警"
            columns={[
              { key: "metric_id", label: "告警项", sticky: true },
              { key: "severity", label: "级别" },
            ]}
            rows={ALERT_ROWS}
          />
        </section>
      </section>
      <TrendChart title="通过率趋势" series={[]} />
    </section>
  );
}
