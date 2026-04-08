import { useEffect, useRef } from "react";
import { LineChart } from "echarts/charts";
import { GridComponent, TitleComponent, TooltipComponent } from "echarts/components";
import { init, use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";

import type { TrendPoint } from "../api/client";

use([LineChart, GridComponent, TitleComponent, TooltipComponent, CanvasRenderer]);

type TrendChartProps = {
  title: string;
  series: TrendPoint[];
};

export function TrendChart({ title, series }: TrendChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!containerRef.current) {
      return;
    }

    const chart = init(containerRef.current);
    chart.setOption({
      backgroundColor: "transparent",
      grid: { left: 24, right: 12, top: 24, bottom: 32 },
      title: {
        text: title,
        left: 0,
        textStyle: {
          color: "#f6f2e8",
          fontFamily: "IBM Plex Sans, Segoe UI, sans-serif",
          fontSize: 16,
          fontWeight: 600,
        },
      },
      tooltip: {
        trigger: "axis",
      },
      xAxis: {
        type: "category",
        axisLine: { lineStyle: { color: "rgba(246, 242, 232, 0.2)" } },
        axisLabel: { color: "rgba(246, 242, 232, 0.64)" },
        data: series.map((point) => point.captured_at.slice(11, 19)),
      },
      yAxis: {
        type: "value",
        min: 0,
        max: 1,
        axisLine: { show: false },
        splitLine: { lineStyle: { color: "rgba(246, 242, 232, 0.08)" } },
        axisLabel: { color: "rgba(246, 242, 232, 0.64)" },
      },
      series: [
        {
          type: "line",
          smooth: true,
          symbolSize: 10,
          lineStyle: {
            color: "#f5a65b",
            width: 3,
          },
          areaStyle: {
            color: "rgba(245, 166, 91, 0.18)",
          },
          itemStyle: {
            color: "#f5a65b",
          },
          data: series.map((point) => Number(point.value.toFixed(2))),
        },
      ],
    });

    const handleResize = () => chart.resize();
    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
      chart.dispose();
    };
  }, [series, title]);

  if (series.length === 0) {
    return (
      <section className="panel chart-panel chart-panel--empty">
        <p className="eyebrow">Trend Dashboard</p>
        <h3>{title}</h3>
        <p className="body-muted">No completed runs are available for this scope yet.</p>
      </section>
    );
  }

  return <div className="panel chart-panel" ref={containerRef} />;
}
