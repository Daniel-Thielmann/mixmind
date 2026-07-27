import { redirect } from "next/navigation";
import { getServerSession } from "@/lib/auth";
import { SpotifyIntegrationCard } from "@/components/auth/SpotifyIntegrationCard";

export default async function IntegrationsPage() {
  const session = await getServerSession();
  if (!session?.user) redirect("/");
  return (
    <div className="flex-1 pb-12 pt-24">
      <div className="mx-auto max-w-3xl px-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight text-text">
            Integrations
          </h1>
          <p className="mt-1 text-text-secondary">
            Connect your accounts to import music and enhance your analysis.
          </p>
        </div>

        <div className="space-y-4">
          <SpotifyIntegrationCard />
        </div>
      </div>
    </div>
  );
}
