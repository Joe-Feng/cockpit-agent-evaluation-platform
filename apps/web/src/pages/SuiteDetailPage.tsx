import { useParams } from "react-router-dom";

import { PageHeader } from "../components/workbench/PageHeader";

export function SuiteDetailPage() {
  const { suiteId = "" } = useParams();

  return (
    <section className="stack">
      <PageHeader
        description="完整 suite 详情、用例清单与版本操作会在后续任务中逐步补齐。"
        eyebrow="测试集"
        title={`Suite 详情 ${suiteId}`}
      />
    </section>
  );
}
