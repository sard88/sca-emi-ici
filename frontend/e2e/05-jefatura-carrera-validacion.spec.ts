import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";
import { visitAndCheck } from "./helpers/navigation";

test("jefatura de carrera consulta actas y pendientes de asignacion", async ({ page }) => {
  await loginAs(page, "jefeCarrera");
  await visitAndCheck(page, "/jefatura-carrera/actas", /actas/i);
  await visitAndCheck(page, "/periodos/pendientes-asignacion-docente", /pendientes|asignaci/i);
  await expect(page.locator("body")).not.toContainText(/borrador docente/i);
});
