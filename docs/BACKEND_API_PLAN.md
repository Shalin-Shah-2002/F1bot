# F1bot Backend API Plan

## Purpose

This document is the single backend-first API source of truth for:
- APIs already implemented
- APIs required to complete MVP robustness
- APIs required for Phase 2 automation and integrations

Scope is backend HTTP APIs only (FastAPI).

## API Conventions

- Base URL: `http://localhost:8000`
- Current prefix: `/api`
- Payload format: JSON unless noted otherwise
- Date/time format: ISO 8601 UTC
- CSV export endpoint returns `text/csv`
- Current auth model: session token is issued, but most business endpoints trust `user_id` query/body (needs hardening)

## Current API Inventory (Implemented)

| Area | Method | Path | Status | Used by Frontend |
|---|---|---|---|---|
| System | GET | `/` | Implemented | No |
| Health | GET | `/api/health` | Implemented | No (manual/debug) |
| Runtime Settings | GET | `/api/settings` | Implemented | Yes |
| Auth | POST | `/api/auth/login` | Implemented | Yes |
| Auth | POST | `/api/auth/register` | Implemented | Yes |
| Profile | GET | `/api/profile?user_id=...` | Implemented | Yes |
| Profile | PUT | `/api/profile` | Implemented | Yes |
| Leads | POST | `/api/leads/scan` | Implemented | Yes |
| Leads | GET | `/api/leads?user_id=...&status=...` | Implemented | Yes |
| Leads | GET | `/api/leads/{lead_id}?user_id=...` | Implemented | Yes |
| Leads | PATCH | `/api/leads/{lead_id}/status?user_id=...` | Implemented | Yes |
| Leads | GET | `/api/leads/export.csv?user_id=...&status=...` | Implemented | Yes |

## Implemented Endpoint Reference

### 1) Auth

#### POST `/api/auth/login`
Request body:
```json
{
  "email": "founder@example.com",
  "password": "password123"
}
```
Response body:
```json
{
  "user_id": "uuid-or-local-id",
  "email": "founder@example.com",
  "access_token": "token",
  "token_type": "bearer"
}
```

#### POST `/api/auth/register`
Request body:
```json
{
  "email": "founder@example.com",
  "password": "password123",
  "full_name": "Founder"
}
```
Response body:
```json
{
  "user_id": "uuid-or-local-id",
  "email": "founder@example.com",
  "access_token": "token-or-empty-if-email-confirmation-required",
  "token_type": "bearer"
}
```

### 2) Profile

#### GET `/api/profile?user_id=...`
Response body:
```json
{
  "user_id": "user-id",
  "business_description": "...",
  "keywords": ["need help", "recommend"],
  "subreddits": ["entrepreneur", "marketing"],
  "updated_at": "2026-03-28T10:20:00Z"
}
```

#### PUT `/api/profile`
Request body (same schema as response):
```json
{
  "user_id": "user-id",
  "business_description": "...",
  "keywords": ["need help", "recommend"],
  "subreddits": ["entrepreneur", "marketing"]
}
```

### 3) Leads

#### POST `/api/leads/scan`
Request body:
```json
{
  "user_id": "user-id",
  "business_description": "We help founders...",
  "keywords": ["need help", "recommend"],
  "subreddits": ["entrepreneur", "smallbusiness"],
  "limit": 20
}
```
Response body:
```json
{
  "leads": [
    {
      "post": {
        "id": "abc123",
        "title": "...",
        "body": "...",
        "subreddit": "entrepreneur",
        "url": "https://reddit.com/...",
        "author": "username",
        "created_utc": "2026-03-28T09:10:00Z",
        "score": 15,
        "num_comments": 8
      },
      "lead_score": 82,
      "qualification_reason": "...",
      "suggested_outreach": "..."
    }
  ],
  "total_candidates": 50,
  "used_ai": true
}
```

#### GET `/api/leads?user_id=...&status=...`
Response body:
```json
{
  "leads": [
    {
      "id": "lead-id",
      "user_id": "user-id",
      "status": "new",
      "post": { "id": "abc123", "title": "...", "body": "...", "subreddit": "entrepreneur", "url": "https://reddit.com/...", "author": "u", "created_utc": "2026-03-28T09:10:00Z", "score": 15, "num_comments": 8 },
      "lead_score": 82,
      "qualification_reason": "...",
      "suggested_outreach": "...",
      "scan_id": "scan-id",
      "created_at": "2026-03-28T09:12:00Z",
      "updated_at": "2026-03-28T09:12:00Z"
    }
  ]
}
```

