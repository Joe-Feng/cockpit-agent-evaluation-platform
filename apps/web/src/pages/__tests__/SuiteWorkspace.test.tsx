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
});
