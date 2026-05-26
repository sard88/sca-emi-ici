import { test } from "@playwright/test";
import { expectProtected } from "./helpers/assertions";
import { loginAs, logout, type QaRole } from "./helpers/auth";

const roles: QaRole[] = ["admin", "estadistica", "docente", "discente", "jefeCarrera", "jefeAcademica", "jefePedagogica"];

test("usuario anonimo no accede al dashboard", async ({ page }) => {
  await expectProtected(page, "/dashboard");
});

for (const role of roles) {
  test(`login y logout ${role}`, async ({ page }) => {
    await loginAs(page, role);
    await logout(page);
  });
}
