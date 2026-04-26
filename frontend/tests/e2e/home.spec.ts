import { expect, test } from "@playwright/test";

test("loads homepage and shows primary CTA", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("link", { name: "Start Free Setup" })).toBeVisible();
});