#### GET `/api/leads/{lead_id}?user_id=...`
Returns one `LeadRecord`.

#### PATCH `/api/leads/{lead_id}/status?user_id=...`
Request body:
```json
{
  "status": "contacted"
}
```
Returns updated `LeadRecord`.

#### GET `/api/leads/export.csv?user_id=...&status=...`
Response:
- Content-Type: `text/csv`
- Columns: `lead_id,status,post_url,subreddit,lead_score,qualification_reason,suggested_outreach`

### 4) Settings and Health

#### GET `/api/settings`
Response body:
```json
{
  "environment": "development",
  "gemini_configured": false,
  "reddit_configured": false,
  "supabase_configured": true
}
```

#### GET `/api/health`
Response body:
```json
{
  "status": "ok",
  "environment": "development",
  "gemini_configured": false,
  "reddit_configured": false
}
```

## APIs To Build Next (Backend-First)

### Priority A: MVP Stability and Security

### A1. Auth identity endpoint (required)
- `GET /api/auth/me`
- Goal: resolve current user from bearer token and return identity payload
- Why: remove trust on client-provided `user_id`

### A2. Auth middleware enforcement (required)
- Apply bearer token verification on profile/leads routes
- Remove `user_id` from query/body when it can be derived from token
- Why: closes impersonation risk

### A3. Auth session lifecycle (recommended)
- `POST /api/auth/logout`
- `POST /api/auth/refresh`
- Why: explicit session management and better UX

### A4. Registration error hardening (required)
- Normalize Supabase rate-limit and email-confirmation responses
- Return stable error codes/messages for frontend handling
- Why: avoid fragile string-based error checks and improve recoverability

### A5. Password recovery (recommended)
- `POST /api/auth/password/forgot`
- `POST /api/auth/password/reset`
- Why: unblock user self-service

### Priority B: Phase 2 Automation

### B1. Scheduled scans
- `POST /api/scans/schedules`
- `GET /api/scans/schedules`
- `PATCH /api/scans/schedules/{schedule_id}`
- `DELETE /api/scans/schedules/{schedule_id}`
- Why: move from manual scans to automated pipeline

### B2. Scan history and rerun
- `GET /api/scans/history`
- `GET /api/scans/{scan_id}`
- `POST /api/scans/{scan_id}/rerun`
- Why: reproducibility and auditability

### B3. Alerting
- `POST /api/alerts/channels` (email/slack/webhook)
- `GET /api/alerts/channels`
- `PATCH /api/alerts/channels/{channel_id}`
- `DELETE /api/alerts/channels/{channel_id}`
- `POST /api/alerts/test`
- Why: real-time lead response loop

### B4. Lead actions at scale
- `PATCH /api/leads/bulk-status`
- `POST /api/leads/{lead_id}/archive`
- `POST /api/leads/{lead_id}/unarchive`
- Why: operational efficiency for larger lead volumes

### Priority C: Integrations and Reporting

### C1. Webhooks/API sync
- `POST /api/integrations/webhooks`
- `GET /api/integrations/webhooks`
- `DELETE /api/integrations/webhooks/{webhook_id}`
- Why: external workflow automation

### C2. CRM push (initial)
- `POST /api/integrations/crm/hubspot/leads/{lead_id}`
- `POST /api/integrations/crm/pipedrive/leads/{lead_id}`
- Why: downstream sales activation

### C3. Analytics
- `GET /api/analytics/funnel`
- `GET /api/analytics/subreddits`
- `GET /api/analytics/keywords`
- Why: optimize conversion and sourcing strategy

## Proposed Delivery Order

1. Implement A1 + A2 together (token-derived identity)
2. Implement A4 (registration error normalization)
3. Implement A3 and A5 (session + recovery)
4. Implement B1 and B2 (scheduled + history)
5. Implement B3 (alerts)
6. Implement B4 + C1 (scale actions + webhook sync)
7. Implement C2 and C3 (CRM + analytics)

## Open Decisions

- Should user identity be fully server-derived (`/api/auth/me`) before any new feature APIs are added?
- For scheduled scans, should execution be internal cron, background queue, or external scheduler trigger?
- Should integrations be synchronous APIs or async job-based with status polling?
- Should analytics endpoints be pre-aggregated tables for performance from the start?
