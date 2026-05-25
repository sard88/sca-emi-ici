import { CareerLogo } from "@/components/brand/CareerLogo";
import type { AuthenticatedUser } from "@/lib/types";

export function PageHeader({ title, description, user }: { title: string; description: string; user: AuthenticatedUser }) {
  const carrera = user.carreras[0];
  return (
    <section className="relative overflow-hidden rounded-[1.75rem] bg-[#073f34] p-6 text-white shadow-institutional sm:p-8">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_24%_20%,rgba(255,255,255,0.12),transparent_18rem),linear-gradient(135deg,#073f34_0%,#075445_52%,#07372f_100%)]" />
      <div className="absolute right-6 top-6 hidden h-40 w-64 opacity-40 md:block" aria-hidden="true">
        <ModuleDotPattern />
      </div>

      <div className="relative flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div className="max-w-3xl">
          <p className="text-xs font-black uppercase tracking-[0.34em] text-[#d4af37]">Módulo institucional</p>
          <h2 className="mt-4 text-3xl font-black tracking-tight sm:text-4xl">{title}</h2>
          <p className="mt-3 text-sm leading-6 text-white/84 sm:text-base sm:leading-7">{description}</p>
          <div className="mt-5 flex flex-wrap gap-2">
            <span className="rounded-full border border-[#d4af37]/45 bg-[#f8f4ea]/10 px-3 py-1 text-xs font-black uppercase tracking-[0.12em] text-[#f4d98b]">
              {user.perfil_principal?.replaceAll("_", " ") || "Sin rol principal"}
            </span>
            {user.cargos_vigentes.slice(0, 2).map((cargo) => (
              <span key={`${cargo.cargo_codigo}-${cargo.vigente_desde}`} className="rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-semibold text-white/90">
                {cargo.cargo}
              </span>
            ))}
          </div>
        </div>

        {carrera ? (
          <div className="flex items-center gap-3 rounded-2xl border border-white/12 bg-[#062f29]/42 p-3 backdrop-blur">
            <CareerLogo code={carrera.clave} className="h-14 w-14 object-contain drop-shadow-[0_10px_16px_rgba(0,0,0,0.32)]" />
            <div>
              <p className="text-xs font-black uppercase tracking-widest text-[#d4af37]">Carrera</p>
              <p className="font-black">{carrera.clave}</p>
              <p className="max-w-52 text-xs leading-5 text-white/72">{carrera.nombre}</p>
            </div>
          </div>
        ) : null}
      </div>
    </section>
  );
}

function ModuleDotPattern() {
  return (
    <svg className="h-full w-full text-[#d4af37]" viewBox="0 0 256 160" fill="none" aria-hidden="true">
      {Array.from({ length: 10 }).map((_, row) =>
        Array.from({ length: 16 }).map((__, col) => (
          <circle key={`${row}-${col}`} cx={col * 16 + 4} cy={row * 16 + 4} r="1.25" fill="currentColor" opacity="0.9" />
        )),
      )}
    </svg>
  );
}
