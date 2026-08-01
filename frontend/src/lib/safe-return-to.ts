const ALLOWED_RETURN_PATHS = new Set([
  "/dashboard",
  "/analyzer",
  "/dashboard/settings",
  "/dashboard/settings/integrations",
]);

export function safeReturnTo(value: string | null | undefined): string {
  if (!value) return "/dashboard";
  const path = value.split("?", 1)[0];
  return ALLOWED_RETURN_PATHS.has(path) ? value : "/dashboard";
}
