import type { DashboardCardItem } from "@/lib/dashboard";
import { resolvePortalHref } from "@/lib/route-mapping";
import { ModuleIcon } from "@/components/ui/icons";
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
    <article className="group flex h-full min-h-[148px] flex-col justify-between rounded-[1.25rem] border border-[#e7dccb] bg-[#fffcf6] p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-[#d8c5a7] hover:bg-white">
      <div>
        <div className="mb-3 flex items-start justify-between gap-3">
          <span className={`flex h-11 w-11 items-center justify-center rounded-full bg-gradient-to-br ${style.bg} text-white shadow-md shadow-black/10`}>
            <ModuleIcon name={item.title} className="h-5 w-5" />
          </span>
          {item.badge ? <StatusBadge tone="warning">{item.badge}</StatusBadge> : null}
        </div>
        <div className="flex items-end justify-between gap-3">
          <h3 className="text-base font-black leading-tight text-[#101b18]">{item.title}</h3>
          {typeof item.value === "number" ? <span className="text-2xl font-black leading-none text-[#152b25]">{item.value}</span> : null}
        </div>
        <p className="mt-2 text-sm leading-5 text-[#5f6764]">{item.description}</p>
      </div>
      <span className={`mt-3 self-end text-2xl leading-none transition group-hover:translate-x-0.5 ${style.arrow}`} aria-hidden="true">
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
