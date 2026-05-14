"use client";

import { ReactNode } from "react";

interface MetricCardProps {
  label: string;
  value: string | number;
  icon?: string;
  trend?: number;
  subtext?: string;
}

export default function MetricCard({ label, value, icon, trend, subtext }: MetricCardProps) {
  const trendColor = trend && trend > 0 ? "#22c55e" : trend && trend < 0 ? "#ef4444" : "#71717a";
  const trendIcon = trend && trend > 0 ? "↑" : trend && trend < 0 ? "↓" : "";

  return (
    <div
      style={{
        background: "#18181b",
        border: "1px solid #27272a",
        borderRadius: "12px",
        padding: "1.25rem",
        display: "flex",
        flexDirection: "column",
        gap: "0.5rem",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span style={{ color: "#71717a", fontSize: "0.8125rem", fontWeight: 500 }}>{label}</span>
        {icon && <span style={{ fontSize: "1.25rem" }}>{icon}</span>}
      </div>
      <div style={{ display: "flex", alignItems: "baseline", gap: "0.75rem" }}>
        <span style={{ fontSize: "1.75rem", fontWeight: 700, color: "#fafafa" }}>
          {typeof value === "number" ? value.toLocaleString() : value}
        </span>
        {trend !== undefined && (
          <span style={{ fontSize: "0.8125rem", color: trendColor, fontWeight: 500 }}>
            {trendIcon} {Math.abs(trend).toFixed(1)}%
          </span>
        )}
      </div>
      {subtext && (
        <span style={{ color: "#52525b", fontSize: "0.75rem" }}>{subtext}</span>
      )}
    </div>
  );
}