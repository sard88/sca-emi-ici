"use client";

import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { DashboardGrid } from "./DashboardGrid";
import { canAccessProfile, dashboardProfiles } from "@/lib/dashboard";
import { useAuth } from "@/lib/auth";

export function ProfilePanel({ profileKey }: { profileKey: keyof typeof dashboardProfiles }) {
  const { user } = useAuth();
  const profile = dashboardProfiles[profileKey];

  return (
    <AppShell showRightPanel>
      {user && !canAccessProfile(user, profile) ? (
        <ErrorMessage message="No tienes permisos para visualizar esta sección del portal." />
      ) : null}
      {user && canAccessProfile(user, profile) ? (
        <div className="space-y-6">
          <PageHeader title={profile.title} description={profile.description} user={user} />
          <DashboardGrid cards={profile.cards} />
        </div>
      ) : null}
    </AppShell>
  );
}
