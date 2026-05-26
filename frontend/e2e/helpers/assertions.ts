import { expect, type Page } from "@playwright/test";

export async function expectNoClientCrash(page: Page) {
  await expect(page.getByText(/application error/i)).toHaveCount(0);
  await expect(page.getByText(/client-side exception/i)).toHaveCount(0);
}

export async function expectInstitutionalPage(page: Page) {
  await expectNoClientCrash(page);
  await expect(page.locator("body")).not.toContainText("localhost:8000");
  await expect(page.locator("body")).not.toContainText("Bloque 9");
}

export async function expectProtected(page: Page, path: string) {
  await page.goto(path);
  await expectNoClientCrash(page);
  const redirectedToLogin = /\/login/.test(page.url());
  if (!redirectedToLogin) {
    await expect(page.getByRole("alert").or(page.getByText(/acceso restringido|no tienes permiso/i)).first()).toBeVisible();
  }
}
