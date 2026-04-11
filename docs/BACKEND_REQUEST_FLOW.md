# Backend Request Flow (Full)

This document maps how a request moves through the backend, starting at the FastAPI app entrypoint and then for every API endpoint through dependencies, controllers, services, and repositories.

## 1. True Backend Entry Point

There is no server.js in this repository. The backend starts from:
- [main.py](../backend/app/main.py)

Typical run command:
- `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`

Startup flow in [main.py](../backend/app/main.py):
1. Build app object (`FastAPI`).
2. Run lifespan startup validation (`_validate_startup_configuration`).
3. Attach CORS middleware.
4. Mount routers:
- auth router
- health router
- profile router
- leads router
- settings router
5. Expose root endpoint `GET /`.

## 2. Shared Layers Used Across Endpoints

### 2.1 Auth dependency layer

Protected APIs depend on [dependencies.py](../backend/app/api/dependencies.py):
- `get_authenticated_context` -> validates bearer token and resolves `user_id` + `access_token`.
- `get_authenticated_user_id` -> shortcut that returns only `user_id`.

Token behavior:
- Supabase auth mode: validates token via `client.auth.get_user(token)`.
- Local fallback mode: validates `demo-token-...` format and extracts user id.

### 2.2 Supabase client layer

[core/supabase_client.py](../backend/app/core/supabase_client.py) provides:
- `get_supabase_auth_client` (anon-key client for auth/user-scoped ops)
- `get_supabase_user_client` (binds user JWT for RLS)
- `get_supabase_admin_client` (service-role client)

### 2.3 Security utility layer

- Client IP resolution: [core/client_ip.py](../backend/app/core/client_ip.py)
- Rate limiting and lockout: [core/scan_limits.py](../backend/app/core/scan_limits.py)

## 3. Endpoint-by-Endpoint Flow

## 3.1 Public endpoints

### GET /
Files involved:
- [main.py](../backend/app/main.py)

Flow:
1. Request hits FastAPI app in [main.py](../backend/app/main.py).
2. Root handler returns static liveness payload.

### POST /api/auth/login
Files involved:
- [main.py](../backend/app/main.py)
- [auth/__init__.py](../backend/app/api/routes/auth/__init__.py)
- [auth/login.py](../backend/app/api/routes/auth/login.py)
- [auth/dependencies.py](../backend/app/api/routes/auth/dependencies.py)
- [core/client_ip.py](../backend/app/core/client_ip.py)
- [core/scan_limits.py](../backend/app/core/scan_limits.py)
- [controllers/auth_controller.py](../backend/app/controllers/auth_controller.py)
- [core/supabase_client.py](../backend/app/core/supabase_client.py)

Flow:
1. Router mounted in [main.py](../backend/app/main.py) sends request to auth router prefix in [auth/__init__.py](../backend/app/api/routes/auth/__init__.py).
2. Endpoint handler in [auth/login.py](../backend/app/api/routes/auth/login.py) receives payload.
3. Builds controller via `get_auth_controller` in [auth/dependencies.py](../backend/app/api/routes/auth/dependencies.py), which creates `AuthController` with `get_supabase_auth_client`.
4. Normalizes identity from payload email.
5. Resolves request IP via `resolve_client_ip` in [core/client_ip.py](../backend/app/core/client_ip.py).
6. Runs auth pre-check limit `enforce_auth_limits` in [core/scan_limits.py](../backend/app/core/scan_limits.py).
7. Calls `AuthController.login` in [controllers/auth_controller.py](../backend/app/controllers/auth_controller.py):
- Supabase mode: `sign_in_with_password`.
- Local fallback mode: returns demo token.
8. On success, clears failure streak with `register_auth_success` in [core/scan_limits.py](../backend/app/core/scan_limits.py).
9. On auth failures (400/401/403), increments streak via `register_auth_failure` in [core/scan_limits.py](../backend/app/core/scan_limits.py).
10. Returns `LoginResponse`.

