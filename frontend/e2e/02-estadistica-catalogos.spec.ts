import { test } from "@playwright/test";
import { loginAs } from "./helpers/auth";
import { visitAndCheck } from "./helpers/navigation";

test("estadistica consulta modulos institucionales", async ({ page }) => {
  await loginAs(page, "estadistica");
  await visitAndCheck(page, "/estadistica/actas", /actas vivas/i);
  await visitAndCheck(page, "/periodos", /per[ií]odos acad[eé]micos/i);
  await visitAndCheck(page, "/reportes", /reportes/i);
  await visitAndCheck(page, "/movimientos-academicos", /movimientos/i);
});
