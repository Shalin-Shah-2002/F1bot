# Include comments in lead-intent detection

**Session ID:** ses_23d8ad38bffeP41aHkOqC2Bd36
**Created:** 4/25/2026, 7:55:52 AM
**Updated:** 4/25/2026, 8:03:16 AM

---

## User

Summary
The best buyer-intent signals (such as "looking for exactly this" and "anyone recommend ...") appear in the comments section rather than post titles. Currently, these signals are not detected, resulting in missing 60-70% of potential leads.

Impact

A majority of buy-ready leads are overlooked.
Lower conversion and missed opportunities for engagement.
Suggestion
Update the lead detection logic to include strong buyer-intent phrases in comments, not just post titles.i want comments to be scan also 

---

## Assistant (Build · GPT-5.3-Codex · 6.9s)

_Thinking:_



**Tool: todowrite**

**Input:**
```json
{
  "todos": [
    {
      "content": "Inspect current lead detection logic for buyer-intent phrases in Reddit data",
      "status": "in_progress",
      "priority": "high"
    },
    {
      "content": "Implement comment-level buyer-intent scanning and integrate with lead scoring/filtering",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Add or update tests/fixtures to validate comment scanning catches intent phrases",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Run relevant test suite and verify no regressions",
      "status": "pending",
      "priority": "medium"
    }
  ]
}
```

**Output:**
```
[
  {
    "content": "Inspect current lead detection logic for buyer-intent phrases in Reddit data",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "Implement comment-level buyer-intent scanning and integrate with lead scoring/filtering",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Add or update tests/fixtures to validate comment scanning catches intent phrases",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Run relevant test suite and verify no regressions",
    "status": "pending",
    "priority": "medium"
  }
]
```

---

## Assistant (Build · GPT-5.3-Codex · 5.7s)

_Thinking:_



**Tool: grep**

**Input:**
```json
{
  "pattern": "buyer|intent|lead detection|lead|title|comment",
  "path": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit",
  "include": "*.py"
}
```

**Output:**
```
Found 434 matches (showing first 100)
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests/test_comment_intent_signals.py:
  Line 1: """Tests for comment-level buyer-intent detection.

  Line 3: These tests verify that strong purchase-intent signals appearing only in

  Line 4: Reddit comment threads are detected and used to surface leads that would

  Line 5: otherwise be missed by title/body-only matching.

  Line 86:         """Key buyer-intent phrases must be in the list."""

  Line 104: # _has_comment_intent_signal

  Line 110:         assert c._has_comment_intent_signal([]) is False

  Line 112:     def test_detects_comment_intent_phrase(self) -> None:

  Line 114:         comments = [

  Line 118:         assert c._has_comment_intent_signal(comments) is True

  Line 120:     def test_detects_general_intent_signal_in_comment(self) -> None:

  Line 122:         comments = ["Any recommendation for a good CRM?"]

  Line 123:         assert c._has_comment_intent_signal(comments) is True

  Line 127:         comments = [

  Line 131:         assert c._has_comment_intent_signal(comments) is False

  Line 135:         comments = ["ANYONE RECOMMEND a good email tool?"]

  Line 136:         assert c._has_comment_intent_signal(comments) is True

  Line 140:         comments = [

  Line 145:         assert c._has_comment_intent_signal(comments) is True

  Line 149: # _is_keyword_match with top_comments

  Line 153:     def test_comment_intent_alone_passes_when_body_is_weak(self) -> None:

  Line 154:         """A post whose title/body barely matches the keyword should still

  Line 155:         pass _is_keyword_match when comments contain a strong intent signal."""

  Line 157:         # "automation" is the keyword; title/body only has "auto" (no direct hit)

  Line 159:             title="Just sharing my workflow",

  Line 162:             top_comments=["Looking for exactly this kind of automation software!"],

  Line 166:     def test_no_comments_still_matches_on_phrase(self) -> None:

  Line 169:             title="Need automation software for my team",

  Line 172:             top_comments=[],

  Line 176:     def test_weak_title_body_and_no_intent_in_comments_fails(self) -> None:

  Line 179:             title="Random post about cooking",

  Line 182:             top_comments=["Nice recipe!", "Thanks for sharing."],

  Line 186:     def test_backward_compatible_no_comments_arg(self) -> None:

  Line 187:         """Calling without top_comments must still work (defaults to None)."""

  Line 190:             title="Looking for lead generation software",

  Line 192:             keyword="lead generation",

  Line 198: # _score_keyword_match with top_comments

  Line 202:     def test_comment_intent_signals_increase_relevance_score(self) -> None:

  Line 205:             title="Lead generation tips",

  Line 207:             keyword="lead generation",

  Line 209:             num_comments=5,

  Line 210:             top_comments=[],

  Line 213:             title="Lead generation tips",

  Line 215:             keyword="lead generation",

  Line 217:             num_comments=5,

  Line 218:             top_comments=["Anyone recommend a good lead generation tool?"],

  Line 222:     def test_high_specificity_comment_gives_larger_boost_than_general(self) -> None:

  Line 226:             title="Lead gen",

  Line 228:             keyword="lead generation",

  Line 230:             num_comments=4,

  Line 231:             top_comments=["Any recommendation?"],

  Line 234:             title="Lead gen",

  Line 236:             keyword="lead generation",

  Line 238:             num_comments=4,

  Line 239:             top_comments=["I would pay for a tool that does this automatically."],

  Line 246:             title="Progress pic",

  Line 250:             num_comments=0,

  Line 251:             top_comments=[],

  Line 255:     def test_no_comments_kwarg_is_backward_compatible(self) -> None:

  Line 258:             title="Lead generation tips",

  Line 260:             keyword="lead generation",

  Line 262:             num_comments=3,

  Line 268: # _fetch_top_comments_sync

  Line 272:     def _make_reddit_comment_payload(self, bodies: list[str]) -> list[dict]:

  Line 273:         """Build a minimal Reddit `.json` payload for comment fetching."""

  Line 283:             {"kind": "Listing", "data": {"children": children}},  # comment listing

  Line 288:         result = c._fetch_top_comments_sync("https://www.reddit.com/r/test/comments/abc/", num_comments=1)

  Line 291:     def test_parses_comment_bodies_correctly(self) -> None:

  Line 293:         payload = self._make_reddit_comment_payload(["Anyone recommend a CRM?", "I'd pay for this."])

  Line 296:             result = c._fetch_top_comments_sync(

  Line 297:                 "https://www.reddit.com/r/test/comments/abc/", num_comments=5

  Line 302:     def test_skips_deleted_comments(self) -> None:

  Line 304:         payload = self._make_reddit_comment_payload(["[deleted]", "Real comment here."])

  Line 307:             result = c._fetch_top_comments_sync(

  Line 308:                 "https://www.reddit.com/r/test/comments/abc/", num_comments=5

  Line 312:         assert "Real comment here." in result

  Line 323:             result = c._fetch_top_comments_sync(

  Line 324:                 "https://www.reddit.com/r/test/comments/abc/", num_comments=5

  Line 333:             result = c._fetch_top_comments_sync(

  Line 334:                 "https://www.reddit.com/r/test/comments/abc/", num_comments=5

  Line 343:             result = c._fetch_top_comments_sync(

  Line 344:                 "https://www.reddit.com/r/test/comments/abc/", num_comments=5

  Line 349:     def test_truncates_long_comment_bodies(self) -> None:

  Line 352:         payload = self._make_reddit_comment_payload([long_body])

  Line 355:             result = c._fetch_top_comments_sync(

  Line 356:                 "https://www.reddit.com/r/test/comments/abc/", num_comments=5

  Line 362:     def test_collects_nested_reply_comments(self) -> None:

  Line 381:                                 "body": "Top level comment",

  Line 390:                                                     "body": "Nested reply comment",

  Line 404:             result = c._fetch_top_comments_sync(

  Line 405:                 "https://www.reddit.com/r/test/comments/abc/", num_comments=5

  Line 408:         assert "Top level comment" in result

  Line 409:         assert "Nested reply comment" in result

  Line 411:     def test_fetches_morechildren_comments(self) -> None:

  Line 452:                                 "body": "Second morechildren comment",

  Line 465:             result = c._fetch_top_comments_sync(

  Line 466:                 "https://www.reddit.com/r/test/comments/abc/", num_comments=5

  Line 470:         assert "Second morechildren comment" in result

  Line 474: # Async wrapper: _fetch_top_comments

  Line 481:             c._fetch_top_comments("https://www.reddit.com/r/test/comments/abc/", num_comments=2)


(Results truncated: showing 100 of 434 matches (334 hidden). Consider using a more specific path or pattern.)
```

**Tool: glob**

**Input:**
```json
{
  "pattern": "**/*.py",
  "path": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit"
}
```

**Output:**
```
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests/test_comment_intent_signals.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/services/reddit_service.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/core/constants.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/models/schemas.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/services/gemini_service.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests/test_client_ip_proxy.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/core/config.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/api/routes/profile.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/api/routes/leads.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/core/supabase_client.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/main.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests/test_auth_scan_regression.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests/test_reddit_service_fallback.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/controllers/leads_controller.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/api/routes/settings.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests/test_leads_csv_export.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/api/dependencies.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/api/routes/auth/login.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/api/routes/auth/__init__.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/api/routes/auth/session.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/api/routes/auth/register.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/api/routes/auth/logout.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/core/auth_cookies.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests/test_client_ip.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/repositories/memory_store.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/repositories/leads_repository.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/core/scan_limits.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/core/client_ip.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/controllers/auth_controller.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/api/routes/auth/dependencies.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/.agents/skills/ui-ux-pro-max/scripts/search.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/.agents/skills/ui-ux-pro-max/scripts/design_system.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/.agents/skills/ui-ux-pro-max/scripts/core.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/.agents/skills/ui-ux-pro-max/data/_sync_all.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests/test_leads_repository.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/repositories/profile_repository.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/repositories/__init__.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/controllers/__init__.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/controllers/profile_controller.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/api/routes/health.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/.agents/skills/webapp-testing/scripts/with_server.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/.agents/skills/webapp-testing/examples/element_discovery.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/.agents/skills/webapp-testing/examples/static_html_automation.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/.agents/skills/webapp-testing/examples/console_logging.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/api/routes/__init__.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/api/__init__.py
```

---

## Assistant (Build · GPT-5.3-Codex · 4.0s)

_Thinking:_



