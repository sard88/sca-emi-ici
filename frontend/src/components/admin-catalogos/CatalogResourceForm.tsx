"use client";

import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { BackendValidationErrors } from "./BackendValidationErrors";
import { FormFieldRenderer } from "./FormFieldRenderer";
import type { AdminCatalogResourceConfig, ResourceItem } from "@/lib/types";

export type ValidationErrorMap = Record<string, string[]>;

export function CatalogResourceForm({
  config,
  item,
  canWrite,
  submitLabel,
  onSubmit,
  onCancel,
}: {
  config: AdminCatalogResourceConfig;
  item?: ResourceItem | null;
  canWrite: boolean;
  submitLabel: string;
  onSubmit: (payload: Record<string, unknown>) => Promise<void>;
  onCancel?: () => void;
}) {
  const initialValues = useMemo(() => buildInitialValues(config, item), [config, item]);
  const [values, setValues] = useState<Record<string, string | boolean>>(initialValues);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [errors, setErrors] = useState<ValidationErrorMap | null>(null);

  useEffect(() => {
    setValues(initialValues);
    setMessage(null);
    setError(null);
    setErrors(null);
  }, [initialValues]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canWrite) return;
    setLoading(true);
    setError(null);
    setErrors(null);
    setMessage(null);
    try {
      await onSubmit(buildPayload(config, values, Boolean(item)));
      setMessage("Registro guardado correctamente.");
      if (!item) setValues(buildInitialValues(config, null));
    } catch (err) {
      const apiError = err as Error & { errors?: ValidationErrorMap };
      setError(apiError.message || "No fue posible guardar el registro.");
      setErrors(apiError.errors ?? null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="rounded-[1.5rem] border border-[#eadfce] bg-white/88 p-5 shadow-sm">
      <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h3 className="text-lg font-black text-[#101b18]">{item ? "Detalle y edición" : "Nuevo registro"}</h3>
          <p className="mt-1 text-sm leading-6 text-[#5f6764]">
            {canWrite ? "Los datos se validan en Django antes de guardarse." : "Consulta de solo lectura para tu perfil."}
          </p>
        </div>
        {onCancel ? (
          <button type="button" onClick={onCancel} className="rounded-xl border border-[#d8c5a7] bg-white px-4 py-2 text-xs font-black text-[#5f4525] transition hover:bg-[#fff7e8]">
            Cancelar
          </button>
        ) : null}
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {config.formFields.filter((field) => !(item && field.createOnly)).map((field) => (
          <label key={field.key} className={field.type === "textarea" ? "space-y-1 md:col-span-2 xl:col-span-3" : "space-y-1"}>
            <span className="px-1 text-xs font-black uppercase tracking-[0.12em] text-[#7b6b58]">
              {field.label}{field.required ? " *" : ""}
            </span>
            <FormFieldRenderer
              field={field}
              value={values[field.key] ?? ""}
              disabled={!canWrite || Boolean(field.readOnly) || loading}
              onChange={(value) => setValues((current) => ({ ...current, [field.key]: value }))}
              values={values}
            />
            {field.help ? <span className="block px-1 text-xs font-bold leading-5 text-[#7b837f]">{field.help}</span> : null}
          </label>
        ))}
      </div>
      {item && config.slug === "usuarios" ? (
        <p className="mt-4 rounded-2xl border border-[#d4af37]/35 bg-[#fff8e6] px-4 py-3 text-sm font-bold text-[#72530d]">
          El cambio de contraseña se realizará mediante un flujo específico de restablecimiento. La contraseña temporal solo aparece al crear una cuenta.
        </p>
      ) : null}

      <div className="mt-5 space-y-3">
        {message ? <p className="rounded-2xl border border-[#b7d9c9] bg-[#edf8f2] p-3 text-sm font-black text-[#0b4a3d]">{message}</p> : null}
        {error ? <p className="rounded-2xl border border-[#e7c3ce] bg-[#fff7f9] p-3 text-sm font-black text-[#7a123d]">{error}</p> : null}
        <BackendValidationErrors errors={errors} />
      </div>

      {canWrite ? (
        <div className="mt-6 flex flex-wrap gap-3">
          <button
            type="submit"
            disabled={loading}
            className="rounded-xl bg-[#7a123d] px-5 py-3 text-sm font-black text-white shadow-sm transition hover:bg-[#5f0f30] disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Guardando..." : submitLabel}
          </button>
        </div>
      ) : null}
    </form>
  );
}

function buildInitialValues(config: AdminCatalogResourceConfig, item?: ResourceItem | null) {
  const values: Record<string, string | boolean> = {};
  config.formFields.forEach((field) => {
    const raw = item?.[field.key];
    if (field.type === "boolean") {
      values[field.key] = Boolean(raw);
    } else if (field.type === "password") {
      values[field.key] = "";
    } else {
      values[field.key] = raw === null || raw === undefined ? "" : String(raw);
    }
  });
  return values;
}

function buildPayload(config: AdminCatalogResourceConfig, values: Record<string, string | boolean>, editing: boolean) {
  const payload: Record<string, unknown> = {};
  config.formFields.forEach((field) => {
    if (field.readOnly || (editing && field.createOnly)) return;
    const value = values[field.key];
    if (editing && field.type === "password" && !value) return;
    if (field.type === "number") {
      payload[field.key] = value === "" || value === undefined ? "" : Number(value);
      return;
    }
    payload[field.key] = value;
  });
  return payload;
}
