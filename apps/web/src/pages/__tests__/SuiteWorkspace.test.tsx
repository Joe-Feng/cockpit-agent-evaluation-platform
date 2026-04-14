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

describe("suite workspace", () => {
  test("workbench home shows quick actions and recent risks", async () => {
    renderWorkbenchRoute("/");

    expect(await screen.findByRole("heading", { name: "Evaluation Workbench" })).toBeTruthy();
    expect(screen.getByRole("link", { name: /导入测试包/i })).toBeTruthy();
    expect(screen.getByRole("link", { name: /新建 Run/i })).toBeTruthy();
  });

  test("suite library shows list-detail workflow with right-side drawer", async () => {
    renderWorkbenchRoute("/suites");

    expect(await screen.findByRole("table", { name: "Suite 列表" })).toBeTruthy();
    expect(screen.getByText("核心巡检")).toBeTruthy();
    expect(screen.getByRole("button", { name: /查看详情/i })).toBeTruthy();
  });

  test("benchmark import previews suite and case counts before submit", async () => {
    renderWorkbenchRoute("/imports/benchmark");

    expect(await screen.findByRole("heading", { name: "导入 Benchmark Package" })).toBeTruthy();
    expect(screen.getByText("导入前预览")).toBeTruthy();
  });

  test("used case editor switches to copy-new-version guidance", async () => {
    renderWorkbenchRoute("/cases/case-used/edit");

    expect(await screen.findByText("该资产已被运行使用，不能原地修改")).toBeTruthy();
    expect(screen.getByRole("link", { name: /复制为新版本/i })).toBeTruthy();
  });
});
