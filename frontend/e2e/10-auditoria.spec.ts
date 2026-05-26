import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers/auth";
import { visitAndCheck } from "./helpers/navigation";

test("admin consulta auditoria sin exponer secretos", async ({ page }) => {
  await loginAs(page, "admin");
  await visitAndCheck(page, "/reportes/auditoria", /auditor/i);
  await expect(page.locator("body")).not.toContainText(/DemoQA2026|sessionid=|csrftoken=|csrfmiddlewaretoken/i);
});
