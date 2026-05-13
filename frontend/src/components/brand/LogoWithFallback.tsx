"use client";

import { useState } from "react";
import { InstitutionalSealPlaceholder } from "./InstitutionalSealPlaceholder";

type LogoProps = {
  src: string;
  alt: string;
  fallback: string;
  className?: string;
};

export function LogoWithFallback({ src, alt, fallback, className }: LogoProps) {
  const [failed, setFailed] = useState(false);

  if (failed) {
    return <InstitutionalSealPlaceholder label={fallback} className={className} />;
  }

  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={src}
      alt={alt}
      className={className ?? "h-12 w-12 rounded-full object-contain"}
      onError={() => setFailed(true)}
    />
  );
}
