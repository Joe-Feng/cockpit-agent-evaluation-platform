type SuiteFormProps = {
  initialValue: {
    id: string;
    name: string;
  };
};

export function SuiteForm({ initialValue }: SuiteFormProps) {
  return (
    <section className="stack">
      <div className="input-panel">
        <label className="input-panel__label" htmlFor="suite-id">
          Suite ID
        </label>
        <input defaultValue={initialValue.id} id="suite-id" />
      </div>
      <div className="input-panel">
        <label className="input-panel__label" htmlFor="suite-name">
          Suite 名称
        </label>
        <input defaultValue={initialValue.name} id="suite-name" />
      </div>
    </section>
  );
}
