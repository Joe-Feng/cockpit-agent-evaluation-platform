export type Tone = "neutral" | "good" | "warm" | "danger";

export function toneForStatus(status: string): Tone {
  const normalized = status.toLowerCase();

  if (["succeeded", "passed", "healthy", "ready", "ok"].includes(normalized)) {
    return "good";
  }

  if (["used"].includes(normalized)) {
    return "warm";
  }

  if (["draft"].includes(normalized)) {
    return "neutral";
  }

  if (["failed", "error", "critical", "regressing", "superseded"].includes(normalized)) {
    return "danger";
  }

  if (["running", "pending", "queued", "warning", "degraded"].includes(normalized)) {
    return "warm";
  }

  if (["中", "预警"].includes(normalized)) {
    return "warm";
  }

  return "neutral";
}

export function toneForSeverity(severity: string): Tone {
  const normalized = severity.toLowerCase();

  if (["critical", "high", "urgent", "sev1", "sev2"].includes(normalized)) {
    return "danger";
  }

  if (["medium", "warning", "warn", "sev3"].includes(normalized)) {
    return "warm";
  }

  if (["高", "严重", "紧急", "一级", "二级"].includes(normalized)) {
    return "danger";
  }

  if (["中", "预警", "三级"].includes(normalized)) {
    return "warm";
  }

  return "neutral";
}
