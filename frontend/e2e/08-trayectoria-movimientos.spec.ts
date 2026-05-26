import { test } from "@playwright/test";
import { loginAs } from "./helpers/auth";
import { visitAndCheck } from "./helpers/navigation";

test("estadistica consulta trayectoria y movimientos", async ({ page }) => {
  await loginAs(page, "estadistica");
  await visitAndCheck(page, "/trayectoria", /trayectoria/i);
  await visitAndCheck(page, "/movimientos-academicos", /movimientos/i);
});
