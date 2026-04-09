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
    if (!containerRef.current || series.length === 0) {
      return;
    }

    const chart = init(containerRef.current);
    chart.setOption({
      backgroundColor: "transparent",
      grid: { left: 24, right: 12, top: 40, bottom: 24 },
      title: {
        text: title,
        left: 0,
        textStyle: {
          color: "#e8eef7",
          fontFamily:
            "IBM Plex Sans, PingFang SC, Hiragino Sans GB, Microsoft YaHei, Segoe UI, sans-serif",
          fontSize: 16,
          fontWeight: 600,
        },
      },
      tooltip: { trigger: "axis" },
      xAxis: {
        type: "category",
        axisLine: { lineStyle: { color: "rgba(232, 238, 247, 0.18)" } },
        axisLabel: { color: "rgba(232, 238, 247, 0.64)" },
        data: series.map((point) => point.captured_at.slice(11, 19)),
      },
      yAxis: {
        type: "value",
        min: 0,
        max: 1,
        axisLine: { show: false },
        splitLine: { lineStyle: { color: "rgba(232, 238, 247, 0.08)" } },
        axisLabel: { color: "rgba(232, 238, 247, 0.64)" },
      },
      series: [
        {
          type: "line",
          smooth: true,
          symbolSize: 10,
          lineStyle: {
            color: "#61b3ff",
            width: 3,
          },
          areaStyle: {
            color: "rgba(97, 179, 255, 0.16)",
          },
          itemStyle: {
            color: "#61b3ff",
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
        <p className="eyebrow">趋势看板</p>
        <h3>{title}</h3>
        <p className="body-muted">当前范围还没有可展示的完成运行数据。</p>
      </section>
    );
  }

  return (
    <section className="panel chart-stage">
      <div className="chart-panel" ref={containerRef} />
    </section>
  );
}
