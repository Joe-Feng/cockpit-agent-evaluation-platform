export type AssetStatus = "draft" | "used" | "superseded";
export type RunStatus = "queued" | "running" | "succeeded" | "failed" | "unknown";
export type RiskSeverity = "info" | "warning" | "critical";
export type ToneName = "neutral" | "good" | "warm" | "danger";

export type SummaryCard = {
  id: string;
  label: string;
  value: string;
  detail: string;
  tone: ToneName;
};

export type QuickAction = {
  label: string;
  href: string;
  tone: "primary" | "neutral" | "warning";
};

export type RecentRunItem = {
  run_id: string;
  status: RunStatus;
  target_id: string;
  env_id: string;
  suite_ids: string[];
  task_count: number;
  passed_count: number;
  created_at: string;
};

export type WorkbenchHome = {
  target_id: string;
  summary_cards: SummaryCard[];
  quick_actions: QuickAction[];
  recent_runs: RecentRunItem[];
  risk_items: Array<{
    run_id: string;
    metric_id: string;
    severity: string;
    should_fire?: boolean;
    captured_at?: string;
  }>;
};

export type SuiteListItem = {
  id: string;
  name: string;
  mode: string;
  case_count: number;
  asset_status: AssetStatus;
  updated_at: string;
};

export type SuiteListRead = {
  items: SuiteListItem[];
};

export type RunListRead = {
  items: RecentRunItem[];
};
