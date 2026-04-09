import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";

import App from "../../App";

const mockFetch = vi.fn(async (input: RequestInfo | URL) => {
  const url = typeof input === "string" ? input : input.toString();

  if (url.includes("/api/v1/dashboard/targets/")) {
    return {
      ok: true,
      json: async () => ({
        target_id: "cockpit_agents",
        latest_status: "running",
        latest_runs: [],
        open_alerts: [],
      }),
    };
  }

  if (url.includes("/api/v1/dashboard/runs/")) {
    return {
      ok: true,
      json: async () => ({
        run_id: "run-002",
        status: "succeeded",
        execution_topology: "direct",
        suite_ids: [],
        normalized_results: [],
        regression_signals: [],
      }),
    };
  }

  if (url.includes("/api/v1/dashboard/cases/")) {
    return {
      ok: true,
      json: async () => ({
        case_id: "health-001",
        latest_status: "passed",
        history: [],
      }),
    };
  }

  if (url.includes("/api/v1/dashboard/trends/")) {
    return {
      ok: true,
      json: async () => ({
        scope_id: "cockpit.contract.api",
        series: [],
      }),
    };
  }

  if (url.includes("/api/v1/dashboard/regressions")) {
    return {
      ok: true,
      json: async () => ({ items: [] }),
    };
  }

  if (url.includes("/api/v1/alerts/events")) {
    return {
      ok: true,
      json: async () => ({ items: [] }),
    };
  }

  throw new Error(`Unhandled request: ${url}`);
});

beforeEach(() => {
  vi.stubGlobal("fetch", mockFetch);
});

afterEach(() => {
  vi.unstubAllGlobals();
  mockFetch.mockClear();
});

async function renderRoute(path: string) {
  render(
    <MemoryRouter
      future={{ v7_relativeSplatPath: true, v7_startTransition: true }}
      initialEntries={[path]}
    >
      <App />
    </MemoryRouter>,
  );

  await waitFor(() => expect(mockFetch).toHaveBeenCalled());
}

describe("dashboard shell", () => {
  test("renders chinese cockpit navigation and masthead on overview", async () => {
    await renderRoute("/");

    expect(screen.getByRole("heading", { name: "治理驾驶舱" })).toBeTruthy();
    expect(screen.queryByText("Phase 3")).toBeNull();
    expect(screen.getByRole("navigation", { name: "主导航" })).toBeTruthy();
    expect(screen.getByText("运行态势总览")).toBeTruthy();
    expect(screen.getByRole("heading", { name: "目标健康、漂移与回归" })).toBeTruthy();
    expect(screen.getByRole("link", { name: /目标总览/i }).getAttribute("aria-current")).toBe(
      "page",
    );
  });

  test("renders run center as a chinese query workbench", async () => {
    await renderRoute("/runs");

    expect(screen.getByRole("heading", { name: /查看单次运行报告/i })).toBeTruthy();
    expect(screen.getByText("运行查询")).toBeTruthy();
    expect((screen.getByRole("textbox", { name: /运行 ID/i }) as HTMLInputElement).value).toBe(
      "run-002",
    );
    expect(screen.getByRole("heading", { name: "套件清单" })).toBeTruthy();
    expect(screen.getByRole("heading", { name: "回归信号" })).toBeTruthy();
  });

  test("keeps the chinese run workbench visible when the lookup request fails", async () => {
    mockFetch.mockImplementationOnce(async () => {
      throw new Error("请求失败：503");
    });

    await renderRoute("/runs");

    await waitFor(() => expect(screen.getByText("请求失败：503")).toBeTruthy());
    expect(screen.getByText("运行查询")).toBeTruthy();
    expect((screen.getByRole("textbox", { name: /运行 ID/i }) as HTMLInputElement).value).toBe(
      "run-002",
    );
  });

  test("renders case explorer as a chinese query workbench", async () => {
    await renderRoute("/cases");

    expect(screen.getByRole("heading", { name: /回看单个用例的执行轨迹/i })).toBeTruthy();
    expect(screen.getByText("用例查询")).toBeTruthy();
    expect((screen.getByRole("textbox", { name: /用例 ID/i }) as HTMLInputElement).value).toBe(
      "health-001",
    );
    expect(screen.getByRole("heading", { name: /health-001 的回放窗口/i })).toBeTruthy();
  });

  test("renders the chinese trend empty state on /trends", async () => {
    await renderRoute("/trends");

    expect(screen.getByRole("heading", { name: "通过率趋势" })).toBeTruthy();
    expect(screen.getByText(/当前范围还没有可展示的完成运行数据/i)).toBeTruthy();
  });

  test("renders the regression page as a chinese risk-first dashboard", async () => {
    await renderRoute("/regressions");

    expect(screen.getByText("风险态势")).toBeTruthy();
    expect(screen.getByText("回归信号")).toBeTruthy();
    expect(screen.getByText("告警事件")).toBeTruthy();
    expect(screen.getByRole("heading", { name: "回归队列" })).toBeTruthy();
    expect(screen.getByRole("heading", { name: "告警流" })).toBeTruthy();
  });
});
