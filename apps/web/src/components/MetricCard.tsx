import type { Tone } from "../utils/tone";

type MetricCardProps = {
  label: string;
  value: string;
  detail: string;
  tone?: Tone;
  variant?: "primary" | "secondary";
};

export function MetricCard({
  label,
  value,
  detail,
  tone = "neutral",
  variant = "secondary",
}: MetricCardProps) {
  return (
    <article className={`metric-card metric-card--${tone} metric-card--${variant}`}>
      <p className="metric-card__label">{label}</p>
      <strong className="metric-card__value">{value}</strong>
      <p className="metric-card__detail">{detail}</p>
    </article>
  );
}