### POST /api/auth/register
Files involved:
- [auth/register.py](../backend/app/api/routes/auth/register.py)
- [auth/dependencies.py](../backend/app/api/routes/auth/dependencies.py)
- [core/client_ip.py](../backend/app/core/client_ip.py)
- [core/scan_limits.py](../backend/app/core/scan_limits.py)
- [controllers/auth_controller.py](../backend/app/controllers/auth_controller.py)

Flow:
1. Handler in [auth/register.py](../backend/app/api/routes/auth/register.py).
2. Builds `AuthController` from [auth/dependencies.py](../backend/app/api/routes/auth/dependencies.py).
3. Normalizes identity, resolves client IP.
4. Applies `enforce_auth_limits`.
5. Calls `AuthController.register` in [controllers/auth_controller.py](../backend/app/controllers/auth_controller.py):
- Supabase mode: `sign_up`.
- Local fallback mode: returns demo token.
6. On success calls `register_auth_success`.
7. On errors (400/401/403/409) calls `register_auth_failure`.
8. Returns `RegisterResponse`.

## 3.2 Protected utility endpoints

### GET /api/health
Files involved:
- [routes/health.py](../backend/app/api/routes/health.py)
- [api/dependencies.py](../backend/app/api/dependencies.py)
- [core/config.py](../backend/app/core/config.py)

Flow:
1. Route uses dependency `get_authenticated_user_id` from [api/dependencies.py](../backend/app/api/dependencies.py).
2. If token is valid, handler returns health/config status flags from settings.

### GET /api/settings
Files involved:
- [routes/settings.py](../backend/app/api/routes/settings.py)
- [api/dependencies.py](../backend/app/api/dependencies.py)
- [core/config.py](../backend/app/core/config.py)

Flow:
1. Route uses dependency `get_authenticated_user_id`.
2. Handler reads runtime config and returns feature/limit values.

## 3.3 Protected profile endpoints

### GET /api/profile
Files involved:
- [routes/profile.py](../backend/app/api/routes/profile.py)
- [api/dependencies.py](../backend/app/api/dependencies.py)
- [controllers/profile_controller.py](../backend/app/controllers/profile_controller.py)
- [repositories/profile_repository.py](../backend/app/repositories/profile_repository.py)
- [core/supabase_client.py](../backend/app/core/supabase_client.py)

Flow:
1. Route gets `AuthContext` via `get_authenticated_context`.
2. `_build_controller` in [routes/profile.py](../backend/app/api/routes/profile.py) creates user-scoped client with `get_supabase_user_client`.
3. Builds `ProfileRepository` and `ProfileController`.
4. Calls `ProfileController.get_or_create_profile`.
5. Controller asks repository `get_profile`.
6. If profile missing, controller creates default profile and calls repository `upsert_profile`.
7. Repository writes to Supabase `profiles` table, or in-memory store fallback.

### PUT /api/profile
Files involved:
- [routes/profile.py](../backend/app/api/routes/profile.py)
- [controllers/profile_controller.py](../backend/app/controllers/profile_controller.py)
- [repositories/profile_repository.py](../backend/app/repositories/profile_repository.py)

Flow:
1. Route validates auth context.
2. Builds controller/repository same as GET profile.
3. Calls `ProfileController.upsert_profile`.
4. Controller builds domain model and sends it to repository `upsert_profile`.
5. Repository persists to Supabase `profiles` table (or memory fallback).

## 3.4 Protected leads endpoints

### POST /api/leads/scan
Files involved:
- [routes/leads.py](../backend/app/api/routes/leads.py)
- [api/dependencies.py](../backend/app/api/dependencies.py)
- [core/scan_limits.py](../backend/app/core/scan_limits.py)
- [controllers/leads_controller.py](../backend/app/controllers/leads_controller.py)
- [services/reddit_service.py](../backend/app/services/reddit_service.py)
- [services/gemini_service.py](../backend/app/services/gemini_service.py)
- [repositories/leads_repository.py](../backend/app/repositories/leads_repository.py)

