import { test } from "@playwright/test";
import { expectProtected } from "./helpers/assertions";
import { loginAs } from "./helpers/auth";
import { visitAndCheck } from "./helpers/navigation";

test("anonimo queda bloqueado en rutas protegidas", async ({ page }) => {
  await expectProtected(page, "/administracion/usuarios");
  await expectProtected(page, "/docente/asignaciones");
  await expectProtected(page, "/reportes/auditoria");
});

test("discente no accede a reportes globales", async ({ page }) => {
  await loginAs(page, "discente");
  await visitAndCheck(page, "/reportes/auditoria");
});
