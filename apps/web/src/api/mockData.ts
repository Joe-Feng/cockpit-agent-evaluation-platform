import type {
  QuickAction,
  RunListRead,
  SuiteListRead,
  SummaryCard,
  WorkbenchHome,
} from "./contracts";
import type {
  AlertEvent,
  CaseExplorer,
  RegressionSignal,
  RunCenter,
  TargetOverview,
  TrendDashboard,
} from "./client";

const mockOverviewRuns = [
  {
    run_id: "run-240409-01",
    status: "succeeded",
    env_id: "预发环境",
    suite_ids: ["核心巡检", "接口回归"],
    task_count: 48,
    passed_count: 48,
  },
  {
    run_id: "run-240409-02",
    status: "running",
    env_id: "生产影子",
    suite_ids: ["多轮对话", "知识检索", "稳定性回归"],
    task_count: 52,
    passed_count: 39,
  },
  {
    run_id: "run-240408-17",
    status: "failed",
    env_id: "生产环境",
    suite_ids: ["工具调用回放"],
    task_count: 24,
    passed_count: 17,
  },
];

const mockOpenAlerts: AlertEvent[] = [
  {
    run_id: "run-240409-02",
    target_id: "驾驶舱智能体集群",
    metric_id: "检索成功率",
    severity: "high",
    should_fire: true,
  },
  {
    run_id: "run-240408-17",
    target_id: "驾驶舱智能体集群",
    metric_id: "工具调用稳定性",
    severity: "medium",
    should_fire: true,
  },
];

const mockRegressionSignals: RegressionSignal[] = [
  {
    run_id: "run-240409-02",
    target_id: "驾驶舱智能体集群",
    env_id: "生产影子",
    metric_id: "检索成功率",
    severity: "high",
    is_regression: true,
    captured_at: "2026-04-09T12:18:00Z",
  },
  {
    run_id: "run-240409-02",
    target_id: "驾驶舱智能体集群",
    env_id: "生产影子",
    metric_id: "回答延迟",
    severity: "warning",
    is_regression: true,
    captured_at: "2026-04-09T12:19:00Z",
  },
  {
    run_id: "run-240408-17",
    target_id: "驾驶舱智能体集群",
    env_id: "生产环境",
    metric_id: "工具调用成功率",
    severity: "critical",
    is_regression: true,
    captured_at: "2026-04-08T23:14:00Z",
  },
];

const mockTargetOverview: TargetOverview = {
  target_id: "驾驶舱智能体集群",
  latest_status: "running",
  latest_runs: mockOverviewRuns,
  open_alerts: mockOpenAlerts,
};

const mockRunCenterBase: RunCenter = {
  run_id: "run-002",
  status: "running",
  execution_topology: "direct",
  suite_ids: ["核心巡检", "多轮对话", "稳定性回归"],
  normalized_results: [
    { case_id: "case-001", result: "passed" },
    { case_id: "case-002", result: "failed" },
  ],
  regression_signals: mockRegressionSignals.slice(0, 2),
};

const mockCaseExplorerBase: CaseExplorer = {
  case_id: "health-001",
  latest_status: "passed",
  history: [
    {
      run_id: "run-240409-02",
      target_id: "驾驶舱智能体集群",
      env_id: "生产影子",
      status: "running",
      created_at: "2026-04-09T12:18:00Z",
    },
    {
      run_id: "run-240409-01",
      target_id: "驾驶舱智能体集群",
      env_id: "预发环境",
      status: "passed",
      created_at: "2026-04-09T09:42:00Z",
    },
    {
      run_id: "run-240408-17",
      target_id: "驾驶舱智能体集群",
      env_id: "生产环境",
      status: "failed",
      created_at: "2026-04-08T23:14:00Z",
    },
  ],
};

