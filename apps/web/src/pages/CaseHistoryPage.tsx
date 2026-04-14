import { useState } from "react";

import { PageHeader } from "../components/workbench/PageHeader";
import { WorkbenchTable } from "../components/workbench/WorkbenchTable";

const HISTORY_ROWS = [
  { id: "run-001", run_id: "run-001", status: "failed", created_at: "2026-04-14 09:00" },
  { id: "run-002", run_id: "run-002", status: "succeeded", created_at: "2026-04-13 18:20" },
];

export function CaseHistoryPage() {
  const [caseId, setCaseId] = useState("health-001");

  return (
    <section className="stack">
      <PageHeader
        description="回答“这个 case 是偶发失败还是稳定退化”。"
        eyebrow="结果"
        title="Case 历史"
      />
      <div className="input-panel">
        <label className="input-panel__label" htmlFor="case-history-id">
          Case ID
        </label>
        <input
          id="case-history-id"
          onChange={(event) => setCaseId(event.target.value)}
          value={caseId}
        />
      </div>
      <WorkbenchTable
        ariaLabel="Case 历史"
        columns={[
          { key: "run_id", label: "Run", sticky: true },
          { key: "status", label: "状态" },
          { key: "created_at", label: "执行时间" },
        ]}
        rows={HISTORY_ROWS}
      />
    </section>
  );
}
