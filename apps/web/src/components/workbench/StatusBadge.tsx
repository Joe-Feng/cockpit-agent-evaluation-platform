import { labelForSeverity, labelForStatus } from "../../utils/labels";
import { toneForSeverity, toneForStatus } from "../../utils/tone";

type StatusBadgeProps = {
  kind: "status" | "severity";
  value: string;
};

export function StatusBadge({ kind, value }: StatusBadgeProps) {
  const tone = kind === "status" ? toneForStatus(value) : toneForSeverity(value);
  const label = kind === "status" ? labelForStatus(value) : labelForSeverity(value);

  return <span className={`status-pill status-pill--${tone}`}>{label}</span>;
}
