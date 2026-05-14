import type { DashboardCardItem } from "@/lib/dashboard";
import { resolvePortalHref } from "@/lib/route-mapping";
import { StatusBadge } from "./StatusBadge";

const cardStyles = [
  { bg: "from-[#7a123d] to-[#a20f45]", arrow: "text-[#7a123d]" },
  { bg: "from-[#b46c13] to-[#d2871b]", arrow: "text-[#b46c13]" },
  { bg: "from-[#0b4a3d] to-[#126b59]", arrow: "text-[#0b4a3d]" },
  { bg: "from-[#7a123d] to-[#611232]", arrow: "text-[#7a123d]" },
];

const toneStyles = {
  guinda: { bg: "from-[#7a123d] to-[#a20f45]", arrow: "text-[#7a123d]" },
  dorado: { bg: "from-[#b46c13] to-[#d2871b]", arrow: "text-[#b46c13]" },
  verde: { bg: "from-[#0b4a3d] to-[#126b59]", arrow: "text-[#0b4a3d]" },
  neutral: { bg: "from-[#7a123d] to-[#611232]", arrow: "text-[#7a123d]" },
};

export function DashboardCard({ item, index = 0 }: { item: DashboardCardItem; index?: number }) {
  const resolved = resolvePortalHref(item.href, item.backend);
  const href = resolved?.href;
  const backend = resolved?.backend ?? false;
  const style = item.tone ? toneStyles[item.tone] : cardStyles[index % cardStyles.length];
  const content = (
    <article className="group flex h-full min-h-[174px] flex-col justify-between rounded-[1.45rem] border border-[#eadfce] bg-white/88 p-5 shadow-institutional transition hover:-translate-y-1 hover:border-[#d8c5a7] hover:bg-white">
      <div>
        <div className="mb-5 flex items-start justify-between gap-3">
          <span className={`flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br ${style.bg} text-white shadow-lg shadow-black/10`}>
            <CardIcon title={item.title} className="h-7 w-7" />
          </span>
          {item.badge ? <StatusBadge tone="warning">{item.badge}</StatusBadge> : null}
        </div>
        <div className="flex items-end justify-between gap-3">
          <h3 className="text-lg font-black leading-tight text-[#101b18]">{item.title}</h3>
          {typeof item.value === "number" ? <span className="text-3xl font-black leading-none text-[#152b25]">{item.value}</span> : null}
        </div>
        <p className="mt-3 text-sm leading-6 text-[#5f6764]">{item.description}</p>
      </div>
      <span className={`mt-5 self-end text-3xl leading-none transition group-hover:translate-x-1 ${style.arrow}`} aria-hidden="true">
        →
      </span>
    </article>
  );

  if (!href) return content;
  return (
    <a href={href} target={backend ? "_blank" : undefined} rel={backend ? "noreferrer" : undefined} className="block h-full">
      {content}
    </a>
  );
}

function CardIcon({ title, className }: { title: string; className?: string }) {
  const normalized = title.toUpperCase();
  if (normalized.includes("USUARIO")) return <UsersIcon className={className} />;
  if (normalized.includes("ROL") || normalized.includes("CARGO")) return <ShieldIcon className={className} />;
  if (normalized.includes("UNIDAD") || normalized.includes("DJANGO")) return <BuildingIcon className={className} />;
  if (normalized.includes("ESTADO") || normalized.includes("HEALTH")) return <PulseIcon className={className} />;
  if (normalized.includes("HISTORIAL") || normalized.includes("TRAYECTORIA") || normalized.includes("ACTA")) return <DocumentIcon className={className} />;
  if (normalized.includes("REPORTE") || normalized.includes("ESTAD")) return <ChartIcon className={className} />;
  return <AcademicIcon className={className} />;
}

function UsersIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M9 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7ZM3.5 20a5.5 5.5 0 0 1 11 0" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M16 11.5a3 3 0 1 0-.8-5.9M16.5 14.5A5 5 0 0 1 21 20" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function ShieldIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M12 3.5 19 6v5.5c0 4.5-3 7.8-7 9-4-1.2-7-4.5-7-9V6l7-2.5Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
      <path d="m8.8 12.2 2.1 2.1 4.4-4.9" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function BuildingIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M4 20h16M6 20V9l6-4 6 4v11" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M9 20v-6h6v6M9 10h.01M12 10h.01M15 10h.01" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function PulseIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M3 12h4l2-5 4 11 2-6h6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function DocumentIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M7 3.5h7l4 4V20H7V3.5Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
      <path d="M14 3.5V8h4M10 12h5M10 16h5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function ChartIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M5 18V11M12 18V7M19 18V4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M4 18h16" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function AcademicIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="m3 8.5 9-4 9 4-9 4-9-4Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
      <path d="M7 10.5v4.2c0 1.1 2.2 2.8 5 2.8s5-1.7 5-2.8v-4.2" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}
