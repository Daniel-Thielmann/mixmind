"use client";

import { Shield, ShieldAlert, ShieldX } from "lucide-react";

interface RiskBadgeProps {
  level: string;
}

export function RiskBadge({ level }: RiskBadgeProps) {
  const low = level.toLowerCase() === "low";
  const high = level.toLowerCase() === "high";

  const color = low
    ? "border-success/30 bg-success/10 text-success"
    : high
      ? "border-danger/30 bg-danger/10 text-danger"
      : "border-yellow-400/30 bg-yellow-400/10 text-yellow-400";

  const Icon = low ? Shield : high ? ShieldX : ShieldAlert;

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-bold uppercase tracking-wider ${color}`}
    >
      <Icon className="h-3.5 w-3.5" />
      {level}
    </span>
  );
}
