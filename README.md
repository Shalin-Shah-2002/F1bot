# F1bot

F1bot is an AI-assisted Reddit lead generation platform built as a monorepo.
It helps teams:

- define business targeting context,
- scan Reddit conversations for buying intent,
- score and prioritize lead opportunities,
- manage lead status workflow,
- export outreach-ready CSV data.

The repo includes a FastAPI backend and a Next.js frontend dashboard.

## Table of Contents

- [1. Project Overview](#1-project-overview)
- [2. Architecture](#2-architecture)
- [3. Repository Structure](#3-repository-structure)
- [4. Backend Deep Dive](#4-backend-deep-dive)
- [5. Frontend Deep Dive](#5-frontend-deep-dive)
- [6. API Reference](#6-api-reference)
- [7. Environment Variables](#7-environment-variables)
- [8. Local Development Setup](#8-local-development-setup)
- [9. Testing](#9-testing)
- [10. Production Deployment Notes](#10-production-deployment-notes)
- [11. Known Limitations](#11-known-limitations)
- [12. Troubleshooting](#12-troubleshooting)
- [13. Related Docs](#13-related-docs)

## 1. Project Overview

### Core capabilities

1. Authentication and session-based dashboard access.
2. Business profile capture (description, keywords, target subreddits).
3. Reddit post discovery and candidate ranking.
4. AI-assisted lead scoring and outreach suggestion generation.
5. Lead inbox management with status tracking.
6. CSV export for outbound workflows.
7. Runtime configuration visibility in the UI.

### Tech stack

- Frontend:
	- Next.js 14 (App Router)
	- React 18
	- TypeScript
	- Tailwind CSS
- Backend:
	- FastAPI
	- Pydantic + pydantic-settings
	- Supabase Python client
	- asyncpraw (authenticated Reddit API path)
	- google-genai (Gemini scoring)

## 2. Architecture

### High-level flow

1. User registers or logs in.
2. Frontend stores session token in localStorage.
3. User configures profile context.
4. User triggers scan from frontend.
5. Backend collects candidate posts from Reddit.
6. Backend scores candidates (Gemini + heuristic blend, with fallback).
7. Backend persists lead records per user.
8. User reviews leads, updates status, exports CSV.

### Authentication model

- Supabase mode:
	- enabled when `SUPABASE_AUTH_ENABLED=true` (or inferred true outside dev-like envs),
	- `/api/auth/login` and `/api/auth/register` use Supabase auth APIs,
	- protected routes validate Bearer JWT using Supabase `auth.get_user(token)`.
- Local fallback mode:
	- used for development when Supabase auth is disabled,
	- auth endpoints return demo tokens prefixed with `demo-token-`,
	- protected routes derive local user id from that token format.

### Startup validation

Backend startup fails fast when auth mode and configuration are inconsistent (for example, auth enabled but missing Supabase URL/key or client initialization failure).

## 3. Repository Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/routes/            # FastAPI route handlers
│   │   ├── controllers/           # business logic orchestration
│   │   ├── core/                  # config, constants, supabase, limits
│   │   ├── models/                # Pydantic schemas
│   │   ├── repositories/          # persistence adapters
│   │   ├── services/              # Reddit + Gemini services
│   │   └── main.py                # app creation and middleware
│   ├── tests/                     # backend regression tests
│   ├── SUPABASE_SETUP.md          # SQL schema and setup guide
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/                       # Next.js routes/pages
│   ├── components/                # shared UI shell/navigation
│   ├── lib/                       # API client + session helpers
│   ├── package.json
│   └── .env.local.example
├── docs/                          # feature and planning docs
└── README.md
```

## 4. Backend Deep Dive

### 4.1 Backend modules

- `app/main.py`
	- creates FastAPI app,
	- applies CORS,
	- validates startup auth config,
	- registers all routers.
- `app/core/config.py`
	- typed settings loaded from `backend/.env`,
	- central auth mode selection,
	- startup configuration validation logic.
- `app/core/scan_limits.py`
	- enforces per-user scan rate limit and daily quota.
- `app/api/dependencies.py`
	- enforces Bearer token auth,
	- resolves user identity in Supabase or local fallback mode.
- `app/controllers/*`
	- orchestrate profile/leads/auth workflows.
- `app/repositories/*`
	- abstract storage (Supabase primary, in-memory fallback paths).
- `app/services/reddit_service.py`
	- Reddit collection pipeline with retry and fallback.
- `app/services/gemini_service.py`
	- Gemini-based scoring + heuristic fallback/blend.

### 4.2 Scan and scoring pipeline

`POST /api/leads/scan` performs:

1. scan quota + rate-limit check,
2. candidate fetch from Reddit service,
3. lead scoring in Gemini service,
4. lead persistence with generated `scan_id`,
5. response containing scored leads and metadata.

### 4.3 Reddit collection behavior

Collection strategy is multi-step:

1. Authenticated Reddit API search (if credentials available).
2. Public Reddit JSON search fallback with:
	- per-query retry,
	- exponential backoff,
	- short TTL in-memory response cache,
	- subreddit/keyword normalization.
3. Static sample post fallback when live collection is unavailable.

### 4.4 Gemini scoring behavior

- Uses a single model (`GEMINI_MODEL_LITE`) and compact prompt payload.
- Applies heuristic pre-ranking first.
- Requests AI refinement for top candidates.
- Blends AI score and baseline heuristic score for stability.
- Falls back to heuristic-only ranking if Gemini is unavailable.

### 4.5 Persistence behavior

- Primary path: Supabase tables (`profiles`, `leads`).
- Fallback path: in-memory dictionaries for local/dev resilience.

### 4.6 Scan protection

Configurable controls:

- `SCAN_RATE_LIMIT_PER_MINUTE`
- `SCAN_RATE_LIMIT_WINDOW_SECONDS`
- `SCAN_DAILY_QUOTA`

Defaults: 6 per 60-second window, 200 scans/day per user.

## 5. Frontend Deep Dive

### 5.1 Frontend route map

- `/` -> redirects to `/login`
- `/login` -> login form + session save
- `/register` -> registration form + session save
- `/profile` -> business profile editor
- `/scan` -> manual lead scan and immediate result cards
- `/leads` -> lead inbox with status filtering
- `/leads/[id]` -> lead detail + status update
- `/export` -> CSV download by status
- `/settings` -> runtime backend configuration display

### 5.2 Session handling

- Session is stored in browser localStorage (`f1bot-session`).
- API client automatically injects `Authorization: Bearer <access_token>` for protected routes.
- Missing/invalid session redirects the user to login pages in protected UI flows.

### 5.3 Design system notes

- Custom brand palette and gradients in `globals.css`.
- `AppShell` + `PhaseNav` provide app-wide structure and top navigation.

## 6. API Reference

All endpoints are under backend base URL (default: `http://localhost:8000`).

### 6.1 Public endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | API liveness message |
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Authenticate user |

#### Register request

```json
{
	"email": "founder@example.com",
	"password": "password123",
	"full_name": "Founder Name"
}
```

#### Login request

```json
{
	"email": "founder@example.com",
	"password": "password123"
}
```

#### Auth response shape

```json
{
	"user_id": "string",
	"email": "string",
	"access_token": "string",
	"token_type": "bearer"
}
```

### 6.2 Protected endpoints

All endpoints below require:

```http
Authorization: Bearer <access_token>
```

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/health` | health + environment/config status |
| GET | `/api/settings` | runtime config summary |
| GET | `/api/profile` | get current user profile (auto-creates default if missing) |
| PUT | `/api/profile` | create/update current user profile |
| POST | `/api/leads/scan` | run lead scan pipeline |
| GET | `/api/leads` | list leads (optional status filter) |
| GET | `/api/leads/{lead_id}` | fetch one lead |
| PATCH | `/api/leads/{lead_id}/status` | update lead status |
| GET | `/api/leads/export.csv` | export leads CSV (optional status filter) |

#### Profile upsert request

```json
{
	"business_description": "We help B2B founders improve conversions.",
	"keywords": ["need help", "recommend"],
	"subreddits": ["entrepreneur", "sales"]
}
```

#### Lead scan request

```json
{
	"business_description": "We help SaaS founders improve conversion to demos.",
	"keywords": ["landing page", "conversion"],
	"subreddits": ["entrepreneur", "smallbusiness"],
	"limit": 20
}
```

#### Lead status update request

```json
{
	"status": "contacted"
}
```

Allowed status values:

- `new`
- `contacted`
- `qualified`
- `ignored`

## 7. Environment Variables

### 7.1 Backend (`backend/.env`)

| Variable | Required | Description |
| --- | --- | --- |
| APP_NAME | No | FastAPI app title |
| APP_ENV | No | Environment label; default `development` |
| FRONTEND_ORIGIN | No | CORS allow-origin for frontend |
| GEMINI_API_KEY | No | Enables Gemini scoring |
| GEMINI_MODEL_LITE | No | Primary AI model (default `gemini-2.5-flash-lite`) |
| GEMINI_MODEL_MAIN | No | Deprecated/unused in current flow |
| REDDIT_CLIENT_ID | No | Optional for authenticated Reddit path |
| REDDIT_CLIENT_SECRET | No | Optional for authenticated Reddit path |
| REDDIT_USER_AGENT | No | Reddit user agent |
| SUPABASE_URL | Conditionally required | Required when Supabase auth is enabled |
| SUPABASE_SERVICE_ROLE_KEY | Conditionally required | Required when Supabase auth is enabled |
| SUPABASE_AUTH_ENABLED | No | Explicitly toggles Supabase auth mode |
| SCAN_RATE_LIMIT_PER_MINUTE | No | Rate limit count (default 6) |
| SCAN_RATE_LIMIT_WINDOW_SECONDS | No | Rate limit window (default 60) |
| SCAN_DAILY_QUOTA | No | Daily scan quota (default 200) |

### 7.2 Frontend (`frontend/.env.local`)

| Variable | Required | Description |
| --- | --- | --- |
| NEXT_PUBLIC_API_BASE_URL | Yes | Backend base URL (default local: `http://localhost:8000`) |

## 8. Local Development Setup

### 8.1 Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 8.2 Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

### 8.3 URLs

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

## 9. Testing

Backend tests cover auth and scan hardening paths plus repository compatibility behavior.

Run tests:

```bash
cd backend
source .venv/bin/activate
pytest -q
```

Current test files:

- `backend/tests/test_auth_scan_regression.py`
- `backend/tests/test_leads_repository.py`

## 10. Production Deployment Notes

Use this checklist before production go-live:

1. Set `APP_ENV=production`.
2. Set `SUPABASE_AUTH_ENABLED=true`.
3. Provide valid `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`.
4. Configure `FRONTEND_ORIGIN` to your deployed frontend domain.
5. Configure `NEXT_PUBLIC_API_BASE_URL` to deployed backend URL.
6. Run Supabase SQL schema from `backend/SUPABASE_SETUP.md`.
7. Ensure secrets are injected via secure runtime environment, not committed files.

## 11. Known Limitations

1. Scan limits are currently in-process memory; they reset on service restart.
2. In multi-instance deployments, rate-limit/quota state is not shared unless moved to shared storage (for example Redis).
3. Repositories still include in-memory fallback behavior for local resilience.

## 12. Troubleshooting

### Backend fails at startup

- Cause: auth mode/config mismatch.
- Fix:
	- if production, ensure Supabase auth is enabled and credentials are valid;
	- if local dev without Supabase, set `SUPABASE_AUTH_ENABLED=false`.

### Protected endpoint returns 401

- Cause: missing or invalid Bearer token.
- Fix:
	- login/register again and confirm frontend session is saved,
	- include `Authorization: Bearer <token>` in API requests.

### Lead scan falls back to sample posts

- Cause: Reddit API unavailable and/or public search unavailable.
- Fix:
	- provide valid Reddit credentials,
	- verify network access to Reddit APIs,
	- check backend logs for fallback warnings.

### AI scoring not active

- Cause: missing or invalid Gemini key.
- Fix:
	- set valid `GEMINI_API_KEY`,
	- confirm `/api/settings` shows Gemini configured.

## 13. Related Docs

- Supabase setup and SQL schema:
	- `backend/SUPABASE_SETUP.md`
- Product planning:
	- `docs/FEATURES.md`
	- `docs/COMPETITOR_FEATURES.md`
	- `docs/FEATURE_COMPARISON.md`
	- `docs/BACKEND_API_PLAN.md`
