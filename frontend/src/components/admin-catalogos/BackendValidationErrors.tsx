export function BackendValidationErrors({ errors }: { errors?: Record<string, string[]> | null }) {
  if (!errors || Object.keys(errors).length === 0) return null;

  return (
    <div className="rounded-2xl border border-[#e7c3ce] bg-[#fff7f9] p-4 text-sm text-[#7a123d]">
      <p className="font-black">Revisa las validaciones del backend</p>
      <ul className="mt-2 space-y-1">
        {Object.entries(errors).map(([field, messages]) => (
          <li key={field}>
            <span className="font-black">{field === "__all__" ? "General" : humanizeKey(field)}:</span> {messages.join(" ")}
          </li>
        ))}
      </ul>
    </div>
  );
}

function humanizeKey(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (match) => match.toUpperCase());
}
