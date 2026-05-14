export function TrajectoryReportBadge({ label, tone = "verde" }: { label: string; tone?: "verde" | "dorado" | "guinda" | "neutral" }) {
  const styles = {
    verde: "border-[#b7d9c9] bg-[#edf8f2] text-[#0b4a3d]",
    dorado: "border-[#d8c5a7] bg-[#fff7e8] text-[#7b4c0c]",
    guinda: "border-[#e7c3ce] bg-[#fff1f5] text-[#7a123d]",
    neutral: "border-[#e5ded2] bg-white text-[#5f6764]",
  }[tone];

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-[11px] font-black uppercase tracking-[0.12em] ${styles}`}>
      {label}
    </span>
  );
}
