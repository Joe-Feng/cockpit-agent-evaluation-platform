import { afterEach, describe, expect, test, vi } from "vitest";

import { shouldUseMockDashboardData, workbenchApi } from "../client";
import { mockDashboardApi } from "../mockData";

describe("shouldUseMockDashboardData", () => {
  test("enables mock data in dev but keeps tests and production on real requests", () => {
    expect(shouldUseMockDashboardData({ DEV: true, VITEST: false })).toBe(true);
    expect(shouldUseMockDashboardData({ DEV: true, VITEST: true })).toBe(false);
    expect(shouldUseMockDashboardData({ DEV: false, VITEST: false })).toBe(false);
  });
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("workbenchApi", () => {
  test("falls back to mock previews only for missing read models", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: false,
        status: 404,
      })),
    );

    const home = await workbenchApi.getHome("cockpit_agents");
    const suites = await workbenchApi.listSuites();

    expect(home.quick_actions[0].href).toBe("/imports/benchmark");
    expect(suites.items[0].asset_status).toBe("draft");
  });
});

describe("mockDashboardApi", () => {
  test("returns populated preview data for the cockpit pages", async () => {
    const overview = await mockDashboardApi.getTargetOverview("cockpit_agents");
    const runCenter = await mockDashboardApi.getRunCenter("run-002");
    const caseExplorer = await mockDashboardApi.getCaseExplorer("health-001");
    const trendDashboard = await mockDashboardApi.getTrendDashboard("cockpit.contract.api");
    const regressionCenter = await mockDashboardApi.getRegressionCenter();
    const alerts = await mockDashboardApi.getAlertEvents();

    expect(overview.latest_runs.length).toBeGreaterThan(0);
    expect(overview.open_alerts.length).toBeGreaterThan(0);
    expect(runCenter.suite_ids.length).toBeGreaterThan(0);
    expect(runCenter.regression_signals.length).toBeGreaterThan(0);
    expect(caseExplorer.history.length).toBeGreaterThan(0);
    expect(trendDashboard.series.length).toBeGreaterThan(0);
    expect(regressionCenter.items.length).toBeGreaterThan(0);
    expect(alerts.items.length).toBeGreaterThan(0);
  });
});
