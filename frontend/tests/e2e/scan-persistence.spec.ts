import { expect, test, type Page } from "@playwright/test";

const SESSION_RESPONSE = { user_id: "user-1", email: "scan-tester@example.com" };
const PROFILE_RESPONSE = {
  user_id: "user-1",
  business_description:
    "CalPal is a calorie tracker that helps people lose weight consistently with simple meal logging, macro guidance, and accountability nudges.",
  keywords: ["calorie tracker", "macro tracking"],
  subreddits: ["loseit", "Fitness"],
};
const SCAN_RESPONSE = {
  leads: [
    {
      post: {
        id: "post-1",
        title: "Need help keeping calories consistent every week",
        body: "I keep falling off track and need a better approach.",
        match_source: "post",
        subreddit: "loseit",
        url: "https://reddit.com/r/loseit/post-1",
        author: "throwaway-user",
        created_utc: "2024-01-01T00:00:00Z",
        score: 12,
        num_comments: 5,
      },
      lead_score: 91,
      qualification_reason: "Actively searching for a calorie tracking workflow.",
      suggested_outreach: "Offer a simple streak-based onboarding flow.",
    },
  ],
  total_candidates: 8,
  used_ai: true,
};

async function mockScanApi(page: Page) {
  await page.route("**/api/auth/session", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(SESSION_RESPONSE) });
  });

  await page.route("**/api/profile", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(PROFILE_RESPONSE) });
  });

  await page.route("**/api/leads/scan", async (route) => {
    const csrfHeader = route.request().headers()["x-csrf-token"];
    if (!csrfHeader) {
      await route.fulfill({ status: 403, contentType: "application/json", body: JSON.stringify({ detail: "Missing CSRF token" }) });
      return;
    }

    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(SCAN_RESPONSE) });
  });
}

test("persists scan results and repeat-scan state across navigation", async ({ page }) => {
  await page.context().addCookies([{ name: "f1bot_csrf_token", value: "test-csrf-token", url: "http://127.0.0.1:3000" }]);
  await mockScanApi(page);
  await page.goto("/");
  await page.evaluate(() => {
    window.sessionStorage.clear();
  });

  await page.goto("/scan");
  await expect(page.getByRole("heading", { name: "Find High-Intent Reddit Leads" })).toBeVisible();

  await page.getByRole("button", { name: "Find Leads" }).click();
  await expect(page.getByText("Need help keeping calories consistent every week")).toBeVisible();
  await expect(page.getByRole("button", { name: /Scan for Fresh Leads/ })).toBeVisible();
  await expect(page.getByText("New this scan: 1")).toBeVisible();

  await page.getByRole("link", { name: "Profile" }).click();
  await expect(page.getByRole("heading", { name: "Describe Your Buyer Context" })).toBeVisible();

  await page.getByRole("link", { name: "Scan" }).click();
  await expect(page.getByRole("heading", { name: "Find High-Intent Reddit Leads" })).toBeVisible();
  await expect(page.getByText("Need help keeping calories consistent every week")).toBeVisible();
  await expect(page.getByRole("button", { name: /Scan for Fresh Leads/ })).toBeVisible();
  await expect(page.getByText("New this scan: 1")).toBeVisible();
});
