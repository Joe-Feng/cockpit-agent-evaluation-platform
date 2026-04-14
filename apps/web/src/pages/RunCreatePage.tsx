import { PageHeader } from "../components/workbench/PageHeader";
import { RunWizard } from "../components/forms/RunWizard";

export function RunCreatePage() {
  return (
    <section className="stack">
      <PageHeader
        description="先选择测试集，再选择环境和执行方式，最后核对范围与任务规模。"
        eyebrow="运行"
        title="创建 Run"
      />
      <RunWizard
        steps={["选择测试集", "选择环境", "选择执行方式", "提交前预览"]}
      />
    </section>
  );
}
