"use client";

import React from "react";
import { SlideChart } from "@/types/deck";

interface SlideChartVisualizerProps {
  chart: SlideChart;
}

export function SlideChartVisualizer({ chart }: SlideChartVisualizerProps) {
  if (chart.chart_type === "pie") {
    // Calculate SVG donut slice angles
    const total = chart.data.reduce((sum, item) => sum + item.value, 0) || 100;
    let cumulativePercent = 0;

    const slices = chart.data.map((item, idx) => {
      const percent = (item.value / total) * 100;
      const startPercent = cumulativePercent;
      cumulativePercent += percent;

      // Calculate strokeDasharray and strokeDashoffset for SVG circle donut
      const circumference = 2 * Math.PI * 40; // r=40
      const strokeDasharray = `${(percent / 100) * circumference} ${circumference}`;
      const strokeDashoffset = -((startPercent / 100) * circumference);

      // Hallmark curated monochrome / warm tones
      const defaultColors = [
        "#18181b", // Charcoal/Primary
        "#c2410c", // Terracotta
        "#15803d", // Emerald
        "#b45309", // Amber
        "#be123c", // Rose
        "#71717a", // Stone Grey
      ];

      const color = item.color || defaultColors[idx % defaultColors.length];

      return {
        ...item,
        percent: Math.round(percent),
        strokeDasharray,
        strokeDashoffset,
        color,
      };
    });

    return (
      <div className="rounded-xl border border-[#e4decf] bg-[#f9f7f2] p-3 flex flex-col justify-between">
        <div className="flex items-center justify-between border-b border-[#e4decf]/70 pb-1.5 mb-2">
          <span className="text-[10px] font-mono font-semibold uppercase tracking-wider text-[#18181b]">
            {chart.title}
          </span>
          <span className="text-[9px] font-mono text-[#71717a]">
            ALLOCATION
          </span>
        </div>

        <div className="flex items-center justify-between gap-3">
          {/* Donut Graphic */}
          <div className="relative w-20 h-20 flex-shrink-0 flex items-center justify-center">
            <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
              <circle
                cx="50"
                cy="50"
                r="40"
                fill="transparent"
                stroke="#e4decf"
                strokeWidth="14"
              />
              {slices.map((slice, i) => (
                <circle
                  key={i}
                  cx="50"
                  cy="50"
                  r="40"
                  fill="transparent"
                  stroke={slice.color}
                  strokeWidth="14"
                  strokeDasharray={slice.strokeDasharray}
                  strokeDashoffset={slice.strokeDashoffset}
                  className="transition-all duration-500 ease-out"
                />
              ))}
            </svg>
            <div className="absolute text-center">
              <span className="text-[11px] font-mono font-bold text-[#18181b]">
                100%
              </span>
            </div>
          </div>

          {/* Key / Legend */}
          <div className="flex-1 space-y-1.5 overflow-hidden">
            {slices.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between text-xs font-mono">
                <div className="flex items-center space-x-2 truncate">
                  <span
                    className="w-2 h-2 rounded-sm flex-shrink-0"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-[#3f3f46] truncate text-[11px]">
                    {item.label}
                  </span>
                </div>
                <span className="text-[#18181b] font-semibold tabular-nums ml-2">
                  {item.percentage !== undefined ? `${item.percentage}%` : `${item.value}%`}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Bar Chart Layout
  const maxValue = Math.max(...chart.data.map((d) => d.value), 1);

  return (
    <div className="rounded-xl border border-[#e4decf] bg-[#f9f7f2] p-3 flex flex-col justify-between">
      <div className="flex items-center justify-between border-b border-[#e4decf]/70 pb-1.5 mb-2">
        <span className="text-[10px] font-mono font-semibold uppercase tracking-wider text-[#18181b]">
          {chart.title}
        </span>
        <span className="text-[9px] font-mono text-[#71717a]">
          PROJECTION
        </span>
      </div>

      <div className="space-y-2 pt-0.5">
        {chart.data.map((d, idx) => {
          const widthPercent = Math.round((d.value / maxValue) * 100);
          return (
            <div key={idx} className="space-y-1">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-[#3f3f46] text-[11px]">{d.label}</span>
                <span className="text-[#18181b] font-bold tabular-nums">
                  {d.percentage !== undefined ? `${d.percentage}%` : d.value}
                </span>
              </div>
              <div className="w-full h-2 rounded-full bg-[#e4decf]/60 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500 ease-out"
                  style={{
                    width: `${widthPercent}%`,
                    backgroundColor: d.color || (idx === 0 ? "#18181b" : "#c2410c"),
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
