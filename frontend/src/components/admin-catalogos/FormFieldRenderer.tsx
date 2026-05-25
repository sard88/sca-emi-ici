"use client";

import { RelationSelect } from "./RelationSelect";
import type { ResourceFormField } from "@/lib/types";

export function FormFieldRenderer({
  field,
  value,
  onChange,
  disabled,
}: {
  field: ResourceFormField;
  value: string | boolean;
  onChange: (value: string | boolean) => void;
  disabled: boolean;
}) {
  const commonClass = "h-12 w-full rounded-2xl border border-[#e4d6c2] bg-white px-4 text-sm font-medium outline-none focus:border-[#bc955c] disabled:bg-[#f5efe6] disabled:text-[#8a8176]";

  if (field.type === "boolean") {
    return (
      <label className="flex h-12 items-center gap-3 rounded-2xl border border-[#e4d6c2] bg-white px-4 text-sm font-black text-[#263b34]">
        <input
          type="checkbox"
          checked={Boolean(value)}
          disabled={disabled}
          onChange={(event) => onChange(event.target.checked)}
          className="h-4 w-4 accent-[#7a123d]"
        />
        Sí
      </label>
    );
  }

  if (field.type === "relation" && field.relationEndpoint) {
    return (
      <RelationSelect
        endpoint={field.relationEndpoint}
        value={String(value ?? "")}
        onChange={onChange}
        labelKey={field.relationLabelKey}
        valueKey={field.relationValueKey}
        disabled={disabled}
        required={field.required}
      />
    );
  }

  if (field.type === "select") {
    return (
      <select
        value={String(value ?? "")}
        disabled={disabled}
        required={field.required}
        onChange={(event) => onChange(event.target.value)}
        className={commonClass}
      >
        {(field.options ?? []).map((option) => (
          <option key={`${field.key}-${option.value}`} value={option.value}>{option.label}</option>
        ))}
      </select>
    );
  }

  if (field.type === "textarea") {
    return (
      <textarea
        value={String(value ?? "")}
        disabled={disabled}
        required={field.required}
        placeholder={field.placeholder}
        onChange={(event) => onChange(event.target.value)}
        className="min-h-28 w-full rounded-2xl border border-[#e4d6c2] bg-white px-4 py-3 text-sm font-medium outline-none focus:border-[#bc955c] disabled:bg-[#f5efe6] disabled:text-[#8a8176]"
      />
    );
  }

  return (
    <input
      value={String(value ?? "")}
      disabled={disabled}
      required={field.required}
      type={inputType(field.type)}
      placeholder={field.placeholder}
      onChange={(event) => onChange(event.target.value)}
      className={commonClass}
    />
  );
}

function inputType(type?: ResourceFormField["type"]) {
  if (type === "number") return "number";
  if (type === "date") return "date";
  if (type === "password") return "password";
  return "text";
}
