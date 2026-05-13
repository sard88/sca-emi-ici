import { careerBrand } from "@/config/branding";
import { LogoWithFallback } from "./LogoWithFallback";

export function CareerLogo({ code, className }: { code?: string | null; className?: string }) {
  const brand = code ? careerBrand[code.toUpperCase()] : null;
  if (!brand) {
    return <LogoWithFallback src={`/brand-logo/careers/${code ?? "sca"}`} alt="Carrera no especificada" fallback={code ?? "SCA"} className={className} />;
  }
  return (
    <LogoWithFallback
      src={brand.logoApiPath}
      alt={brand.name}
      fallback={brand.shortName}
      className={className}
    />
  );
}
