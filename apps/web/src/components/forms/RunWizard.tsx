type RunWizardProps = {
  steps: string[];
};

export function RunWizard({ steps }: RunWizardProps) {
  return (
    <section className="stack">
      {steps.map((step, index) => (
        <div className="panel" key={step}>
          <strong>
            {index + 1}. {step}
          </strong>
        </div>
      ))}
    </section>
  );
}
