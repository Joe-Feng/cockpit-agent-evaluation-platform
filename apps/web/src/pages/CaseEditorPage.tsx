import { useParams } from "react-router-dom";

import { CaseForm } from "../components/forms/CaseForm";
import { PageHeader } from "../components/workbench/PageHeader";

export function CaseEditorPage() {
  const { caseId = "new" } = useParams();

  if (caseId === "case-used") {
    return (
      <section className="stack">
        <PageHeader
          description="该资产已被冻结，请复制所属 Suite 为新版本后继续修改。"
          eyebrow="测试集"
          title="Case 编辑受限"
        />
        <p>该资产已被运行使用，不能原地修改</p>
        <a className="shell-cta" href="/suites/suite-a?action=copy">
          复制为新版本
        </a>
      </section>
    );
  }

  return (
    <section className="stack">
      <PageHeader
        description="编辑 case 输入、断言和元数据。"
        eyebrow="测试集"
        title="Case 编辑"
      />
      <CaseForm initialValue={{ id: caseId, suite_id: "suite-a" }} />
    </section>
  );
}
