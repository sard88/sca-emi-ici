import { test } from "@playwright/test";
import { loginAs } from "./helpers/auth";
import { visitAndCheck } from "./helpers/navigation";

test("estadistica consulta periodos y procesos de cierre", async ({ page }) => {
  await loginAs(page, "estadistica");
  await visitAndCheck(page, "/periodos", /per[ií]odos acad[eé]micos/i);
  await visitAndCheck(page, "/periodos/pendientes-asignacion-docente", /pendientes|asignaci/i);
});
