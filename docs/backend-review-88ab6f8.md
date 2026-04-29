# Backend Code Review (0bf0d28..88ab6f8)

Date: 2026-04-29
Scope: Backend-only review for latest commit range.

## Strengths

- Added seller-promo detection and connected it to filtering and scoring, aligned with lead-quality goals (`backend/app/services/reddit_service.py:908`, `backend/app/services/reddit_service.py:998`).
- Added regression coverage for non-AI fallback behavior when `GEMINI_API_KEY` is absent (`backend/tests/test_auth_scan_regression.py:172`).
- Added targeted tests for signal behavior and scoring impacts (`backend/tests/test_comment_intent_signals.py:102`, `backend/tests/test_comment_intent_signals.py:205`, `backend/tests/test_comment_intent_signals.py:293`).
- Updated Gemini prompt guidance to reduce seller-style lead scoring (`backend/app/services/gemini_service.py:101`).

## Issues

### Critical (Must Fix)

- None found in this backend scope.

### Important (Should Fix)

1. Broad substring matching can over-filter valid leads.
   - File: `backend/app/services/reddit_service.py:96`
   - Problem: Seller detection relies on raw phrase inclusion checks (e.g., `"for hire"`, `"contact me"`, `"message me"`) with no boundary/context validation.
   - Impact: Legitimate buyer-intent posts can be incorrectly filtered out.
   - Fix: Use regex boundaries and context checks (e.g., first-person self-promo context) before classifying as seller promo.

2. Hard reject happens before comment-level buyer-intent evidence is considered.
   - File: `backend/app/services/reddit_service.py:911`
   - Problem: `_is_keyword_match` excludes seller-promo posts before evaluating strong buyer signals from comments.
   - Impact: Potentially valid leads may be dropped.
   - Fix: Add an override path for high-confidence buyer-intent comments, or change hard reject into strong penalty + threshold.

### Minor (Nice to Have)

1. Missing false-positive edge-case tests for seller signals.
   - File: `backend/tests/test_comment_intent_signals.py:102`
   - Problem: Tests focus on positive detection paths but not common non-promotional phrase collisions.
   - Impact: Future signal list changes can increase false positives unnoticed.
   - Fix: Add table-driven negative tests (quoted phrases, advisory posts, non-self-promo context).

2. Prompt-only policy lacks deterministic backend guardrail.
   - File: `backend/app/services/gemini_service.py:101`
   - Problem: Seller down-scoring is expressed in prompt text but not enforced after model output.
   - Impact: Model variance can reintroduce low-quality leads.
   - Fix: Add post-AI score cap/penalty when seller-promo signal is present, with tests.

## Recommendations

- Introduce confidence tiers for seller detection (`high` => reject, `medium` => penalty).
- Replace plain substring checks with boundary/context-aware rules.
- Add scan-output regression tests for borderline buyer vs seller phrasing.
- Add observability counters for seller-filter rejections to monitor over-filtering.

## Assessment

Backend Readiness Verdict: **Ready with fixes**

The implementation is directionally strong with meaningful test additions. Main risk is lead recall loss from broad phrase matching and hard-reject ordering; tightening detection logic and adding edge-case tests should resolve this.
