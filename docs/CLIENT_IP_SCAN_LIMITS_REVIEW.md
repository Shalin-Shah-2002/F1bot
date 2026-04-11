# Client IP and Scan/Auth Limits Review

Date: 2026-04-11
Scope: backend review of client IP resolution and auth/scan limiting behavior.

## Summary

- Reviewed [client_ip.py](../backend/app/core/client_ip.py) and [scan_limits.py](../backend/app/core/scan_limits.py).
- Traced where these functions are used in route and controller layers.
- No critical defects found in the two reviewed files.
- Found 3 important risks and 1 minor risk.

## Findings

### Critical (Must Fix)

- None found in the reviewed files.

### Important (Should Fix)

1. Account lockout is identity-only, which can enable targeted user lockout.
- Evidence: [scan_limits.py](../backend/app/core/scan_limits.py#L83), [scan_limits.py](../backend/app/core/scan_limits.py#L144), [scan_limits.py](../backend/app/core/scan_limits.py#L151), [scan_limits.py](../backend/app/core/scan_limits.py#L162)
- Why this matters: an attacker can repeatedly fail logins for a known email and force lockout for a legitimate user.
- Suggested fix: combine identity with additional risk dimensions (IP/device fingerprint), and add challenge gates (captcha/step-up verification) before hard lockout.

2. Limiter state is in-process memory only.
- Evidence: [scan_limits.py](../backend/app/core/scan_limits.py#L21), [scan_limits.py](../backend/app/core/scan_limits.py#L22), [scan_limits.py](../backend/app/core/scan_limits.py#L24), [scan_limits.py](../backend/app/core/scan_limits.py#L25), [scan_limits.py](../backend/app/core/scan_limits.py#L26), [scan_limits.py](../backend/app/core/scan_limits.py#L27)
- Why this matters: limits are inconsistent across multiple workers/instances and reset on restart.
- Suggested fix: move counters and lockouts to a shared store (Redis or Postgres) with TTL.

3. In-memory limiter maps can grow without bounded eviction.
- Evidence: writes to key stores in [scan_limits.py](../backend/app/core/scan_limits.py#L55), [scan_limits.py](../backend/app/core/scan_limits.py#L75), [scan_limits.py](../backend/app/core/scan_limits.py#L86), [scan_limits.py](../backend/app/core/scan_limits.py#L119), [scan_limits.py](../backend/app/core/scan_limits.py#L151)
- Why this matters: long-running deployments with many distinct users/IPs can accumulate memory.
- Suggested fix: periodic cleanup, TTL expiry, and max-key safeguards.

### Minor (Nice to Have)

1. Invalid trusted proxy CIDRs are silently ignored.
- Evidence: [client_ip.py](../backend/app/core/client_ip.py#L44), [client_ip.py](../backend/app/core/client_ip.py#L60)
- Why this matters: misconfiguration can go unnoticed and produce incorrect client IP attribution.
- Suggested fix: log validation warnings during startup/config validation.

## Where These Files Are Used

### client_ip.py

- Public entrypoint function: [client_ip.py](../backend/app/core/client_ip.py#L114)
- Reads forwarded chain and trusted CIDRs: [client_ip.py](../backend/app/core/client_ip.py#L117), [client_ip.py](../backend/app/core/client_ip.py#L121)
- Called by auth routes:
- [login.py](../backend/app/api/routes/auth/login.py#L18)
- [register.py](../backend/app/api/routes/auth/register.py#L18)
- Core behavior tested in [test_client_ip.py](../backend/tests/test_client_ip.py#L5)

### scan_limits.py

- Scan limiter function: [scan_limits.py](../backend/app/core/scan_limits.py#L49)
- Auth limiter function: [scan_limits.py](../backend/app/core/scan_limits.py#L78)
- Auth failure register: [scan_limits.py](../backend/app/core/scan_limits.py#L142)
- Auth success reset: [scan_limits.py](../backend/app/core/scan_limits.py#L173)
- Test reset helper: [scan_limits.py](../backend/app/core/scan_limits.py#L183)
- Called from routes:
- [leads.py](../backend/app/api/routes/leads.py#L41)
- [login.py](../backend/app/api/routes/auth/login.py#L20)
- [register.py](../backend/app/api/routes/auth/register.py#L20)
- [login.py](../backend/app/api/routes/auth/login.py#L24)
- [login.py](../backend/app/api/routes/auth/login.py#L28)
- [register.py](../backend/app/api/routes/auth/register.py#L24)
- [register.py](../backend/app/api/routes/auth/register.py#L28)

## Layer-by-Layer Backend Flow

There is no server.js in this repository. Backend entrypoint is FastAPI.

1. Start command: [README.md](../README.md#L356)
2. App bootstrap and router registration: [main.py](../backend/app/main.py#L38), [main.py](../backend/app/main.py#L48), [main.py](../backend/app/main.py#L51)
3. Auth route namespace and handlers: [auth/__init__.py](../backend/app/api/routes/auth/__init__.py#L6), [login.py](../backend/app/api/routes/auth/login.py#L14), [register.py](../backend/app/api/routes/auth/register.py#L14)
4. Auth controller layer: [auth/dependencies.py](../backend/app/api/routes/auth/dependencies.py#L5), [auth_controller.py](../backend/app/controllers/auth_controller.py#L19), [auth_controller.py](../backend/app/controllers/auth_controller.py#L40), [auth_controller.py](../backend/app/controllers/auth_controller.py#L69)
5. Scan route and controller layer: [leads.py](../backend/app/api/routes/leads.py#L36), [leads.py](../backend/app/api/routes/leads.py#L41), [leads_controller.py](../backend/app/controllers/leads_controller.py#L21)
6. Auth context dependency for protected endpoints: [dependencies.py](../backend/app/api/dependencies.py#L34)

## Test Evidence (Current)

Command run:

```bash
cd backend && .venv/bin/python -m pytest tests/test_client_ip.py tests/test_auth_scan_regression.py -q
```

Result:

- 17 passed
- 2 failed

Failing tests:

- [test_auth_scan_regression.py](../backend/tests/test_auth_scan_regression.py#L131)
- [test_auth_scan_regression.py](../backend/tests/test_auth_scan_regression.py#L159)

Observed failure path involves JWT parsing in Supabase repository calls:

- [leads.py](../backend/app/api/routes/leads.py#L44)
- [leads_repository.py](../backend/app/repositories/leads_repository.py#L114)
