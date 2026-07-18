"use client";

import { useCallback, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
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
} from "lucide-react";
import { UserAvatar } from "./UserAvatar";
import { PlanBadge } from "./PlanBadge";

export function UserDropdown() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [open, setOpen] = useState(false);

  const handleNavigation = useCallback(
    (path: string) => {
      router.push(path);
      setOpen(false);
    },
    [router]
  );

  if (!user) return null;

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 rounded-full outline-none focus-visible:ring-2 focus-visible:ring-primary/50"
      >
        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
          <UserAvatar name={user.name} image={user.image} />
        </motion.div>
      </button>

      <AnimatePresence>
        {open && (
          <>
            <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -4 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -4 }}
              transition={{ duration: 0.15, ease: "easeOut" }}
              className="absolute right-0 top-full z-50 mt-2 w-60 overflow-hidden rounded-xl border border-border/50 bg-card/90 backdrop-blur-2xl p-1.5 shadow-2xl"
            >
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

              <div className="mx-2 my-1.5 h-px bg-border/50" />

              <div className="px-1.5 py-1 text-xs font-medium text-text-tertiary uppercase tracking-wider">Navigation</div>

              {[
                { label: "Dashboard", icon: LayoutDashboard, path: "/dashboard" },
                { label: "My Analyses", icon: BarChart3, path: "/dashboard/analyses" },
                { label: "History", icon: History, path: "/dashboard/history" },
                { label: "Favorites", icon: Heart, path: "/dashboard/favorites" },
              ].map((item) => (
                <button
                  key={item.path}
                  onClick={() => handleNavigation(item.path)}
                  className="flex w-full cursor-pointer items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-text-secondary outline-none transition-colors hover:bg-card-hover hover:text-text"
                >
                  <item.icon className="h-4 w-4" />
                  {item.label}
                </button>
              ))}

              <div className="mx-2 my-1.5 h-px bg-border/50" />

              {[
                { label: "Settings", icon: Settings, path: "/dashboard/settings" },
                { label: "Billing", icon: CreditCard, path: "/dashboard/billing" },
                { label: "API Keys", icon: Key, path: "/dashboard/api-keys" },
              ].map((item) => (
                <button
                  key={item.path}
                  onClick={() => handleNavigation(item.path)}
                  className="flex w-full cursor-pointer items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-text-secondary outline-none transition-colors hover:bg-card-hover hover:text-text"
                >
                  <item.icon className="h-4 w-4" />
                  {item.label}
                </button>
              ))}

              <div className="mx-2 my-1.5 h-px bg-border/50" />

              <button
                onClick={() => { logout(); setOpen(false); }}
                className="flex w-full cursor-pointer items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-danger outline-none transition-colors hover:bg-danger/10"
              >
                <LogOut className="h-4 w-4" />
                Logout
              </button>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
