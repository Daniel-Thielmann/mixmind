"use client";

import { useState } from "react";

interface TabsProps {
  tabs: { key: string; label: string }[];
  defaultKey?: string;
  children: (activeKey: string) => React.ReactNode;
}

export function Tabs({ tabs, defaultKey, children }: TabsProps) {
  const [active, setActive] = useState(defaultKey || tabs[0]?.key || "");

  return (
    <div>
      <div className="mb-4 flex gap-1 rounded-xl border border-zinc-800 bg-zinc-900/40 p-1">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            type="button"
            onClick={() => setActive(tab.key)}
            className={`flex-1 rounded-lg px-3 py-2 text-xs font-semibold uppercase tracking-wider transition-all duration-200 ${
              active === tab.key
                ? "bg-zinc-800 text-text shadow-sm"
                : "text-text-secondary/60 hover:text-text/80"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
      {children(active)}
    </div>
  );
}
