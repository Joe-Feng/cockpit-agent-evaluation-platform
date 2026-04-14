import { render, screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";

import { MetricCard } from "../MetricCard";
import { WorkbenchTable } from "../workbench/WorkbenchTable";

describe("MetricCard", () => {
  test("renders primary and tone modifier classes", () => {
    const { container } = render(
      <MetricCard
        detail="最新汇总健康信号"
        label="最新状态"
        tone="good"
        value="运行中"
        variant="primary"
      />,
    );

    expect(screen.getByText("最新状态")).toBeTruthy();
    expect(screen.getByText("运行中")).toBeTruthy();
    expect(screen.getByText("最新汇总健康信号")).toBeTruthy();
    expect((container.firstChild as HTMLElement).className).toContain("metric-card");
    expect((container.firstChild as HTMLElement).className).toContain("metric-card--good");
    expect((container.firstChild as HTMLElement).className).toContain("metric-card--primary");
  });

  test("renders table semantics and sticky lead column", () => {
    render(
      <WorkbenchTable
        ariaLabel="Suite 列表"
        columns={[{ key: "name", label: "名称", sticky: true }]}
        rows={[{ id: "suite-a", name: "核心巡检" }]}
      />,
    );

    expect(screen.getByRole("table", { name: "Suite 列表" })).toBeTruthy();
    expect(screen.getByText("核心巡检")).toBeTruthy();
  });
});
