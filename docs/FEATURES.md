# Product Features

This document defines what to build first for **F1bot**.

## Product Goal

Help founders/marketers discover high-intent Reddit posts, score them as leads, and take outreach action quickly.

---

## MVP Features (Build First)

### 1) Business Profile Setup
- User enters business description (what they sell + ideal customer).
- User saves target keywords and pain-point phrases.
- User selects target subreddits.

**Done when:** profile can be created/updated and used by scan endpoint.

### 2) Manual Lead Scan
- User clicks **Find Leads** to run a scan instantly.
- Backend fetches posts from selected subreddits.
- System de-duplicates and normalizes post data.

**Done when:** one scan returns a candidate set with metadata.

### 3) Two-Stage AI Qualification (Gemini-only)
- Stage A: `gemini-2.5-flash-lite` filters low-value posts.
- Stage B: `gemini-2.5-flash` gives final lead score + reason + outreach suggestion.
- Fallback to heuristic scoring if AI key is missing.

**Done when:** each lead has score (0-100), reason, and outreach recommendation.

### 4) Leads Inbox UI
- Show lead cards/table with title, subreddit, score, reason, and source URL.
- Default sort by highest score.
- Show scan metadata: total candidates, AI mode used.

**Done when:** user can review top opportunities in one screen.

### 5) Lead Status Tracking
- Status values: `new`, `contacted`, `qualified`, `ignored`.
- User can change status from UI.

**Done when:** status updates persist and are visible after refresh.

### 6) Basic Export
- Export filtered leads to CSV.
- Include key fields: post URL, score, status, outreach suggestion.

**Done when:** user can download and use leads externally.

---

## Phase 2 Features (After MVP)

### 7) Scheduled Scans
- Run scans automatically every X hours.
- Save only new leads since last run.

### 8) Alerts
- Email/Slack alert when lead score >= threshold.

### 9) Outreach Draft Variants
- Generate 2-3 outreach drafts per lead tone/persona.

### 10) Advanced Filtering
- Filter by subreddit, date range, score range, status.

---

## Phase 3 Features (Scale)

### 11) Multi-workspace / Team Access
- Multiple business profiles per account.
- Team members and role-based access.

### 12) CRM Integrations
- Push qualified leads to HubSpot / Pipedrive / Notion.

### 13) Analytics Dashboard
- Track scan-to-contact and contact-to-qualified conversion.

---

## Non-Goals for MVP

- Auto-posting on Reddit.
- Fully autonomous agent replying without review.
- Complex multi-step workflow builder.

---

## Suggested Build Order (Execution)

1. Business profile persistence
2. Manual scan + two-stage AI scoring
3. Leads inbox improvements
4. Status tracking
5. CSV export
6. Scheduler + alerts