const mockTrendDashboardBase: TrendDashboard = {
  scope_id: "cockpit.contract.api",
  series: [
    {
      scope_type: "suite",
      scope_id: "cockpit.contract.api",
      metric_id: "pass_rate",
      dimension_key: "环境：生产影子",
      value: 0.91,
      captured_at: "2026-04-09T08:00:00Z",
    },
    {
      scope_type: "suite",
      scope_id: "cockpit.contract.api",
      metric_id: "pass_rate",
      dimension_key: "环境：生产影子",
      value: 0.88,
      captured_at: "2026-04-09T09:00:00Z",
    },
    {
      scope_type: "suite",
      scope_id: "cockpit.contract.api",
      metric_id: "pass_rate",
      dimension_key: "环境：生产影子",
      value: 0.86,
      captured_at: "2026-04-09T10:00:00Z",
    },
    {
      scope_type: "suite",
      scope_id: "cockpit.contract.api",
      metric_id: "pass_rate",
      dimension_key: "环境：生产影子",
      value: 0.9,
      captured_at: "2026-04-09T11:00:00Z",
    },
    {
      scope_type: "suite",
      scope_id: "cockpit.contract.api",
      metric_id: "pass_rate",
      dimension_key: "环境：生产影子",
      value: 0.93,
      captured_at: "2026-04-09T12:00:00Z",
    },
  ],
};

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

export const mockDashboardApi = {
  async getTargetOverview(targetId: string): Promise<TargetOverview> {
    return {
      ...clone(mockTargetOverview),
      target_id: targetId === "cockpit_agents" ? "驾驶舱智能体集群" : targetId,
    };
  },
  async getRunCenter(runId: string): Promise<RunCenter> {
    return {
      ...clone(mockRunCenterBase),
      run_id: runId,
    };
  },
  async getCaseExplorer(caseId: string): Promise<CaseExplorer> {
    return {
      ...clone(mockCaseExplorerBase),
      case_id: caseId,
    };
  },
  async getTrendDashboard(scopeId: string): Promise<TrendDashboard> {
    return {
      ...clone(mockTrendDashboardBase),
      scope_id: scopeId,
    };
  },
  async getRegressionCenter(): Promise<{ items: RegressionSignal[] }> {
    return {
      items: clone(mockRegressionSignals),
    };
  },
  async getAlertEvents(): Promise<{ items: AlertEvent[] }> {
    return {
      items: clone(mockOpenAlerts),
    };
  },
};

const mockWorkbenchSummaryCards: SummaryCard[] = [
  {
    id: "suite-count",
    label: "测试集",
    value: "12",
    detail: "已接入的 suite 数量",
    tone: "neutral",
  },
  {
    id: "run-count",
    label: "近次运行",
    value: "3",
    detail: "最近进入工作台视图的运行",
    tone: "good",
  },
  {
    id: "risk-count",
    label: "风险条目",
    value: "2",
    detail: "需要人工处理的信号",
    tone: "warm",
  },
];

const mockQuickActions: QuickAction[] = [
  { label: "导入 Benchmark", href: "/imports/benchmark", tone: "primary" },
  { label: "查看测试集", href: "/suites", tone: "neutral" },
  { label: "创建 Run", href: "/runs/new", tone: "neutral" },
];

const mockSuiteList: SuiteListRead = {
  items: [
    {
      id: "suite-a",
      name: "核心巡检",
      mode: "contract",
      case_count: 14,
      asset_status: "draft",
      updated_at: "2026-04-14T00:00:00Z",
    },
    {
      id: "suite-b",
      name: "工具调用稳定性",
      mode: "contract",
      case_count: 9,
      asset_status: "used",
      updated_at: "2026-04-13T20:00:00Z",
    },
  ],
};

const mockRunList: RunListRead = {
  items: [
    {
      run_id: "run-240409-02",
      status: "running",
      target_id: "cockpit_agents",
      env_id: "生产影子",
      suite_ids: ["核心巡检", "稳定性回归"],
      task_count: 52,
      passed_count: 39,
      created_at: "2026-04-09T12:18:00Z",
    },
    {
      run_id: "run-240409-01",
      status: "succeeded",
      target_id: "cockpit_agents",
      env_id: "预发环境",
      suite_ids: ["接口回归"],
      task_count: 48,
      passed_count: 48,
      created_at: "2026-04-09T09:42:00Z",
    },
  ],
};

export const mockWorkbenchApi = {
  async getHome(targetId: string): Promise<WorkbenchHome> {
    return {
      target_id: targetId,
      summary_cards: clone(mockWorkbenchSummaryCards),
      quick_actions: clone(mockQuickActions),
      recent_runs: clone(mockRunList.items),
      risk_items: clone(mockOpenAlerts),
    };
  },
  async listSuites(): Promise<SuiteListRead> {
    return clone(mockSuiteList);
  },
  async listRuns(): Promise<RunListRead> {
    return clone(mockRunList);
  },
};
