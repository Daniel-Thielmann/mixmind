"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  LayoutDashboard,
  BarChart3,
  History,
  Heart,
  Settings,
  CreditCard,
  Key,
  LogOut,
  ChevronDown,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { UserAvatar } from "./UserAvatar";
import { PlanBadge } from "./PlanBadge";

const PRIMARY_LINKS = [
  { label: "Dashboard", icon: LayoutDashboard, path: "/dashboard" },
  { label: "My Analyses", icon: BarChart3, path: "/dashboard/analyses" },
  { label: "History", icon: History, path: "/dashboard/history" },
  { label: "Favorites", icon: Heart, path: "/dashboard/favorites" },
];

const SETTINGS_LINKS = [
  { label: "Settings", icon: Settings, path: "/dashboard/settings" },
  { label: "Billing", icon: CreditCard, path: "/dashboard/billing" },
  { label: "API Keys", icon: Key, path: "/dashboard/api-keys" },
];

export function UserDropdown() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;

    const closeOnOutsideClick = (event: PointerEvent) => {
      if (!containerRef.current?.contains(event.target as Node)) setOpen(false);
    };
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };

    document.addEventListener("pointerdown", closeOnOutsideClick);
    document.addEventListener("keydown", closeOnEscape);
    return () => {
      document.removeEventListener("pointerdown", closeOnOutsideClick);
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, [open]);

  const handleNavigation = useCallback(
    (path: string) => {
      setOpen(false);
      router.push(path);
    },
    [router],
  );

  if (!user) return null;

  const renderLinks = (
    links: typeof PRIMARY_LINKS,
  ) => links.map((item) => (
    <button
      key={item.path}
      type="button"
      role="menuitem"
      onClick={() => handleNavigation(item.path)}
      className="flex w-full cursor-pointer items-center gap-2.5 rounded-lg px-3 py-2 text-left text-sm text-text-secondary outline-none transition-colors hover:bg-card-hover hover:text-text focus-visible:bg-card-hover focus-visible:text-text"
    >
      <item.icon className="h-4 w-4" />
      {item.label}
    </button>
  ));

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        aria-label="Open user menu"
        aria-haspopup="menu"
        aria-expanded={open}
        onClick={() => setOpen((current) => !current)}
        className="group flex items-center gap-1.5 rounded-full outline-none focus-visible:ring-2 focus-visible:ring-primary/50"
      >
        <span className="transition-transform group-hover:scale-105">
          <UserAvatar name={user.name} image={user.image} />
        </span>
        <ChevronDown
          className={`h-4 w-4 text-text-tertiary transition-transform duration-200 group-hover:text-text ${
            open ? "rotate-180" : ""
          }`}
        />
      </button>

      {open && (
        <div
          role="menu"
          aria-label="User menu"
          style={{ zIndex: 1000 }}
          className="absolute right-0 top-full mt-3 w-60 overflow-hidden rounded-xl border border-border bg-card p-1.5 text-text shadow-2xl"
        >
          <div className="px-3 py-3">
            <div className="flex items-center gap-3">
              <UserAvatar name={user.name} image={user.image} />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium leading-none text-text">{user.name}</p>
                <p className="mt-1 truncate text-xs text-text-secondary">{user.email}</p>
              </div>
            </div>
            <div className="mt-3 flex items-center gap-2">
              <PlanBadge plan={user.plan} />
              <span className="text-xs text-text-tertiary">
                {user.aiCreditsUsed} / {user.aiCreditsLimit} credits
              </span>
            </div>
          </div>

          <div className="mx-2 my-1.5 h-px bg-border/50" />
          <p className="px-3 py-1.5 text-xs font-medium uppercase tracking-wider text-text-tertiary">
            Navigation
          </p>
          {renderLinks(PRIMARY_LINKS)}

          <div className="mx-2 my-1.5 h-px bg-border/50" />
          {renderLinks(SETTINGS_LINKS)}

          <div className="mx-2 my-1.5 h-px bg-border/50" />
          <button
            type="button"
            role="menuitem"
            onClick={() => {
              setOpen(false);
              void logout();
            }}
            className="flex w-full cursor-pointer items-center gap-2.5 rounded-lg px-3 py-2 text-left text-sm text-danger outline-none transition-colors hover:bg-danger/10 focus-visible:bg-danger/10"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </div>
      )}
    </div>
  );
}
