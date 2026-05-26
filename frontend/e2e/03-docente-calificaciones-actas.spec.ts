import { expect, test } from "@playwright/test";
import { expectInstitutionalPage } from "./helpers/assertions";
import { loginAs } from "./helpers/auth";
import { visitAndCheck } from "./helpers/navigation";

test("docente consulta asignaciones y actas propias", async ({ page }) => {
  await loginAs(page, "docente");
  await visitAndCheck(page, "/docente/asignaciones", /asignaciones/i);
  await visitAndCheck(page, "/docente/actas", /actas/i);
  await expect(page.locator("body")).not.toContainText(/auditor[ií]a institucional/i);
});

test("docente no entra a administracion", async ({ page }) => {
  await loginAs(page, "docente");
  await page.goto("/administracion/usuarios");
  await expectInstitutionalPage(page);
  await expect(page.locator("body")).not.toContainText(/gestiona los usuarios/i);
});
