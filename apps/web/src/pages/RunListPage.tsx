import { WorkbenchTable } from "../components/workbench/WorkbenchTable";
import { PageHeader } from "../components/workbench/PageHeader";
import { StatusBadge } from "../components/workbench/StatusBadge";

const RUN_ROWS = [
  { id: "run-001", run_id: "run-001", status: "failed" },
  { id: "run-002", run_id: "run-002", status: "running" },
];

export function RunListPage() {
  return (
    <section className="stack">
      <PageHeader
        description="默认入口从 run_id 手输切换为可浏览的运行列表。"
        eyebrow="运行"
        title="Run 列表"
      />
      <WorkbenchTable
        ariaLabel="Run 列表"
        columns={[
          { key: "run_id", label: "Run", sticky: true },
          {
            key: "status",
            label: "状态",
            render: (row) => <StatusBadge kind="status" value={row.status} />,
          },
        ]}
        rows={RUN_ROWS}
      />
    </section>
  );
}
