import { institutionBrand } from "@/config/branding";
import { LogoWithFallback } from "./LogoWithFallback";

export function InstitutionLogo({ code, className }: { code: keyof typeof institutionBrand; className?: string }) {
  const brand = institutionBrand[code];
  return (
    <LogoWithFallback
      src={brand.logoApiPath}
      alt={brand.name}
      fallback={brand.shortName}
      className={className}
    />
  );
}
