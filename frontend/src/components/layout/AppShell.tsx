"use client";

import type { ReactNode } from "react";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { LoadingState } from "@/components/states/LoadingState";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { DashboardSidePanel } from "@/components/dashboard/DashboardSidePanel";
import { Sidebar, MobileModuleNav } from "./Sidebar";
import { Topbar } from "./Topbar";
import { useAuth } from "@/lib/auth";

export function AppShell({ children, showRightPanel = false }: { children: ReactNode; showRightPanel?: boolean }) {
  const { user, loading, error } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, user, router]);

  if (loading) return <LoadingState />;
  if (error) return <main className="p-6"><ErrorMessage message={error} /></main>;
  if (!user) return <LoadingState label="Redirigiendo a inicio de sesión..." />;

  return (
    <div className="min-h-screen bg-[#f8f2e8] text-[#152b25]">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_8%_8%,rgba(188,149,92,0.16),transparent_24rem),radial-gradient(circle_at_88%_0%,rgba(255,255,255,0.9),transparent_28rem)]" />
      <div className="relative lg:flex">
        <Sidebar user={user} />
        <div className="min-w-0 flex-1">
          <Topbar user={user} />
          <MobileModuleNav user={user} />
          <main className="grid w-full grid-cols-1 gap-5 px-4 py-6 sm:pl-6 sm:pr-4 xl:grid-cols-[minmax(0,1fr)_340px] xl:pl-8 xl:pr-4 2xl:grid-cols-[minmax(0,1fr)_350px] 2xl:pr-6">
            <section className="min-w-0">{children}</section>
            {showRightPanel ? <DashboardSidePanel user={user} /> : null}
          </main>
          <footer className="px-4 pb-8 text-center text-xs font-black uppercase tracking-[0.26em] text-[#b6aa98] sm:px-6 xl:px-8">
            Escuela Militar de Ingeniería <span className="mx-3">•</span> Crisol de la ciencia y el honor
          </footer>
        </div>
      </div>
    </div>
  );
}
