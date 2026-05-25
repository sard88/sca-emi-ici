"use client";

import type { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";
import { backendUrl, getActividadReciente, getCalendarioMes, getEventosProximos } from "@/lib/api";
import type { ActividadRecienteItem, AuthenticatedUser, CalendarioMes, EventoCalendario } from "@/lib/types";

export function DashboardSidePanel({ user }: { user: AuthenticatedUser }) {
  const today = useMemo(() => new Date(), []);
  const [actividad, setActividad] = useState<ActividadRecienteItem[]>([]);
  const [calendario, setCalendario] = useState<CalendarioMes | null>(null);
  const [eventos, setEventos] = useState<EventoCalendario[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [actividadResponse, calendarioResponse, eventosResponse] = await Promise.all([
          getActividadReciente(),
          getCalendarioMes(today.getFullYear(), today.getMonth() + 1),
          getEventosProximos(),
        ]);
        setActividad(actividadResponse.items);
        setCalendario(calendarioResponse);
        setEventos(eventosResponse.items);
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [today]);

  return (
    <aside className="space-y-5 xl:sticky xl:top-28 xl:self-start">
      <PanelCard title="Actividad reciente" action="Ver todo">
        {loading ? <PanelState text="Cargando actividad..." /> : <Timeline items={actividad} user={user} />}
      </PanelCard>

      <PanelCard title="Calendario institucional">
        <MiniCalendar date={today} eventDays={new Set(calendario?.dias_con_eventos ?? [])} />
      </PanelCard>

      <PanelCard title="Eventos próximos" action="Ver agenda">
        {loading ? <PanelState text="Cargando eventos..." /> : <EventsList eventos={eventos} />}
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

function Timeline({ items, user }: { items: ActividadRecienteItem[]; user: AuthenticatedUser }) {
  if (items.length === 0) {
    return (
      <div className="relative space-y-4 pl-6 before:absolute before:left-2 before:top-2 before:h-[calc(100%-1rem)] before:w-px before:bg-[#eadbc4]">
        <TimelinePlaceholder color="#0b4a3d" title="Sin actividad reciente registrada" description={`Las acciones de ${user.nombre_visible || user.username} aparecerán aquí cuando exista auditoría operativa.`} />
      </div>
    );
  }

  return (
    <div className="relative space-y-4 pl-6 before:absolute before:left-2 before:top-2 before:h-[calc(100%-1rem)] before:w-px before:bg-[#eadbc4]">
      {items.map((item) => <TimelineItem key={item.id} item={item} />)}
    </div>
  );
}

function TimelineItem({ item }: { item: ActividadRecienteItem }) {
  const color = item.tipo === "ACTA" ? "#7a123d" : item.tipo === "CAPTURA" ? "#b56f12" : "#0b4a3d";
  const content = (
    <>
      <p className="text-sm font-black text-[#152b25]">{item.titulo}</p>
      <p className="mt-1 text-xs leading-5 text-[#5f6764]">{item.descripcion}</p>
      <p className="mt-1 text-[11px] font-bold uppercase tracking-[0.12em] text-[#9f6a22]">{formatDate(item.fecha)}</p>
    </>
  );

  return (
    <div className="relative">
      <span className="absolute -left-[1.15rem] top-1.5 h-3 w-3 rounded-full ring-4 ring-white" style={{ backgroundColor: color }} />
      {item.url ? (
        <a href={item.backend ? backendUrl(item.url) : item.url} target={item.backend ? "_blank" : undefined} rel={item.backend ? "noreferrer" : undefined} className="block rounded-xl transition hover:bg-[#f7efe2]">
          {content}
        </a>
      ) : content}
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

function MiniCalendar({ date, eventDays }: { date: Date; eventDays: Set<string> }) {
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
        {days.map((item) => {
          const hasEvent = eventDays.has(item.key);
          const isToday = item.key === todayKey;
          return (
            <span
              key={item.key}
              className={isToday ? "relative mx-auto flex h-8 w-8 items-center justify-center rounded-full bg-[#7a123d] font-black text-white" : item.currentMonth ? "relative mx-auto flex h-8 w-8 items-center justify-center" : "relative mx-auto flex h-8 w-8 items-center justify-center text-[#9ca39f]"}
            >
              {item.day}
              {hasEvent ? <span className="absolute bottom-0.5 h-1.5 w-1.5 rounded-full bg-[#d4af37]" /> : null}
            </span>
          );
        })}
      </div>
      {eventDays.size === 0 ? <p className="mt-4 text-xs leading-5 text-[#5f6764]">No hay eventos registrados en este mes.</p> : null}
    </div>
  );
}

function EventsList({ eventos }: { eventos: EventoCalendario[] }) {
  if (eventos.length === 0) {
    return (
      <div className="space-y-4">
        <EventPlaceholder color="#7a123d" title="No hay eventos próximos registrados" description="Cuando se cargue el calendario institucional, aparecerán aquí los eventos vigentes." />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {eventos.map((evento) => (
        <EventItem key={evento.id} evento={evento} />
      ))}
    </div>
  );
}

function EventItem({ evento }: { evento: EventoCalendario }) {
  const content = (
    <>
      <p className="text-sm font-black text-[#152b25]">{evento.titulo}</p>
      <p className="mt-1 text-xs font-bold uppercase tracking-[0.12em] text-[#9f6a22]">{formatDate(evento.fecha_inicio)} · {evento.tipo_evento_label}</p>
      {evento.descripcion ? <p className="mt-1 text-xs leading-5 text-[#5f6764]">{evento.descripcion}</p> : null}
    </>
  );

  return (
    <div className="flex gap-3">
      <span className="mt-1.5 h-3 w-3 flex-none rounded-full bg-[#0b4a3d]" />
      <div>
        {evento.url_destino ? (
          <a href={backendUrl(evento.url_destino)} target="_blank" rel="noreferrer" className="block rounded-xl hover:bg-[#f7efe2]">
            {content}
          </a>
        ) : content}
      </div>
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

function PanelState({ text }: { text: string }) {
  return <p className="text-sm font-semibold text-[#5f6764]">{text}</p>;
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
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${date.getFullYear()}-${month}-${day}`;
}

function formatDate(value: string | null) {
  if (!value) return "Sin fecha";
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium" }).format(new Date(value));
}
