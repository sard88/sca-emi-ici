"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { EmptyState } from "@/components/states/EmptyState";
import { getPerfilMe } from "@/lib/api";
import type { PerfilUsuario } from "@/lib/types";

export default function PerfilPage() {
  const [perfil, setPerfil] = useState<PerfilUsuario | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        setPerfil(await getPerfilMe());
      } catch (err) {
        setError(err instanceof Error ? err.message : "No fue posible cargar el perfil.");
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, []);

  return (
    <AppShell>
      <div className="space-y-6">
        <section className="relative overflow-hidden rounded-[1.75rem] bg-[#073f34] p-6 text-white shadow-institutional sm:p-8">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_24%_20%,rgba(255,255,255,0.12),transparent_18rem),linear-gradient(135deg,#073f34_0%,#075445_52%,#07372f_100%)]" />
          <div className="relative max-w-3xl">
            <p className="text-xs font-black uppercase tracking-[0.34em] text-[#d4af37]">Perfil institucional</p>
            <h2 className="mt-4 text-3xl font-black tracking-tight sm:text-4xl">Mi perfil</h2>
            <p className="mt-3 text-sm leading-6 text-white/84 sm:text-base sm:leading-7">
              Consulta de datos institucionales, roles y cargos vigentes. Esta vista es solo lectura en el Bloque 10B.
            </p>
          </div>
        </section>

        {loading ? <EmptyState title="Cargando perfil" description="Estamos consultando tus datos institucionales." /> : null}
        {error ? <EmptyState title="Perfil no disponible" description={error} /> : null}
        {perfil ? <PerfilCard perfil={perfil} /> : null}
      </div>
    </AppShell>
  );
}

function PerfilCard({ perfil }: { perfil: PerfilUsuario }) {
  return (
    <section className="rounded-[1.75rem] border border-[#eadfce] bg-white/88 p-6 shadow-institutional">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <Info label="Nombre completo" value={perfil.nombre_completo || perfil.nombre_visible} />
        <Info label="Nombre institucional" value={perfil.nombre_institucional} />
        <Info label="Usuario" value={perfil.username} />
        <Info label="Correo" value={perfil.correo || perfil.email || "Sin correo registrado"} />
        <Info label="Estado de cuenta" value={perfil.estado_cuenta_label} />
        <Info label="Último acceso" value={formatDateTime(perfil.ultimo_acceso || perfil.last_login)} />
        <Info label="Grado/empleo" value={perfil.grado_empleo ? `${perfil.grado_empleo.abreviatura} · ${perfil.grado_empleo.nombre}` : "Sin grado/empleo"} />
        <Info label="Rol principal" value={perfil.perfil_principal?.replaceAll("_", " ") || "Sin rol principal"} />
        <Info label="Fecha de creación" value={formatDateTime(perfil.date_joined)} />
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <DetailList title="Roles" empty="Sin roles asignados" items={perfil.roles.map((rol) => rol.replaceAll("_", " "))} />
        <DetailList title="Carreras / ámbito" empty="Sin carrera asociada" items={perfil.carreras.map((carrera) => `${carrera.clave} · ${carrera.nombre}`)} />
      </div>

      <div className="mt-8">
        <h3 className="text-lg font-black text-[#101b18]">Cargos vigentes</h3>
        {perfil.cargos_vigentes.length === 0 ? <p className="mt-2 text-sm text-[#5f6764]">No hay cargos vigentes registrados.</p> : null}
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          {perfil.cargos_vigentes.map((cargo) => (
            <article key={`${cargo.cargo_codigo}-${cargo.vigente_desde}-${cargo.vigente_hasta}`} className="rounded-2xl border border-[#eadfce] bg-[#fffaf1] p-4">
              <p className="text-sm font-black text-[#152b25]">{cargo.cargo}</p>
              <p className="mt-1 text-xs font-bold uppercase tracking-[0.12em] text-[#9f6a22]">{cargo.tipo_designacion}</p>
              <p className="mt-2 text-sm text-[#5f6764]">Unidad: {cargo.unidad_organizacional?.nombre || "Sin unidad"}</p>
              <p className="text-sm text-[#5f6764]">Carrera: {cargo.carrera ? `${cargo.carrera.clave} · ${cargo.carrera.nombre}` : "Sin carrera"}</p>
              <p className="mt-2 text-xs text-[#7b837f]">Vigencia: {cargo.vigente_desde || "sin inicio"} - {cargo.vigente_hasta || "vigente"}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-[#eadfce] bg-[#fffaf1] p-4">
      <p className="text-xs font-black uppercase tracking-[0.16em] text-[#9f6a22]">{label}</p>
      <p className="mt-2 text-sm font-black text-[#152b25]">{value}</p>
    </div>
  );
}

function DetailList({ title, items, empty }: { title: string; items: string[]; empty: string }) {
  return (
    <div>
      <h3 className="text-lg font-black text-[#101b18]">{title}</h3>
      {items.length === 0 ? <p className="mt-2 text-sm text-[#5f6764]">{empty}</p> : null}
      <div className="mt-3 flex flex-wrap gap-2">
        {items.map((item) => (
          <span key={item} className="rounded-full border border-[#d8c5a7] bg-[#f8f4ea] px-3 py-1.5 text-xs font-black text-[#152b25]">
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}

function formatDateTime(value: string | null) {
  if (!value) return "Sin registro";
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}
