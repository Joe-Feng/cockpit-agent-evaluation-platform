import { useState } from "react";

import type { SuiteListRead } from "../api/contracts";
import { workbenchApi } from "../api/client";
import { DetailDrawer } from "../components/workbench/DetailDrawer";
import { PageHeader } from "../components/workbench/PageHeader";
import { StatusBadge } from "../components/workbench/StatusBadge";
import { WorkbenchTable } from "../components/workbench/WorkbenchTable";
import { useResource } from "../hooks/useResource";

const EMPTY_SUITE_LIST: SuiteListRead = {
  items: [
    {
      id: "suite-a",
      name: "核心巡检",
      mode: "contract",
      case_count: 14,
      asset_status: "draft",
      updated_at: "2026-04-14T00:00:00Z",
    },
    {
      id: "suite-b",
      name: "工具调用稳定性",
      mode: "contract",
      case_count: 9,
      asset_status: "used",
      updated_at: "2026-04-13T20:00:00Z",
    },
  ],
};

export function SuiteLibraryPage() {
  const { data } = useResource(() => workbenchApi.listSuites(), EMPTY_SUITE_LIST, []);
  const [selectedSuiteId, setSelectedSuiteId] = useState<string | null>(data.items[0]?.id ?? null);

  const selectedSuite =
    data.items.find((item) => item.id === selectedSuiteId) ?? data.items[0] ?? null;

  return (
    <section className="stack">
      <PageHeader
        description="浏览 suite、识别资产状态，并从这里进入编辑、导入和创建 run。"
        eyebrow="测试集"
        title="Suite 列表"
      />

      <WorkbenchTable
        ariaLabel="Suite 列表"
        columns={[
          { key: "name", label: "名称", sticky: true },
          {
            key: "asset_status",
            label: "状态",
            render: (row) => <StatusBadge kind="status" value={row.asset_status} />,
          },
          { key: "updated_at", label: "更新时间" },
          {
            key: "id",
            label: "操作",
            render: (row) => (
              row.id === (selectedSuite?.id ?? data.items[0]?.id) ? (
                <button onClick={() => setSelectedSuiteId(row.id)} type="button">
                  查看详情
                </button>
              ) : (
                <button onClick={() => setSelectedSuiteId(row.id)} type="button">
                  设为当前
                </button>
              )
            ),
          },
        ]}
        rows={data.items}
      />

      <DetailDrawer
        description="右侧抽屉会在后续任务中承接更完整的 suite 摘要与操作。"
        title="Suite 详情"
      >
        <p className="body-muted">当前选中：{selectedSuite?.name ?? "未选择"}</p>
        {selectedSuite ? (
          <a className="shell-cta" href={`/suites/${selectedSuite.id}`}>
            打开完整详情
          </a>
        ) : null}
      </DetailDrawer>
    </section>
  );
}
