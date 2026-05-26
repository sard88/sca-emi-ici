import { expect, type Download, type Page } from "@playwright/test";

export async function expectDownloadFrom(page: Page, action: () => Promise<unknown>): Promise<Download> {
  const [download] = await Promise.all([page.waitForEvent("download"), action()]);
  expect(download.suggestedFilename()).toBeTruthy();
  return download;
}
