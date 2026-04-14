type CaseFormProps = {
  initialValue: {
    id: string;
    suite_id: string;
  };
};

export function CaseForm({ initialValue }: CaseFormProps) {
  return (
    <section className="stack">
      <div className="input-panel">
        <label className="input-panel__label" htmlFor="case-id">
          Case ID
        </label>
        <input defaultValue={initialValue.id} id="case-id" />
      </div>
      <div className="input-panel">
        <label className="input-panel__label" htmlFor="suite-id">
          Suite ID
        </label>
        <input defaultValue={initialValue.suite_id} id="suite-id" />
      </div>
    </section>
  );
}