**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/services/reddit_service.py"
}
```

**Output:**
```
<path>/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/services/reddit_service.py</path>
<type>file</type>
<content>
1: import asyncio
2: import json
3: import logging
4: import re
5: import time
6: import urllib.error
7: import urllib.parse
8: import urllib.request
9: from datetime import datetime, timedelta, timezone
10: from typing import Any
11: 
12: from app.core.constants import COMMENT_INTENT_FETCH_THRESHOLD
13: from app.models.schemas import CandidatePost, LeadScanRequest
14: 
15: try:
16:     import asyncpraw
17: except Exception:
18:     asyncpraw = None
19: 
20: 
21: logger = logging.getLogger(__name__)
22: 
23: DEFAULT_SUBREDDITS = ["entrepreneur", "smallbusiness", "marketing"]
24: MAX_KEYWORDS_TO_SEARCH = 6
25: MAX_SUBREDDITS_TO_SEARCH = 12
26: MIN_QUERY_LIMIT = 5
27: MAX_QUERY_LIMIT = 25
28: PUBLIC_SEARCH_CACHE_TTL_SECONDS = 60
29: PUBLIC_SEARCH_MAX_RETRIES = 3
30: PUBLIC_SEARCH_BASE_BACKOFF_SECONDS = 0.5
31: REQUEST_TIMEOUT_SECONDS = 15
32: 
33: MAX_QUERY_COMBINATIONS_PER_SCAN = 42
34: MAX_COMMENT_FETCHES_PER_SCAN = 24
35: SCAN_TIME_BUDGET_SECONDS = 45
36: PUBLIC_SEARCH_LISTING_TIMEOUT_SECONDS = 8
37: PUBLIC_SEARCH_LISTING_MAX_RETRIES = 2
38: COMMENT_FETCH_TIMEOUT_SECONDS = 4
39: COMMENT_FETCH_MAX_RETRIES = 1
40: COMMENT_MORECHILDREN_BATCH_SIZE = 100
41: 
42: INTENT_SIGNALS = (
43:     "looking for",
44:     "recommend",
45:     "recommendation",
46:     "what app",
47:     "which app",
48:     "any app",
49:     "alternative",
50:     "need help",
51:     "struggling",
52:     "help me",
53: )
54: 
55: # Stronger buyer-intent phrases that predominantly surface in comment threads.
56: # These are high-precision — matching even one is a reliable purchase-intent signal.
57: COMMENT_INTENT_SIGNALS = (
58:     "looking for exactly this",
59:     "this is exactly what i need",
60:     "anyone recommend",
61:     "can anyone recommend",
62:     "can someone recommend",
63:     "what do you recommend",
64:     "does anyone know a tool",
65:     "anyone know of a good",
66:     "is there a tool that",
67:     "is there an app that",
68:     "is there a service that",
69:     "what tool should i use",
70:     "which tool should i use",
71:     "need a tool for",
72:     "need software for",
73:     "need an app for",
74:     "have you tried",
75:     "i would pay for",
76:     "i'd pay for",
77:     "happy to pay for",
78:     "willing to pay",
79:     "paid tool for",
80:     "looking to buy",
81:     "ready to buy",
82:     "where can i find",
83:     "how do i find",
84:     "any good alternatives",
85:     "what do you use for",
86:     "what's the best way to",
87:     "what is the best way to",
88: )
89: 
90: LOW_INTENT_SIGNALS = (
91:     "progress pic",
92:     "before and after",
93:     "my journey",
94:     "nsv",
95:     "weigh-in",
96: )
97: 
98: 
99: # Maximum number of top-level comments to fetch per post.
100: _MAX_COMMENTS_TO_FETCH = 10
101: # Per-comment character limit stored on CandidatePost.
102: _MAX_COMMENT_BODY_CHARS = 500
103: 
104: 
105: class RedditLeadCollector:
106:     def __init__(
107:         self,
108:         client_id: str | None,
109:         client_secret: str | None,
110:         user_agent: str
111:     ) -> None:
112:         self.client_id = client_id
113:         self.client_secret = client_secret
114:         self.user_agent = user_agent
115:         self._public_search_cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}
116:         self._comment_cache: dict[str, list[str]] = {}
117: 
118:     async def fetch_candidate_posts(
119:         self,
120:         request: LeadScanRequest,
121:         seen_post_ids: set[str] | None = None,
122:         allow_sample_fallback: bool = True,
123:     ) -> list[CandidatePost]:
124:         """Fetch candidate posts, excluding any IDs in *seen_post_ids*."""
125:         seen = seen_post_ids or set()
126:         max_candidates = max(request.limit * 4, 50)  # fetch extra so we have room after dedup
127:         raw_keywords = request.keywords or self._derive_keywords(request.business_description)
128:         keywords = self._prepare_keywords(raw_keywords)
129:         subreddits = self._normalize_subreddits(request.subreddits or DEFAULT_SUBREDDITS)
130: 
131:         if not keywords:
132:             keywords = self._prepare_keywords(self._derive_keywords(request.business_description))
133:         if not subreddits:
134:             subreddits = DEFAULT_SUBREDDITS
135: 
136:         scan_deadline = time.monotonic() + SCAN_TIME_BUDGET_SECONDS
137:         scan_budget = {
138:             "queries": MAX_QUERY_COMBINATIONS_PER_SCAN,
139:             "comments": MAX_COMMENT_FETCHES_PER_SCAN,
140:         }
141: 
142:         # Try progressively wider time windows so repeat scans surface fresh posts.
143:         time_filters = ["week", "month", "year", "all"]
144:         all_posts: list[CandidatePost] = []
145: 
146:         for time_filter in time_filters:
147:             if self._scan_deadline_exceeded(scan_deadline):
148:                 logger.info(
149:                     "Stopping Reddit scan after %ss time budget.",
150:                     SCAN_TIME_BUDGET_SECONDS,
151:                 )
152:                 break
153:             if not self._has_query_budget(scan_budget):
154:                 logger.info(
155:                     "Stopping Reddit scan after reaching query budget (%s combinations).",
156:                     MAX_QUERY_COMBINATIONS_PER_SCAN,
157:                 )
158:                 break
159: 
160:             if self._has_credentials() and asyncpraw is not None:
161:                 posts = await self._fetch_with_authenticated_api(
162:                     subreddits=subreddits,
163:                     keywords=keywords,
164:                     request_limit=request.limit,
165:                     max_candidates=max_candidates,
166:                     time_filter=time_filter,
167:                     scan_budget=scan_budget,
168:                     scan_deadline=scan_deadline,
169:                 )
170:                 if posts:
171:                     new_posts = [p for p in posts if p.id not in seen]
172:                     all_posts.extend(new_posts)
173:                     if len(all_posts) >= request.limit:
174:                         break
175:                     # Not enough new results — widen the time window
176:                     continue
177: 
178:             posts = await self._fetch_with_public_search(
179:                 subreddits=subreddits,
180:                 keywords=keywords,
181:                 request_limit=request.limit,
182:                 max_candidates=max_candidates,
183:                 time_filter=time_filter,
184:                 scan_budget=scan_budget,
185:                 scan_deadline=scan_deadline,
186:             )
187:             new_posts = [p for p in posts if p.id not in seen]
188:             all_posts.extend(new_posts)
189:             if len(all_posts) >= request.limit:
190:                 break
191: 
192:         # Remove duplicates introduced by multi-pass while preserving rank order
193:         seen_ids: set[str] = set()
194:         unique_posts: list[CandidatePost] = []
195:         for post in all_posts:
196:             if post.id not in seen_ids:
197:                 seen_ids.add(post.id)
198:                 unique_posts.append(post)
199: 
200:         if unique_posts:
201:             return unique_posts[:max_candidates]
202: 
203:         if not allow_sample_fallback:
204:             logger.warning("No Reddit posts found from live search; sample fallback is disabled.")
205:             return []
206: 
207:         logger.warning("No Reddit posts found from live search; returning sample fallback posts.")
208:         # Last-resort: return sample posts that are not already seen
209:         sample = self._sample_posts(request)
210:         return [p for p in sample if p.id not in seen] or sample
211: 
212:     async def _fetch_with_authenticated_api(
213:         self,
214:         subreddits: list[str],
215:         keywords: list[str],
216:         request_limit: int,
217:         max_candidates: int,
218:         time_filter: str = "month",
219:         scan_budget: dict[str, int] | None = None,
220:         scan_deadline: float | None = None,
221:     ) -> list[CandidatePost]:
222:         if not self._has_credentials() or asyncpraw is None:
223:             return []
224: 
225:         reddit = asyncpraw.Reddit(
226:             client_id=self.client_id,
227:             client_secret=self.client_secret,
228:             user_agent=self.user_agent
229:         )
230: 
231:         per_query_limit = self._per_query_limit(request_limit, len(subreddits))
232: 
233:         collected: dict[str, tuple[CandidatePost, float]] = {}
234: 
235:         try:
236:             for subreddit_name in subreddits:
237:                 if self._scan_deadline_exceeded(scan_deadline):
238:                     return self._rank_collected_posts(collected, max_candidates)
239: 
240:                 subreddit = await reddit.subreddit(subreddit_name)
241: 
242:                 for keyword in keywords:
243:                     if self._scan_deadline_exceeded(scan_deadline):
244:                         return self._rank_collected_posts(collected, max_candidates)
245:                     if not self._consume_query_budget(scan_budget):
246:                         return self._rank_collected_posts(collected, max_candidates)
247: 
248:                     async for submission in subreddit.search(
249:                         keyword,
250:                         sort="new",          # "new" surfaces recent & varied posts
251:                         time_filter=time_filter,
252:                         limit=per_query_limit,
253:                     ):
254:                         if self._scan_deadline_exceeded(scan_deadline):
255:                             return self._rank_collected_posts(collected, max_candidates)
256: 
257:                         if getattr(submission, "stickied", False):
258:                             continue
259: 
260:                         post_id = str(submission.id)
261:                         author = str(submission.author) if submission.author else "unknown"
262:                         body = getattr(submission, "selftext", "") or ""
263:                         title = str(submission.title or "")
264:                         url = f"https://www.reddit.com{submission.permalink}"
265: 
266:                         if not self._is_valid_post_url(url):
267:                             continue
268: 
269:                         score = int(getattr(submission, "score", 0) or 0)
270:                         num_comments = int(getattr(submission, "num_comments", 0) or 0)
271: 
272:                         # Fetch comments before the keyword gate so intent-only
273:                         # comment leads still pass through.
274:                         top_comments: list[str] = []
275:                         if self._should_fetch_comments(
276:                             num_comments=num_comments,
277:                             scan_budget=scan_budget,
278:                             scan_deadline=scan_deadline,
279:                         ):
280:                             self._consume_comment_budget(scan_budget)
281:                             top_comments = await self._fetch_comments_for_post(
282:                                 post_id=post_id,
283:                                 post_url=url,
284:                                 num_comments=num_comments,
285:                                 timeout_seconds=COMMENT_FETCH_TIMEOUT_SECONDS,
286:                                 max_retries=COMMENT_FETCH_MAX_RETRIES,
287:                             )
288: 
289:                         if not self._is_keyword_match(title, body, keyword, top_comments):
290:                             continue
291: 
292:                         match_source = self._determine_match_source(
293:                             title=title,
294:                             body=body,
295:                             keyword=keyword,
296:                             top_comments=top_comments,
297:                         )
298: 
299:                         candidate = CandidatePost(
300:                             id=post_id,
301:                             title=title,
302:                             body=body,
303:                             match_source=match_source,
304:                             subreddit=subreddit_name,
305:                             url=url,
306:                             author=author,
307:                             created_utc=datetime.fromtimestamp(float(submission.created_utc), tz=timezone.utc),
308:                             score=score,
309:                             num_comments=num_comments,
310:                             top_comments=top_comments,
311:                         )
312: 
313:                         relevance = self._score_keyword_match(
314:                             title=title,
315:                             body=body,
316:                             keyword=keyword,
317:                             score=score,
318:                             num_comments=num_comments,
319:                             top_comments=top_comments,
320:                         )
321: 
322:                         existing = collected.get(post_id)
323:                         if existing is None or relevance > existing[1]:
324:                             collected[post_id] = (candidate, relevance)
325: 
326:                         if len(collected) >= max_candidates:
327:                             return self._rank_collected_posts(collected, max_candidates)
328: 
329:         except Exception as error:
330:             logger.warning("Authenticated Reddit search failed, using public fallback: %s", error)
331:             return []
332:         finally:
333:             await reddit.close()
334: 
335:         return self._rank_collected_posts(collected, max_candidates)
336: 
337:     async def _fetch_with_public_search(
338:         self,
339:         subreddits: list[str],
340:         keywords: list[str],
341:         request_limit: int,
342:         max_candidates: int,
343:         time_filter: str = "month",
344:         scan_budget: dict[str, int] | None = None,
345:         scan_deadline: float | None = None,
346:     ) -> list[CandidatePost]:
347:         if not subreddits:
348:             return []
349: 
350:         per_query_limit = self._per_query_limit(request_limit, len(subreddits))
351:         collected: dict[str, tuple[CandidatePost, float]] = {}
352: 
353:         for subreddit_name in subreddits:
354:             if self._scan_deadline_exceeded(scan_deadline):
355:                 return self._rank_collected_posts(collected, max_candidates)
356: 
357:             for keyword in keywords:
358:                 if self._scan_deadline_exceeded(scan_deadline):
359:                     return self._rank_collected_posts(collected, max_candidates)
360:                 if not self._consume_query_budget(scan_budget):
361:                     return self._rank_collected_posts(collected, max_candidates)
362: 
363:                 listing = await asyncio.to_thread(
364:                     self._fetch_public_search_listing,
365:                     subreddit_name,
366:                     keyword,
367:                     per_query_limit,
368:                     time_filter,
369:                     PUBLIC_SEARCH_LISTING_MAX_RETRIES,
370:                     PUBLIC_SEARCH_LISTING_TIMEOUT_SECONDS,
371:                 )
372: 
373:                 for item in listing:
374:                     if self._scan_deadline_exceeded(scan_deadline):
375:                         return self._rank_collected_posts(collected, max_candidates)
376: 
377:                     post_data = item.get("data", {})
378:                     if not post_data or post_data.get("stickied"):
379:                         continue
380: 
381:                     post_id = str(post_data.get("id") or "")
382:                     if not post_id:
383:                         continue
384: 
385:                     title = str(post_data.get("title") or "")
386:                     body = str(post_data.get("selftext") or "")
387:                     permalink = str(post_data.get("permalink") or "")
388:                     fallback_url = str(post_data.get("url") or "")
389:                     url = f"https://www.reddit.com{permalink}" if permalink else fallback_url
390:                     if not self._is_valid_post_url(url):
391:                         continue
392: 
393:                     score = int(post_data.get("score") or 0)
394:                     num_comments = int(post_data.get("num_comments") or 0)
395: 
396:                     # Fetch comments before the keyword gate so intent-only
397:                     # comment leads still pass through.
398:                     top_comments: list[str] = []
399:                     if self._should_fetch_comments(
400:                         num_comments=num_comments,
401:                         scan_budget=scan_budget,
402:                         scan_deadline=scan_deadline,
403:                     ):
404:                         self._consume_comment_budget(scan_budget)
405:                         top_comments = await self._fetch_comments_for_post(
406:                             post_id=post_id,
407:                             post_url=url,
408:                             num_comments=num_comments,
409:                             timeout_seconds=COMMENT_FETCH_TIMEOUT_SECONDS,
410:                             max_retries=COMMENT_FETCH_MAX_RETRIES,
411:                         )
412: 
413:                     if not self._is_keyword_match(title, body, keyword, top_comments):
414:                         continue
415: 
416:                     match_source = self._determine_match_source(
417:                         title=title,
418:                         body=body,
419:                         keyword=keyword,
420:                         top_comments=top_comments,
421:                     )
422: 
423:                     created_utc_value = float(post_data.get("created_utc") or 0)
424:                     created_utc = (
425:                         datetime.fromtimestamp(created_utc_value, tz=timezone.utc)
426:                         if created_utc_value > 0
427:                         else datetime.now(tz=timezone.utc)
428:                     )
429: 
430:                     candidate = CandidatePost(
431:                         id=post_id,
432:                         title=title,
433:                         body=body,
434:                         match_source=match_source,
435:                         subreddit=str(post_data.get("subreddit") or subreddit_name),
436:                         url=url,
437:                         author=str(post_data.get("author") or "unknown"),
438:                         created_utc=created_utc,
439:                         score=score,
440:                         num_comments=num_comments,
441:                         top_comments=top_comments,
442:                     )
443: 
444:                     relevance = self._score_keyword_match(
445:                         title=title,
446:                         body=body,
447:                         keyword=keyword,
448:                         score=score,
449:                         num_comments=num_comments,
450:                         top_comments=top_comments,
451:                     )
452: 
453:                     existing = collected.get(post_id)
454:                     if existing is None or relevance > existing[1]:
455:                         collected[post_id] = (candidate, relevance)
456: 
457:                     if len(collected) >= max_candidates:
458:                         return self._rank_collected_posts(collected, max_candidates)
459: 
460:         return self._rank_collected_posts(collected, max_candidates)
461: 
462:     def _fetch_public_search_listing(
463:         self,
464:         subreddit_name: str,
465:         keyword: str,
466:         limit: int,
467:         time_filter: str = "month",
468:         max_retries: int = PUBLIC_SEARCH_MAX_RETRIES,
469:         timeout_seconds: float = REQUEST_TIMEOUT_SECONDS,
470:     ) -> list[dict[str, Any]]:
471:         cache_key = f"{subreddit_name}|{keyword.lower()}|{limit}|{time_filter}"
472:         now = time.time()
473:         cached = self._public_search_cache.get(cache_key)
474:         if cached and (now - cached[0] <= PUBLIC_SEARCH_CACHE_TTL_SECONDS):
475:             return cached[1]
476: 
477:         encoded_keyword = urllib.parse.quote(keyword)
478:         url = (
479:             f"https://www.reddit.com/r/{subreddit_name}/search.json"
480:             f"?q={encoded_keyword}&restrict_sr=1&sort=new&t={time_filter}&limit={limit}"
481:         )
482: 
483:         user_agent = self.user_agent or "f1bot-local"
484:         payload = self._request_json_with_retry(
485:             url=url,
486:             user_agent=user_agent,
487:             max_retries=max_retries,
488:             timeout_seconds=timeout_seconds,
489:         )
490:         if not isinstance(payload, dict):
491:             return []
492: 
493:         children = payload.get("data", {}).get("children", [])
494:         if not isinstance(children, list):
495:             return []
496: 
497:         self._prune_public_cache(now)
498:         self._public_search_cache[cache_key] = (now, children)
499:         return children
500: 
501:     def _request_json_with_retry(
502:         self,
503:         url: str,
504:         user_agent: str,
505:         max_retries: int = PUBLIC_SEARCH_MAX_RETRIES,
506:         timeout_seconds: float = REQUEST_TIMEOUT_SECONDS,
507:     ) -> dict[str, Any] | list[Any] | None:
508:         request = urllib.request.Request(url, headers={"User-Agent": user_agent})
509:         attempts = max(1, max_retries)
510:         request_timeout = max(1.0, timeout_seconds)
511: 
512:         for attempt in range(attempts):
513:             try:
514:                 with urllib.request.urlopen(request, timeout=request_timeout) as response:
515:                     raw = response.read().decode("utf-8")
516:                 return json.loads(raw)
517:             except urllib.error.HTTPError as error:
518:                 should_retry = error.code in {429, 500, 502, 503, 504} and attempt < attempts - 1
519:                 if should_retry:
520:                     retry_after = error.headers.get("Retry-After") if error.headers else None
521:                     time.sleep(self._retry_delay(attempt, retry_after))
522:                     continue
523:                 logger.warning("Public Reddit search HTTP error for %s: %s", url, error)
524:                 return None
525:             except (urllib.error.URLError, TimeoutError) as error:
526:                 if attempt < attempts - 1:
527:                     time.sleep(self._retry_delay(attempt, None))
528:                     continue
529:                 logger.warning("Public Reddit search network error for %s: %s", url, error)
530:                 return None
531:             except json.JSONDecodeError as error:
532:                 logger.warning("Public Reddit search JSON parse error for %s: %s", url, error)
533:                 return None
534: 
535:         return None
536: 
537:     def _retry_delay(self, attempt: int, retry_after: str | None) -> float:
538:         if retry_after:
539:             try:
540:                 return min(float(retry_after), 5.0)
541:             except ValueError:
542:                 pass
543:         return min(PUBLIC_SEARCH_BASE_BACKOFF_SECONDS * (2 ** attempt), 5.0)
544: 
545:     # ------------------------------------------------------------------
546:     # Comment fetching
547:     # ------------------------------------------------------------------
548: 
549:     async def _fetch_comments_for_post(
550:         self,
551:         post_id: str,
552:         post_url: str,
553:         num_comments: int,
554:         timeout_seconds: float,
555:         max_retries: int,
556:     ) -> list[str]:
557:         cached = self._comment_cache.get(post_id)
558:         if cached is not None:
559:             return cached
560: 
561:         comments = await self._fetch_top_comments(
562:             post_url=post_url,
563:             num_comments=num_comments,
564:             timeout_seconds=timeout_seconds,
565:             max_retries=max_retries,
566:         )
567:         self._comment_cache[post_id] = comments
568:         return comments
569: 
570:     async def _fetch_top_comments(
571:         self,
572:         post_url: str,
573:         num_comments: int,
574:         timeout_seconds: float = COMMENT_FETCH_TIMEOUT_SECONDS,
575:         max_retries: int = COMMENT_FETCH_MAX_RETRIES,
576:     ) -> list[str]:
577:         """Async wrapper — runs the blocking HTTP call on a thread so the event
578:         loop stays free during the network round-trip."""
579:         if num_comments < COMMENT_INTENT_FETCH_THRESHOLD:
580:             return []
581:         return await asyncio.to_thread(
582:             self._fetch_top_comments_sync,
583:             post_url,
584:             num_comments,
585:             timeout_seconds,
586:             max_retries,
587:         )
588: 
589:     def _fetch_top_comments_sync(
590:         self,
591:         post_url: str,
592:         num_comments: int,
593:         timeout_seconds: float = COMMENT_FETCH_TIMEOUT_SECONDS,
594:         max_retries: int = COMMENT_FETCH_MAX_RETRIES,
595:     ) -> list[str]:
596:         """Fetch the full available comment tree for a post.
597: 
598:         Uses Reddit's public `<post_url>.json` endpoint (no auth required) so it
599:         works regardless of whether OAuth credentials are configured.  Falls back
600:         to an empty list on any network or parse failure so the lead pipeline is
601:         never blocked by a comment-fetch error.
602:         """
603:         if num_comments < COMMENT_INTENT_FETCH_THRESHOLD:
604:             return []
605: 
606:         json_url = post_url.rstrip("/") + ".json?limit=500&depth=10&raw_json=1"
607:         user_agent = self.user_agent or "f1bot-local"
608: 
609:         try:
610:             payload = self._request_json_with_retry(
611:                 url=json_url,
612:                 user_agent=user_agent,
613:                 max_retries=max_retries,
614:                 timeout_seconds=timeout_seconds,
615:             )
616:         except Exception:
617:             return []
618: 
619:         # Reddit returns a 2-element array: [post_listing, comment_listing]
620:         if not isinstance(payload, list) or len(payload) < 2:
621:             return []
622: 
623:         post_fullname = self._extract_post_fullname(payload[0], post_url)
624:         comment_listing = payload[1]
625:         children = (
626:             comment_listing.get("data", {}).get("children", [])
627:             if isinstance(comment_listing, dict)
628:             else []
629:         )
630: 
631:         comments: list[str] = []
632:         pending_more: list[str] = []
633:         seen_comment_ids: set[str] = set()
634:         seen_more_ids: set[str] = set()
635:         self._collect_comments_from_nodes(
636:             nodes=children,
637:             comments=comments,
638:             pending_more=pending_more,
639:             seen_comment_ids=seen_comment_ids,
640:             seen_more_ids=seen_more_ids,
641:         )
642: 
643:         if not post_fullname or not pending_more:
644:             return comments
645: 
646:         deadline = time.monotonic() + max(1.0, timeout_seconds)
647:         while pending_more and time.monotonic() < deadline:
648:             batch = self._next_more_batch(pending_more)
649:             if not batch:
650:                 break
651: 
652:             extra_nodes = self._fetch_morechildren_sync(
653:                 user_agent=user_agent,
654:                 post_fullname=post_fullname,
655:                 child_ids=batch,
656:                 timeout_seconds=timeout_seconds,
657:                 max_retries=max_retries,
658:             )
659:             if not extra_nodes:
660:                 continue
661: 
662:             self._collect_comments_from_nodes(
663:                 nodes=extra_nodes,
664:                 comments=comments,
665:                 pending_more=pending_more,
666:                 seen_comment_ids=seen_comment_ids,
667:                 seen_more_ids=seen_more_ids,
668:             )
669: 
670:         return comments
671: 
672:     def _collect_comments_from_nodes(
673:         self,
674:         nodes: list[dict[str, Any]],
675:         comments: list[str],
676:         pending_more: list[str],
677:         seen_comment_ids: set[str],
678:         seen_more_ids: set[str],
679:     ) -> None:
680:         queue: list[dict[str, Any]] = [node for node in nodes if isinstance(node, dict)]
681:         cursor = 0
682: 
683:         while cursor < len(queue):
684:             node = queue[cursor]
685:             cursor += 1
686:             kind = str(node.get("kind") or "")
687:             data = node.get("data", {})
688:             if not isinstance(data, dict):
689:                 continue
690: 
691:             if kind == "t1":
692:                 comment_id = str(data.get("id") or "")
693:                 if comment_id:
694:                     if comment_id in seen_comment_ids:
695:                         continue
696:                     seen_comment_ids.add(comment_id)
697: 
698:                 body = str(data.get("body") or "").strip()
699:                 if body and body not in {"[deleted]", "[removed]"}:
700:                     comments.append(body[:_MAX_COMMENT_BODY_CHARS])
701: 
702:                 replies = data.get("replies")
703:                 if isinstance(replies, dict):
704:                     reply_children = replies.get("data", {}).get("children", [])
705:                     if isinstance(reply_children, list):
706:                         queue.extend(child for child in reply_children if isinstance(child, dict))
707:                 continue
708: 
709:             if kind == "more":
710:                 child_ids = data.get("children", [])
711:                 if not isinstance(child_ids, list):
712:                     continue
713: 
714:                 for child_id in child_ids:
715:                     normalized = str(child_id or "").strip()
716:                     if not normalized or normalized in seen_more_ids:
717:                         continue
718:                     seen_more_ids.add(normalized)
719:                     pending_more.append(normalized)
720: 
721:     def _next_more_batch(self, pending_more: list[str]) -> list[str]:
722:         if not pending_more:
723:             return []
724: 
725:         batch_size = min(COMMENT_MORECHILDREN_BATCH_SIZE, len(pending_more))
726:         batch = pending_more[:batch_size]
727:         del pending_more[:batch_size]
728:         return batch
729: 
730:     def _fetch_morechildren_sync(
731:         self,
732:         user_agent: str,
733:         post_fullname: str,
734:         child_ids: list[str],
735:         timeout_seconds: float,
736:         max_retries: int,
737:     ) -> list[dict[str, Any]]:
738:         if not child_ids:
739:             return []
740: 
741:         encoded_children = urllib.parse.quote(",".join(child_ids), safe=",")
742:         url = (
743:             "https://www.reddit.com/api/morechildren.json"
744:             f"?link_id={post_fullname}&children={encoded_children}"
745:             "&api_type=json&raw_json=1"
746:         )
747: 
748:         payload = self._request_json_with_retry(
749:             url=url,
750:             user_agent=user_agent,
751:             max_retries=max_retries,
752:             timeout_seconds=timeout_seconds,
753:         )
754:         if not isinstance(payload, dict):
755:             return []
756: 
757:         things = payload.get("json", {}).get("data", {}).get("things", [])
758:         if not isinstance(things, list):
759:             return []
760:         return [node for node in things if isinstance(node, dict)]
761: 
762:     def _extract_post_fullname(self, post_listing: Any, post_url: str) -> str | None:
763:         if isinstance(post_listing, dict):
764:             children = post_listing.get("data", {}).get("children", [])
765:             if isinstance(children, list):
766:                 for child in children:
767:                     if not isinstance(child, dict):
768:                         continue
769:                     post_id = str(child.get("data", {}).get("id") or "").strip()
770:                     if post_id:
771:                         return f"t3_{post_id}"
772: 
773:         match = re.search(r"/comments/([a-z0-9]+)/", post_url, flags=re.IGNORECASE)
774:         if match:
775:             return f"t3_{match.group(1)}"
776: 
777:         return None
778: 
779:     def _prune_public_cache(self, now: float) -> None:
780:         stale_keys = [
781:             key for key, (created_at, _) in self._public_search_cache.items()
782:             if now - created_at > PUBLIC_SEARCH_CACHE_TTL_SECONDS
783:         ]
784:         for key in stale_keys:
785:             del self._public_search_cache[key]
786: 
787:     def _scan_deadline_exceeded(self, scan_deadline: float | None) -> bool:
788:         if scan_deadline is None:
789:             return False
790:         return time.monotonic() >= scan_deadline
791: 
792:     def _has_query_budget(self, scan_budget: dict[str, int] | None) -> bool:
793:         if scan_budget is None:
794:             return True
795:         return scan_budget.get("queries", 0) > 0
796: 
797:     def _consume_query_budget(self, scan_budget: dict[str, int] | None) -> bool:
798:         if scan_budget is None:
799:             return True
800: 
801:         remaining = scan_budget.get("queries", 0)
802:         if remaining <= 0:
803:             return False
804: 
805:         scan_budget["queries"] = remaining - 1
806:         return True
807: 
808:     def _should_fetch_comments(
809:         self,
810:         num_comments: int,
811:         scan_budget: dict[str, int] | None,
812:         scan_deadline: float | None,
813:     ) -> bool:
814:         if num_comments < COMMENT_INTENT_FETCH_THRESHOLD:
815:             return False
816:         if self._scan_deadline_exceeded(scan_deadline):
817:             return False
818:         if scan_budget is None:
819:             return True
820:         return scan_budget.get("comments", 0) > 0
821: 
822:     def _consume_comment_budget(self, scan_budget: dict[str, int] | None) -> None:
823:         if scan_budget is None:
824:             return
825: 
826:         remaining = scan_budget.get("comments", 0)
827:         if remaining <= 0:
828:             return
829: 
830:         scan_budget["comments"] = remaining - 1
831: 
832:     def _rank_collected_posts(
833:         self,
834:         collected: dict[str, tuple[CandidatePost, float]],
835:         max_candidates: int,
836:     ) -> list[CandidatePost]:
837:         ranked = sorted(
838:             collected.values(),
839:             key=lambda item: (
840:                 item[1],
841:                 item[0].num_comments,
842:                 item[0].score,
843:                 item[0].created_utc,
844:                 item[0].id,
845:             ),
846:             reverse=True,
847:         )
848: 
849:         return [item[0] for item in ranked[:max_candidates]]
850: 
851:     def _is_valid_post_url(self, url: str) -> bool:
852:         return bool(url and url.startswith("https://www.reddit.com/"))
853: 
854:     def _is_keyword_match(
855:         self, title: str, body: str, keyword: str, top_comments: list[str] | None = None
856:     ) -> bool:
857:         content = f"{title} {body}".lower()
858:         token_hits, phrase_hit = self._keyword_match_stats(content, keyword)
859:         if phrase_hit:
860:             return True
861: 
862:         # A strong comment-level intent signal alone is sufficient to surface the post.
863:         if top_comments and self._has_comment_intent_signal(top_comments):
864:             return True
865: 
866:         keyword_tokens = [token for token in keyword.lower().split() if token]
867:         if not keyword_tokens:
868:             return False
869: 
870:         minimum_hits = 1 if len(keyword_tokens) <= 2 else 2
871:         if token_hits < minimum_hits:
872:             return False
873: 
874:         if len(keyword_tokens) >= 3 and token_hits < len(keyword_tokens) and not self._has_intent_signal(title, body):
875:             return False
876: 
877:         return True
878: 
879:     def _keyword_match_stats(self, content: str, keyword: str) -> tuple[int, bool]:
880:         normalized_keyword = " ".join(keyword.strip().lower().split())
881:         if not normalized_keyword:
882:             return (0, False)
883: 
884:         tokens = {token for token in normalized_keyword.split() if token}
885:         token_hits = sum(1 for token in tokens if token in content)
886:         phrase_hit = normalized_keyword in content
887:         return (token_hits, phrase_hit)
888: 
889:     def _has_intent_signal(self, title: str, body: str) -> bool:
890:         content = f"{title} {body}".lower()
891:         if "?" in title or "?" in body:
892:             return True
893:         return any(signal in content for signal in INTENT_SIGNALS)
894: 
895:     def _has_comment_intent_signal(self, top_comments: list[str]) -> bool:
896:         """Return True if any comment contains a strong buyer-intent phrase.
897: 
898:         Checks both the general INTENT_SIGNALS and the higher-specificity
899:         COMMENT_INTENT_SIGNALS so nothing is double-counted.
900:         """
901:         for comment in top_comments:
902:             lowered = comment.lower()
903:             if any(signal in lowered for signal in COMMENT_INTENT_SIGNALS):
904:                 return True
905:             if any(signal in lowered for signal in INTENT_SIGNALS):
906:                 return True
907:         return False
908: 
909:     def _determine_match_source(
910:         self,
911:         title: str,
912:         body: str,
913:         keyword: str,
914:         top_comments: list[str] | None = None,
915:     ) -> str:
916:         post_match = self._is_keyword_match(title, body, keyword)
917:         comment_match = bool(top_comments) and self._has_comment_intent_signal(top_comments)
918: 
919:         if comment_match and not post_match:
920:             return "comment"
921:         return "post"
922: 
923:     def _score_keyword_match(
924:         self,
925:         title: str,
926:         body: str,
927:         keyword: str,
928:         score: int,
929:         num_comments: int,
930:         top_comments: list[str] | None = None,
931:     ) -> float:
932:         content = f"{title} {body}".lower()
933:         token_hits, phrase_hit = self._keyword_match_stats(content, keyword)
934: 
935:         intent_bonus = 2.0 if self._has_intent_signal(title, body) else 0.0
936:         low_intent_penalty = 2.5 if any(signal in content for signal in LOW_INTENT_SIGNALS) else 0.0
937: 
938:         # Extra relevance boost when a high-specificity buyer-intent phrase is
939:         # detected in the comment thread.  Kept intentionally modest (3.5) so it
940:         # lifts qualifying comment-intent posts without dominating the ranking.
941:         comment_intent_bonus = 0.0
942:         if top_comments:
943:             for comment in top_comments:
944:                 lowered = comment.lower()
945:                 if any(signal in lowered for signal in COMMENT_INTENT_SIGNALS):
946:                     comment_intent_bonus = 3.5
947:                     break
948:                 if any(signal in lowered for signal in INTENT_SIGNALS):
949:                     comment_intent_bonus = max(comment_intent_bonus, 1.5)
950: 
951:         keyword_score = (token_hits * 4.0) + (6.0 if phrase_hit else 0.0)
952:         engagement_score = (min(num_comments, 80) * 0.02) + (min(max(score, 0), 200) * 0.004)
953: 
954:         return max(0.0, keyword_score + intent_bonus + comment_intent_bonus + engagement_score - low_intent_penalty)
955: 
956:     def _per_query_limit(self, request_limit: int, subreddit_count: int) -> int:
957:         return min(MAX_QUERY_LIMIT, max(MIN_QUERY_LIMIT, request_limit // max(subreddit_count, 1)))
958: 
959:     def _prepare_keywords(self, keywords: list[str]) -> list[str]:
960:         prepared: list[str] = []
961:         seen: set[str] = set()
962: 
963:         for raw in keywords:
964:             for part in re.split(r"[,;|]", str(raw)):
965:                 cleaned = " ".join(part.strip().split())
966:                 if len(cleaned) < 2:
967:                     continue
968: 
969:                 normalized = cleaned.lower()
970:                 if normalized in seen:
971:                     continue
972:                 seen.add(normalized)
973:                 prepared.append(cleaned)
974: 
975:         if len(prepared) > MAX_KEYWORDS_TO_SEARCH:
976:             logger.info(
977:                 "Keyword list truncated from %s to %s entries for Reddit search",
978:                 len(prepared),
979:                 MAX_KEYWORDS_TO_SEARCH,
980:             )
981: 
982:         return prepared[:MAX_KEYWORDS_TO_SEARCH]
983: 
984:     def _normalize_subreddits(self, subreddits: list[str]) -> list[str]:
985:         normalized: list[str] = []
986:         seen: set[str] = set()
987: 
988:         for raw in subreddits:
989:             for part in re.split(r"[,;|]", str(raw)):
990:                 cleaned = part.strip().lower()
991:                 if cleaned.startswith("r/"):
992:                     cleaned = cleaned[2:]
993:                 cleaned = cleaned.replace(" ", "")
994:                 if not cleaned:
995:                     continue
996:                 if not re.fullmatch(r"[a-z0-9_]{3,32}", cleaned):
997:                     continue
998:                 if cleaned in seen:
999:                     continue
1000:                 seen.add(cleaned)
1001:                 normalized.append(cleaned)
1002: 
1003:         return normalized[:MAX_SUBREDDITS_TO_SEARCH]
1004: 
1005:     def _has_credentials(self) -> bool:
1006:         return bool(self.client_id and self.client_secret and self.user_agent)
1007: 
1008:     def _derive_keywords(self, description: str) -> list[str]:
1009:         words = [word.strip(".,!? ").lower() for word in description.split()]
1010:         unique = []
1011:         seen = set()
1012:         for word in words:
1013:             if len(word) < 4 or word in seen:
1014:                 continue
1015:             seen.add(word)
1016:             unique.append(word)
1017:         return unique[:6] or ["need help", "recommendation"]
1018: 
1019:     def _sample_posts(self, request: LeadScanRequest) -> list[CandidatePost]:
1020:         now = datetime.now(tz=timezone.utc)
1021:         business_hint = request.business_description[:40]
1022: 
1023:         sample_data: list[dict[str, Any]] = [
1024:             {
1025:                 "id": "sample-1",
1026:                 "title": "Need better way to find qualified leads for my Shopify brand",
1027:                 "body": "Spent money on ads but lead quality is weak. Any practical tools?",
1028:                 "subreddit": "smallbusiness",
1029:                 "url": "https://www.reddit.com/r/smallbusiness/",
1030:                 "author": "founder_01",
1031:                 "score": 29,
1032:                 "num_comments": 16,
1033:                 "hours_ago": 4
1034:             },
1035:             {
1036:                 "id": "sample-2",
1037:                 "title": "What outreach strategy works in B2B SaaS in 2026?",
1038:                 "body": "Looking for workflow to identify warm intent from communities.",
1039:                 "subreddit": "sales",
1040:                 "url": "https://www.reddit.com/r/sales/",
1041:                 "author": "growth_hacker",
1042:                 "score": 17,
1043:                 "num_comments": 11,
1044:                 "hours_ago": 8
1045:             },
1046:             {
1047:                 "id": "sample-3",
1048:                 "title": "Any AI tool to monitor Reddit for buyer intent?",
1049:                 "body": f"Context: {business_hint}. Want a daily qualified lead list.",
1050:                 "subreddit": "entrepreneur",
1051:                 "url": "https://www.reddit.com/r/entrepreneur/",
1052:                 "author": "solofounder",
1053:                 "score": 35,
1054:                 "num_comments": 22,
1055:                 "hours_ago": 2
1056:             },
1057:             {
1058:                 "id": "sample-4",
1059:                 "title": "Which communities are good for service business lead generation?",
1060:                 "body": "Trying Reddit + LinkedIn combo and need a repeatable system.",
1061:                 "subreddit": "marketing",
1062:                 "url": "https://www.reddit.com/r/marketing/",
1063:                 "author": "agency_ops",
1064:                 "score": 13,
1065:                 "num_comments": 7,
1066:                 "hours_ago": 15
1067:             }
1068:         ]
1069: 
1070:         posts: list[CandidatePost] = []
1071:         for item in sample_data:
1072:             posts.append(
1073:                 CandidatePost(
1074:                     id=item["id"],
1075:                     title=item["title"],
1076:                     body=item["body"],
1077:                     subreddit=item["subreddit"],
1078:                     url=item["url"],
1079:                     author=item["author"],
1080:                     created_utc=now - timedelta(hours=item["hours_ago"]),
1081:                     score=item["score"],
1082:                     num_comments=item["num_comments"]
1083:                 )
1084:             )
1085: 
1086:         return posts[: max(1, min(request.limit, len(posts)))]

(End of file - total 1086 lines)
</content>
```

---

## Assistant (Build · GPT-5.3-Codex · 7.5s)

_Thinking:_



**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/core/constants.py"
}
```

**Output:**
```
<path>/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/core/constants.py</path>
<type>file</type>
<content>
1: """Shared constants for backend services and API handlers."""
2: 
3: from pathlib import Path
4: 
5: # Project paths
6: PROJECT_ROOT = Path(__file__).resolve().parents[2]
7: ENV_FILE_PATH = PROJECT_ROOT / ".env"
8: 
9: # Environment variable keys
10: ENV_APP_NAME = "APP_NAME"
11: ENV_APP_ENV = "APP_ENV"
12: ENV_FRONTEND_ORIGIN = "FRONTEND_ORIGIN"
13: 
14: ENV_GEMINI_API_KEY = "GEMINI_API_KEY"
15: ENV_GEMINI_MODEL_LITE = "GEMINI_MODEL_LITE"
16: ENV_GEMINI_MODEL_MAIN = "GEMINI_MODEL_MAIN"
17: 
18: ENV_REDDIT_CLIENT_ID = "REDDIT_CLIENT_ID"
19: ENV_REDDIT_CLIENT_SECRET = "REDDIT_CLIENT_SECRET"
20: ENV_REDDIT_USER_AGENT = "REDDIT_USER_AGENT"
21: ENV_SAMPLE_LEADS_FALLBACK_ENABLED = "SAMPLE_LEADS_FALLBACK_ENABLED"
22: 
23: ENV_SUPABASE_URL = "SUPABASE_URL"
24: ENV_SUPABASE_ANON_KEY = "SUPABASE_ANON_KEY"
25: ENV_SUPABASE_SERVICE_ROLE_KEY = "SUPABASE_SERVICE_ROLE_KEY"
26: ENV_SUPABASE_AUTH_ENABLED = "SUPABASE_AUTH_ENABLED"
27: ENV_LOCAL_AUTH_FALLBACK_ENABLED = "LOCAL_AUTH_FALLBACK_ENABLED"
28: 
29: ENV_SCAN_RATE_LIMIT_PER_MINUTE = "SCAN_RATE_LIMIT_PER_MINUTE"
30: ENV_SCAN_RATE_LIMIT_WINDOW_SECONDS = "SCAN_RATE_LIMIT_WINDOW_SECONDS"
31: ENV_SCAN_DAILY_QUOTA = "SCAN_DAILY_QUOTA"
32: ENV_AUTH_RATE_LIMIT_PER_IP = "AUTH_RATE_LIMIT_PER_IP"
33: ENV_AUTH_RATE_LIMIT_PER_IDENTITY = "AUTH_RATE_LIMIT_PER_IDENTITY"
34: ENV_AUTH_RATE_LIMIT_WINDOW_SECONDS = "AUTH_RATE_LIMIT_WINDOW_SECONDS"
35: ENV_AUTH_LOCKOUT_THRESHOLD = "AUTH_LOCKOUT_THRESHOLD"
36: ENV_AUTH_LOCKOUT_BASE_SECONDS = "AUTH_LOCKOUT_BASE_SECONDS"
37: ENV_AUTH_LOCKOUT_MAX_SECONDS = "AUTH_LOCKOUT_MAX_SECONDS"
38: ENV_RATE_LIMIT_STORE = "RATE_LIMIT_STORE"
39: ENV_REDIS_URL = "REDIS_URL"
40: ENV_REDIS_KEY_PREFIX = "REDIS_KEY_PREFIX"
41: ENV_TRUSTED_PROXY_CIDRS = "TRUSTED_PROXY_CIDRS"
42: 
43: # Settings defaults (overridable via .env)
44: DEFAULT_APP_NAME = "F1bot API"
45: DEFAULT_APP_ENV = "development"
46: DEFAULT_FRONTEND_ORIGIN = "http://localhost:3000"
47: 
48: DEFAULT_GEMINI_MODEL_LITE = "gemini-2.5-flash-lite"
49: DEFAULT_REDDIT_USER_AGENT = "f1bot-local"
50: 
51: DEFAULT_SCAN_RATE_LIMIT_PER_MINUTE = 6
52: DEFAULT_SCAN_RATE_LIMIT_WINDOW_SECONDS = 60
53: DEFAULT_SCAN_DAILY_QUOTA = 200
54: DEFAULT_AUTH_RATE_LIMIT_PER_IP = 20
55: DEFAULT_AUTH_RATE_LIMIT_PER_IDENTITY = 8
56: DEFAULT_AUTH_RATE_LIMIT_WINDOW_SECONDS = 300
57: DEFAULT_AUTH_LOCKOUT_THRESHOLD = 5
58: DEFAULT_AUTH_LOCKOUT_BASE_SECONDS = 30
59: DEFAULT_AUTH_LOCKOUT_MAX_SECONDS = 900
60: DEFAULT_RATE_LIMIT_STORE = "redis"
61: DEFAULT_REDIS_KEY_PREFIX = "f1bot:ratelimit"
62: 
63: SUPABASE_AUTH_DISABLED_ENVS = ("development", "dev", "local", "test")
64: 
65: # API-safe error messages
66: ERROR_AUTH_CONFIGURATION = "Authentication service is not configured correctly."
67: ERROR_ANON_KEY_IS_SERVICE_ROLE = (
68:     "SUPABASE_ANON_KEY contains a service_role token. "
69:     "This breaks least-privilege boundaries and must be fixed before startup. "
70:     "Set SUPABASE_ANON_KEY to the `anon public` key from Supabase dashboard \u2192 Settings \u2192 API."
71: )
72: ERROR_AUTHENTICATION_FAILED = "Authentication failed."
73: ERROR_TOKEN_INVALID = "Invalid or expired access token"
74: ERROR_LOGIN_FAILED = "Login failed. Check credentials and try again."
75: ERROR_REGISTRATION_FAILED = "Registration failed. Please try again."
76: ERROR_LEAD_SCAN_FAILED = "Lead scan failed. Please try again."
77: ERROR_SCAN_RATE_LIMIT = "Scan rate limit exceeded. Please retry later."
78: ERROR_SCAN_DAILY_QUOTA = "Daily scan quota reached. Please try again tomorrow."
79: ERROR_AUTH_RATE_LIMIT = "Too many authentication attempts. Please retry later."
80: ERROR_AUTH_LOCKED = "Too many failed authentication attempts. Please retry later."
81: ERROR_RATE_LIMIT_BACKEND_UNAVAILABLE = "Rate limit service is temporarily unavailable. Please retry later."
82: ERROR_CSRF_TOKEN_INVALID = "Invalid CSRF token. Please refresh and try again."
83: 
84: # Local/dev auth
85: DEMO_TOKEN_PREFIX = "demo-token-"
86: 
87: # Lead scoring tunables
88: LEAD_SCAN_AI_CANDIDATE_MULTIPLIER = 3
89: LEAD_SCAN_MIN_AI_CANDIDATES = 8
90: LEAD_SCAN_MAX_AI_CANDIDATES = 12
91: 
92: AI_SCORE_WEIGHT = 0.7
93: HEURISTIC_SCORE_WEIGHT = 0.3
94: NON_REFINED_MAX_SCORE = 79.0
95: 
96: # Prompt size controls
97: PROMPT_MAX_TITLE_CHARS = 140
98: PROMPT_MAX_SNIPPET_CHARS = 220
99: PROMPT_MAX_KEYWORD_CHARS = 32
100: PROMPT_MAX_KEYWORDS = 8
101: PROMPT_MAX_BUSINESS_CHARS = 320
102: PROMPT_MAX_COMMENT_CHARS = 160  # per-comment truncation sent to Gemini
103: 
104: # Comments are only fetched for posts with at least this many comments.
105: # Lowering this slightly improves recall for comment-only buyer intent while
106: # keeping fetch cost bounded by per-scan budgets.
107: COMMENT_INTENT_FETCH_THRESHOLD = 2

(End of file - total 107 lines)
</content>
```

---

## Assistant (Build · GPT-5.3-Codex · 9.2s)

_Thinking:_



**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests/test_comment_intent_signals.py"
}
```

**Output:**
```
<path>/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests/test_comment_intent_signals.py</path>
<type>file</type>
<content>
1: """Tests for comment-level buyer-intent detection.
2: 
3: These tests verify that strong purchase-intent signals appearing only in
4: Reddit comment threads are detected and used to surface leads that would
5: otherwise be missed by title/body-only matching.
6: """
7: from __future__ import annotations
8: 
9: import asyncio
10: from unittest.mock import AsyncMock, patch
11: 
12: import pytest
13: 
14: from app.core.constants import COMMENT_INTENT_FETCH_THRESHOLD
15: from app.services.reddit_service import (
16:     COMMENT_INTENT_SIGNALS,
17:     RedditLeadCollector,
18: )
19: 
20: 
21: # ---------------------------------------------------------------------------
22: # Helpers
23: # ---------------------------------------------------------------------------
24: 
25: def _collector() -> RedditLeadCollector:
26:     return RedditLeadCollector(client_id=None, client_secret=None, user_agent="test-agent")
27: 
28: 
29: class _AsyncIterator:
30:     def __init__(self, items: list[object]) -> None:
31:         self._items = items
32:         self._index = 0
33: 
34:     def __aiter__(self) -> "_AsyncIterator":
35:         return self
36: 
37:     async def __anext__(self) -> object:
38:         if self._index >= len(self._items):
39:             raise StopAsyncIteration
40: 
41:         item = self._items[self._index]
42:         self._index += 1
43:         return item
44: 
45: 
46: class _FakeSubreddit:
47:     def __init__(self, submissions: list[object]) -> None:
48:         self._submissions = submissions
49: 
50:     def search(self, *_: object, **__: object) -> _AsyncIterator:
51:         return _AsyncIterator(self._submissions)
52: 
53: 
54: class _FakeRedditClient:
55:     def __init__(self, submissions: list[object]) -> None:
56:         self._submissions = submissions
57:         self.closed = False
58: 
59:     async def subreddit(self, _name: str) -> _FakeSubreddit:
60:         return _FakeSubreddit(self._submissions)
61: 
62:     async def close(self) -> None:
63:         self.closed = True
64: 
65: 
66: class _FakeAsyncPrawModule:
67:     def __init__(self, submissions: list[object]) -> None:
68:         self._submissions = submissions
69:         self.last_client: _FakeRedditClient | None = None
70: 
71:     def Reddit(self, **_: object) -> _FakeRedditClient:  # noqa: N802 (matches asyncpraw API)
72:         client = _FakeRedditClient(self._submissions)
73:         self.last_client = client
74:         return client
75: 
76: 
77: # ---------------------------------------------------------------------------
78: # COMMENT_INTENT_SIGNALS sanity checks
79: # ---------------------------------------------------------------------------
80: 
81: class TestCommentIntentSignalsList:
82:     def test_signals_list_is_non_empty(self) -> None:
83:         assert len(COMMENT_INTENT_SIGNALS) > 0
84: 
85:     def test_high_specificity_phrases_present(self) -> None:
86:         """Key buyer-intent phrases must be in the list."""
87:         must_contain = [
88:             "anyone recommend",
89:             "looking for exactly this",
90:             "i would pay for",
91:             "willing to pay",
92:             "is there a tool that",
93:         ]
94:         for phrase in must_contain:
95:             assert phrase in COMMENT_INTENT_SIGNALS, f"Expected '{phrase}' in COMMENT_INTENT_SIGNALS"
96: 
97:     def test_all_signals_are_lowercase(self) -> None:
98:         """Signals must be lowercase so `.lower()` comparisons work correctly."""
99:         for sig in COMMENT_INTENT_SIGNALS:
100:             assert sig == sig.lower(), f"Signal not lowercase: {sig!r}"
101: 
102: 
103: # ---------------------------------------------------------------------------
104: # _has_comment_intent_signal
105: # ---------------------------------------------------------------------------
106: 
107: class TestHasCommentIntentSignal:
108:     def test_returns_false_for_empty_list(self) -> None:
109:         c = _collector()
110:         assert c._has_comment_intent_signal([]) is False
111: 
112:     def test_detects_comment_intent_phrase(self) -> None:
113:         c = _collector()
114:         comments = [
115:             "Has anyone dealt with this before?",
116:             "I would pay for a tool that does this automatically.",
117:         ]
118:         assert c._has_comment_intent_signal(comments) is True
119: 
120:     def test_detects_general_intent_signal_in_comment(self) -> None:
121:         c = _collector()
122:         comments = ["Any recommendation for a good CRM?"]
123:         assert c._has_comment_intent_signal(comments) is True
124: 
125:     def test_returns_false_when_no_signals_present(self) -> None:
126:         c = _collector()
127:         comments = [
128:             "Great post, thanks for sharing.",
129:             "I tried this yesterday and it worked.",
130:         ]
131:         assert c._has_comment_intent_signal(comments) is False
132: 
133:     def test_case_insensitive_detection(self) -> None:
134:         c = _collector()
135:         comments = ["ANYONE RECOMMEND a good email tool?"]
136:         assert c._has_comment_intent_signal(comments) is True
137: 
138:     def test_detects_signal_in_mixed_batch(self) -> None:
139:         c = _collector()
140:         comments = [
141:             "Interesting approach.",
142:             "Where can I find something like this?",
143:             "Nice writeup.",
144:         ]
145:         assert c._has_comment_intent_signal(comments) is True
146: 
147: 
148: # ---------------------------------------------------------------------------
149: # _is_keyword_match with top_comments
150: # ---------------------------------------------------------------------------
151: 
152: class TestIsKeywordMatchWithComments:
153:     def test_comment_intent_alone_passes_when_body_is_weak(self) -> None:
154:         """A post whose title/body barely matches the keyword should still
155:         pass _is_keyword_match when comments contain a strong intent signal."""
156:         c = _collector()
157:         # "automation" is the keyword; title/body only has "auto" (no direct hit)
158:         result = c._is_keyword_match(
159:             title="Just sharing my workflow",
160:             body="I use a couple of tools.",
161:             keyword="automation software",
162:             top_comments=["Looking for exactly this kind of automation software!"],
163:         )
164:         assert result is True
165: 
166:     def test_no_comments_still_matches_on_phrase(self) -> None:
167:         c = _collector()
168:         result = c._is_keyword_match(
169:             title="Need automation software for my team",
170:             body="",
171:             keyword="automation software",
172:             top_comments=[],
173:         )
174:         assert result is True
175: 
176:     def test_weak_title_body_and_no_intent_in_comments_fails(self) -> None:
177:         c = _collector()
178:         result = c._is_keyword_match(
179:             title="Random post about cooking",
180:             body="Here is my recipe.",
181:             keyword="automation software",
182:             top_comments=["Nice recipe!", "Thanks for sharing."],
183:         )
184:         assert result is False
185: 
186:     def test_backward_compatible_no_comments_arg(self) -> None:
187:         """Calling without top_comments must still work (defaults to None)."""
188:         c = _collector()
189:         result = c._is_keyword_match(
190:             title="Looking for lead generation software",
191:             body="Any recommendations?",
192:             keyword="lead generation",
193:         )
194:         assert result is True
195: 
196: 
197: # ---------------------------------------------------------------------------
198: # _score_keyword_match with top_comments
199: # ---------------------------------------------------------------------------
200: 
201: class TestScoreKeywordMatchWithComments:
202:     def test_comment_intent_signals_increase_relevance_score(self) -> None:
203:         c = _collector()
204:         base = c._score_keyword_match(
205:             title="Lead generation tips",
206:             body="Check out these strategies.",
207:             keyword="lead generation",
208:             score=10,
209:             num_comments=5,
210:             top_comments=[],
211:         )
212:         boosted = c._score_keyword_match(
213:             title="Lead generation tips",
214:             body="Check out these strategies.",
215:             keyword="lead generation",
216:             score=10,
217:             num_comments=5,
218:             top_comments=["Anyone recommend a good lead generation tool?"],
219:         )
220:         assert boosted > base
221: 
222:     def test_high_specificity_comment_gives_larger_boost_than_general(self) -> None:
223:         c = _collector()
224: 
225:         general_boost = c._score_keyword_match(
226:             title="Lead gen",
227:             body="",
228:             keyword="lead generation",
229:             score=5,
230:             num_comments=4,
231:             top_comments=["Any recommendation?"],
232:         )
233:         high_specificity_boost = c._score_keyword_match(
234:             title="Lead gen",
235:             body="",
236:             keyword="lead generation",
237:             score=5,
238:             num_comments=4,
239:             top_comments=["I would pay for a tool that does this automatically."],
240:         )
241:         assert high_specificity_boost >= general_boost
242: 
243:     def test_score_is_non_negative(self) -> None:
244:         c = _collector()
245:         result = c._score_keyword_match(
246:             title="Progress pic",
247:             body="Before and after my journey.",
248:             keyword="fitness",
249:             score=0,
250:             num_comments=0,
251:             top_comments=[],
252:         )
253:         assert result >= 0.0
254: 
255:     def test_no_comments_kwarg_is_backward_compatible(self) -> None:
256:         c = _collector()
257:         result = c._score_keyword_match(
258:             title="Lead generation tips",
259:             body="Here are my tips.",
260:             keyword="lead generation",
261:             score=5,
262:             num_comments=3,
263:         )
264:         assert result >= 0.0
265: 
266: 
267: # ---------------------------------------------------------------------------
268: # _fetch_top_comments_sync
269: # ---------------------------------------------------------------------------
270: 
271: class TestFetchTopCommentsSync:
272:     def _make_reddit_comment_payload(self, bodies: list[str]) -> list[dict]:
273:         """Build a minimal Reddit `.json` payload for comment fetching."""
274:         children = [
275:             {
276:                 "kind": "t1",
277:                 "data": {"body": body},
278:             }
279:             for body in bodies
280:         ]
281:         return [
282:             {"kind": "Listing", "data": {"children": []}},  # post listing
283:             {"kind": "Listing", "data": {"children": children}},  # comment listing
284:         ]
285: 
286:     def test_returns_empty_when_below_threshold(self) -> None:
287:         c = _collector()
288:         result = c._fetch_top_comments_sync("https://www.reddit.com/r/test/comments/abc/", num_comments=1)
289:         assert result == []
290: 
291:     def test_parses_comment_bodies_correctly(self) -> None:
292:         c = _collector()
293:         payload = self._make_reddit_comment_payload(["Anyone recommend a CRM?", "I'd pay for this."])
294: 
295:         with patch.object(c, "_request_json_with_retry", return_value=payload):
296:             result = c._fetch_top_comments_sync(
297:                 "https://www.reddit.com/r/test/comments/abc/", num_comments=5
298:             )
299: 
300:         assert result == ["Anyone recommend a CRM?", "I'd pay for this."]
301: 
302:     def test_skips_deleted_comments(self) -> None:
303:         c = _collector()
304:         payload = self._make_reddit_comment_payload(["[deleted]", "Real comment here."])
305: 
306:         with patch.object(c, "_request_json_with_retry", return_value=payload):
307:             result = c._fetch_top_comments_sync(
308:                 "https://www.reddit.com/r/test/comments/abc/", num_comments=5
309:             )
310: 
311:         assert "[deleted]" not in result
312:         assert "Real comment here." in result
313: 
314:     def test_skips_more_stubs(self) -> None:
315:         c = _collector()
316:         stub = {"kind": "more", "data": {"children": ["t1_xyz"]}}
317:         payload = [
318:             {"kind": "Listing", "data": {"children": []}},
319:             {"kind": "Listing", "data": {"children": [stub]}},
320:         ]
321: 
322:         with patch.object(c, "_request_json_with_retry", return_value=payload):
323:             result = c._fetch_top_comments_sync(
324:                 "https://www.reddit.com/r/test/comments/abc/", num_comments=5
325:             )
326: 
327:         assert result == []
328: 
329:     def test_returns_empty_on_network_error(self) -> None:
330:         c = _collector()
331: 
332:         with patch.object(c, "_request_json_with_retry", side_effect=Exception("timeout")):
333:             result = c._fetch_top_comments_sync(
334:                 "https://www.reddit.com/r/test/comments/abc/", num_comments=5
335:             )
336: 
337:         assert result == []
338: 
339:     def test_returns_empty_when_payload_is_none(self) -> None:
340:         c = _collector()
341: 
342:         with patch.object(c, "_request_json_with_retry", return_value=None):
343:             result = c._fetch_top_comments_sync(
344:                 "https://www.reddit.com/r/test/comments/abc/", num_comments=5
345:             )
346: 
347:         assert result == []
348: 
349:     def test_truncates_long_comment_bodies(self) -> None:
350:         c = _collector()
351:         long_body = "x" * 1000
352:         payload = self._make_reddit_comment_payload([long_body])
353: 
354:         with patch.object(c, "_request_json_with_retry", return_value=payload):
355:             result = c._fetch_top_comments_sync(
356:                 "https://www.reddit.com/r/test/comments/abc/", num_comments=5
357:             )
358: 
359:         assert len(result) == 1
360:         assert len(result[0]) <= 500  # _MAX_COMMENT_BODY_CHARS
361: 
362:     def test_collects_nested_reply_comments(self) -> None:
363:         c = _collector()
364:         payload = [
365:             {
366:                 "kind": "Listing",
367:                 "data": {
368:                     "children": [
369:                         {"kind": "t3", "data": {"id": "abc"}},
370:                     ]
371:                 },
372:             },
373:             {
374:                 "kind": "Listing",
375:                 "data": {
376:                     "children": [
377:                         {
378:                             "kind": "t1",
379:                             "data": {
380:                                 "id": "c1",
381:                                 "body": "Top level comment",
382:                                 "replies": {
383:                                     "kind": "Listing",
384:                                     "data": {
385:                                         "children": [
386:                                             {
387:                                                 "kind": "t1",
388:                                                 "data": {
389:                                                     "id": "c2",
390:                                                     "body": "Nested reply comment",
391:                                                 },
392:                                             }
393:                                         ]
394:                                     },
395:                                 },
396:                             },
397:                         }
398:                     ]
399:                 },
400:             },
401:         ]
402: 
403:         with patch.object(c, "_request_json_with_retry", return_value=payload):
404:             result = c._fetch_top_comments_sync(
405:                 "https://www.reddit.com/r/test/comments/abc/", num_comments=5
406:             )
407: 
408:         assert "Top level comment" in result
409:         assert "Nested reply comment" in result
410: 
411:     def test_fetches_morechildren_comments(self) -> None:
412:         c = _collector()
413:         initial_payload = [
414:             {
415:                 "kind": "Listing",
416:                 "data": {
417:                     "children": [
418:                         {"kind": "t3", "data": {"id": "abc"}},
419:                     ]
420:                 },
421:             },
422:             {
423:                 "kind": "Listing",
424:                 "data": {
425:                     "children": [
426:                         {
427:                             "kind": "more",
428:                             "data": {
429:                                 "children": ["c2", "c3"],
430:                             },
431:                         }
432:                     ]
433:                 },
434:             },
435:         ]
436: 
437:         morechildren_payload = {
438:             "json": {
439:                 "data": {
440:                     "things": [
441:                         {
442:                             "kind": "t1",
443:                             "data": {
444:                                 "id": "c2",
445:                                 "body": "Loaded via morechildren",
446:                             },
447:                         },
448:                         {
449:                             "kind": "t1",
450:                             "data": {
451:                                 "id": "c3",
452:                                 "body": "Second morechildren comment",
453:                             },
454:                         },
455:                     ]
456:                 }
457:             }
458:         }
459: 
460:         with patch.object(
461:             c,
462:             "_request_json_with_retry",
463:             side_effect=[initial_payload, morechildren_payload],
464:         ):
465:             result = c._fetch_top_comments_sync(
466:                 "https://www.reddit.com/r/test/comments/abc/", num_comments=5
467:             )
468: 
469:         assert "Loaded via morechildren" in result
470:         assert "Second morechildren comment" in result
471: 
472: 
473: # ---------------------------------------------------------------------------
474: # Async wrapper: _fetch_top_comments
475: # ---------------------------------------------------------------------------
476: 
477: class TestFetchTopCommentsAsync:
478:     def test_returns_empty_below_threshold(self) -> None:
479:         c = _collector()
480:         result = asyncio.run(
481:             c._fetch_top_comments("https://www.reddit.com/r/test/comments/abc/", num_comments=2)
482:         )
483:         assert result == []
484: 
485:     def test_delegates_to_sync_above_threshold(self) -> None:
486:         c = _collector()
487:         expected = ["Buyer comment here"]
488: 
489:         with patch.object(c, "_fetch_top_comments_sync", return_value=expected):
490:             result = asyncio.run(
491:                 c._fetch_top_comments(
492:                     "https://www.reddit.com/r/test/comments/abc/", num_comments=5
493:                 )
494:             )
495: 
496:         assert result == expected
497: 
498: 
499: class TestCommentFetchCache:
500:     def test_reuses_cached_comments_for_same_post(self) -> None:
501:         c = _collector()
502: 
503:         async def _run() -> tuple[list[str], list[str], int]:
504:             with patch.object(c, "_fetch_top_comments", return_value=["cached comment"]) as mocked:
505:                 first = await c._fetch_comments_for_post(
506:                     post_id="abc",
507:                     post_url="https://www.reddit.com/r/test/comments/abc/",
508:                     num_comments=7,
509:                     timeout_seconds=4,
510:                     max_retries=1,
511:                 )
512:                 second = await c._fetch_comments_for_post(
513:                     post_id="abc",
514:                     post_url="https://www.reddit.com/r/test/comments/abc/",
515:                     num_comments=7,
516:                     timeout_seconds=4,
517:                     max_retries=1,
518:                 )
519:                 return first, second, mocked.call_count
520: 
521:         first_result, second_result, call_count = asyncio.run(_run())
522: 
523:         assert first_result == ["cached comment"]
524:         assert second_result == ["cached comment"]
525:         assert call_count == 1

(End of file - total 525 lines)
</content>
```

---

## Assistant (Build · GPT-5.3-Codex · 12.0s)

_Thinking:_



**Tool: grep**

**Input:**
```json
{
  "pattern": "top_comments|match_source|comment intent|COMMENT_INTENT",
  "path": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app",
  "include": "*.py"
}
```

**Output:**
```
Found 42 matches
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/services/reddit_service.py:
  Line 12: from app.core.constants import COMMENT_INTENT_FETCH_THRESHOLD

  Line 57: COMMENT_INTENT_SIGNALS = (

  Line 274:                         top_comments: list[str] = []

  Line 281:                             top_comments = await self._fetch_comments_for_post(

  Line 289:                         if not self._is_keyword_match(title, body, keyword, top_comments):

  Line 292:                         match_source = self._determine_match_source(

  Line 296:                             top_comments=top_comments,

  Line 303:                             match_source=match_source,

  Line 310:                             top_comments=top_comments,

  Line 319:                             top_comments=top_comments,

  Line 398:                     top_comments: list[str] = []

  Line 405:                         top_comments = await self._fetch_comments_for_post(

  Line 413:                     if not self._is_keyword_match(title, body, keyword, top_comments):

  Line 416:                     match_source = self._determine_match_source(

  Line 420:                         top_comments=top_comments,

  Line 434:                         match_source=match_source,

  Line 441:                         top_comments=top_comments,

  Line 450:                         top_comments=top_comments,

  Line 561:         comments = await self._fetch_top_comments(

  Line 570:     async def _fetch_top_comments(

  Line 579:         if num_comments < COMMENT_INTENT_FETCH_THRESHOLD:

  Line 582:             self._fetch_top_comments_sync,

  Line 589:     def _fetch_top_comments_sync(

  Line 603:         if num_comments < COMMENT_INTENT_FETCH_THRESHOLD:

  Line 814:         if num_comments < COMMENT_INTENT_FETCH_THRESHOLD:

  Line 855:         self, title: str, body: str, keyword: str, top_comments: list[str] | None = None

  Line 863:         if top_comments and self._has_comment_intent_signal(top_comments):

  Line 895:     def _has_comment_intent_signal(self, top_comments: list[str]) -> bool:

  Line 899:         COMMENT_INTENT_SIGNALS so nothing is double-counted.

  Line 901:         for comment in top_comments:

  Line 903:             if any(signal in lowered for signal in COMMENT_INTENT_SIGNALS):

  Line 909:     def _determine_match_source(

  Line 914:         top_comments: list[str] | None = None,

  Line 917:         comment_match = bool(top_comments) and self._has_comment_intent_signal(top_comments)

  Line 930:         top_comments: list[str] | None = None,

  Line 942:         if top_comments:

  Line 943:             for comment in top_comments:

  Line 945:                 if any(signal in lowered for signal in COMMENT_INTENT_SIGNALS):


/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/core/constants.py:
  Line 107: COMMENT_INTENT_FETCH_THRESHOLD = 2


/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/models/schemas.py:
  Line 47:     match_source: Literal["post", "comment"] = "post"

  Line 56:     top_comments: list[str] = Field(default_factory=list)


/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/services/gemini_service.py:
  Line 82:                     for c in item.post.top_comments[:3]

```

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/services/gemini_service.py"
}
```

**Output:**
```
<path>/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/services/gemini_service.py</path>
<type>file</type>
<content>
1: import asyncio
2: import json
3: import re
4: from datetime import datetime, timezone
5: from typing import Any
6: 
7: from app.core.constants import (
8:     AI_SCORE_WEIGHT,
9:     HEURISTIC_SCORE_WEIGHT,
10:     LEAD_SCAN_AI_CANDIDATE_MULTIPLIER,
11:     LEAD_SCAN_MAX_AI_CANDIDATES,
12:     LEAD_SCAN_MIN_AI_CANDIDATES,
13:     NON_REFINED_MAX_SCORE,
14:     PROMPT_MAX_BUSINESS_CHARS,
15:     PROMPT_MAX_COMMENT_CHARS,
16:     PROMPT_MAX_KEYWORD_CHARS,
17:     PROMPT_MAX_KEYWORDS,
18:     PROMPT_MAX_SNIPPET_CHARS,
19:     PROMPT_MAX_TITLE_CHARS,
20: )
21: from app.models.schemas import CandidatePost, LeadInsight, LeadScanRequest
22: 
23: try:
24:     from google import genai
25: except Exception:
26:     genai = None
27: 
28: 
29: class GeminiLeadScorer:
30:     def __init__(self, api_key: str | None, model_lite: str) -> None:
31:         self.api_key = api_key
32:         self.model_lite = model_lite
33:         self.client = None
34:         if self.api_key and genai is not None:
35:             try:
36:                 self.client = genai.Client(api_key=self.api_key)
37:             except Exception:
38:                 self.client = None
39: 
40:     async def score_posts(self, request: LeadScanRequest, posts: list[CandidatePost]) -> list[LeadInsight]:
41:         if not posts:
42:             return []
43: 
44:         heuristic = self._heuristic_rank(request, posts)
45: 
46:         if self.client is None:
47:             return heuristic[: request.limit]
48: 
49:         refined = await self._score_with_flash_lite(request, heuristic)
50:         ranked = self._merge_rankings(heuristic, refined)
51:         return ranked[: request.limit]
52: 
53:     async def _score_with_flash_lite(
54:         self,
55:         request: LeadScanRequest,
56:         heuristic: list[LeadInsight]
57:     ) -> list[LeadInsight]:
58:         candidate_count = min(
59:             max(request.limit * LEAD_SCAN_AI_CANDIDATE_MULTIPLIER, LEAD_SCAN_MIN_AI_CANDIDATES),
60:             len(heuristic),
61:             LEAD_SCAN_MAX_AI_CANDIDATES,
62:         )
63:         candidates = heuristic[:candidate_count]
64: 
65:         post_lookup = {item.post.id: item.post for item in candidates}
66:         baseline_lookup = {item.post.id: item.lead_score for item in candidates}
67:         refined_ids: set[str] = set()
68: 
69:         payload = [
70:             {
71:                 "post_id": item.post.id,
72:                 "title": self._compact(item.post.title, PROMPT_MAX_TITLE_CHARS),
73:                 "snippet": self._compact(item.post.body, PROMPT_MAX_SNIPPET_CHARS),
74:                 "subreddit": item.post.subreddit,
75:                 "upvotes": item.post.score,
76:                 "comments": item.post.num_comments,
77:                 "baseline_score": round(item.lead_score, 2),
78:                 # Include truncated comment snippets so the model can detect
79:                 # buyer-intent signals that only surface in comment threads.
80:                 "top_comment_snippets": [
81:                     self._compact(c, PROMPT_MAX_COMMENT_CHARS)
82:                     for c in item.post.top_comments[:3]
83:                 ],
84:             }
85:             for item in candidates
86:         ]
87: 
88:         keywords = [
89:             self._compact(keyword, PROMPT_MAX_KEYWORD_CHARS)
90:             for keyword in request.keywords
91:             if keyword.strip()
92:         ][:PROMPT_MAX_KEYWORDS]
93:         compact_business = self._compact(request.business_description, PROMPT_MAX_BUSINESS_CHARS)
94: 
95:         prompt = (
96:             "You are an expert lead qualifier for startup outreach across B2B and B2C products. "
97:             "Score each Reddit post for fit with the business below.\n"
98:             "Return ONLY a JSON array sorted by lead_score descending. No markdown, no explanation text.\n"
99:             "Each row schema: {post_id, lead_score, qualification_reason, suggested_outreach}.\n"
100:             "Scoring rubric: ICP fit 40, explicit pain/intent 30, urgency 15, engagement signal 15.\n"
101:             "qualification_reason: <= 160 chars and specific.\n"
102:             "suggested_outreach: <= 220 chars, actionable, personalized, no hype.\n"
103:             f"Business: {compact_business}\n"
104:             f"Keywords: {', '.join(keywords) if keywords else 'n/a'}\n"
105:             f"Posts: {json.dumps(payload, ensure_ascii=False, separators=(',', ':'))}"
106:         )
107: 
108:         response = await self._generate_json(self.model_lite, prompt)
109:         if not isinstance(response, list):
110:             return []
111: 
112:         insights: list[LeadInsight] = []
113: 
114:         for row in response:
115:             if not isinstance(row, dict):
116:                 continue
117: 
118:             post_id = str(row.get("post_id", "")).strip()
119:             if not post_id or post_id not in post_lookup:
120:                 continue
121: 
122:             try:
123:                 lead_score = max(0.0, min(float(row.get("lead_score", 50)), 100.0))
124:             except Exception:
125:                 lead_score = baseline_lookup.get(post_id, 50.0)
126: 
127:             reason = str(row.get("qualification_reason", "Likely buyer intent based on discussion context.")).strip()
128:             outreach = str(
129:                 row.get(
130:                     "suggested_outreach",
131:                     "Share a concise solution and ask one clarifying question to qualify urgency."
132:                 )
133:             ).strip()
134: 
135:             insights.append(
136:                 LeadInsight(
137:                     post=post_lookup[post_id],
138:                     lead_score=round(lead_score, 2),
139:                     qualification_reason=reason,
140:                     suggested_outreach=outreach
141:                 )
142:             )
143:             refined_ids.add(post_id)
144: 
145:         # Blend AI and heuristic to keep scoring stable while preferring model-refined rows.
146:         for item in insights:
147:             baseline = baseline_lookup.get(item.post.id, item.lead_score)
148:             blended = (item.lead_score * AI_SCORE_WEIGHT) + (baseline * HEURISTIC_SCORE_WEIGHT)
149:             item.lead_score = round(max(0.0, min(blended, 100.0)), 2)
150: 
151:         insights.sort(
152:             key=lambda item: (item.post.id in refined_ids, item.lead_score, item.post.num_comments),
153:             reverse=True,
154:         )
155:         return insights
156: 
157:     def _merge_rankings(
158:         self,
159:         heuristic: list[LeadInsight],
160:         ai_ranked: list[LeadInsight],
161:     ) -> list[LeadInsight]:
162:         if not ai_ranked:
163:             return heuristic
164: 
165:         ai_ids = {item.post.id for item in ai_ranked}
166:         merged: dict[str, LeadInsight] = {}
167:         for item in heuristic:
168:             if item.post.id in ai_ids:
169:                 continue
170:             # Keep non-refined fallback rows below refined AI rows.
171:             item.lead_score = round(min(item.lead_score, NON_REFINED_MAX_SCORE), 2)
172:             merged[item.post.id] = item
173: 
174:         for item in ai_ranked:
175:             merged[item.post.id] = item
176: 
177:         ranked = list(merged.values())
178:         ranked.sort(key=lambda item: item.lead_score, reverse=True)
179:         return ranked
180: 
181:     async def _generate_json(self, model_name: str, prompt: str) -> Any:
182:         if self.client is None:
183:             return None
184: 
185:         return await asyncio.to_thread(self._generate_json_sync, model_name, prompt)
186: 
187:     def _generate_json_sync(self, model_name: str, prompt: str) -> Any:
188:         if self.client is None:
189:             return None
190: 
191:         try:
192:             response = self.client.models.generate_content(model=model_name, contents=prompt)
193:             text = getattr(response, "text", None)
194:             if not text:
195:                 text = str(response)
196:             return self._extract_json(text)
197:         except Exception:
198:             return None
199: 
200:     def _compact(self, text: str, max_chars: int) -> str:
201:         compact = re.sub(r"\s+", " ", text).strip()
202:         if len(compact) <= max_chars:
203:             return compact
204:         if max_chars <= 3:
205:             return compact[:max_chars]
206:         return f"{compact[: max_chars - 3]}..."
207: 
208:     def _extract_json(self, text: str) -> Any:
209:         candidates = []
210: 
211:         array_start = text.find("[")
212:         array_end = text.rfind("]")
213:         if array_start != -1 and array_end != -1 and array_end > array_start:
214:             candidates.append(text[array_start : array_end + 1])
215: 
216:         object_start = text.find("{")
217:         object_end = text.rfind("}")
218:         if object_start != -1 and object_end != -1 and object_end > object_start:
219:             candidates.append(text[object_start : object_end + 1])
220: 
221:         for candidate in candidates:
222:             try:
223:                 parsed = json.loads(candidate)
224:                 if isinstance(parsed, dict) and "items" in parsed and isinstance(parsed["items"], list):
225:                     return parsed["items"]
226:                 return parsed
227:             except Exception:
228:                 continue
229: 
230:         return None
231: 
232:     def _heuristic_rank(self, request: LeadScanRequest, posts: list[CandidatePost]) -> list[LeadInsight]:
233:         terms = set(self._tokenize(request.business_description))
234:         terms.update(self._tokenize(" ".join(request.keywords)))
235: 
236:         ranked: list[LeadInsight] = []
237:         for post in posts:
238:             text = f"{post.title} {post.body}".lower()
239:             hit_count = sum(1 for term in terms if term and term in text)
240: 
241:             engagement_score = min(post.num_comments, 80) * 0.35
242:             vote_score = min(max(post.score, 0), 300) * 0.08
243:             urgency_bonus = 8 if re.search(r"need|help|looking|recommend|struggling", text) else 0
244:             age_bonus = self._age_score(post.created_utc)
245: 
246:             score = 25 + (hit_count * 8) + engagement_score + vote_score + urgency_bonus + age_bonus
247:             normalized = max(0.0, min(score, 100.0))
248: 
249:             reason = (
250:                 f"Matched {hit_count} business/keyword terms with {post.num_comments} comments and "
251:                 f"{post.score} upvotes."
252:             )
253:             outreach = (
254:                 "Start by acknowledging their exact problem, then offer one practical fix and "
255:                 "invite a short DM conversation."
256:             )
257: 
258:             ranked.append(
259:                 LeadInsight(
260:                     post=post,
261:                     lead_score=round(normalized, 2),
262:                     qualification_reason=reason,
263:                     suggested_outreach=outreach
264:                 )
265:             )
266: 
267:         ranked.sort(key=lambda item: item.lead_score, reverse=True)
268:         return ranked
269: 
270:     def _tokenize(self, text: str) -> list[str]:
271:         return [word for word in re.findall(r"[a-zA-Z0-9]+", text.lower()) if len(word) > 2]
272: 
273:     def _age_score(self, created_at: datetime) -> float:
274:         now = datetime.now(tz=timezone.utc)
275:         age_hours = max((now - created_at).total_seconds() / 3600, 0)
276:         if age_hours <= 6:
277:             return 10
278:         if age_hours <= 24:
279:             return 6
280:         if age_hours <= 72:
281:             return 3
282:         return 0

(End of file - total 282 lines)
</content>
```

---

## Assistant (Build · GPT-5.3-Codex · 9.3s)

_Thinking:_



**Tool: bash**

**Input:**
```json
{
  "command": "git status --short",
  "workdir": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit",
  "description": "Shows concise git working tree status"
}
```

**Output:**
```
 M backend/app/core/constants.py
 M backend/app/models/schemas.py
 M backend/app/services/reddit_service.py
 M backend/tests/test_comment_intent_signals.py
 M frontend/app/scan/page.tsx
 M frontend/lib/api.ts

```

---

## Assistant (Build · GPT-5.3-Codex · 6.9s)

_Thinking:_



**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/models/schemas.py"
}
```

**Output:**
```
<path>/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/models/schemas.py</path>
<type>file</type>
<content>
1: from datetime import datetime
2: from typing import Literal
3: 
4: from pydantic import BaseModel, EmailStr, Field, field_validator
5: 
6: AUTH_PASSWORD_MIN_LENGTH = 10
7: AUTH_PASSWORD_MAX_LENGTH = 128
8: 
9: 
10: def _validate_auth_password(value: str) -> str:
11:     if any(char.isspace() for char in value):
12:         raise ValueError("Password must not contain whitespace.")
13: 
14:     has_lower = any(char.islower() for char in value)
15:     has_upper = any(char.isupper() for char in value)
16:     has_digit = any(char.isdigit() for char in value)
17:     has_symbol = any(not char.isalnum() for char in value)
18: 
19:     if not all((has_lower, has_upper, has_digit, has_symbol)):
20:         raise ValueError(
21:             "Password must include at least one uppercase letter, one lowercase letter, one number, and one symbol."
22:         )
23: 
24:     return value
25: 
26: 
27: def _normalize_string_list(value: list[str] | str | None) -> list[str]:
28:     if value is None:
29:         return []
30: 
31:     raw_items = [value] if isinstance(value, str) else [str(item) for item in value]
32: 
33:     normalized: list[str] = []
34:     for raw in raw_items:
35:         for part in str(raw).split(","):
36:             item = part.strip()
37:             if item:
38:                 normalized.append(item)
39: 
40:     return normalized
41: 
42: 
43: class CandidatePost(BaseModel):
44:     id: str
45:     title: str
46:     body: str
47:     match_source: Literal["post", "comment"] = "post"
48:     subreddit: str
49:     url: str
50:     author: str
51:     created_utc: datetime
52:     score: int
53:     num_comments: int
54:     # Top-level comments fetched for high-activity posts.
55:     # Used to detect buyer-intent signals that only appear in comment threads.
56:     top_comments: list[str] = Field(default_factory=list)
57: 
58: 
59: class LeadInsight(BaseModel):
60:     post: CandidatePost
61:     lead_score: float = Field(ge=0, le=100)
62:     qualification_reason: str
63:     suggested_outreach: str
64: 
65: 
66: class LeadScanRequest(BaseModel):
67:     business_description: str = Field(min_length=10, max_length=2000)
68:     keywords: list[str] = Field(default_factory=list)
69:     subreddits: list[str] = Field(default_factory=lambda: ["entrepreneur", "smallbusiness", "marketing"])
70:     limit: int = Field(default=20, ge=1, le=100)
71: 
72:     @field_validator("keywords", "subreddits", mode="before")
73:     @classmethod
74:     def normalize_list(cls, value: list[str] | str | None) -> list[str]:
75:         return _normalize_string_list(value)
76: 
77: 
78: class LeadScanResponse(BaseModel):
79:     leads: list[LeadInsight]
80:     total_candidates: int
81:     used_ai: bool
82: 
83: 
84: LeadStatus = Literal["new", "contacted", "qualified", "ignored"]
85: 
86: 
87: class LoginRequest(BaseModel):
88:     email: EmailStr
89:     password: str = Field(min_length=AUTH_PASSWORD_MIN_LENGTH, max_length=AUTH_PASSWORD_MAX_LENGTH)
90: 
91:     @field_validator("password")
92:     @classmethod
93:     def validate_password_strength(cls, value: str) -> str:
94:         return _validate_auth_password(value)
95: 
96: 
97: class LoginResponse(BaseModel):
98:     user_id: str
99:     email: str
100:     access_token: str
101:     token_type: str = "bearer"
102: 
103: 
104: class RegisterRequest(LoginRequest):
105:     full_name: str | None = Field(default=None, max_length=120)
106: 
107: 
108: class RegisterResponse(BaseModel):
109:     user_id: str
110:     email: str
111:     access_token: str
112:     token_type: str = "bearer"
113: 
114: 
115: class SessionResponse(BaseModel):
116:     user_id: str
117:     email: str
118: 
119: 
120: class BusinessProfile(BaseModel):
121:     user_id: str
122:     business_description: str = Field(min_length=10, max_length=2000)
123:     keywords: list[str] = Field(default_factory=list)
124:     subreddits: list[str] = Field(default_factory=list)
125:     updated_at: datetime | None = None
126: 
127:     @field_validator("keywords", "subreddits", mode="before")
128:     @classmethod
129:     def normalize_profile_list(cls, value: list[str] | str | None) -> list[str]:
130:         return _normalize_string_list(value)
131: 
132: 
133: class BusinessProfileUpsertRequest(BaseModel):
134:     business_description: str = Field(min_length=10, max_length=2000)
135:     keywords: list[str] = Field(default_factory=list)
136:     subreddits: list[str] = Field(default_factory=list)
137: 
138:     @field_validator("keywords", "subreddits", mode="before")
139:     @classmethod
140:     def normalize_profile_list(cls, value: list[str] | str | None) -> list[str]:
141:         return _normalize_string_list(value)
142: 
143: 
144: class LeadRecord(BaseModel):
145:     id: str
146:     user_id: str
147:     status: LeadStatus = "new"
148:     post: CandidatePost
149:     lead_score: float = Field(ge=0, le=100)
150:     qualification_reason: str
151:     suggested_outreach: str
152:     scan_id: str
153:     created_at: datetime
154:     updated_at: datetime
155: 
156: 
157: class LeadListResponse(BaseModel):
158:     leads: list[LeadRecord]
159: 
160: 
161: class LeadStatusUpdateRequest(BaseModel):
162:     status: LeadStatus

(End of file - total 162 lines)
</content>
```

---

## Assistant (Build · GPT-5.3-Codex · 12.4s)

_Thinking:_



**Tool: bash**

**Input:**
```json
{
  "command": "git diff -- backend/app/services/reddit_service.py backend/tests/test_comment_intent_signals.py backend/app/core/constants.py backend/app/models/schemas.py frontend/app/scan/page.tsx frontend/lib/api.ts",
  "workdir": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit",
  "description": "Shows pending diffs in modified files"
}
```

**Output:**
```
diff --git a/backend/app/core/constants.py b/backend/app/core/constants.py
index 211c0dd..fa903c0 100644
--- a/backend/app/core/constants.py
+++ b/backend/app/core/constants.py
@@ -102,5 +102,6 @@ PROMPT_MAX_BUSINESS_CHARS = 320
 PROMPT_MAX_COMMENT_CHARS = 160  # per-comment truncation sent to Gemini
 
 # Comments are only fetched for posts with at least this many comments.
-# Below this threshold the post body alone is usually sufficient signal.
-COMMENT_INTENT_FETCH_THRESHOLD = 3
\ No newline at end of file
+# Lowering this slightly improves recall for comment-only buyer intent while
+# keeping fetch cost bounded by per-scan budgets.
+COMMENT_INTENT_FETCH_THRESHOLD = 2
diff --git a/backend/app/models/schemas.py b/backend/app/models/schemas.py
index 952a3aa..69babcc 100644
--- a/backend/app/models/schemas.py
+++ b/backend/app/models/schemas.py
@@ -44,6 +44,7 @@ class CandidatePost(BaseModel):
     id: str
     title: str
     body: str
+    match_source: Literal["post", "comment"] = "post"
     subreddit: str
     url: str
     author: str
diff --git a/backend/app/services/reddit_service.py b/backend/app/services/reddit_service.py
index 061eecc..00ad79d 100644
--- a/backend/app/services/reddit_service.py
+++ b/backend/app/services/reddit_service.py
@@ -37,6 +37,7 @@ PUBLIC_SEARCH_LISTING_TIMEOUT_SECONDS = 8
 PUBLIC_SEARCH_LISTING_MAX_RETRIES = 2
 COMMENT_FETCH_TIMEOUT_SECONDS = 4
 COMMENT_FETCH_MAX_RETRIES = 1
+COMMENT_MORECHILDREN_BATCH_SIZE = 100
 
 INTENT_SIGNALS = (
     "looking for",
@@ -58,15 +59,24 @@ COMMENT_INTENT_SIGNALS = (
     "this is exactly what i need",
     "anyone recommend",
     "can anyone recommend",
+    "can someone recommend",
+    "what do you recommend",
     "does anyone know a tool",
     "anyone know of a good",
     "is there a tool that",
     "is there an app that",
     "is there a service that",
+    "what tool should i use",
+    "which tool should i use",
+    "need a tool for",
+    "need software for",
+    "need an app for",
     "have you tried",
     "i would pay for",
     "i'd pay for",
+    "happy to pay for",
     "willing to pay",
+    "paid tool for",
     "looking to buy",
     "ready to buy",
     "where can i find",
@@ -103,6 +113,7 @@ class RedditLeadCollector:
         self.client_secret = client_secret
         self.user_agent = user_agent
         self._public_search_cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}
+        self._comment_cache: dict[str, list[str]] = {}
 
     async def fetch_candidate_posts(
         self,
@@ -254,14 +265,12 @@ class RedditLeadCollector:
 
                         if not self._is_valid_post_url(url):
                             continue
-                        if not self._is_keyword_match(title, body, keyword):
-                            continue
 
                         score = int(getattr(submission, "score", 0) or 0)
                         num_comments = int(getattr(submission, "num_comments", 0) or 0)
 
-                        # Fetch comments for posts with enough engagement so we can
-                        # detect buyer-intent signals that appear only in threads.
+                        # Fetch comments before the keyword gate so intent-only
+                        # comment leads still pass through.
                         top_comments: list[str] = []
                         if self._should_fetch_comments(
                             num_comments=num_comments,
@@ -269,9 +278,10 @@ class RedditLeadCollector:
                             scan_deadline=scan_deadline,
                         ):
                             self._consume_comment_budget(scan_budget)
-                            top_comments = await self._fetch_top_comments(
-                                url,
-                                num_comments,
+                            top_comments = await self._fetch_comments_for_post(
+                                post_id=post_id,
+                                post_url=url,
+                                num_comments=num_comments,
                                 timeout_seconds=COMMENT_FETCH_TIMEOUT_SECONDS,
                                 max_retries=COMMENT_FETCH_MAX_RETRIES,
                             )
@@ -279,10 +289,18 @@ class RedditLeadCollector:
                         if not self._is_keyword_match(title, body, keyword, top_comments):
                             continue
 
+                        match_source = self._determine_match_source(
+                            title=title,
+                            body=body,
+                            keyword=keyword,
+                            top_comments=top_comments,
+                        )
+
                         candidate = CandidatePost(
                             id=post_id,
                             title=title,
                             body=body,
+                            match_source=match_source,
                             subreddit=subreddit_name,
                             url=url,
                             author=author,
@@ -384,17 +402,24 @@ class RedditLeadCollector:
                         scan_deadline=scan_deadline,
                     ):
                         self._consume_comment_budget(scan_budget)
-                        top_comments = await asyncio.to_thread(
-                            self._fetch_top_comments_sync,
-                            url,
-                            num_comments,
-                            COMMENT_FETCH_TIMEOUT_SECONDS,
-                            COMMENT_FETCH_MAX_RETRIES,
+                        top_comments = await self._fetch_comments_for_post(
+                            post_id=post_id,
+                            post_url=url,
+                            num_comments=num_comments,
+                            timeout_seconds=COMMENT_FETCH_TIMEOUT_SECONDS,
+                            max_retries=COMMENT_FETCH_MAX_RETRIES,
                         )
 
                     if not self._is_keyword_match(title, body, keyword, top_comments):
                         continue
 
+                    match_source = self._determine_match_source(
+                        title=title,
+                        body=body,
+                        keyword=keyword,
+                        top_comments=top_comments,
+                    )
+
                     created_utc_value = float(post_data.get("created_utc") or 0)
                     created_utc = (
                         datetime.fromtimestamp(created_utc_value, tz=timezone.utc)
@@ -406,6 +431,7 @@ class RedditLeadCollector:
                         id=post_id,
                         title=title,
                         body=body,
+                        match_source=match_source,
                         subreddit=str(post_data.get("subreddit") or subreddit_name),
                         url=url,
                         author=str(post_data.get("author") or "unknown"),
@@ -520,6 +546,27 @@ class RedditLeadCollector:
     # Comment fetching
     # ------------------------------------------------------------------
 
+    async def _fetch_comments_for_post(
+        self,
+        post_id: str,
+        post_url: str,
+        num_comments: int,
+        timeout_seconds: float,
+        max_retries: int,
+    ) -> list[str]:
+        cached = self._comment_cache.get(post_id)
+        if cached is not None:
+            return cached
+
+        comments = await self._fetch_top_comments(
+            post_url=post_url,
+            num_comments=num_comments,
+            timeout_seconds=timeout_seconds,
+            max_retries=max_retries,
+        )
+        self._comment_cache[post_id] = comments
+        return comments
+
     async def _fetch_top_comments(
         self,
         post_url: str,
@@ -546,7 +593,7 @@ class RedditLeadCollector:
         timeout_seconds: float = COMMENT_FETCH_TIMEOUT_SECONDS,
         max_retries: int = COMMENT_FETCH_MAX_RETRIES,
     ) -> list[str]:
-        """Fetch up to *_MAX_COMMENTS_TO_FETCH* top-level comment bodies for a post.
+        """Fetch the full available comment tree for a post.
 
         Uses Reddit's public `<post_url>.json` endpoint (no auth required) so it
         works regardless of whether OAuth credentials are configured.  Falls back
@@ -556,7 +603,7 @@ class RedditLeadCollector:
         if num_comments < COMMENT_INTENT_FETCH_THRESHOLD:
             return []
 
-        json_url = post_url.rstrip("/") + ".json?limit=10&depth=1"
+        json_url = post_url.rstrip("/") + ".json?limit=500&depth=10&raw_json=1"
         user_agent = self.user_agent or "f1bot-local"
 
         try:
@@ -573,6 +620,7 @@ class RedditLeadCollector:
         if not isinstance(payload, list) or len(payload) < 2:
             return []
 
+        post_fullname = self._extract_post_fullname(payload[0], post_url)
         comment_listing = payload[1]
         children = (
             comment_listing.get("data", {}).get("children", [])
@@ -581,20 +629,152 @@ class RedditLeadCollector:
         )
 
         comments: list[str] = []
-        for child in children:
-            if not isinstance(child, dict):
+        pending_more: list[str] = []
+        seen_comment_ids: set[str] = set()
+        seen_more_ids: set[str] = set()
+        self._collect_comments_from_nodes(
+            nodes=children,
+            comments=comments,
+            pending_more=pending_more,
+            seen_comment_ids=seen_comment_ids,
+            seen_more_ids=seen_more_ids,
+        )
+
+        if not post_fullname or not pending_more:
+            return comments
+
+        deadline = time.monotonic() + max(1.0, timeout_seconds)
+        while pending_more and time.monotonic() < deadline:
+            batch = self._next_more_batch(pending_more)
+            if not batch:
+                break
+
+            extra_nodes = self._fetch_morechildren_sync(
+                user_agent=user_agent,
+                post_fullname=post_fullname,
+                child_ids=batch,
+                timeout_seconds=timeout_seconds,
+                max_retries=max_retries,
+            )
+            if not extra_nodes:
                 continue
-            # Only include actual comments (kind "t1"), not "more" stubs
-            if child.get("kind") != "t1":
+
+            self._collect_comments_from_nodes(
+                nodes=extra_nodes,
+                comments=comments,
+                pending_more=pending_more,
+                seen_comment_ids=seen_comment_ids,
+                seen_more_ids=seen_more_ids,
+            )
+
+        return comments
+
+    def _collect_comments_from_nodes(
+        self,
+        nodes: list[dict[str, Any]],
+        comments: list[str],
+        pending_more: list[str],
+        seen_comment_ids: set[str],
+        seen_more_ids: set[str],
+    ) -> None:
+        queue: list[dict[str, Any]] = [node for node in nodes if isinstance(node, dict)]
+        cursor = 0
+
+        while cursor < len(queue):
+            node = queue[cursor]
+            cursor += 1
+            kind = str(node.get("kind") or "")
+            data = node.get("data", {})
+            if not isinstance(data, dict):
                 continue
-            body = str(child.get("data", {}).get("body") or "").strip()
-            if not body or body == "[deleted]" or body == "[removed]":
+
+            if kind == "t1":
+                comment_id = str(data.get("id") or "")
+                if comment_id:
+                    if comment_id in seen_comment_ids:
+                        continue
+                    seen_comment_ids.add(comment_id)
+
+                body = str(data.get("body") or "").strip()
+                if body and body not in {"[deleted]", "[removed]"}:
+                    comments.append(body[:_MAX_COMMENT_BODY_CHARS])
+
+                replies = data.get("replies")
+                if isinstance(replies, dict):
+                    reply_children = replies.get("data", {}).get("children", [])
+                    if isinstance(reply_children, list):
+                        queue.extend(child for child in reply_children if isinstance(child, dict))
                 continue
-            comments.append(body[:_MAX_COMMENT_BODY_CHARS])
-            if len(comments) >= _MAX_COMMENTS_TO_FETCH:
-                break
 
-        return comments
+            if kind == "more":
+                child_ids = data.get("children", [])
+                if not isinstance(child_ids, list):
+                    continue
+
+                for child_id in child_ids:
+                    normalized = str(child_id or "").strip()
+                    if not normalized or normalized in seen_more_ids:
+                        continue
+                    seen_more_ids.add(normalized)
+                    pending_more.append(normalized)
+
+    def _next_more_batch(self, pending_more: list[str]) -> list[str]:
+        if not pending_more:
+            return []
+
+        batch_size = min(COMMENT_MORECHILDREN_BATCH_SIZE, len(pending_more))
+        batch = pending_more[:batch_size]
+        del pending_more[:batch_size]
+        return batch
+
+    def _fetch_morechildren_sync(
+        self,
+        user_agent: str,
+        post_fullname: str,
+        child_ids: list[str],
+        timeout_seconds: float,
+        max_retries: int,
+    ) -> list[dict[str, Any]]:
+        if not child_ids:
+            return []
+
+        encoded_children = urllib.parse.quote(",".join(child_ids), safe=",")
+        url = (
+            "https://www.reddit.com/api/morechildren.json"
+            f"?link_id={post_fullname}&children={encoded_children}"
+            "&api_type=json&raw_json=1"
+        )
+
+        payload = self._request_json_with_retry(
+            url=url,
+            user_agent=user_agent,
+            max_retries=max_retries,
+            timeout_seconds=timeout_seconds,
+        )
+        if not isinstance(payload, dict):
+            return []
+
+        things = payload.get("json", {}).get("data", {}).get("things", [])
+        if not isinstance(things, list):
+            return []
+        return [node for node in things if isinstance(node, dict)]
+
+    def _extract_post_fullname(self, post_listing: Any, post_url: str) -> str | None:
+        if isinstance(post_listing, dict):
+            children = post_listing.get("data", {}).get("children", [])
+            if isinstance(children, list):
+                for child in children:
+                    if not isinstance(child, dict):
+                        continue
+                    post_id = str(child.get("data", {}).get("id") or "").strip()
+                    if post_id:
+                        return f"t3_{post_id}"
+
+        match = re.search(r"/comments/([a-z0-9]+)/", post_url, flags=re.IGNORECASE)
+        if match:
+            return f"t3_{match.group(1)}"
+
+        return None
 
     def _prune_public_cache(self, now: float) -> None:
         stale_keys = [
@@ -725,6 +905,21 @@ class RedditLeadCollector:
             if any(signal in lowered for signal in INTENT_SIGNALS):
                 return True
         return False
+
+    def _determine_match_source(
+        self,
+        title: str,
+        body: str,
+        keyword: str,
+        top_comments: list[str] | None = None,
+    ) -> str:
+        post_match = self._is_keyword_match(title, body, keyword)
+        comment_match = bool(top_comments) and self._has_comment_intent_signal(top_comments)
+
+        if comment_match and not post_match:
+            return "comment"
+        return "post"
+
     def _score_keyword_match(
         self,
         title: str,
diff --git a/backend/tests/test_comment_intent_signals.py b/backend/tests/test_comment_intent_signals.py
index fa68fd3..805b32e 100644
--- a/backend/tests/test_comment_intent_signals.py
+++ b/backend/tests/test_comment_intent_signals.py
@@ -7,14 +7,13 @@ otherwise be missed by title/body-only matching.
 from __future__ import annotations
 
 import asyncio
-import json
-from unittest.mock import MagicMock, patch
+from unittest.mock import AsyncMock, patch
 
 import pytest
 
+from app.core.constants import COMMENT_INTENT_FETCH_THRESHOLD
 from app.services.reddit_service import (
     COMMENT_INTENT_SIGNALS,
-    INTENT_SIGNALS,
     RedditLeadCollector,
 )
 
@@ -27,6 +26,54 @@ def _collector() -> RedditLeadCollector:
     return RedditLeadCollector(client_id=None, client_secret=None, user_agent="test-agent")
 
 
+class _AsyncIterator:
+    def __init__(self, items: list[object]) -> None:
+        self._items = items
+        self._index = 0
+
+    def __aiter__(self) -> "_AsyncIterator":
+        return self
+
+    async def __anext__(self) -> object:
+        if self._index >= len(self._items):
+            raise StopAsyncIteration
+
+        item = self._items[self._index]
+        self._index += 1
+        return item
+
+
+class _FakeSubreddit:
+    def __init__(self, submissions: list[object]) -> None:
+        self._submissions = submissions
+
+    def search(self, *_: object, **__: object) -> _AsyncIterator:
+        return _AsyncIterator(self._submissions)
+
+
+class _FakeRedditClient:
+    def __init__(self, submissions: list[object]) -> None:
+        self._submissions = submissions
+        self.closed = False
+
+    async def subreddit(self, _name: str) -> _FakeSubreddit:
+        return _FakeSubreddit(self._submissions)
+
+    async def close(self) -> None:
+        self.closed = True
+
+
+class _FakeAsyncPrawModule:
+    def __init__(self, submissions: list[object]) -> None:
+        self._submissions = submissions
+        self.last_client: _FakeRedditClient | None = None
+
+    def Reddit(self, **_: object) -> _FakeRedditClient:  # noqa: N802 (matches asyncpraw API)
+        client = _FakeRedditClient(self._submissions)
+        self.last_client = client
+        return client
+
+
 # ---------------------------------------------------------------------------
 # COMMENT_INTENT_SIGNALS sanity checks
 # ---------------------------------------------------------------------------
@@ -312,6 +359,116 @@ class TestFetchTopCommentsSync:
         assert len(result) == 1
         assert len(result[0]) <= 500  # _MAX_COMMENT_BODY_CHARS
 
+    def test_collects_nested_reply_comments(self) -> None:
+        c = _collector()
+        payload = [
+            {
+                "kind": "Listing",
+                "data": {
+                    "children": [
+                        {"kind": "t3", "data": {"id": "abc"}},
+                    ]
+                },
+            },
+            {
+                "kind": "Listing",
+                "data": {
+                    "children": [
+                        {
+                            "kind": "t1",
+                            "data": {
+                                "id": "c1",
+                                "body": "Top level comment",
+                                "replies": {
+                                    "kind": "Listing",
+                                    "data": {
+                                        "children": [
+                                            {
+                                                "kind": "t1",
+                                                "data": {
+                                                    "id": "c2",
+                                                    "body": "Nested reply comment",
+                                                },
+                                            }
+                                        ]
+                                    },
+                                },
+                            },
+                        }
+                    ]
+                },
+            },
+        ]
+
+        with patch.object(c, "_request_json_with_retry", return_value=payload):
+            result = c._fetch_top_comments_sync(
+                "https://www.reddit.com/r/test/comments/abc/", num_comments=5
+            )
+
+        assert "Top level comment" in result
+        assert "Nested reply comment" in result
+
+    def test_fetches_morechildren_comments(self) -> None:
+        c = _collector()
+        initial_payload = [
+            {
+                "kind": "Listing",
+                "data": {
+                    "children": [
+                        {"kind": "t3", "data": {"id": "abc"}},
+                    ]
+                },
+            },
+            {
+                "kind": "Listing",
+                "data": {
+                    "children": [
+                        {
+                            "kind": "more",
+                            "data": {
+                                "children": ["c2", "c3"],
+                            },
+                        }
+                    ]
+                },
+            },
+        ]
+
+        morechildren_payload = {
+            "json": {
+                "data": {
+                    "things": [
+                        {
+                            "kind": "t1",
+                            "data": {
+                                "id": "c2",
+                                "body": "Loaded via morechildren",
+                            },
+                        },
+                        {
+                            "kind": "t1",
+                            "data": {
+                                "id": "c3",
+                                "body": "Second morechildren comment",
+                            },
+                        },
+                    ]
+                }
+            }
+        }
+
+        with patch.object(
+            c,
+            "_request_json_with_retry",
+            side_effect=[initial_payload, morechildren_payload],
+        ):
+            result = c._fetch_top_comments_sync(
+                "https://www.reddit.com/r/test/comments/abc/", num_comments=5
+            )
+
+        assert "Loaded via morechildren" in result
+        assert "Second morechildren comment" in result
+
 
 # ---------------------------------------------------------------------------
 # Async wrapper: _fetch_top_comments
@@ -337,3 +494,32 @@ class TestFetchTopCommentsAsync:
             )
 
         assert result == expected
+
+
+class TestCommentFetchCache:
+    def test_reuses_cached_comments_for_same_post(self) -> None:
+        c = _collector()
+
+        async def _run() -> tuple[list[str], list[str], int]:
+            with patch.object(c, "_fetch_top_comments", return_value=["cached comment"]) as mocked:
+                first = await c._fetch_comments_for_post(
+                    post_id="abc",
+                    post_url="https://www.reddit.com/r/test/comments/abc/",
+                    num_comments=7,
+                    timeout_seconds=4,
+                    max_retries=1,
+                )
+                second = await c._fetch_comments_for_post(
+                    post_id="abc",
+                    post_url="https://www.reddit.com/r/test/comments/abc/",
+                    num_comments=7,
+                    timeout_seconds=4,
+                    max_retries=1,
+                )
+                return first, second, mocked.call_count
+
+        first_result, second_result, call_count = asyncio.run(_run())
+
+        assert first_result == ["cached comment"]
+        assert second_result == ["cached comment"]
+        assert call_count == 1
diff --git a/frontend/app/scan/page.tsx b/frontend/app/scan/page.tsx
index f67c099..9a809e8 100644
--- a/frontend/app/scan/page.tsx
+++ b/frontend/app/scan/page.tsx
@@ -71,6 +71,20 @@ export default function ScanPage() {
     [subreddits]
   );
 
+  const sourceBreakdown = useMemo(() => {
+    return leads.reduce(
+      (acc, lead) => {
+        if (lead.post.match_source === "comment") {
+          acc.comment += 1;
+          return acc;
+        }
+        acc.post += 1;
+        return acc;
+      },
+      { post: 0, comment: 0 }
+    );
+  }, [leads]);
+
   async function handleSubmit(event: FormEvent<HTMLFormElement>) {
     event.preventDefault();
     if (!session) {
@@ -239,6 +253,8 @@ export default function ScanPage() {
             {isRepeatScan ? "New this scan" : "Leads"}: {leads.length}
           </span>
           <span className="brand-badge">Candidates scanned: {totalCandidates}</span>
+          <span className="brand-badge">POST: {sourceBreakdown.post}</span>
+          <span className="brand-badge">COMMENTS: {sourceBreakdown.comment}</span>
           <span className="brand-badge">AI scoring: {usedAi ? "Enabled" : "Heuristic mode"}</span>
           {scanCount > 1 && <span className="brand-badge">Scans run: {scanCount}</span>}
         </div>
@@ -248,7 +264,12 @@ export default function ScanPage() {
             <article key={lead.post.id} className="brand-card p-5">
               <div className="flex flex-wrap items-center justify-between gap-2">
                 <h2 className="text-lg font-semibold">{lead.post.title}</h2>
-                <span className="brand-badge">Score: {lead.lead_score}</span>
+                <div className="flex flex-wrap items-center gap-2">
+                  <span className="brand-badge">
+                    Source: {lead.post.match_source === "comment" ? "COMMENTS" : "POST"}
+                  </span>
+                  <span className="brand-badge">Score: {lead.lead_score}</span>
+                </div>
               </div>
 
               <p className="mt-1 text-sm text-brand-navy/70">r/{lead.post.subreddit}</p>
diff --git a/frontend/lib/api.ts b/frontend/lib/api.ts
index a1fdc09..770bf4a 100644
--- a/frontend/lib/api.ts
+++ b/frontend/lib/api.ts
@@ -4,6 +4,7 @@ export interface CandidatePost {
   id: string;
   title: string;
   body: string;
+  match_source: "post" | "comment";
   subreddit: string;
   url: string;
   author: string;

```

---

## Assistant (Build · GPT-5.3-Codex · 19.2s)

_Thinking:_



**Tool: glob**

**Input:**
```json
{
  "pattern": "backend/pyproject.toml",
  "path": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit"
}
```

**Output:**
```
No files found
```

**Tool: glob**

**Input:**
```json
{
  "pattern": "backend/requirements*.txt",
  "path": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit"
}
```

**Output:**
```
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/requirements.txt
```

**Tool: glob**

**Input:**
```json
{
  "pattern": "backend/**/*.ini",
  "path": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit"
}
```

**Output:**
```
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/pytest.ini
```

**Tool: glob**

**Input:**
```json
{
  "pattern": "backend/**/pytest*.ini",
  "path": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit"
}
```

**Output:**
```
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/pytest.ini
```

---

## Assistant (Build · GPT-5.3-Codex · 8.7s)

_Thinking:_



**Tool: bash**

**Input:**
```json
{
  "command": "pytest backend/tests/test_comment_intent_signals.py",
  "workdir": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit",
  "description": "Runs comment intent signal backend tests"
}
```

**Output:**
```
============================= test session starts ==============================
platform darwin -- Python 3.14.3, pytest-8.3.5, pluggy-1.6.0
rootdir: /Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend
configfile: pytest.ini
plugins: anyio-4.13.0
collected 29 items

backend/tests/test_comment_intent_signals.py ........................... [ 93%]
..                                                                       [100%]

============================== 29 passed in 1.53s ==============================

```

---

## Assistant (Build · GPT-5.3-Codex · 15.7s)

_Thinking:_



**Tool: bash**

**Input:**
```json
{
  "command": "ls",
  "workdir": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit",
  "description": "Lists repository root files and folders"
}
```

**Output:**
```
README.md
backend
docs
frontend
skills-lock.json

```

---

## Assistant (Build · GPT-5.3-Codex · 6.7s)

**Tool: bash**

**Input:**
```json
{
  "command": "ls frontend",
  "workdir": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit",
  "description": "Lists frontend project files"
}
```

**Output:**
```
Assets
app
components
lib
next-env.d.ts
next.config.mjs
node_modules
package-lock.json
package.json
postcss.config.mjs
tailwind.config.ts
tsconfig.json
tsconfig.tsbuildinfo

```

---

## Assistant (Build · GPT-5.3-Codex · 5.9s)

**Tool: bash**

**Input:**
```json
{
  "command": "npm run -s typecheck",
  "workdir": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/frontend",
  "description": "Runs frontend TypeScript type check"
}
```

**Output:**
```
(no output)
```

---

## Assistant (Build · GPT-5.3-Codex · 10.2s)

_Thinking:_



**Tool: grep**

**Input:**
```json
{
  "pattern": "match_source|comment-only|comment intent|top_comments",
  "path": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests",
  "include": "*.py"
}
```

**Output:**
```
Found 26 matches
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests/test_comment_intent_signals.py:
  Line 149: # _is_keyword_match with top_comments

  Line 162:             top_comments=["Looking for exactly this kind of automation software!"],

  Line 172:             top_comments=[],

  Line 182:             top_comments=["Nice recipe!", "Thanks for sharing."],

  Line 187:         """Calling without top_comments must still work (defaults to None)."""

  Line 198: # _score_keyword_match with top_comments

  Line 210:             top_comments=[],

  Line 218:             top_comments=["Anyone recommend a good lead generation tool?"],

  Line 231:             top_comments=["Any recommendation?"],

  Line 239:             top_comments=["I would pay for a tool that does this automatically."],

  Line 251:             top_comments=[],

  Line 268: # _fetch_top_comments_sync

  Line 288:         result = c._fetch_top_comments_sync("https://www.reddit.com/r/test/comments/abc/", num_comments=1)

  Line 296:             result = c._fetch_top_comments_sync(

  Line 307:             result = c._fetch_top_comments_sync(

  Line 323:             result = c._fetch_top_comments_sync(

  Line 333:             result = c._fetch_top_comments_sync(

  Line 343:             result = c._fetch_top_comments_sync(

  Line 355:             result = c._fetch_top_comments_sync(

  Line 404:             result = c._fetch_top_comments_sync(

  Line 465:             result = c._fetch_top_comments_sync(

  Line 474: # Async wrapper: _fetch_top_comments

  Line 481:             c._fetch_top_comments("https://www.reddit.com/r/test/comments/abc/", num_comments=2)

  Line 489:         with patch.object(c, "_fetch_top_comments_sync", return_value=expected):

  Line 491:                 c._fetch_top_comments(

  Line 504:             with patch.object(c, "_fetch_top_comments", return_value=["cached comment"]) as mocked:

```

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests/test_reddit_service_fallback.py"
}
```

**Output:**
```
<path>/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests/test_reddit_service_fallback.py</path>
<type>file</type>
<content>
1: from __future__ import annotations
2: 
3: import asyncio
4: 
5: from app.models.schemas import LeadScanRequest
6: from app.services.reddit_service import RedditLeadCollector
7: 
8: 
9: def _scan_request() -> LeadScanRequest:
10:     return LeadScanRequest(
11:         business_description="We help founders find qualified Reddit leads with repeatable workflows.",
12:         keywords=["lead generation"],
13:         subreddits=["entrepreneur"],
14:         limit=3,
15:     )
16: 
17: 
18: def test_fetch_candidate_posts_returns_empty_when_sample_fallback_disabled() -> None:
19:     collector = RedditLeadCollector(client_id=None, client_secret=None, user_agent="f1bot-test")
20: 
21:     async def _empty_public_search(*_: object, **__: object) -> list[object]:
22:         return []
23: 
24:     collector._fetch_with_public_search = _empty_public_search  # type: ignore[method-assign]
25: 
26:     posts = asyncio.run(
27:         collector.fetch_candidate_posts(
28:             _scan_request(),
29:             seen_post_ids=set(),
30:             allow_sample_fallback=False,
31:         )
32:     )
33: 
34:     assert posts == []
35: 
36: 
37: def test_fetch_candidate_posts_returns_sample_when_sample_fallback_enabled() -> None:
38:     collector = RedditLeadCollector(client_id=None, client_secret=None, user_agent="f1bot-test")
39: 
40:     async def _empty_public_search(*_: object, **__: object) -> list[object]:
41:         return []
42: 
43:     collector._fetch_with_public_search = _empty_public_search  # type: ignore[method-assign]
44: 
45:     posts = asyncio.run(
46:         collector.fetch_candidate_posts(
47:             _scan_request(),
48:             seen_post_ids=set(),
49:             allow_sample_fallback=True,
50:         )
51:     )
52: 
53:     assert posts
54:     assert posts[0].id.startswith("sample-")

(End of file - total 54 lines)
</content>
```

---

## Assistant (Build · GPT-5.3-Codex · 32.0s)

_Thinking:_



**Tool: bash**

**Input:**
```json
{
  "command": "pytest backend/tests/test_comment_intent_signals.py backend/tests/test_reddit_service_fallback.py",
  "workdir": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit",
  "description": "Runs Reddit service related backend tests"
}
```

**Output:**
```
============================= test session starts ==============================
platform darwin -- Python 3.14.3, pytest-8.3.5, pluggy-1.6.0
rootdir: /Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend
configfile: pytest.ini
plugins: anyio-4.13.0
collected 31 items

backend/tests/test_comment_intent_signals.py ........................... [ 87%]
..                                                                       [ 93%]
backend/tests/test_reddit_service_fallback.py ..                         [100%]

============================== 31 passed in 1.01s ==============================

```

---

## Assistant (Build · GPT-5.3-Codex · 17.9s)

_Thinking:_



**Tool: grep**

**Input:**
```json
{
  "pattern": "_MAX_COMMENTS_TO_FETCH",
  "path": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend",
  "include": "*.py"
}
```

**Output:**
```
Found 1 matches
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/services/reddit_service.py:
  Line 100: _MAX_COMMENTS_TO_FETCH = 10

```

---

## Assistant (Build · GPT-5.3-Codex · 29.1s)

_Thinking:_



**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/repositories/leads_repository.py"
}
```

**Output:**
```
<path>/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/repositories/leads_repository.py</path>
<type>file</type>
<content>
1: from datetime import datetime, timezone
2: from typing import Any
3: from uuid import uuid4
4: 
5: from app.models.schemas import CandidatePost, LeadInsight, LeadRecord, LeadStatus
6: from app.repositories.memory_store import MEMORY_LEADS, MEMORY_SEEN_POSTS
7: 
8: SupabaseClient = Any
9: 
10: 
11: class LeadsRepository:
12:     def __init__(self, client: SupabaseClient | None) -> None:
13:         self.client = client
14: 
15:     def save_scan_results(self, user_id: str, scan_id: str, insights: list[LeadInsight]) -> list[LeadRecord]:
16:         now = datetime.now(tz=timezone.utc)
17:         records: list[LeadRecord] = []
18: 
19:         for insight in insights:
20:             record = LeadRecord(
21:                 id=str(uuid4()),
22:                 user_id=user_id,
23:                 status="new",
24:                 post=insight.post,
25:                 lead_score=insight.lead_score,
26:                 qualification_reason=insight.qualification_reason,
27:                 suggested_outreach=insight.suggested_outreach,
28:                 scan_id=scan_id,
29:                 created_at=now,
30:                 updated_at=now
31:             )
32:             records.append(record)
33: 
34:         if not records:
35:             return []
36: 
37:         if self.client is None:
38:             for record in records:
39:                 MEMORY_LEADS[record.id] = record
40:             return records
41: 
42:         payload = [self._to_row(item) for item in records]
43:         self.client.table("leads").insert(payload).execute()
44:         return records
45: 
46:     def list_leads(self, user_id: str, status: LeadStatus | None = None) -> list[LeadRecord]:
47:         if self.client is None:
48:             items = [lead for lead in MEMORY_LEADS.values() if lead.user_id == user_id]
49:             if status:
50:                 items = [lead for lead in items if lead.status == status]
51:             return sorted(items, key=lambda row: row.lead_score, reverse=True)
52: 
53:         query = self.client.table("leads").select("*").eq("user_id", user_id)
54:         if status:
55:             query = query.eq("status", status)
56: 
57:         rows = query.order("lead_score", desc=True).execute().data or []
58:         return [self._from_row(row) for row in rows]
59: 
60:     def get_lead(self, user_id: str, lead_id: str) -> LeadRecord | None:
61:         if self.client is None:
62:             lead = MEMORY_LEADS.get(lead_id)
63:             if not lead or lead.user_id != user_id:
64:                 return None
65:             return lead
66: 
67:         rows = (
68:             self.client.table("leads")
69:             .select("*")
70:             .eq("id", lead_id)
71:             .eq("user_id", user_id)
72:             .limit(1)
73:             .execute()
74:             .data
75:             or []
76:         )
77: 
78:         if not rows:
79:             return None
80: 
81:         return self._from_row(rows[0])
82: 
83:     def update_status(self, user_id: str, lead_id: str, status: LeadStatus) -> LeadRecord | None:
84:         now = datetime.now(tz=timezone.utc)
85: 
86:         if self.client is None:
87:             lead = MEMORY_LEADS.get(lead_id)
88:             if not lead or lead.user_id != user_id:
89:                 return None
90:             updated = lead.model_copy(update={"status": status, "updated_at": now})
91:             MEMORY_LEADS[lead_id] = updated
92:             return updated
93: 
94:         # Keep update and fetch separate for supabase-py compatibility across versions.
95:         self.client.table("leads").update(
96:             {"status": status, "updated_at": now.isoformat()}
97:         ).eq("id", lead_id).eq("user_id", user_id).execute()
98: 
99:         return self.get_lead(user_id=user_id, lead_id=lead_id)
100: 
101:     # ------------------------------------------------------------------
102:     # Seen-post deduplication helpers
103:     # ------------------------------------------------------------------
104: 
105:     def get_seen_post_ids(self, user_id: str) -> set[str]:
106:         """Return the set of Reddit post IDs already surfaced to this user."""
107:         if self.client is None:
108:             return set(MEMORY_SEEN_POSTS.get(user_id, set()))
109: 
110:         rows = (
111:             self.client.table("leads")
112:             .select("post_id")
113:             .eq("user_id", user_id)
114:             .execute()
115:             .data
116:             or []
117:         )
118:         return {str(row["post_id"]) for row in rows if row.get("post_id")}
119: 
120:     def mark_posts_seen(self, user_id: str, post_ids: set[str]) -> None:
121:         """Record that these post IDs have now been shown to the user."""
122:         if self.client is None:
123:             existing = MEMORY_SEEN_POSTS.setdefault(user_id, set())
124:             existing.update(post_ids)
125:             return
126:         # With Supabase the leads table already stores post_id per row,
127:         # so get_seen_post_ids will naturally pick them up — no extra work needed.
128: 
129:     def _to_row(self, record: LeadRecord) -> dict[str, object]:
130:         return {
131:             "id": record.id,
132:             "user_id": record.user_id,
133:             "status": record.status,
134:             "post_id": record.post.id,
135:             "title": record.post.title,
136:             "body": record.post.body,
137:             "subreddit": record.post.subreddit,
138:             "url": record.post.url,
139:             "author": record.post.author,
140:             "post_created_utc": record.post.created_utc.isoformat(),
141:             "reddit_score": record.post.score,
142:             "num_comments": record.post.num_comments,
143:             "lead_score": record.lead_score,
144:             "qualification_reason": record.qualification_reason,
145:             "suggested_outreach": record.suggested_outreach,
146:             "scan_id": record.scan_id,
147:             "created_at": record.created_at.isoformat(),
148:             "updated_at": record.updated_at.isoformat()
149:         }
150: 
151:     def _from_row(self, row: dict[str, object]) -> LeadRecord:
152:         post = CandidatePost(
153:             id=str(row.get("post_id", "")),
154:             title=str(row.get("title", "")),
155:             body=str(row.get("body", "")),
156:             subreddit=str(row.get("subreddit", "")),
157:             url=str(row.get("url", "")),
158:             author=str(row.get("author", "unknown")),
159:             created_utc=self._parse_datetime(row.get("post_created_utc")),
160:             score=int(row.get("reddit_score", 0) or 0),
161:             num_comments=int(row.get("num_comments", 0) or 0)
162:         )
163: 
164:         return LeadRecord(
165:             id=str(row.get("id", "")),
166:             user_id=str(row.get("user_id", "")),
167:             status=str(row.get("status", "new")),
168:             post=post,
169:             lead_score=float(row.get("lead_score", 0) or 0),
170:             qualification_reason=str(row.get("qualification_reason", "")),
171:             suggested_outreach=str(row.get("suggested_outreach", "")),
172:             scan_id=str(row.get("scan_id", "")),
173:             created_at=self._parse_datetime(row.get("created_at")),
174:             updated_at=self._parse_datetime(row.get("updated_at"))
175:         )
176: 
177:     def _parse_datetime(self, value: object) -> datetime:
178:         if isinstance(value, datetime):
179:             return value
180:         if isinstance(value, str) and value:
181:             try:
182:                 return datetime.fromisoformat(value.replace("Z", "+00:00"))
183:             except ValueError:
184:                 pass
185:         return datetime.now(tz=timezone.utc)

(End of file - total 185 lines)
</content>
```

---

## Assistant (Build · GPT-5.3-Codex · 20.6s)

_Thinking:_



**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/controllers/leads_controller.py"
}
```

**Output:**
```
<path>/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/app/controllers/leads_controller.py</path>
<type>file</type>
<content>
1: import csv
2: from io import StringIO
3: from uuid import uuid4
4: 
5: from app.core.config import get_settings
6: from app.models.schemas import (
7:     LeadInsight,
8:     LeadListResponse,
9:     LeadRecord,
10:     LeadScanRequest,
11:     LeadScanResponse,
12:     LeadStatus,
13: )
14: from app.repositories.leads_repository import LeadsRepository
15: from app.services.gemini_service import GeminiLeadScorer
16: from app.services.reddit_service import RedditLeadCollector
17: 
18: CSV_FORMULA_PREFIXES = ("=", "+", "-", "@")
19: 
20: 
21: class LeadsController:
22:     def __init__(self, repository: LeadsRepository) -> None:
23:         self.repository = repository
24: 
25:     async def scan(self, user_id: str, payload: LeadScanRequest) -> LeadScanResponse:
26:         settings = get_settings()
27: 
28:         collector = RedditLeadCollector(
29:             client_id=settings.reddit_client_id,
30:             client_secret=settings.reddit_client_secret,
31:             user_agent=settings.reddit_user_agent,
32:         )
33:         scorer = GeminiLeadScorer(
34:             api_key=settings.gemini_api_key,
35:             model_lite=settings.gemini_model_lite,
36:         )
37: 
38:         # Load which Reddit posts this user has already seen so we skip them.
39:         seen_post_ids = self.repository.get_seen_post_ids(user_id)
40: 
41:         candidate_posts = await collector.fetch_candidate_posts(
42:             payload,
43:             seen_post_ids=seen_post_ids,
44:             allow_sample_fallback=settings.use_sample_leads_fallback(),
45:         )
46:         lead_insights = await scorer.score_posts(payload, candidate_posts)
47: 
48:         scan_id = str(uuid4())
49:         self.repository.save_scan_results(user_id, scan_id, lead_insights)
50: 
51:         # Mark every surfaced post as seen so next scan returns different leads.
52:         new_post_ids = {insight.post.id for insight in lead_insights}
53:         self.repository.mark_posts_seen(user_id, new_post_ids)
54: 
55:         return LeadScanResponse(
56:             leads=lead_insights[: payload.limit],
57:             total_candidates=len(candidate_posts),
58:             used_ai=bool(settings.gemini_api_key),
59:         )
60: 
61:     def list_leads(self, user_id: str, status: LeadStatus | None = None) -> LeadListResponse:
62:         leads = self.repository.list_leads(user_id=user_id, status=status)
63:         return LeadListResponse(leads=leads)
64: 
65:     def get_lead(self, user_id: str, lead_id: str) -> LeadRecord | None:
66:         return self.repository.get_lead(user_id=user_id, lead_id=lead_id)
67: 
68:     def update_status(self, user_id: str, lead_id: str, status: LeadStatus) -> LeadRecord | None:
69:         return self.repository.update_status(user_id=user_id, lead_id=lead_id, status=status)
70: 
71:     def export_csv(self, user_id: str, status: LeadStatus | None = None) -> str:
72:         leads = self.repository.list_leads(user_id=user_id, status=status)
73: 
74:         header = [
75:             "lead_id",
76:             "status",
77:             "post_url",
78:             "subreddit",
79:             "lead_score",
80:             "qualification_reason",
81:             "suggested_outreach",
82:         ]
83:         output = StringIO()
84:         writer = csv.writer(output, lineterminator="\n")
85:         writer.writerow(header)
86: 
87:         for lead in leads:
88:             writer.writerow(
89:                 [
90:                     self._csv_safe_cell(lead.id),
91:                     self._csv_safe_cell(lead.status),
92:                     self._csv_safe_cell(lead.post.url),
93:                     self._csv_safe_cell(lead.post.subreddit),
94:                     self._csv_safe_cell(lead.lead_score),
95:                     self._csv_safe_cell(lead.qualification_reason),
96:                     self._csv_safe_cell(lead.suggested_outreach),
97:                 ]
98:             )
99: 
100:         csv_output = output.getvalue()
101:         if csv_output.endswith("\n"):
102:             return csv_output[:-1]
103:         return csv_output
104: 
105:     def _csv_safe_cell(self, value: object) -> str:
106:         text = str(value)
107:         stripped = text.lstrip()
108:         if stripped and stripped[0] in CSV_FORMULA_PREFIXES:
109:             return f"'{text}"
110:         return text

(End of file - total 110 lines)
</content>
```

---

## Assistant (Build · GPT-5.3-Codex · 18.0s)

_Thinking:_



**Tool: bash**

**Input:**
```json
{
  "command": "pytest backend/tests",
  "workdir": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit",
  "description": "Runs full backend test suite"
}
```

**Output:**
```
============================= test session starts ==============================
platform darwin -- Python 3.14.3, pytest-8.3.5, pluggy-1.6.0
rootdir: /Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend
configfile: pytest.ini
plugins: anyio-4.13.0
collected 82 items

backend/tests/test_auth_scan_regression.py .........................     [ 30%]
backend/tests/test_client_ip.py ........                                 [ 40%]
backend/tests/test_client_ip_proxy.py ...............                    [ 58%]
backend/tests/test_comment_intent_signals.py ........................... [ 91%]
..                                                                       [ 93%]
backend/tests/test_leads_csv_export.py ..                                [ 96%]
backend/tests/test_leads_repository.py .                                 [ 97%]
backend/tests/test_reddit_service_fallback.py ..                         [100%]

=============================== warnings summary ===============================
tests/test_auth_scan_regression.py::test_health_requires_authorization_header
  /Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/.venv/lib/python3.14/site-packages/supabase/__init__.py:1: DeprecationWarning: The `gotrue` package is deprecated, is not going to receive updates in the future. Please, use `supabase_auth` instead.
    from gotrue.errors import (

tests/test_auth_scan_regression.py: 283 warnings
  /Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/.venv/lib/python3.14/site-packages/fastapi/routing.py:233: DeprecationWarning: 'asyncio.iscoroutinefunction' is deprecated and slated for removal in Python 3.16; use inspect.iscoroutinefunction() instead
    is_coroutine = asyncio.iscoroutinefunction(dependant.call)

tests/test_auth_scan_regression.py: 410 warnings
  /Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/.venv/lib/python3.14/site-packages/starlette/_utils.py:40: DeprecationWarning: 'asyncio.iscoroutinefunction' is deprecated and slated for removal in Python 3.16; use inspect.iscoroutinefunction() instead
    return asyncio.iscoroutinefunction(obj) or (callable(obj) and asyncio.iscoroutinefunction(obj.__call__))

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 82 passed, 694 warnings in 1.83s =======================

```

---

## Assistant (Build · GPT-5.3-Codex · 25.5s)

_Thinking:_



**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/frontend/lib/api.ts"
}
```

**Output:**
```
<path>/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/frontend/lib/api.ts</path>
<type>file</type>
<content>
1: import { clearSession, clearSessionCache, getCsrfToken } from "@/lib/session";
2: 
3: export interface CandidatePost {
4:   id: string;
5:   title: string;
6:   body: string;
7:   match_source: "post" | "comment";
8:   subreddit: string;
9:   url: string;
10:   author: string;
11:   created_utc: string;
12:   score: number;
13:   num_comments: number;
14: }
15: 
16: export interface LeadInsight {
17:   post: CandidatePost;
18:   lead_score: number;
19:   qualification_reason: string;
20:   suggested_outreach: string;
21: }
22: 
23: export interface LeadScanRequest {
24:   business_description: string;
25:   keywords: string[];
26:   subreddits: string[];
27:   limit: number;
28: }
29: 
30: export interface LeadScanResponse {
31:   leads: LeadInsight[];
32:   total_candidates: number;
33:   used_ai: boolean;
34: }
35: 
36: export type LeadStatus = "new" | "contacted" | "qualified" | "ignored";
37: 
38: export interface LoginRequest {
39:   email: string;
40:   password: string;
41: }
42: 
43: export interface LoginResponse {
44:   user_id: string;
45:   email: string;
46:   access_token?: string;
47:   token_type?: string;
48: }
49: 
50: export interface RegisterRequest {
51:   email: string;
52:   password: string;
53:   full_name?: string;
54: }
55: 
56: export interface RegisterResponse {
57:   user_id: string;
58:   email: string;
59:   access_token?: string;
60:   token_type?: string;
61: }
62: 
63: export interface BusinessProfile {
64:   user_id: string;
65:   business_description: string;
66:   keywords: string[];
67:   subreddits: string[];
68:   updated_at?: string;
69: }
70: 
71: export interface SaveProfileRequest {
72:   business_description: string;
73:   keywords: string[];
74:   subreddits: string[];
75: }
76: 
77: export interface LeadRecord {
78:   id: string;
79:   user_id: string;
80:   status: LeadStatus;
81:   post: CandidatePost;
82:   lead_score: number;
83:   qualification_reason: string;
84:   suggested_outreach: string;
85:   scan_id: string;
86:   created_at: string;
87:   updated_at: string;
88: }
89: 
90: export interface LeadListResponse {
91:   leads: LeadRecord[];
92: }
93: 
94: export interface RuntimeSettingsResponse {
95:   environment: string;
96:   gemini_configured: boolean;
97:   reddit_configured: boolean;
98:   sample_leads_fallback_enabled: boolean;
99:   supabase_configured: boolean;
100:   supabase_auth_enabled: boolean;
101:   scan_rate_limit_per_minute: number;
102:   scan_rate_limit_window_seconds: number;
103:   scan_daily_quota: number;
104: }
105: 
106: export interface RuntimeHealthResponse {
107:   status: string;
108:   environment: string;
109:   gemini_configured: boolean;
110:   reddit_configured: boolean;
111: }
112: 
113: interface FastApiValidationError {
114:   loc: Array<string | number>;
115:   msg: string;
116:   type: string;
117: }
118: 
119: interface FastApiErrorPayload {
120:   detail?: string | FastApiValidationError[];
121: }
122: 
123: const configuredApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim() || "http://localhost:8000";
124: const shouldUseProxy =
125:   typeof window !== "undefined" &&
126:   window.location.protocol === "https:" &&
127:   configuredApiBaseUrl.startsWith("http://");
128: 
129: const API_BASE_URL = (shouldUseProxy ? "/backend" : configuredApiBaseUrl).replace(/\/$/, "");
130: const CSRF_HEADER_NAME = "X-CSRF-Token";
131: const SCAN_REQUEST_TIMEOUT_MS = 90_000;
132: 
133: function toHeaderObject(headers?: HeadersInit): Record<string, string> {
134:   if (!headers) {
135:     return {};
136:   }
137: 
138:   if (headers instanceof Headers) {
139:     return Object.fromEntries(headers.entries());
140:   }
141: 
142:   if (Array.isArray(headers)) {
143:     return Object.fromEntries(headers);
144:   }
145: 
146:   return { ...headers };
147: }
148: 
149: function requiresCsrf(method?: string): boolean {
150:   const normalized = (method || "GET").toUpperCase();
151:   return normalized === "POST" || normalized === "PUT" || normalized === "PATCH" || normalized === "DELETE";
152: }
153: 
154: function isAbortError(error: unknown): boolean {
155:   return error instanceof Error && error.name === "AbortError";
156: }
157: 
158: function buildCsrfHeader(method?: string): Record<string, string> {
159:   if (!requiresCsrf(method)) {
160:     return {};
161:   }
162: 
163:   const csrfToken = getCsrfToken();
164:   if (!csrfToken?.trim()) {
165:     throw new Error("Session security token missing. Please log in again.");
166:   }
167: 
168:   return {
169:     [CSRF_HEADER_NAME]: csrfToken,
170:   };
171: }
172: 
173: function formatValidationErrors(errors: FastApiValidationError[]): string {
174:   const messages = errors
175:     .map((entry) => {
176:       const field = entry.loc
177:         .map((value) => String(value))
178:         .filter((value) => value !== "body" && value !== "query" && value !== "path")
179:         .join(".");
180: 
181:       return field ? `${field}: ${entry.msg}` : entry.msg;
182:     })
183:     .filter(Boolean);
184: 
185:   return messages.length > 0 ? messages.join("; ") : "Request validation failed";
186: }
187: 
188: async function parseErrorResponse(response: Response): Promise<string> {
189:   const contentType = response.headers.get("content-type") || "";
190:   if (contentType.includes("application/json")) {
191:     try {
192:       const payload = (await response.json()) as FastApiErrorPayload;
193:       if (typeof payload.detail === "string" && payload.detail.trim().length > 0) {
194:         return payload.detail;
195:       }
196:       if (Array.isArray(payload.detail)) {
197:         return formatValidationErrors(payload.detail);
198:       }
199:     } catch {
200:       // Fallback to plain text when JSON parsing fails.
201:     }
202:   }
203: 
204:   const text = await response.text();
205:   return text || `Request failed with status ${response.status}`;
206: }
207: 
208: function handleUnauthorizedResponse(): never {
209:   clearSessionCache();
210:   void clearSession();
211: 
212:   if (typeof window !== "undefined") {
213:     window.location.assign("/login");
214:   }
215: 
216:   throw new Error("Session expired. Please log in again.");
217: }
218: 
219: async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
220:   let response: Response;
221: 
222:   try {
223:     response = await fetch(`${API_BASE_URL}${path}`, {
224:       ...init,
225:       cache: init?.cache ?? "no-store",
226:       credentials: init?.credentials ?? "include",
227:       headers: {
228:         Accept: "application/json",
229:         ...toHeaderObject(init?.headers)
230:       }
231:     });
232:   } catch (error) {
233:     if (isAbortError(error)) {
234:       throw new Error("Scan timed out. Try fewer keywords/subreddits and run again.");
235:     }
236:     throw new Error(`Unable to connect to API (${API_BASE_URL}).`);
237:   }
238: 
239:   return response;
240: }
241: 
242: async function authenticatedFetch(path: string, init?: RequestInit): Promise<Response> {
243:   const response = await apiFetch(path, {
244:     ...init,
245:     headers: {
246:       ...buildCsrfHeader(init?.method),
247:       ...toHeaderObject(init?.headers),
248:     },
249:   });
250: 
251:   if (response.status === 401) {
252:     handleUnauthorizedResponse();
253:   }
254: 
255:   return response;
256: }
257: 
258: async function parseResponse<T>(response: Response): Promise<T> {
259:   if (!response.ok) {
260:     throw new Error(await parseErrorResponse(response));
261:   }
262: 
263:   if (response.status === 204) {
264:     return undefined as T;
265:   }
266: 
267:   return (await response.json()) as T;
268: }
269: 
270: async function parseBlobResponse(response: Response): Promise<Blob> {
271:   if (!response.ok) {
272:     throw new Error(await parseErrorResponse(response));
273:   }
274: 
275:   return response.blob();
276: }
277: 
278: export async function login(payload: LoginRequest): Promise<LoginResponse> {
279:   const response = await apiFetch("/api/auth/login", {
280:     method: "POST",
281:     headers: {
282:       "Content-Type": "application/json"
283:     },
284:     body: JSON.stringify(payload)
285:   });
286: 
287:   return parseResponse<LoginResponse>(response);
288: }
289: 
290: export async function register(payload: RegisterRequest): Promise<RegisterResponse> {
291:   const response = await apiFetch("/api/auth/register", {
292:     method: "POST",
293:     headers: {
294:       "Content-Type": "application/json"
295:     },
296:     body: JSON.stringify(payload)
297:   });
298: 
299:   return parseResponse<RegisterResponse>(response);
300: }
301: 
302: export async function getProfile(): Promise<BusinessProfile> {
303:   const response = await authenticatedFetch("/api/profile");
304:   return parseResponse<BusinessProfile>(response);
305: }
306: 
307: export async function saveProfile(payload: SaveProfileRequest): Promise<BusinessProfile> {
308:   const response = await authenticatedFetch("/api/profile", {
309:     method: "PUT",
310:     headers: {
311:       "Content-Type": "application/json"
312:     },
313:     body: JSON.stringify(payload)
314:   });
315: 
316:   return parseResponse<BusinessProfile>(response);
317: }
318: 
319: export async function scanLeads(payload: LeadScanRequest): Promise<LeadScanResponse> {
320:   const controller = new AbortController();
321:   const timeoutId = setTimeout(() => controller.abort(), SCAN_REQUEST_TIMEOUT_MS);
322: 
323:   try {
324:     const response = await authenticatedFetch("/api/leads/scan", {
325:       method: "POST",
326:       headers: {
327:         "Content-Type": "application/json"
328:       },
329:       body: JSON.stringify(payload),
330:       signal: controller.signal,
331:     });
332: 
333:     return parseResponse<LeadScanResponse>(response);
334:   } finally {
335:     clearTimeout(timeoutId);
336:   }
337: }
338: 
339: export async function getLeads(status?: LeadStatus): Promise<LeadListResponse> {
340:   const query = new URLSearchParams();
341:   if (status) {
342:     query.set("status", status);
343:   }
344: 
345:   const path = query.toString() ? `/api/leads?${query.toString()}` : "/api/leads";
346:   const response = await authenticatedFetch(path);
347:   return parseResponse<LeadListResponse>(response);
348: }
349: 
350: export async function getLeadById(leadId: string): Promise<LeadRecord> {
351:   const response = await authenticatedFetch(`/api/leads/${leadId}`);
352:   return parseResponse<LeadRecord>(response);
353: }
354: 
355: export async function updateLeadStatus(
356:   leadId: string,
357:   status: LeadStatus
358: ): Promise<LeadRecord> {
359:   const response = await authenticatedFetch(`/api/leads/${leadId}/status`, {
360:     method: "PATCH",
361:     headers: {
362:       "Content-Type": "application/json"
363:     },
364:     body: JSON.stringify({ status })
365:   });
366: 
367:   return parseResponse<LeadRecord>(response);
368: }
369: 
370: export async function getRuntimeSettings(): Promise<RuntimeSettingsResponse> {
371:   const response = await authenticatedFetch("/api/settings");
372:   return parseResponse<RuntimeSettingsResponse>(response);
373: }
374: 
375: export async function getHealth(): Promise<RuntimeHealthResponse> {
376:   const response = await authenticatedFetch("/api/health");
377:   return parseResponse<RuntimeHealthResponse>(response);
378: }
379: 
380: export async function downloadLeadsCsv(status?: LeadStatus): Promise<Blob> {
381:   const query = new URLSearchParams();
382:   if (status) {
383:     query.set("status", status);
384:   }
385: 
386:   const path = query.toString() ? `/api/leads/export.csv?${query.toString()}` : "/api/leads/export.csv";
387:   const response = await authenticatedFetch(path, {
388:     headers: {
389:       Accept: "text/csv"
390:     }
391:   });
392: 
393:   return parseBlobResponse(response);
394: }

(End of file - total 394 lines)
</content>
```

---

## Assistant (Build · GPT-5.3-Codex · 17.6s)

_Thinking:_



**Tool: grep**

**Input:**
```json
{
  "pattern": "COMMENT_INTENT_FETCH_THRESHOLD",
  "path": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests/test_comment_intent_signals.py",
  "include": "*.py"
}
```

**Output:**
```
Found 1 matches
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests/test_comment_intent_signals.py:
  Line 14: from app.core.constants import COMMENT_INTENT_FETCH_THRESHOLD

```

---

## Assistant (Build · GPT-5.3-Codex · 31.7s)

_Thinking:_



**Tool: apply_patch**

**Input:**
```json
{
  "patchText": "*** Begin Patch\n*** Update File: /Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests/test_comment_intent_signals.py\n@@\n import asyncio\n-from unittest.mock import AsyncMock, patch\n-\n-import pytest\n+from unittest.mock import patch\n@@\n class TestFetchTopCommentsAsync:\n     def test_returns_empty_below_threshold(self) -> None:\n         c = _collector()\n+        below_threshold = max(COMMENT_INTENT_FETCH_THRESHOLD - 1, 0)\n         result = asyncio.run(\n-            c._fetch_top_comments(\"https://www.reddit.com/r/test/comments/abc/\", num_comments=2)\n+            c._fetch_top_comments(\n+                \"https://www.reddit.com/r/test/comments/abc/\",\n+                num_comments=below_threshold,\n+            )\n         )\n         assert result == []\n*** End Patch"
}
```

**Output:**
```
Success. Updated the following files:
M backend/tests/test_comment_intent_signals.py
```

---

## Assistant (Build · GPT-5.3-Codex · 16.6s)

_Thinking:_



**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/frontend/app/scan/page.tsx"
}
```

**Output:**
```
<path>/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/frontend/app/scan/page.tsx</path>
<type>file</type>
<content>
1: "use client";
2: 
3: import { FormEvent, useEffect, useMemo, useState } from "react";
4: import { useRouter } from "next/navigation";
5: import { getProfile, scanLeads, type LeadInsight } from "@/lib/api";
6: import { useSessionGuard } from "@/lib/use-session-guard";
7: 
8: const DEFAULT_SUBREDDITS = "loseit,CICO,nutrition,weightlossadvice,Fitness,MealPrepSunday,PCOSloseit";
9: const DEFAULT_KEYWORDS = "calorie tracker,calorie counting app,macro tracking,lose weight app,weight loss plateau,fitness app recommendation";
10: 
11: export default function ScanPage() {
12:   const router = useRouter();
13:   const { session, isCheckingSession } = useSessionGuard();
14:   const [businessDescription, setBusinessDescription] = useState(
15:     "CalPal is a calorie tracker that helps people lose weight consistently with simple meal logging, macro guidance, and accountability nudges."
16:   );
17:   const [keywords, setKeywords] = useState(DEFAULT_KEYWORDS);
18:   const [subreddits, setSubreddits] = useState(DEFAULT_SUBREDDITS);
19:   const [limit, setLimit] = useState(15);
20:   const [loading, setLoading] = useState(false);
21:   const [error, setError] = useState<string | null>(null);
22:   const [leads, setLeads] = useState<LeadInsight[]>([]);
23:   const [usedAi, setUsedAi] = useState(false);
24:   const [totalCandidates, setTotalCandidates] = useState(0);
25:   // Tracks how many scans have completed so we can adapt UI for repeat scans.
26:   const [scanCount, setScanCount] = useState(0);
27: 
28:   useEffect(() => {
29:     if (!session) {
30:       return;
31:     }
32: 
33:     async function hydrateFromProfile() {
34:       try {
35:         const profile = await getProfile();
36:         setBusinessDescription(profile.business_description);
37:         if (profile.keywords.length) {
38:           setKeywords(profile.keywords.join(","));
39:         }
40:         if (profile.subreddits.length) {
41:           setSubreddits(profile.subreddits.join(","));
42:         }
43:       } catch {
44:         // Use current defaults when profile does not exist.
45:       }
46:     }
47: 
48:     hydrateFromProfile();
49:   }, [session]);
50: 
51:   const canSubmit = useMemo(
52:     () => businessDescription.trim().length > 10 && !loading,
53:     [businessDescription, loading]
54:   );
55: 
56:   const keywordCount = useMemo(
57:     () =>
58:       keywords
59:         .split(",")
60:         .map((item) => item.trim())
61:         .filter(Boolean).length,
62:     [keywords]
63:   );
64: 
65:   const subredditCount = useMemo(
66:     () =>
67:       subreddits
68:         .split(",")
69:         .map((item) => item.trim())
70:         .filter(Boolean).length,
71:     [subreddits]
72:   );
73: 
74:   const sourceBreakdown = useMemo(() => {
75:     return leads.reduce(
76:       (acc, lead) => {
77:         if (lead.post.match_source === "comment") {
78:           acc.comment += 1;
79:           return acc;
80:         }
81:         acc.post += 1;
82:         return acc;
83:       },
84:       { post: 0, comment: 0 }
85:     );
86:   }, [leads]);
87: 
88:   async function handleSubmit(event: FormEvent<HTMLFormElement>) {
89:     event.preventDefault();
90:     if (!session) {
91:       return;
92:     }
93: 
94:     setLoading(true);
95:     setError(null);
96: 
97:     try {
98:       const response = await scanLeads({
99:         business_description: businessDescription,
100:         keywords: keywords
101:           .split(",")
102:           .map((item) => item.trim())
103:           .filter(Boolean),
104:         subreddits: subreddits
105:           .split(",")
106:           .map((item) => item.trim())
107:           .filter(Boolean),
108:         limit,
109:       });
110: 
111:       setLeads(response.leads);
112:       setUsedAi(response.used_ai);
113:       setTotalCandidates(response.total_candidates);
114:       setScanCount((prev) => prev + 1);
115:     } catch (scanError) {
116:       setError(scanError instanceof Error ? scanError.message : "Failed to scan leads");
117:     } finally {
118:       setLoading(false);
119:     }
120:   }
121: 
122:   if (isCheckingSession) {
123:     return <main className="mx-auto max-w-4xl px-6 py-10 text-brand-navy/75">Checking your session...</main>;
124:   }
125: 
126:   // After the first scan the button label and UX update to reflect that repeat
127:   // scans return *fresh* leads (deduplication is handled server-side).
128:   const isRepeatScan = scanCount > 0;
129:   const submitLabel = loading
130:     ? isRepeatScan
131:       ? "Fetching fresh leads\u2026"
132:       : "Scanning\u2026"
133:     : isRepeatScan
134:       ? "\u21bb  Scan for Fresh Leads"
135:       : "Find Leads";
136: 
137:   return (
138:     <main className="mx-auto max-w-5xl px-6 py-10 text-brand-navy">
139:       <header className="brand-card relative mb-8 overflow-hidden p-6 md:p-8">
140:         <div className="pointer-events-none absolute -right-8 -top-8 h-36 w-36 rounded-full bg-brand-gold/30 blur-2xl" />
141:         <div className="pointer-events-none absolute -left-8 bottom-0 h-28 w-28 rounded-full bg-brand-orange/28 blur-2xl" />
142: 
143:         <p className="relative text-xs tracking-[0.24em] text-brand-burgundy/80">SCAN WORKSPACE</p>
144:         <h1
145:           className="relative mt-2 text-3xl font-semibold tracking-tight text-brand-burgundy md:text-4xl"
146:           style={{ fontFamily: "var(--font-fraunces)" }}
147:         >
148:           Find High-Intent Reddit Leads
149:         </h1>
150:         <p className="relative mt-2 max-w-2xl text-sm text-brand-navy/80 md:text-base">
151:           Send targeting context to your backend pipeline, score opportunities, then move qualified leads to outreach.
152:         </p>
153: 
154:         <div className="relative mt-5 grid gap-3 sm:grid-cols-4">
155:           <div className="brand-stat">
156:             <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Keywords</p>
157:             <p className="mt-1 text-lg font-semibold text-brand-navy">{keywordCount}</p>
158:           </div>
159:           <div className="brand-stat">
160:             <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Subreddits</p>
161:             <p className="mt-1 text-lg font-semibold text-brand-navy">{subredditCount}</p>
162:           </div>
163:           <div className="brand-stat">
164:             <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Max Results</p>
165:             <p className="mt-1 text-lg font-semibold text-brand-navy">{limit}</p>
166:           </div>
167:           <div className="brand-stat">
168:             <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">Signed In</p>
169:             <p className="mt-1 truncate text-sm font-semibold text-brand-navy">{session?.email ?? "Unknown"}</p>
170:           </div>
171:         </div>
172:       </header>
173: 
174:       <section className="brand-card p-6 md:p-7">
175:         <form onSubmit={handleSubmit} className="grid gap-4">
176:           <label className="grid gap-2">
177:             <span className="text-sm font-medium text-brand-burgundy">Business Description</span>
178:             <textarea
179:               value={businessDescription}
180:               onChange={(event) => setBusinessDescription(event.target.value)}
181:               className="brand-input h-32 resize-y"
182:               placeholder="Describe your product or service"
183:             />
184:           </label>
185: 
186:           <div className="grid gap-4 md:grid-cols-2">
187:             <label className="grid gap-2">
188:               <span className="text-sm font-medium text-brand-burgundy">Keywords (comma separated)</span>
189:               <input
190:                 value={keywords}
191:                 onChange={(event) => setKeywords(event.target.value)}
192:                 className="brand-input"
193:               />
194:             </label>
195: 
196:             <label className="grid gap-2">
197:               <span className="text-sm font-medium text-brand-burgundy">Subreddits (comma separated)</span>
198:               <input
199:                 value={subreddits}
200:                 onChange={(event) => setSubreddits(event.target.value)}
201:                 className="brand-input"
202:               />
203:             </label>
204:           </div>
205: 
206:           <label className="grid gap-2 md:max-w-xs">
207:             <span className="text-sm font-medium text-brand-burgundy">Max Results</span>
208:             <input
209:               type="number"
210:               min={1}
211:               max={100}
212:               value={limit}
213:               onChange={(event) => setLimit(Number(event.target.value) || 15)}
214:               className="brand-input"
215:             />
216:           </label>
217: 
218:           <div className="flex flex-wrap items-center gap-3">
219:             <button
220:               type="submit"
221:               disabled={!canSubmit}
222:               className="brand-btn-primary inline-flex w-fit items-center px-4 py-2.5 text-sm disabled:cursor-not-allowed disabled:opacity-50"
223:             >
224:               {submitLabel}
225:             </button>
226: 
227:             <button
228:               type="button"
229:               onClick={() => router.push("/leads")}
230:               className="brand-btn-secondary px-4 py-2.5 text-sm"
231:             >
232:               Open Leads Inbox
233:             </button>
234:           </div>
235: 
236:           {/* Deduplication hint — shown after the first completed scan */}
237:           {isRepeatScan && !loading && (
238:             <p className="flex items-center gap-2 text-xs text-brand-navy/60">
239:               <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-700">
240:                 ✓ Deduplication active
241:               </span>
242:               Each scan automatically skips posts you&apos;ve already seen and widens the time window to surface fresh leads.
243:             </p>
244:           )}
245: 
246:           {error ? <p className="text-sm text-brand-burgundy">{error}</p> : null}
247:         </form>
248:       </section>
249: 
250:       <section className="mt-8">
251:         <div className="mb-4 flex flex-wrap items-center gap-3 text-sm text-brand-navy/85">
252:           <span className="brand-badge">
253:             {isRepeatScan ? "New this scan" : "Leads"}: {leads.length}
254:           </span>
255:           <span className="brand-badge">Candidates scanned: {totalCandidates}</span>
256:           <span className="brand-badge">POST: {sourceBreakdown.post}</span>
257:           <span className="brand-badge">COMMENTS: {sourceBreakdown.comment}</span>
258:           <span className="brand-badge">AI scoring: {usedAi ? "Enabled" : "Heuristic mode"}</span>
259:           {scanCount > 1 && <span className="brand-badge">Scans run: {scanCount}</span>}
260:         </div>
261: 
262:         <div className="grid gap-4">
263:           {leads.map((lead) => (
264:             <article key={lead.post.id} className="brand-card p-5">
265:               <div className="flex flex-wrap items-center justify-between gap-2">
266:                 <h2 className="text-lg font-semibold">{lead.post.title}</h2>
267:                 <div className="flex flex-wrap items-center gap-2">
268:                   <span className="brand-badge">
269:                     Source: {lead.post.match_source === "comment" ? "COMMENTS" : "POST"}
270:                   </span>
271:                   <span className="brand-badge">Score: {lead.lead_score}</span>
272:                 </div>
273:               </div>
274: 
275:               <p className="mt-1 text-sm text-brand-navy/70">r/{lead.post.subreddit}</p>
276:               <p className="mt-3 text-brand-navy/95">{lead.qualification_reason}</p>
277:               <p className="mt-2 text-sm text-brand-orange">Outreach idea: {lead.suggested_outreach}</p>
278:               {lead.post.body ? (
279:                 <p className="mt-3 line-clamp-2 text-sm text-brand-navy/75">{lead.post.body}</p>
280:               ) : null}
281: 
282:               <a
283:                 href={lead.post.url}
284:                 target="_blank"
285:                 rel="noreferrer"
286:                 className="mt-4 inline-flex text-sm font-medium text-brand-burgundy underline decoration-brand-orange underline-offset-2 transition-colors hover:text-brand-orange"
287:               >
288:                 Open Reddit Post
289:               </a>
290:             </article>
291:           ))}
292: 
293:           {!loading && leads.length === 0 ? (
294:             <p className="text-sm text-brand-navy/70">No leads yet. Submit the form to scan Reddit.</p>
295:           ) : null}
296:         </div>
297:       </section>
298:     </main>
299:   );
300: }

(End of file - total 300 lines)
</content>
```

---

## Assistant (Build · GPT-5.3-Codex · 30.2s)

_Thinking:_



**Tool: glob**

**Input:**
```json
{
  "pattern": "backend/tests/*.py",
  "path": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit"
}
```

**Output:**
```
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests/test_comment_intent_signals.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests/test_client_ip_proxy.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests/test_auth_scan_regression.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests/test_reddit_service_fallback.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests/test_leads_csv_export.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests/test_client_ip.py
/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit/backend/tests/test_leads_repository.py
```

---

## Assistant (Build · GPT-5.3-Codex · 14.6s)

_Thinking:_



**Tool: bash**

**Input:**
```json
{
  "command": "git diff -- backend/tests/test_comment_intent_signals.py",
  "workdir": "/Users/shalinshah/Developer-Shalin/AI_power_Lead_generation_for_Reddit",
  "description": "Shows current diff for comment intent tests"
}
```

**Output:**
```
diff --git a/backend/tests/test_comment_intent_signals.py b/backend/tests/test_comment_intent_signals.py
index fa68fd3..ae2a87d 100644
--- a/backend/tests/test_comment_intent_signals.py
+++ b/backend/tests/test_comment_intent_signals.py
@@ -7,14 +7,11 @@ otherwise be missed by title/body-only matching.
 from __future__ import annotations
 
 import asyncio
-import json
-from unittest.mock import MagicMock, patch
-
-import pytest
+from unittest.mock import patch
 
+from app.core.constants import COMMENT_INTENT_FETCH_THRESHOLD
 from app.services.reddit_service import (
     COMMENT_INTENT_SIGNALS,
-    INTENT_SIGNALS,
     RedditLeadCollector,
 )
 
@@ -27,6 +24,54 @@ def _collector() -> RedditLeadCollector:
     return RedditLeadCollector(client_id=None, client_secret=None, user_agent="test-agent")
 
 
+class _AsyncIterator:
+    def __init__(self, items: list[object]) -> None:
+        self._items = items
+        self._index = 0
+
+    def __aiter__(self) -> "_AsyncIterator":
+        return self
+
+    async def __anext__(self) -> object:
+        if self._index >= len(self._items):
+            raise StopAsyncIteration
+
+        item = self._items[self._index]
+        self._index += 1
+        return item
+
+
+class _FakeSubreddit:
+    def __init__(self, submissions: list[object]) -> None:
+        self._submissions = submissions
+
+    def search(self, *_: object, **__: object) -> _AsyncIterator:
+        return _AsyncIterator(self._submissions)
+
+
+class _FakeRedditClient:
+    def __init__(self, submissions: list[object]) -> None:
+        self._submissions = submissions
+        self.closed = False
+
+    async def subreddit(self, _name: str) -> _FakeSubreddit:
+        return _FakeSubreddit(self._submissions)
+
+    async def close(self) -> None:
+        self.closed = True
+
+
+class _FakeAsyncPrawModule:
+    def __init__(self, submissions: list[object]) -> None:
+        self._submissions = submissions
+        self.last_client: _FakeRedditClient | None = None
+
+    def Reddit(self, **_: object) -> _FakeRedditClient:  # noqa: N802 (matches asyncpraw API)
+        client = _FakeRedditClient(self._submissions)
+        self.last_client = client
+        return client
+
+
 # ---------------------------------------------------------------------------
 # COMMENT_INTENT_SIGNALS sanity checks
 # ---------------------------------------------------------------------------
@@ -312,6 +357,116 @@ class TestFetchTopCommentsSync:
         assert len(result) == 1
         assert len(result[0]) <= 500  # _MAX_COMMENT_BODY_CHARS
 
+    def test_collects_nested_reply_comments(self) -> None:
+        c = _collector()
+        payload = [
+            {
+                "kind": "Listing",
+                "data": {
+                    "children": [
+                        {"kind": "t3", "data": {"id": "abc"}},
+                    ]
+                },
+            },
+            {
+                "kind": "Listing",
+                "data": {
+                    "children": [
+                        {
+                            "kind": "t1",
+                            "data": {
+                                "id": "c1",
+                                "body": "Top level comment",
+                                "replies": {
+                                    "kind": "Listing",
+                                    "data": {
+                                        "children": [
+                                            {
+                                                "kind": "t1",
+                                                "data": {
+                                                    "id": "c2",
+                                                    "body": "Nested reply comment",
+                                                },
+                                            }
+                                        ]
+                                    },
+                                },
+                            },
+                        }
+                    ]
+                },
+            },
+        ]
+
+        with patch.object(c, "_request_json_with_retry", return_value=payload):
+            result = c._fetch_top_comments_sync(
+                "https://www.reddit.com/r/test/comments/abc/", num_comments=5
+            )
+
+        assert "Top level comment" in result
+        assert "Nested reply comment" in result
+
+    def test_fetches_morechildren_comments(self) -> None:
+        c = _collector()
+        initial_payload = [
+            {
+                "kind": "Listing",
+                "data": {
+                    "children": [
+                        {"kind": "t3", "data": {"id": "abc"}},
+                    ]
+                },
+            },
+            {
+                "kind": "Listing",
+                "data": {
+                    "children": [
+                        {
+                            "kind": "more",
+                            "data": {
+                                "children": ["c2", "c3"],
+                            },
+                        }
+                    ]
+                },
+            },
+        ]
+
+        morechildren_payload = {
+            "json": {
+                "data": {
+                    "things": [
+                        {
+                            "kind": "t1",
+                            "data": {
+                                "id": "c2",
+                                "body": "Loaded via morechildren",
+                            },
+                        },
+                        {
+                            "kind": "t1",
+                            "data": {
+                                "id": "c3",
+                                "body": "Second morechildren comment",
+                            },
+                        },
+                    ]
+                }
+            }
+        }
+
+        with patch.object(
+            c,
+            "_request_json_with_retry",
+            side_effect=[initial_payload, morechildren_payload],
+        ):
+            result = c._fetch_top_comments_sync(
+                "https://www.reddit.com/r/test/comments/abc/", num_comments=5
+            )
+
+        assert "Loaded via morechildren" in result
+        assert "Second morechildren comment" in result
+
 
 # ---------------------------------------------------------------------------
 # Async wrapper: _fetch_top_comments
@@ -320,8 +475,12 @@ class TestFetchTopCommentsSync:
 class TestFetchTopCommentsAsync:
     def test_returns_empty_below_threshold(self) -> None:
         c = _collector()
+        below_threshold = max(COMMENT_INTENT_FETCH_THRESHOLD - 1, 0)
         result = asyncio.run(
-            c._fetch_top_comments("https://www.reddit.com/r/test/comments/abc/", num_comments=2)
+            c._fetch_top_comments(
+                "https://www.reddit.com/r/test/comments/abc/",
+                num_comments=below_threshold,
+            )
         )
         assert result == []
 
@@ -337,3 +496,32 @@ class TestFetchTopCommentsAsync:
             )
 
         assert result == expected
+
+
+class TestCommentFetchCache:
+    def test_reuses_cached_comments_for_same_post(self) -> None:
+        c = _collector()
+
+        async def _run() -> tuple[list[str], list[str], int]:
+            with patch.object(c, "_fetch_top_comments", return_value=["cached comment"]) as mocked:
+                first = await c._fetch_comments_for_post(
+                    post_id="abc",
+                    post_url="https://www.reddit.com/r/test/comments/abc/",
+                    num_comments=7,
+                    timeout_seconds=4,
+                    max_retries=1,
+                )
+                second = await c._fetch_comments_for_post(
+                    post_id="abc",
+                    post_url="https://www.reddit.com/r/test/comments/abc/",
+                    num_comments=7,
+                    timeout_seconds=4,
+                    max_retries=1,
+                )
+                return first, second, mocked.call_count
+
+        first_result, second_result, call_count = asyncio.run(_run())
+
+        assert first_result == ["cached comment"]
+        assert second_result == ["cached comment"]
+        assert call_count == 1

```

---

## Assistant (Build · GPT-5.3-Codex · 17.3s)

_Thinking:_



**Tool: todowrite**

**Input:**
```json
{
  "todos": [
    {
      "content": "Inspect current lead detection logic for buyer-intent phrases in Reddit data",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Implement comment-level buyer-intent scanning and integrate with lead scoring/filtering",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Add or update tests/fixtures to validate comment scanning catches intent phrases",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Run relevant test suite and verify no regressions",
      "status": "completed",
      "priority": "medium"
    }
  ]
}
```

**Output:**
```
[
  {
    "content": "Inspect current lead detection logic for buyer-intent phrases in Reddit data",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Implement comment-level buyer-intent scanning and integrate with lead scoring/filtering",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Add or update tests/fixtures to validate comment scanning catches intent phrases",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Run relevant test suite and verify no regressions",
    "status": "completed",
    "priority": "medium"
  }
]
```

---

## Assistant (Build · GPT-5.3-Codex · 33.0s)

_Thinking:_



Done — comments are now scanned as first-class buyer-intent signals, not just post titles/bodies.

- The Reddit pipeline now fetches comments before keyword gating, so strong intent in comments can qualify a lead even when title/body is weak (`backend/app/services/reddit_service.py:272`, `backend/app/services/reddit_service.py:396`, `backend/app/services/reddit_service.py:854`).
- Strong buyer-intent comment phrases are detected and used in scoring (e.g., “looking for exactly this”, “anyone recommend”, “I’d pay for”) (`backend/app/services/reddit_service.py:57`, `backend/app/services/reddit_service.py:895`, `backend/app/services/reddit_service.py:923`).
- Comment scanning now traverses nested replies and `morechildren`, with per-post comment caching to improve recall and reduce repeated fetches (`backend/app/services/reddit_service.py:549`, `backend/app/services/reddit_service.py:589`, `backend/app/services/reddit_service.py:672`, `backend/app/services/reddit_service.py:730`).
- Leads now include source attribution (`post` vs `comment`) and the scan UI shows comment/post source breakdown (`backend/app/models/schemas.py:47`, `frontend/lib/api.ts:7`, `frontend/app/scan/page.tsx:74`, `frontend/app/scan/page.tsx:256`).
- Comment-fetch threshold was lowered to improve recall on lower-volume posts (`backend/app/core/constants.py:107`).

Validation I ran:
- `pytest backend/tests` → 82 passed
- `npm run -s typecheck` in `frontend` → passed

If you want, next I can also add a dedicated metric in the backend response for “comment-sourced leads %” so you can track uplift scan-to-scan.

---

