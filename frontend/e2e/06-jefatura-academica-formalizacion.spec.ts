import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";
import { visitAndCheck } from "./helpers/navigation";

test("jefatura academica consulta pendientes y formalizadas", async ({ page }) => {
  await loginAs(page, "jefeAcademica");
  await visitAndCheck(page, "/jefatura-academica/actas", /actas/i);
  await visitAndCheck(page, "/jefatura-academica/actas?estado=formalizadas", /actas formalizadas/i);
  await expect(page.locator("body")).not.toContainText(/actas operativas/i);
});
