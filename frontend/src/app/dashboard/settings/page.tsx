import { redirect } from "next/navigation";
import { getServerSession } from "@/lib/auth";

export default async function SettingsPage() {
  const session = await getServerSession();
  if (!session?.user) redirect("/");
  redirect("/dashboard/settings/integrations");
}
