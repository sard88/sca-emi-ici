import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";
import { visitAndCheck } from "./helpers/navigation";

test("discente consulta carga, actas e historial", async ({ page }) => {
  await loginAs(page, "discente");
  await visitAndCheck(page, "/discente/carga-academica", /carga|materias/i);
  await visitAndCheck(page, "/discente/actas", /actas/i);
  await visitAndCheck(page, "/discente/historial-academico", /historial/i);
  await expect(page.locator("body")).not.toContainText(/auditor[ií]a institucional/i);
});
