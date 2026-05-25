import type { SVGProps } from "react";

export type IconName =
  | "home"
  | "workspace"
  | "actas"
  | "calificaciones"
  | "trayectoria"
  | "movimientos"
  | "periodos"
  | "administracion"
  | "catalogos"
  | "reportes"
  | "kardex"
  | "exportaciones"
  | "auditoria"
  | "soporte"
  | "warning"
  | "success"
  | "blocked"
  | "pending"
  | "official"
  | "search"
  | "empty";

export const iconNames = [
  "home",
  "workspace",
  "actas",
  "calificaciones",
  "trayectoria",
  "movimientos",
  "periodos",
  "administracion",
  "catalogos",
  "reportes",
  "kardex",
  "exportaciones",
  "auditoria",
  "soporte",
  "warning",
  "success",
  "blocked",
  "pending",
  "official",
  "search",
  "empty",
] as const satisfies readonly IconName[];

type IconProps = SVGProps<SVGSVGElement>;

export function Icon({ name, className }: { name: IconName; className?: string }) {
  const props = { className, "aria-hidden": true };
  switch (name) {
    case "home":
      return <HomeIcon {...props} />;
    case "workspace":
      return <IdIcon {...props} />;
    case "actas":
      return <DocumentIcon {...props} />;
    case "calificaciones":
      return <GradeIcon {...props} />;
    case "trayectoria":
      return <AcademicIcon {...props} />;
    case "movimientos":
      return <MoveIcon {...props} />;
    case "periodos":
      return <CalendarIcon {...props} />;
    case "administracion":
      return <SettingsIcon {...props} />;
    case "catalogos":
      return <CatalogIcon {...props} />;
    case "reportes":
      return <ChartIcon {...props} />;
    case "kardex":
      return <CertificateIcon {...props} />;
    case "exportaciones":
      return <ExportIcon {...props} />;
    case "auditoria":
      return <ShieldIcon {...props} />;
    case "soporte":
      return <ToolIcon {...props} />;
    case "warning":
      return <WarningIcon {...props} />;
    case "success":
      return <SuccessIcon {...props} />;
    case "blocked":
      return <BlockedIcon {...props} />;
    case "pending":
      return <PendingIcon {...props} />;
    case "official":
      return <SealIcon {...props} />;
    case "search":
      return <SearchIcon {...props} />;
    case "empty":
      return <EmptyIcon {...props} />;
    default:
      return <DocumentIcon {...props} />;
  }
}

export function moduleIconName(value: string): IconName {
  const normalized = value.toUpperCase();
  if (normalized.includes("PANEL") || normalized.includes("INICIO")) return "home";
  if (normalized.includes("DOCENTE") || normalized.includes("DISCENTE")) return "workspace";
  if (normalized.includes("ACTA")) return "actas";
  if (normalized.includes("CALIFIC")) return "calificaciones";
  if (normalized.includes("MOVIMIENTO")) return "movimientos";
  if (normalized.includes("TRAYECTORIA") || normalized.includes("JEFE") || normalized.includes("JEFATURA")) return "trayectoria";
  if (normalized.includes("PERIODO")) return "periodos";
  if (normalized.includes("ADMIN")) return "administracion";
  if (normalized.includes("CATALOGO") || normalized.includes("CATÁLOGO")) return "catalogos";
  if (normalized.includes("KÁRDEX") || normalized.includes("KARDEX")) return "kardex";
  if (normalized.includes("EXPORT")) return "exportaciones";
  if (normalized.includes("AUDITOR") || normalized.includes("SEGURIDAD")) return "auditoria";
  if (normalized.includes("SOPORTE") || normalized.includes("HEALTH")) return "soporte";
  if (normalized.includes("REPORTE") || normalized.includes("DESEMPEÑO") || normalized.includes("ESTAD")) return "reportes";
  return "catalogos";
}

export function ModuleIcon({ name, className }: { name: string; className?: string }) {
  return <Icon name={moduleIconName(name)} className={className} />;
}

function BaseIcon({ children, ...props }: IconProps) {
  return (
    <svg {...props} viewBox="0 0 24 24" fill="none">
      {children}
    </svg>
  );
}

function HomeIcon(props: IconProps) {
  return <BaseIcon {...props}><path d="M3.5 11.2 12 4l8.5 7.2V20h-5.2v-5.4H8.7V20H3.5v-8.8Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /></BaseIcon>;
}

function IdIcon(props: IconProps) {
  return <BaseIcon {...props}><path d="M5 4h14v16H5V4Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /><path d="M9 9h6M9 13h6M9 17h4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></BaseIcon>;
}

function DocumentIcon(props: IconProps) {
  return <BaseIcon {...props}><path d="M7 3.5h6.5L18 8v12.5H7V3.5Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /><path d="M13.5 3.8V8H18M9.8 12h5.4M9.8 15h5.4M9.8 18h3.4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></BaseIcon>;
}

function GradeIcon(props: IconProps) {
  return <BaseIcon {...props}><path d="M5 5h14v14H5V5Z" stroke="currentColor" strokeWidth="1.8" /><path d="m8 12 2.2 2.2L16.5 8" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></BaseIcon>;
}

