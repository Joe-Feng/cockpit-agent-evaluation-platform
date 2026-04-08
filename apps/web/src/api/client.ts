export type RunSummary = {
  run_id: string;
  status: string;
  env_id: string;
  suite_ids: string[];
  task_count: number;
  passed_count: number;
};

export type TargetOverview = {
  target_id: string;
  latest_status: string;
  latest_runs: RunSummary[];
  open_alerts: AlertEvent[];
};

export type RunCenter = {
  run_id: string;
  status: string;
  execution_topology: string;
  suite_ids: string[];
  normalized_results: Array<Record<string, unknown>>;
  regression_signals: RegressionSignal[];
};

export type CaseExplorer = {
  case_id: string;
  latest_status: string;
  history: Array<{
    run_id: string;
    target_id: string;
    env_id: string;
    status: string;
    created_at: string;
  }>;
};

export type TrendPoint = {
  scope_type: string;
  scope_id: string;
  metric_id: string;
  dimension_key: string;
  value: number;
  captured_at: string;
};

export type TrendDashboard = {
  scope_id: string;
  series: TrendPoint[];
};

export type RegressionSignal = {
  run_id: string;
  target_id?: string;
  env_id?: string;
  metric_id: string;
  severity: string;
  is_regression?: boolean;
  captured_at?: string;
};

export type AlertEvent = {
  run_id: string;
  target_id?: string;
  metric_id: string;
  severity: string;
  should_fire: boolean;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

function buildUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

export async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(buildUrl(path), {
    headers: {
      Accept: "application/json",
    },
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return (await response.json()) as T;
}

export const dashboardApi = {
  getTargetOverview(targetId: string) {
    return fetchJson<TargetOverview>(`/api/v1/dashboard/targets/${targetId}`);
  },
  getRunCenter(runId: string) {
    return fetchJson<RunCenter>(`/api/v1/dashboard/runs/${runId}`);
  },
  getCaseExplorer(caseId: string) {
    return fetchJson<CaseExplorer>(`/api/v1/dashboard/cases/${caseId}`);
  },
  getTrendDashboard(scopeId: string) {
    return fetchJson<TrendDashboard>(`/api/v1/dashboard/trends/${scopeId}`);
  },
  getRegressionCenter() {
    return fetchJson<{ items: RegressionSignal[] }>("/api/v1/dashboard/regressions");
  },
  getAlertEvents() {
    return fetchJson<{ items: AlertEvent[] }>("/api/v1/alerts/events");
  },
};
