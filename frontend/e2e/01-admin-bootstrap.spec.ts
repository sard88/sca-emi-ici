import { test } from "@playwright/test";
import { loginAs } from "./helpers/auth";
import { visitAndCheck } from "./helpers/navigation";

test("admin consulta dashboard y administracion", async ({ page }) => {
  await loginAs(page, "admin");
  await visitAndCheck(page, "/administracion/usuarios", /usuarios|administraci/i);
  await visitAndCheck(page, "/catalogos", /cat[aá]logos|gesti[oó]n/i);
  await visitAndCheck(page, "/reportes/auditoria", /auditor/i);
});
