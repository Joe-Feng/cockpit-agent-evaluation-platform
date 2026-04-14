import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, test } from "vitest";

import App from "../../App";

function renderWorkbenchRoute(path: string) {
  render(
    <MemoryRouter
      future={{ v7_relativeSplatPath: true, v7_startTransition: true }}
      initialEntries={[path]}
    >
      <App />
    </MemoryRouter>,
  );
}

describe("run workspace", () => {
  test("run creation wizard shows four steps and preview summary", async () => {
    renderWorkbenchRoute("/runs/new");

    expect(await screen.findByRole("heading", { name: "创建 Run" })).toBeTruthy();
    expect(screen.getByText("1. 选择测试集")).toBeTruthy();
    expect(screen.getByText("4. 提交前预览")).toBeTruthy();
  });

  test("run list replaces manual run_id lookup as the default entry", async () => {
    renderWorkbenchRoute("/runs");

    expect(await screen.findByRole("table", { name: "Run 列表" })).toBeTruthy();
    expect(screen.getByText("run-001")).toBeTruthy();
  });

  test("run detail shows failures, regression signals, and rerun action", async () => {
    renderWorkbenchRoute("/runs/run-001");

    expect(await screen.findByRole("heading", { name: "Run 详情" })).toBeTruthy();
    expect(screen.getByRole("button", { name: /复跑本次运行/i })).toBeTruthy();
    expect(screen.getByText("失败项")).toBeTruthy();
  });
});
