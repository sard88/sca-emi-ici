import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";
import { AuthProvider } from "@/lib/auth";

export const metadata: Metadata = {
  title: "SCA EMI - ICI",
  description: "Portal institucional del Sistema de Control Académico EMI - ICI",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="es-MX">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
