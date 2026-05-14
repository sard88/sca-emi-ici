export function TrajectoryMetricCard({ label, value, tone = "verde" }: { label: string; value: string | number; tone?: "verde" | "dorado" | "guinda" }) {
  const styles = {
    verde: "text-[#10372e]",
    dorado: "text-[#7b4c0c]",
    guinda: "text-[#7a123d]",
  }[tone];

  return (
    <div className="rounded-[1.25rem] border border-[#eadfce] bg-white/88 p-4 shadow-sm">
      <p className="text-xs font-black uppercase tracking-[0.14em] text-[#9f6a22]">{label}</p>
      <p className={`mt-2 text-2xl font-black ${styles}`}>{formatMetricValue(value)}</p>
    </div>
  );
}

function formatMetricValue(value: string | number) {
  if (typeof value === "number") return Number.isInteger(value) ? value : value.toFixed(1);
  return value;
}
