import { useParams } from "react-router-dom";

import { DetailDrawer } from "../components/workbench/DetailDrawer";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/workbench/PageHeader";
import { WorkbenchTable } from "../components/workbench/WorkbenchTable";

const TASK_ROWS = [
  { id: "task-001", task_id: "task-001", status: "failed", adapter_type: "http" },
  { id: "task-002", task_id: "task-002", status: "succeeded", adapter_type: "native_test" },
];

export function RunDetailPage() {
  const { runId = "" } = useParams();

  return (
    <section className="stack">
      <PageHeader
        description={`优先展示 ${runId} 的失败项、风险信号与原始证据。`}
        eyebrow="运行"
        title="Run 详情"
      />
      <section className="metric-grid">
        <MetricCard detail="当前运行聚合状态" label="运行状态" tone="warm" value="failed" />
        <MetricCard detail="检测到的风险数量" label="回归信号" tone="danger" value="2" />
        <MetricCard detail="失败任务数量" label="失败任务" tone="danger" value="1" />
      </section>
      <WorkbenchTable
        ariaLabel="执行任务明细"
        columns={[
          { key: "task_id", label: "任务 ID", sticky: true },
          { key: "status", label: "状态" },
          { key: "adapter_type", label: "适配器" },
        ]}
        rows={TASK_ROWS}
      />
      <DetailDrawer description="证据抽屉会在后续任务中承接 artifact 摘录与复跑动作。" title="失败项">
        <p className="body-muted">artifact_excerpt: {"{\"result\":\"error\"}"}</p>
        <button type="button">复跑本次运行</button>
      </DetailDrawer>
    </section>
  );
}
