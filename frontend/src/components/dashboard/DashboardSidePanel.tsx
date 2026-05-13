"use client";

import type { ReactNode } from "react";
import type { AuthenticatedUser } from "@/lib/types";

export function DashboardSidePanel({ user }: { user: AuthenticatedUser }) {
  const today = new Date();

  return (
    <aside className="space-y-5 xl:sticky xl:top-28 xl:self-start">
      <PanelCard title="Actividad reciente" action="Ver todo">
        <EmptyTimeline user={user} />
      </PanelCard>

      <PanelCard title="Calendario institucional">
        <MiniCalendar date={today} />
      </PanelCard>

      <PanelCard title="Eventos próximos" action="Ver agenda">
        <EmptyEvents />
      </PanelCard>
    </aside>
  );
}

function PanelCard({ title, action, children }: { title: string; action?: string; children: ReactNode }) {
  return (
    <section className="rounded-[1.75rem] border border-[#eadfce] bg-white/86 p-5 shadow-institutional backdrop-blur">
      <div className="mb-5 flex items-center justify-between gap-3">
        <h3 className="text-base font-black text-[#101b18]">{title}</h3>
        {action ? (
          <span className="rounded-xl bg-[#f2e7d8] px-3 py-2 text-xs font-black text-[#432b20]">{action}</span>
        ) : null}
      </div>
      {children}
    </section>
  );
}

function EmptyTimeline({ user }: { user: AuthenticatedUser }) {
  return (
    <div className="relative space-y-4 pl-6 before:absolute before:left-2 before:top-2 before:h-[calc(100%-1rem)] before:w-px before:bg-[#eadbc4]">
      <TimelinePlaceholder color="#0b4a3d" title="Sin actividad reciente registrada" description={`Las acciones de ${user.nombre_visible || user.username} aparecerán aquí cuando exista auditoría operativa.`} />
      <TimelinePlaceholder color="#b56f12" title="Espacio reservado" description="Validaciones, capturas, movimientos y accesos podrán mostrarse en esta sección." />
    </div>
  );
}

function TimelinePlaceholder({ color, title, description }: { color: string; title: string; description: string }) {
  return (
    <div className="relative">
      <span className="absolute -left-[1.15rem] top-1.5 h-3 w-3 rounded-full ring-4 ring-white" style={{ backgroundColor: color }} />
      <p className="text-sm font-black text-[#152b25]">{title}</p>
      <p className="mt-1 text-xs leading-5 text-[#5f6764]">{description}</p>
    </div>
  );
}

function MiniCalendar({ date }: { date: Date }) {
  const days = buildCalendar(date);
  const monthLabel = new Intl.DateTimeFormat("es-MX", { month: "long", year: "numeric" }).format(date);
  const todayKey = dateKey(date);

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <p className="font-black capitalize text-[#152b25]">{monthLabel}</p>
        <div className="flex gap-2 text-[#152b25]">
          <span aria-hidden="true">‹</span>
          <span aria-hidden="true">›</span>
        </div>
      </div>
      <div className="grid grid-cols-7 gap-y-2 text-center text-xs font-black text-[#152b25]">
        {["L", "M", "M", "J", "V", "S", "D"].map((day) => <span key={day}>{day}</span>)}
      </div>
      <div className="mt-3 grid grid-cols-7 gap-y-2 text-center text-sm text-[#152b25]">
        {days.map((item) => (
          <span
            key={item.key}
            className={item.key === todayKey ? "mx-auto flex h-8 w-8 items-center justify-center rounded-full bg-[#7a123d] font-black text-white" : item.currentMonth ? "py-1" : "py-1 text-[#9ca39f]"}
          >
            {item.day}
          </span>
        ))}
      </div>
    </div>
  );
}

function EmptyEvents() {
  return (
    <div className="space-y-4">
      <EventPlaceholder color="#7a123d" title="Sin eventos próximos registrados" description="Cuando se cargue el calendario institucional, aparecerán aquí los eventos vigentes." />
      <EventPlaceholder color="#0b4a3d" title="Calendario operativo pendiente" description="Este espacio queda preparado para eventos académicos e institucionales." />
    </div>
  );
}

function EventPlaceholder({ color, title, description }: { color: string; title: string; description: string }) {
  return (
    <div className="flex gap-3">
      <span className="mt-1.5 h-3 w-3 flex-none rounded-full" style={{ backgroundColor: color }} />
      <div>
        <p className="text-sm font-black text-[#152b25]">{title}</p>
        <p className="mt-1 text-xs leading-5 text-[#5f6764]">{description}</p>
      </div>
    </div>
  );
}

function buildCalendar(date: Date) {
  const year = date.getFullYear();
  const month = date.getMonth();
  const firstDay = new Date(year, month, 1);
  const firstWeekDay = (firstDay.getDay() + 6) % 7;
  const start = new Date(year, month, 1 - firstWeekDay);

  return Array.from({ length: 42 }, (_, index) => {
    const day = new Date(start);
    day.setDate(start.getDate() + index);
    return {
      key: dateKey(day),
      day: day.getDate(),
      currentMonth: day.getMonth() === month,
    };
  });
}

function dateKey(date: Date) {
  return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
}