Flow:
1. Route resolves `AuthContext` via `get_authenticated_context`.
2. Enforces per-user scan limit with `enforce_scan_limits`.
3. `_build_controller` creates user-scoped Supabase client and `LeadsRepository`.
4. Calls `LeadsController.scan`.
5. Controller builds:
- `RedditLeadCollector`
- `GeminiLeadScorer`
6. Controller gets seen post ids from repository (`get_seen_post_ids`).
7. Collector fetches candidate posts.
8. Scorer ranks/scores candidates.
9. Controller persists results via `save_scan_results`.
10. Controller marks surfaced post IDs via `mark_posts_seen`.
11. Returns `LeadScanResponse`.

### GET /api/leads
Files involved:
- [routes/leads.py](../backend/app/api/routes/leads.py)
- [controllers/leads_controller.py](../backend/app/controllers/leads_controller.py)
- [repositories/leads_repository.py](../backend/app/repositories/leads_repository.py)

Flow:
1. Route authenticates request.
2. Builds controller.
3. Calls `LeadsController.list_leads`.
4. Controller calls repository `list_leads` (with optional status filter).
5. Returns `LeadListResponse`.

### GET /api/leads/export.csv
Files involved:
- [routes/leads.py](../backend/app/api/routes/leads.py)
- [controllers/leads_controller.py](../backend/app/controllers/leads_controller.py)
- [repositories/leads_repository.py](../backend/app/repositories/leads_repository.py)

Flow:
1. Route authenticates request.
2. Builds controller.
3. Calls `LeadsController.export_csv`.
4. Controller reads leads from repository and formats CSV rows.
5. Route returns `PlainTextResponse` with CSV headers.

### GET /api/leads/{lead_id}
Files involved:
- [routes/leads.py](../backend/app/api/routes/leads.py)
- [controllers/leads_controller.py](../backend/app/controllers/leads_controller.py)
- [repositories/leads_repository.py](../backend/app/repositories/leads_repository.py)

Flow:
1. Route authenticates request.
2. Builds controller.
3. Calls `LeadsController.get_lead`.
4. Controller calls repository `get_lead`.
5. If no record, route returns 404.

### PATCH /api/leads/{lead_id}/status
Files involved:
- [routes/leads.py](../backend/app/api/routes/leads.py)
- [controllers/leads_controller.py](../backend/app/controllers/leads_controller.py)
- [repositories/leads_repository.py](../backend/app/repositories/leads_repository.py)

Flow:
1. Route authenticates request.
2. Builds controller.
3. Calls `LeadsController.update_status`.
4. Controller calls repository `update_status`.
5. If no record, route returns 404.

## 4. Controller to Endpoint Map

- `AuthController.login` <- `POST /api/auth/login`
- `AuthController.register` <- `POST /api/auth/register`
- `ProfileController.get_or_create_profile` <- `GET /api/profile`
- `ProfileController.upsert_profile` <- `PUT /api/profile`
- `LeadsController.scan` <- `POST /api/leads/scan`
- `LeadsController.list_leads` <- `GET /api/leads`
- `LeadsController.export_csv` <- `GET /api/leads/export.csv`
- `LeadsController.get_lead` <- `GET /api/leads/{lead_id}`
- `LeadsController.update_status` <- `PATCH /api/leads/{lead_id}/status`

## 5. Repository to Controller Map

- `ProfileRepository.get_profile` <- `ProfileController.get_profile/get_or_create_profile`
- `ProfileRepository.upsert_profile` <- `ProfileController.get_or_create_profile/upsert_profile`
- `LeadsRepository.save_scan_results` <- `LeadsController.scan`
- `LeadsRepository.get_seen_post_ids` <- `LeadsController.scan`
- `LeadsRepository.mark_posts_seen` <- `LeadsController.scan`
- `LeadsRepository.list_leads` <- `LeadsController.list_leads/export_csv`
- `LeadsRepository.get_lead` <- `LeadsController.get_lead`
- `LeadsRepository.update_status` <- `LeadsController.update_status`

## 6. One-Line End-to-End Pattern

For most protected APIs, the backend pattern is:

`main.py router -> route handler -> auth dependency -> controller -> repository/services -> response model`
