import { render, screen } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";

const setOption = vi.fn();
const resize = vi.fn();
const dispose = vi.fn();

vi.mock("echarts/core", () => ({
  init: vi.fn(() => ({ setOption, resize, dispose })),
  use: vi.fn(),
}));

vi.mock("echarts/charts", () => ({ LineChart: {} }));
vi.mock("echarts/components", () => ({
  GridComponent: {},
  TitleComponent: {},
  TooltipComponent: {},
}));
vi.mock("echarts/renderers", () => ({ CanvasRenderer: {} }));

import { TrendChart } from "../TrendChart";

describe("TrendChart", () => {
  test("renders the empty state copy when there is no series", () => {
    render(<TrendChart series={[]} title="通过率趋势" />);

    expect(screen.getByRole("heading", { name: "通过率趋势" })).toBeTruthy();
    expect(screen.getByText(/当前范围还没有可展示的完成运行数据/i)).toBeTruthy();
  });

  test("mounts a chart stage when series exists", () => {
    const { container } = render(
      <TrendChart
        title="通过率趋势"
        series={[
          {
            scope_type: "suite",
            scope_id: "cockpit.contract.api",
            metric_id: "pass_rate",
            dimension_key: "env=ci",
            value: 0.92,
            captured_at: "2026-04-09T12:00:00Z",
          },
        ]}
      />,
    );

    expect(container.querySelector(".chart-stage")).toBeTruthy();
    expect(container.querySelector(".chart-panel")).toBeTruthy();
    expect(setOption).toHaveBeenCalled();
  });
});