function AcademicIcon(props: IconProps) {
  return <BaseIcon {...props}><path d="m3 8.5 9-4 9 4-9 4-9-4Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /><path d="M7 10.5v4.2c0 1.1 2.2 2.8 5 2.8s5-1.7 5-2.8v-4.2" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></BaseIcon>;
}

function MoveIcon(props: IconProps) {
  return <BaseIcon {...props}><path d="M4 7h12m0 0-3-3m3 3-3 3M20 17H8m0 0 3-3m-3 3 3 3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></BaseIcon>;
}

function CalendarIcon(props: IconProps) {
  return <BaseIcon {...props}><path d="M6 4v3M18 4v3M4.5 9h15M5 6h14v14H5V6Z" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></BaseIcon>;
}

function SettingsIcon(props: IconProps) {
  return <BaseIcon {...props}><path d="M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7Z" stroke="currentColor" strokeWidth="1.8" /><path d="M19 13.6v-3.2l-2.1-.7a5.6 5.6 0 0 0-.7-1.6l1-2-2.3-2.3-2 .9a6 6 0 0 0-1.8-.4L10.4 2H7.2l-.7 2.2a5.6 5.6 0 0 0-1.6.7l-2-.9L.6 6.3l.9 2a6 6 0 0 0-.4 1.8L-1 10.8V14l2.1.7c.2.6.4 1.1.7 1.6l-1 2 2.3 2.3 2-.9c.5.3 1.1.5 1.8.7l.7 2.1h3.2l.7-2.1c.6-.2 1.1-.4 1.6-.7l2 .9 2.3-2.3-.9-2c.3-.5.5-1.1.7-1.8l1.8-.9Z" transform="translate(2.5 .3)" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" /></BaseIcon>;
}

function CatalogIcon(props: IconProps) {
  return <BaseIcon {...props}><path d="M5 5.5h14M5 12h14M5 18.5h14" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /><path d="M4 4h3v3H4V4ZM4 10.5h3v3H4v-3ZM4 17h3v3H4v-3Z" stroke="currentColor" strokeWidth="1.4" /></BaseIcon>;
}

function ChartIcon(props: IconProps) {
  return <BaseIcon {...props}><path d="M4 19V5M4 19h16" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /><path d="M8 16v-5M12 16V8M16 16v-3M20 16V6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></BaseIcon>;
}

function CertificateIcon(props: IconProps) {
  return <BaseIcon {...props}><path d="M6 4h12v16H6V4Z" stroke="currentColor" strokeWidth="1.8" /><path d="M9 8h6M9 11h6M9 14h3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /><path d="m15 16 1.2 1.1 1.8-2.2" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></BaseIcon>;
}

function ExportIcon(props: IconProps) {
  return <BaseIcon {...props}><path d="M12 4v10m0 0 3.5-3.5M12 14l-3.5-3.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /><path d="M5 16v4h14v-4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></BaseIcon>;
}

function ShieldIcon(props: IconProps) {
  return <BaseIcon {...props}><path d="M12 3.5 19 6v5.5c0 4.5-3 7.8-7 9-4-1.2-7-4.5-7-9V6l7-2.5Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /><path d="m8.8 12.2 2.1 2.1 4.4-4.9" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></BaseIcon>;
}

function ToolIcon(props: IconProps) {
  return <BaseIcon {...props}><path d="M14.5 5.5a4.5 4.5 0 0 0 4 6.1l-7 7a3 3 0 1 1-4.2-4.2l7-7a4.5 4.5 0 0 0 .2-1.9Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /></BaseIcon>;
}

function WarningIcon(props: IconProps) {
  return <BaseIcon {...props}><path d="M12 4 21 20H3L12 4Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /><path d="M12 9v5M12 17h.01" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></BaseIcon>;
}

function SuccessIcon(props: IconProps) {
  return <BaseIcon {...props}><path d="M20 6 9 17l-5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></BaseIcon>;
}

function BlockedIcon(props: IconProps) {
  return <BaseIcon {...props}><path d="M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z" stroke="currentColor" strokeWidth="1.8" /><path d="m7 7 10 10" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></BaseIcon>;
}

function PendingIcon(props: IconProps) {
  return <BaseIcon {...props}><path d="M12 6v6l4 2M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></BaseIcon>;
}

function SealIcon(props: IconProps) {
  return <BaseIcon {...props}><path d="M12 3.5 14 6l3.2-.2.7 3.1 2.6 1.6-1.6 2.8.4 3.1-3.1.9-2.1 2.4-2.1-2.4-3.1-.9.4-3.1-1.6-2.8 2.6-1.6.7-3.1L10 6l2-2.5Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" /><path d="m8.8 12.2 2.1 2.1 4.4-4.9" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></BaseIcon>;
}

function SearchIcon(props: IconProps) {
  return <BaseIcon {...props}><path d="M10.5 18a7.5 7.5 0 1 1 5.3-2.2L21 21" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></BaseIcon>;
}

function EmptyIcon(props: IconProps) {
  return <BaseIcon {...props}><path d="M5 7h14v11H5V7Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /><path d="M8 7l1.5-3h5L16 7M9 12h6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></BaseIcon>;
}
