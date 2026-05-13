export type BrandEntry = {
  code: string;
  name: string;
  shortName: string;
  logoSvgPath: string;
  logoPngPath: string;
  logoApiPath: string;
  primaryColor?: string;
  secondaryColor?: string;
};

export const institutionBrand: Record<string, BrandEntry> = {
  EMI: {
    code: "EMI",
    name: "Escuela Militar de Ingeniería",
    shortName: "EMI",
    logoSvgPath: "/brand/institutions/emi.svg",
    logoPngPath: "/brand/institutions/emi.png",
    logoApiPath: "/brand-logo/institutions/emi",
    primaryColor: "#611232",
    secondaryColor: "#BC955C",
  },
  UDEFA: {
    code: "UDEFA",
    name: "Universidad del Ejército y Fuerza Aérea",
    shortName: "UDEFA",
    logoSvgPath: "/brand/institutions/udefa.svg",
    logoPngPath: "/brand/institutions/udefa.png",
    logoApiPath: "/brand-logo/institutions/udefa",
    primaryColor: "#235B4E",
    secondaryColor: "#D4AF37",
  },
  GOBIERNO: {
    code: "GOBIERNO",
    name: "Gobierno de México",
    shortName: "Gobierno",
    logoSvgPath: "/brand/institutions/gobierno.svg",
    logoPngPath: "/brand/institutions/gobierno.png",
    logoApiPath: "/brand-logo/institutions/gobierno",
  },
  SEDENA: {
    code: "SEDENA",
    name: "Secretaría de la Defensa Nacional",
    shortName: "SEDENA",
    logoSvgPath: "/brand/institutions/sedena.svg",
    logoPngPath: "/brand/institutions/sedena.png",
    logoApiPath: "/brand-logo/institutions/sedena",
  },
};

export const careerBrand: Record<string, BrandEntry> = {
  ICI: {
    code: "ICI",
    name: "Ingeniería en Computación e Informática",
    shortName: "ICI",
    logoSvgPath: "/brand/careers/ici.svg",
    logoPngPath: "/brand/careers/ici.png",
    logoApiPath: "/brand-logo/careers/ici",
    primaryColor: "#611232",
  },
  ICE: {
    code: "ICE",
    name: "Ingeniería en Comunicaciones y Electrónica",
    shortName: "ICE",
    logoSvgPath: "/brand/careers/ice.svg",
    logoPngPath: "/brand/careers/ice.png",
    logoApiPath: "/brand-logo/careers/ice",
    primaryColor: "#235B4E",
  },
  IC: {
    code: "IC",
    name: "Ingeniería Civil",
    shortName: "IC",
    logoSvgPath: "/brand/careers/ic.svg",
    logoPngPath: "/brand/careers/ic.png",
    logoApiPath: "/brand-logo/careers/ic",
    primaryColor: "#3A4A32",
  },
  II: {
    code: "II",
    name: "Ingeniería Industrial",
    shortName: "II",
    logoSvgPath: "/brand/careers/ii.svg",
    logoPngPath: "/brand/careers/ii.png",
    logoApiPath: "/brand-logo/careers/ii",
    primaryColor: "#9F2241",
  },
};

export function getCareerBrand(code?: string | null) {
  if (!code) return null;
  return careerBrand[code.toUpperCase()] ?? null;
}
