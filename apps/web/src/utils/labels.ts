export function labelForStatus(status: string): string {
  const normalized = status.toLowerCase();

  const statusLabels: Record<string, string> = {
    unknown: "未知",
    succeeded: "成功",
    passed: "通过",
    running: "运行中",
    failed: "失败",
    error: "错误",
    queued: "排队中",
    pending: "等待中",
    healthy: "健康",
    ready: "就绪",
    ok: "正常",
    warning: "预警",
    degraded: "已降级",
    regressing: "回归中",
  };

  return statusLabels[normalized] ?? status;
}

export function labelForSeverity(severity: string): string {
  const normalized = severity.toLowerCase();

  const severityLabels: Record<string, string> = {
    critical: "严重",
    urgent: "紧急",
    high: "高",
    medium: "中",
    low: "低",
    warning: "预警",
    warn: "预警",
    info: "信息",
    sev1: "一级",
    sev2: "二级",
    sev3: "三级",
  };

  return severityLabels[normalized] ?? severity;
}

export function labelForTopology(topology: string): string {
  const normalized = topology.toLowerCase();

  const topologyLabels: Record<string, string> = {
    direct: "直连执行",
    runner: "Runner 执行",
    hybrid: "混合执行",
    unknown: "未知拓扑",
  };

  return topologyLabels[normalized] ?? topology;
}
