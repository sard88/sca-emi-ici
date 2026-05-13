import { InstitutionLogo } from "./InstitutionLogo";
import { CareerLogo } from "./CareerLogo";

export function BrandHeader({ careerCode }: { careerCode?: string | null }) {
  const appName = process.env.NEXT_PUBLIC_APP_NAME ?? "Sistema de Control Académico EMI - ICI";
  return (
    <div className="flex items-center gap-4">
      <div className="flex -space-x-2">
        <InstitutionLogo code="EMI" className="h-12 w-12 rounded-full bg-white object-contain p-1 ring-2 ring-white" />
        <InstitutionLogo code="UDEFA" className="h-12 w-12 rounded-full bg-white object-contain p-1 ring-2 ring-white" />
      </div>
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.25em] text-oro-muted">EMI · UDEFA</p>
        <h1 className="text-lg font-black leading-tight text-white sm:text-xl">{appName}</h1>
      </div>
      {careerCode ? <CareerLogo code={careerCode} className="ml-auto hidden h-10 w-10 rounded-2xl bg-white object-contain p-1 sm:block" /> : null}
    </div>
  );
}
