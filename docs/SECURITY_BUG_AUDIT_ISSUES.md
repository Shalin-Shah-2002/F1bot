# Security And Bug Audit Issues

Date: 2026-04-11
Scope: Backend endpoints, auth flow, token handling, rate limiting, API contract, and frontend session handling.

## Critical Issues (Must Fix)

1. Supabase key role misconfiguration in runtime env.
- File: backend/.env (lines 15-16)
- Problem: SUPABASE_ANON_KEY and SUPABASE_SERVICE_ROLE_KEY are set to the same service_role token.
- Risk: Breaks least-privilege boundaries and increases blast radius for auth/client mistakes.
- Fix:
  - Rotate keys immediately.
  - Set a real anon key for SUPABASE_ANON_KEY.
  - Keep service role key only in SUPABASE_SERVICE_ROLE_KEY.
  - Add startup validation to reject service_role token in anon slot.

## Important Issues (Should Fix)

1. Local fallback auth enables easy impersonation if enabled outside local/dev/test.
- Files:
  - backend/app/controllers/auth_controller.py
  - backend/app/api/dependencies.py
- Problem: Demo token mode accepts predictable demo-token-{user_id} tokens.
- Risk: Account impersonation if fallback is turned on in a real environment.
- Fix:
  - Keep LOCAL_AUTH_FALLBACK_ENABLED=false outside local/dev/test.
  - Prefer removing fallback or using signed short-lived local tokens.

2. Local fallback path can still hit Supabase and produce 500 errors.
- Files:
  - backend/app/api/routes/leads.py
  - backend/app/api/routes/profile.py
  - backend/app/core/supabase_client.py
  - backend/app/repositories/leads_repository.py
- Problem: Route controller builder always attempts user-scoped Supabase client; demo tokens can reach PostgREST and fail JWT parsing.
- Risk: Broken scans/profile behavior in fallback test/dev scenarios.
- Proof: pytest currently fails scan rate-limit and daily-quota tests because first scan returns 500.
- Fix:
  - When Supabase auth is disabled, force repository client=None and skip user token binding.

3. Static OpenAPI contract is stale and mismatched with real auth model.
- File: backend/openapi.json
- Problem:
  - Still documents user_id query parameters on protected endpoints.
  - Includes user_id in LeadScanRequest schema.
  - Missing securitySchemes/Bearer auth declarations.
- Risk: Client generators/integrators implement wrong contract and auth behavior.
- Fix:
  - Regenerate OpenAPI from current app code.
  - Add bearer security scheme and per-path security requirements.

4. CSV export is vulnerable to spreadsheet formula injection.
- File: backend/app/controllers/leads_controller.py
- Problem: CSV escaping only handles quotes, not formula-leading characters (=, +, -, @).
- Risk: Opening exported CSV in spreadsheet tools may execute malicious formulas.
- Fix:
  - Prefix formula-leading values with single quote before writing CSV.

## Medium Issues

1. Access token stored in browser localStorage.
- File: frontend/lib/session.ts
- Risk: XSS can exfiltrate tokens.
- Fix: Move to httpOnly secure cookies with CSRF protection.

2. Auth input validation is weak for identity quality.
- File: backend/app/models/schemas.py
- Problem: Login email/password only min_length=3.
- Fix: Use EmailStr and stronger password policy.

3. Rate limits are in-memory only.
- File: backend/app/core/scan_limits.py
- Risk: Resets on restart, not shared across instances.
- Fix: Move counters/lockouts to Redis or database-backed storage.

4. Unknown IP fallback can cause shared throttling.
- Files:
  - backend/app/core/scan_limits.py
  - backend/app/core/client_ip.py
- Risk: Multiple users can share same unknown bucket under proxy misconfiguration.
- Fix: Enforce trusted proxy config at startup for proxied deployments.

5. CORS is broad in production posture.
- File: backend/app/main.py
- Problem: allow_methods and allow_headers are wildcard.
- Fix: Restrict to explicit methods/headers in production.

## Current Test Status Snapshot

- Backend tests executed: 20
- Passed: 18
- Failed: 2
- Failing file: backend/tests/test_auth_scan_regression.py
- Failing cases:
  - test_scan_rate_limit_enforced
  - test_scan_daily_quota_enforced
- Failure cause: demo token path unexpectedly reaches Supabase PostgREST JWT parser.

## Suggested Fix Order

1. Correct and rotate Supabase keys (critical).
2. Fix fallback client wiring to prevent Supabase calls in local fallback mode.
3. Patch CSV formula injection defense.
4. Regenerate and publish updated OpenAPI spec.
5. Harden session/token handling and rate-limit persistence.
