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

describe("results risk settings", () => {
  test("results page lets the user inspect case history without remembering run_id", async () => {
    renderWorkbenchRoute("/results");

    expect(await screen.findByRole("heading", { name: "Case 历史" })).toBeTruthy();
    expect(screen.getByRole("textbox", { name: /Case ID/i })).toBeTruthy();
  });

  test("risk center prioritizes regressions and alerts before trend charts", async () => {
    renderWorkbenchRoute("/risks");

    expect(await screen.findByRole("heading", { name: "风险中心" })).toBeTruthy();
    expect(screen.getByText("当前打开的回归")).toBeTruthy();
    expect(screen.getByText("当前打开的告警")).toBeTruthy();
  });

  test("settings page shows environments, target profile, and alert rules", async () => {
    renderWorkbenchRoute("/settings");

    expect(await screen.findByRole("heading", { name: "设置" })).toBeTruthy();
    expect(screen.getByText("Environment 管理")).toBeTruthy();
    expect(screen.getByText("告警规则")).toBeTruthy();
  });
});
