import { expect, type Page } from "@playwright/test";

export type QaRole =
  | "admin"
  | "estadistica"
  | "docente"
  | "discente"
  | "jefeCarrera"
  | "jefeAcademica"
  | "jefePedagogica";

const users: Record<QaRole, string> = {
  admin: process.env.E2E_ADMIN_USER || "qa_admin",
  estadistica: process.env.E2E_ESTADISTICA_USER || "qa_estadistica",
  docente: process.env.E2E_DOCENTE_USER || "qa_docente_ici_01",
  discente: process.env.E2E_DISCENTE_USER || "qa_discente_ici_4a_01",
  jefeCarrera: process.env.E2E_JEFE_CARRERA_USER || "qa_jefe_carrera_ici",
  jefeAcademica: process.env.E2E_JEFE_ACADEMICA_USER || "qa_jefatura_academica",
  jefePedagogica: process.env.E2E_JEFE_PEDAGOGICA_USER || "qa_jefatura_pedagogica",
};

export function qaPassword() {
  return process.env.E2E_QA_PASSWORD || process.env.DEMO_QA_PASSWORD || "DemoQA2026!";
}

export function usernameFor(role: QaRole) {
  return users[role];
}

export async function loginAs(page: Page, role: QaRole) {
  await page.goto("/login");
  await page.getByPlaceholder(/usuario institucional/i).fill(usernameFor(role));
  await page.getByPlaceholder(/contrase/i).fill(qaPassword());
  await page.getByRole("button", { name: /iniciar sesi/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);
  await expect(page.getByText(/panel de control institucional/i)).toBeVisible();
}

export async function logout(page: Page) {
  await page.locator("summary").filter({ hasText: /rol:/i }).click();
  await page.getByRole("button", { name: /cerrar sesi/i }).click();
  await expect(page).toHaveURL(/\/login/);
}
