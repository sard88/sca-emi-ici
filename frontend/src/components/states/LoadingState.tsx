export function LoadingState({ label = "Cargando información institucional..." }: { label?: string }) {
  return (
    <div className="flex min-h-[40vh] items-center justify-center text-center text-carbon">
      <div>
        <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-4 border-guinda/20 border-t-guinda" />
        <p className="font-medium">{label}</p>
      </div>
    </div>
  );
}
