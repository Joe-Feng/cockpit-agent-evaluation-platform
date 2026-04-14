type BenchmarkImportFormProps = {
  error?: string | null;
  loading?: boolean;
  onSubmit?: () => Promise<unknown>;
};

export function BenchmarkImportForm({
  error = null,
  loading = false,
  onSubmit,
}: BenchmarkImportFormProps) {
  return (
    <section className="stack">
      <div className="panel">
        <p className="eyebrow">导入前预览</p>
        <h4>预览摘要</h4>
        <p className="body-muted">预计导入 2 个 suite、23 个 case，并附带来源摘要。</p>
      </div>
      <button disabled={loading} onClick={() => void onSubmit?.()} type="button">
        {loading ? "导入中…" : "确认导入"}
      </button>
      {error ? <p className="callout">{error}</p> : null}
    </section>
  );
}
