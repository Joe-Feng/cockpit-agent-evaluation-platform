import { BenchmarkImportForm } from "../components/forms/BenchmarkImportForm";
import { PageHeader } from "../components/workbench/PageHeader";
import { useAsyncAction } from "../hooks/useAsyncAction";

async function submitImportPreview() {
  return { imported: true };
}

export function BenchmarkImportPage() {
  const { loading, error, run } = useAsyncAction(submitImportPreview);

  return (
    <section className="stack">
      <PageHeader
        description="上传 benchmark 导出包，先预览 suite / case 摘要，再确认导入。"
        eyebrow="测试集"
        title="导入 Benchmark Package"
      />
      <BenchmarkImportForm error={error} loading={loading} onSubmit={run} />
    </section>
  );
}
