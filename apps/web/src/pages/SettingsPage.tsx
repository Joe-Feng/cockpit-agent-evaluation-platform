import { PageHeader } from "../components/workbench/PageHeader";
import { WorkbenchTable } from "../components/workbench/WorkbenchTable";

const ENV_ROWS = [{ id: "local-mock", name: "本地 Mock", value: "direct" }];
const TARGET_ROWS = [{ id: "cockpit_agents", name: "Cockpit Agents", value: "单主 target" }];
const ALERT_ROWS = [{ id: "pass-rate", name: "通过率", value: "warning" }];

export function SettingsPage() {
  return (
    <section className="stack">
      <PageHeader
        description="低频配置与查看能力集中在这里。"
        eyebrow="设置"
        title="设置"
      />
      <section className="panel-grid">
        <section className="stack">
          <h4>Environment 管理</h4>
          <WorkbenchTable
            ariaLabel="Environment 管理"
            columns={[
              { key: "id", label: "环境", sticky: true },
              { key: "name", label: "名称" },
            ]}
            rows={ENV_ROWS}
          />
        </section>
        <section className="stack">
          <h4>目标信息</h4>
          <WorkbenchTable
            ariaLabel="目标信息"
            columns={[
              { key: "id", label: "Target", sticky: true },
              { key: "name", label: "名称" },
            ]}
            rows={TARGET_ROWS}
          />
        </section>
        <section className="stack">
          <h4>告警规则</h4>
          <WorkbenchTable
            ariaLabel="告警规则"
            columns={[
              { key: "name", label: "指标", sticky: true },
              { key: "value", label: "级别" },
            ]}
            rows={ALERT_ROWS}
          />
        </section>
      </section>
    </section>
  );
}
