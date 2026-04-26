import { expect, test } from "@playwright/test";

const PUBLIC_ROUTES = [
  { path: "/", heading: "Build A High-Intent Prospect Pipeline From Real Conversations" },
  { path: "/login", heading: "Welcome Back" },
  { path: "/register", heading: "Create Account" }
] as const;

const PROTECTED_ROUTES = ["/profile", "/scan", "/leads", "/leads/demo-lead-id", "/export", "/settings"] as const;

test("renders all public pages", async ({ page }) => {
  for (const route of PUBLIC_ROUTES) {
    await page.goto(route.path);
    await page.waitForLoadState("networkidle");
    await expect(page.getByRole("heading", { name: route.heading })).toBeVisible();
  }
});

test("redirects protected pages to login when unauthenticated", async ({ page }) => {
  for (const route of PROTECTED_ROUTES) {
    await page.goto(route);
    await page.waitForURL("**/login", { timeout: 15_000 });
    await expect(page.getByRole("heading", { name: "Welcome Back" })).toBeVisible();
  }
});
