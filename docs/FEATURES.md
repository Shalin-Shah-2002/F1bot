# Product Features & Phased Roadmap

This document defines a detailed product roadmap for **F1bot**.

## Product Goal

Help founders and growth teams find high-intent Reddit conversations, qualify them with AI, and convert them into real outreach opportunities.

## Product Principles

1. **Intent first, volume second**: prioritize quality over noisy mention volume.
2. **Fast action loop**: discovery → qualification → outreach should happen in minutes.
3. **Simple by default**: founder-friendly UX before enterprise complexity.
4. **Cost-aware AI**: use `gemini-2.5-flash-lite` for broad filtering, `gemini-2.5-flash` for high-value scoring.

---

## Phase 1 — MVP (Core Value Release)

### Objective

Ship a usable lead discovery workflow end-to-end for a solo founder or small team.

### Features

#### 1) Business Profile Setup
- User defines business summary, target customer, keywords, and subreddit targets.
- Profile is stored and reused for every scan.

**Why it matters:** AI quality depends on clear business context.

**Done when:** Profile can be created, edited, saved, and injected into scan requests.

#### 2) Manual Lead Scan
- User clicks **Find Leads** to run immediate scan.
- Backend pulls candidate Reddit posts from selected subreddits.
- De-duplication and normalized post schema applied.

**Why it matters:** fast feedback loop for learning what converts.

**Done when:** Scan returns candidate set with post metadata and source URLs.

#### 3) Two-Stage AI Qualification (Gemini)
- Stage A (`gemini-2.5-flash-lite`): filter low-intent/noisy candidates.
- Stage B (`gemini-2.5-flash`): assign final lead score + reason + outreach suggestion.
- Fallback to heuristic scoring when AI key is unavailable.

**Why it matters:** keeps token cost low while preserving decision quality.

**Done when:** Each returned lead has score (0-100), qualification reason, and suggested outreach angle.

#### 4) Leads Inbox UI
- Display leads in one view (title, subreddit, score, reason, URL).
- Sort by highest score by default.
- Show scan diagnostics (candidate count, AI mode used).

**Why it matters:** users need a clear priority queue, not raw data.

**Done when:** User can review and open high-priority leads directly from inbox.

#### 5) Lead Status Tracking
- Status lifecycle: `new`, `contacted`, `qualified`, `ignored`.
- Status changes persist across refresh.

**Why it matters:** creates a lightweight sales pipeline inside product.

**Done when:** Status updates are saved and reflected in inbox consistently.

#### 6) CSV Export
- Export selected/filtered leads to CSV.
- Include: post URL, score, status, reason, outreach suggestion.

**Why it matters:** users can take leads into spreadsheets and sales workflows immediately.

**Done when:** Export file downloads with correct columns and current filters.

### MVP Success Criteria

- User can go from profile setup to first qualified lead list in under 5 minutes.
- Top lead list quality is good enough for manual outreach.
- At least one repeat workflow exists: scan → status update → export.

---

## Phase 2 — Growth & Automation

### Objective

Reduce manual effort and increase consistency of lead capture.

### Features

#### 1) Scheduled Scans
- Configurable frequency (e.g., every 2h / 6h / 24h).
- Incremental scan behavior: save only new or changed lead candidates.

**Value:** continuous lead capture without manual triggering.

#### 2) Alerting
- Email/Slack alerts for leads above score threshold.
- Optional per-profile threshold settings.

**Value:** real-time reaction to high-intent opportunities.

#### 3) Outreach Draft Variants
- Generate 2-3 outreach drafts per lead.
- Tone presets (helpful, direct, consultative).

**Value:** faster outreach execution with less writing effort.

#### 4) Advanced Filtering
- Filter by subreddit, date range, score range, status, keyword match.
- Save common filter presets.

**Value:** better control at higher data volume.

#### 5) Webhook/API Improvements
- Push high-score leads to external endpoints.
- API endpoints for lead list and status updates.

**Value:** integration-ready for growth ops workflows.

### Phase 2 Success Criteria

- Majority of active users rely on scheduled scans instead of manual scans.
- Alerted leads have higher conversion than non-alerted baseline.
- Outreach time per lead decreases with draft suggestions.

---

## Future Phase — Scale Platform

### Objective

Evolve from founder tool into team-ready lead intelligence platform.

### Features

#### 1) Multi-Workspace + Team Access
- Multiple business profiles/workspaces.
- Team member invitations and role-based permissions.

#### 2) CRM Integrations
- Native integrations (HubSpot, Pipedrive, Notion, others).
- One-click push of qualified leads with activity history.

#### 3) Advanced Analytics Dashboard
- Funnel tracking: scan → contacted → qualified.
- Subreddit quality performance and keyword effectiveness.
- Outreach response tracking and ROI-style reporting.

#### 4) Source Expansion Beyond Reddit
- Add selected communities where intent is high (optional by workspace).
- Keep Reddit-first identity while supporting expansion.

#### 5) Enterprise Controls (Optional Track)
- Audit logs, SSO, data retention controls, compliance settings.

### Future Phase Success Criteria

- Teams can operate across multiple campaigns without workflow conflicts.
- CRM sync becomes a primary downstream workflow.
- Analytics clearly guides which channels and keywords produce revenue.

---

## Non-Goals (for MVP)

- Auto-posting/replying on Reddit without human review.
- Fully autonomous outbound agent.
- Complex workflow automation builder.
- Broad enterprise compliance features in first release.

---

## Suggested Execution Order

1. Profile persistence + scan context handling
2. Candidate fetch + two-stage AI scoring
3. Inbox UX + status tracking
4. Export + quality tuning loop
5. Scheduler + alerts
6. Integrations + analytics
