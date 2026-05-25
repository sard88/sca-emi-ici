export function EmptyState({ title, description }: { title: string; description: string }) {
  return (
    <div className="rounded-3xl border border-dashed border-gray-300 bg-white/70 p-8 text-center">
      <h3 className="text-lg font-semibold text-carbon">{title}</h3>
      <p className="mt-2 text-sm text-gray-600">{description}</p>
    </div>
  );
}
