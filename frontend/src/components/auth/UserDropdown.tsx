"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
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
import { UserAvatar } from "./UserAvatar";
import { PlanBadge } from "./PlanBadge";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";

export function UserDropdown() {
  const { user, logout } = useAuth();
  const router = useRouter();

  const handleNavigation = useCallback(
    (path: string) => {
      router.push(path);
    },
    [router]
  );

  if (!user) return null;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
      <button type="button" aria-label="Open user menu"
        className="group flex items-center gap-1.5 rounded-full outline-none focus-visible:ring-2 focus-visible:ring-primary/50"
      >
        <span className="transition-transform group-hover:scale-105">
          <UserAvatar name={user.name} image={user.image} />
        </span>
        <span className="text-text-tertiary transition-colors group-hover:text-text group-data-[state=open]:rotate-180">
          <ChevronDown className="h-4 w-4" />
        </span>
      </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" side="bottom" sideOffset={10} className="w-60">
              <div className="px-3 py-3">
                <div className="flex items-center gap-3">
                  <UserAvatar name={user.name} image={user.image} />
                  <div className="flex flex-col gap-0.5">
                    <p className="text-sm font-medium text-text leading-none">{user.name}</p>
                    <p className="text-xs text-text-secondary truncate max-w-[10rem]">{user.email}</p>
                  </div>
                </div>
                <div className="mt-3 flex items-center gap-2">
                  <PlanBadge plan={user.plan} />
                  <span className="text-xs text-text-tertiary">
                    {user.aiCreditsUsed} / {user.aiCreditsLimit} credits
                  </span>
                </div>
              </div>

              <DropdownMenuSeparator />
              <DropdownMenuLabel>Navigation</DropdownMenuLabel>

              {[
                { label: "Dashboard", icon: LayoutDashboard, path: "/dashboard" },
                { label: "My Analyses", icon: BarChart3, path: "/dashboard/analyses" },
                { label: "History", icon: History, path: "/dashboard/history" },
                { label: "Favorites", icon: Heart, path: "/dashboard/favorites" },
              ].map((item) => (
                <DropdownMenuItem
                  key={item.path}
                  onSelect={() => handleNavigation(item.path)}
                >
                  <item.icon className="h-4 w-4" />
                  {item.label}
                </DropdownMenuItem>
              ))}

              <DropdownMenuSeparator />

              {[
                { label: "Settings", icon: Settings, path: "/dashboard/settings" },
                { label: "Billing", icon: CreditCard, path: "/dashboard/billing" },
                { label: "API Keys", icon: Key, path: "/dashboard/api-keys" },
              ].map((item) => (
                <DropdownMenuItem
                  key={item.path}
                  onSelect={() => handleNavigation(item.path)}
                >
                  <item.icon className="h-4 w-4" />
                  {item.label}
                </DropdownMenuItem>
              ))}

              <DropdownMenuSeparator />

              <DropdownMenuItem
                onSelect={() => void logout()}
                className="text-destructive focus-visible:bg-destructive/10 focus-visible:text-destructive"
              >
                <LogOut className="h-4 w-4" />
                Logout
              </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
