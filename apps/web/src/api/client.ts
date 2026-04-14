import type { RunListRead, SuiteListRead, WorkbenchHome } from "./contracts";
import { mockDashboardApi, mockWorkbenchApi } from "./mockData";

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

type RuntimeEnv = {
  DEV?: boolean;
  VITEST?: boolean;
};

function buildUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

export function shouldUseMockDashboardData(env: RuntimeEnv = import.meta.env): boolean {
  return Boolean(env.DEV) && !Boolean(env.VITEST);
}

export async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(buildUrl(path), {
    headers: {
      Accept: "application/json",
    },
  });
  if (!response.ok) {
    throw new Error(`请求失败：${response.status}`);
  }
  return (await response.json()) as T;
}

async function fetchJsonOrMock<T>(path: string, fallback: Promise<T>): Promise<T> {
  try {
    return await fetchJson<T>(path);
  } catch (error) {
    if (
      error instanceof Error &&
      /404|501|Failed to parse URL|fetch is not defined|Failed to fetch/i.test(error.message)
    ) {
      return fallback;
    }
    throw error;
  }
}

const realDashboardApi = {
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

export const dashboardApi = shouldUseMockDashboardData() ? mockDashboardApi : realDashboardApi;

const realWorkbenchApi = {
  getHome(targetId: string) {
    return fetchJsonOrMock<WorkbenchHome>(
      `/api/v1/workbench/home?target_id=${targetId}`,
      mockWorkbenchApi.getHome(targetId),
    );
  },
  listSuites() {
    return fetchJsonOrMock<SuiteListRead>("/api/v1/workbench/suites", mockWorkbenchApi.listSuites());
  },
  listRuns() {
    return fetchJsonOrMock<RunListRead>("/api/v1/workbench/runs", mockWorkbenchApi.listRuns());
  },
};

export const workbenchApi = shouldUseMockDashboardData() ? mockWorkbenchApi : realWorkbenchApi;
