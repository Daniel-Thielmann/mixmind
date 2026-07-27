import { redirect } from "next/navigation";
import { getServerSession } from "@/lib/auth";
import { DashboardContent } from "./content";

export default async function DashboardPage() {
  const session = await getServerSession();
  if (!session?.user) redirect("/");
  return <DashboardContent />;
}
