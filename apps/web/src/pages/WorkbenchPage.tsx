import type { WorkbenchHome } from "../api/contracts";
import { workbenchApi } from "../api/client";
import { DetailDrawer } from "../components/workbench/DetailDrawer";
import { PageHeader } from "../components/workbench/PageHeader";
import { QuickActionCard } from "../components/workbench/QuickActionCard";
import { StatusBadge } from "../components/workbench/StatusBadge";
import { WorkbenchTable } from "../components/workbench/WorkbenchTable";
import { useResource } from "../hooks/useResource";

const EMPTY_HOME: WorkbenchHome = {
  target_id: "cockpit_agents",
  summary_cards: [
    {
      id: "suite-count",
      label: "测试集",
      value: "12",
      detail: "已接入的 suite 数量",
      tone: "neutral",
    },
  ],
  quick_actions: [
    { label: "导入测试包", href: "/imports/benchmark", tone: "primary" },
    { label: "查看测试集", href: "/suites", tone: "neutral" },
    { label: "新建 Run", href: "/runs/new", tone: "neutral" },
  ],
  recent_runs: [
    {
      run_id: "run-240409-02",
      status: "running",
      target_id: "cockpit_agents",
      env_id: "生产影子",
      suite_ids: ["核心巡检"],
      task_count: 52,
      passed_count: 39,
      created_at: "2026-04-09T12:18:00Z",
    },
  ],
  risk_items: [
    {
      run_id: "run-240409-02",
      metric_id: "检索成功率",
      severity: "warning",
    },
  ],
};

export function WorkbenchPage() {
  const { data, loading, error } = useResource(
    () => workbenchApi.getHome("cockpit_agents"),
    EMPTY_HOME,
    [],
  );

  const recentRiskRows = data.risk_items.map((item, index) => ({
    id: `${item.run_id}-${item.metric_id}-${index}`,
    metric_id: item.metric_id,
    severity: item.severity,
  }));

  return (
    <section className="stack">
      <PageHeader
        actions={
          <div className="shell-context__meta">
            {data.summary_cards.map((card) => (
              <span className="shell-chip" key={card.id}>
                {card.label} {card.value}
              </span>
            ))}
          </div>
        }
        description="从测试集准备到风险处理，围绕当前 target 的关键任务组织今日工作。"
        eyebrow="工作台"
        title="Evaluation Workbench"
      />

      <section className="panel-grid">
        {data.quick_actions.map((action) => (
          <QuickActionCard
            description={`进入${action.label}工作流`}
            href={action.href}
            key={action.href}
            title={action.label === "创建 Run" ? "新建 Run" : action.label}
          />
        ))}
      </section>

      <section className="panel-grid">
        <WorkbenchTable
          ariaLabel="最近运行"
          columns={[
            { key: "run_id", label: "Run", sticky: true },
            {
              key: "status",
              label: "状态",
              render: (row) => <StatusBadge kind="status" value={row.status} />,
            },
          ]}
          rows={data.recent_runs.map((run) => ({ ...run, id: run.run_id }))}
        />
        <WorkbenchTable
          ariaLabel="当前风险"
          columns={[
            { key: "metric_id", label: "风险点", sticky: true },
            {
              key: "severity",
              label: "级别",
              render: (row) => <StatusBadge kind="severity" value={row.severity} />,
            },
          ]}
          rows={recentRiskRows}
        />
      </section>

      <DetailDrawer
        description="最新风险和最近运行会在后续任务中补齐跳转、筛选和证据抽屉。"
        title="工作台说明"
      >
        {loading ? <p className="body-muted">加载中…</p> : null}
        {error ? <p className="callout">{error}</p> : null}
      </DetailDrawer>
    </section>
  );
}
