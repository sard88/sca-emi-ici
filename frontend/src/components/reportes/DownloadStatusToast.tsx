export function DownloadStatusToast({ message, tone = "info" }: { message: string | null; tone?: "info" | "error" }) {
  if (!message) return null;

  const styles = tone === "error"
    ? "border-[#efc3c7] bg-[#fff1f2] text-[#8c1239]"
    : "border-[#d8c5a7] bg-[#fffaf1] text-[#5f4525]";

  return <div className={`rounded-2xl border px-4 py-3 text-sm font-bold ${styles}`}>{message}</div>;
}
