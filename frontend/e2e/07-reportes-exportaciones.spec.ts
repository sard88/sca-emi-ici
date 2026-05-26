import { test } from "@playwright/test";
import { loginAs } from "./helpers/auth";
import { visitAndCheck } from "./helpers/navigation";

test("estadistica navega reportes y consolidado", async ({ page }) => {
  await loginAs(page, "estadistica");
  await visitAndCheck(page, "/reportes", /reportes/i);
  await visitAndCheck(page, "/reportes/desempeno", /desempe/i);
  await visitAndCheck(page, "/reportes/desempeno/consolidado-materia", /consolidado/i);
  await visitAndCheck(page, "/reportes/operativos", /operativos/i);
  await visitAndCheck(page, "/reportes/trayectoria", /trayectoria/i);
});
