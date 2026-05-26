import { expect, type Page } from "@playwright/test";
import { expectInstitutionalPage } from "./assertions";

export async function visitAndCheck(page: Page, path: string, heading?: RegExp) {
  await page.goto(path);
  await expectInstitutionalPage(page);
  if (heading) {
    await expect(page.getByRole("heading", { name: heading }).first()).toBeVisible();
  }
}
