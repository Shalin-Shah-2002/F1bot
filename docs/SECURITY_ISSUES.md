# Security Issues Report

Date: 2026-04-08
Project: AI_power_Lead_generation_for_Reddit
Scope: Backend auth, API route protection, frontend session handling, dependency posture, secret handling

## Executive Summary

This document captures the issues found during the security review.

High-level outcome:
- 1 Critical issue
- 4 Important issues
- No direct auth bypass found on protected business routes

## Findings

## 1) Critical - Authentication Can Downgrade To Predictable Demo Tokens

Description:
- If deployment environment configuration is incorrect, authentication can fall back to demo-token based identity.
- Demo tokens are predictable, making impersonation feasible.

Evidence:
- backend/app/core/constants.py:32
- backend/app/core/constants.py:42
- backend/app/core/config.py:66
- backend/app/core/config.py:70
- backend/app/api/dependencies.py:16
- backend/app/api/dependencies.py:36
- backend/app/controllers/auth_controller.py:63
- backend/app/controllers/auth_controller.py:102

Risk:
- Account takeover and unauthorized data access if fallback mode is active outside local-only use.

Recommended Fix:
- Change default environment from development to production-safe behavior.
- Require explicit opt-in flag for local demo auth fallback.
- Fail startup when fallback mode is enabled outside local/dev/test.
- Add test coverage for fail-closed startup behavior when APP_ENV is missing or malformed.

## 2) Important - No Brute-Force Protection On Login/Register

Description:
- Login and registration endpoints are not rate-limited.
- Existing rate limiting only covers lead scan endpoints.

Evidence:
- backend/app/api/routes/auth/login.py:9
- backend/app/api/routes/auth/register.py:9
- backend/app/core/scan_limits.py:21
- backend/app/api/routes/leads.py:35

Risk:
- Credential stuffing and password spraying risk.

Recommended Fix:
- Add per-IP and per-identity rate limits for auth endpoints.
- Add lockout/backoff policy after repeated failures.
- Emit security events for repeated auth failures.

## 3) Important - Access Tokens Stored In Browser localStorage

Description:
- Session access tokens are read/written from localStorage.

Evidence:
- frontend/lib/session.ts:30
- frontend/lib/session.ts:53

Risk:
- Any XSS can exfiltrate bearer tokens and hijack user sessions.

Recommended Fix:
- Move to HttpOnly, Secure, SameSite cookies for session tokens.
- Add CSRF protections for state-changing routes.
- Reduce token lifetime and support token rotation.

## 4) Important - Next.js Version Has Known High-Severity Advisory

Description:
- Frontend is pinned to a version with known advisories.
- Security audit indicated high severity exposure in current dependency range.

Evidence:
- frontend/package.json:12
- npm audit --omit=dev (executed 2026-04-08)

Risk:
- Potential denial-of-service and other framework-level vulnerabilities depending on deployment profile.

Recommended Fix:
- Upgrade Next.js to at least 14.2.35 (or latest secure patch for current major).
- Re-run npm audit and production smoke tests after upgrade.

## 5) Important (Operational) - High-Privilege Secrets Present In Local Env File

Description:
- Service role key and historical key material are present in local environment file.

Evidence:
- backend/.env:15
- backend/.env:5
- .gitignore:21
- .gitignore:22

Risk:
- Secret leakage via terminal history, screenshots, copy/paste, logs, or local compromise.

Notes:
- Current repository rules ignore .env files, so this is not currently a committed-secret finding.

Recommended Fix:
- Rotate exposed keys immediately.
- Remove commented historical keys.
- Use a secret manager and short-lived credentials where possible.

## Confirmed Safe Areas From This Review

- Protected business endpoints use authenticated user dependency in current route definitions:
  - backend/app/api/routes/leads.py
  - backend/app/api/routes/profile.py
  - backend/app/api/routes/health.py
  - backend/app/api/routes/settings.py

## Test Gaps

- Missing tests for auth brute-force protections on login/register.
- Missing tests validating that demo fallback auth cannot be enabled by default in non-local deployments.
- Missing frontend security tests around token storage and session hardening.

## Prioritized Remediation Plan

P0 (Immediate):
- Eliminate fail-open demo auth behavior in production-like deployments.
- Rotate Supabase service role key and remove legacy key artifacts from local env.
- Upgrade Next.js to patched version and verify audit is clean.

P1 (Near-term):
- Add auth endpoint rate limiting and lockout/backoff.
- Move session storage from localStorage to HttpOnly cookies.

P2 (Follow-up):
- Add security regression tests for auth mode enforcement and brute-force controls.
- Add monitoring/alerts for repeated failed auth attempts and suspicious token validation failures.

## Merge Readiness

Current recommendation: Do not merge to production until P0 items are completed.