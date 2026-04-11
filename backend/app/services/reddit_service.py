import asyncio
import json
import logging
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any

from app.models.schemas import CandidatePost, LeadScanRequest

try:
    import asyncpraw
except Exception:
    asyncpraw = None


logger = logging.getLogger(__name__)

DEFAULT_SUBREDDITS = ["entrepreneur", "smallbusiness", "marketing"]
MAX_KEYWORDS_TO_SEARCH = 6
MAX_SUBREDDITS_TO_SEARCH = 12
MIN_QUERY_LIMIT = 5
MAX_QUERY_LIMIT = 25
PUBLIC_SEARCH_CACHE_TTL_SECONDS = 60
PUBLIC_SEARCH_MAX_RETRIES = 3
PUBLIC_SEARCH_BASE_BACKOFF_SECONDS = 0.5
REQUEST_TIMEOUT_SECONDS = 15

INTENT_SIGNALS = (
    "looking for",
    "recommend",
    "recommendation",
    "what app",
    "which app",
    "any app",
    "alternative",
    "need help",
    "struggling",
    "help me",
)

LOW_INTENT_SIGNALS = (
    "progress pic",
    "before and after",
    "my journey",
    "nsv",
    "weigh-in",
)


class RedditLeadCollector:
    def __init__(
        self,
        client_id: str | None,
        client_secret: str | None,
        user_agent: str
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self._public_search_cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}

    async def fetch_candidate_posts(
        self,
        request: LeadScanRequest,
        seen_post_ids: set[str] | None = None,
    ) -> list[CandidatePost]:
        """Fetch candidate posts, excluding any IDs in *seen_post_ids*."""
        seen = seen_post_ids or set()
        max_candidates = max(request.limit * 4, 50)  # fetch extra so we have room after dedup
        raw_keywords = request.keywords or self._derive_keywords(request.business_description)
        keywords = self._prepare_keywords(raw_keywords)
        subreddits = self._normalize_subreddits(request.subreddits or DEFAULT_SUBREDDITS)

        if not keywords:
            keywords = self._prepare_keywords(self._derive_keywords(request.business_description))
        if not subreddits:
            subreddits = DEFAULT_SUBREDDITS

        # Try progressively wider time windows so repeat scans surface fresh posts.
        time_filters = ["week", "month", "year", "all"]
        all_posts: list[CandidatePost] = []

        for time_filter in time_filters:
            if self._has_credentials() and asyncpraw is not None:
                posts = await self._fetch_with_authenticated_api(
                    subreddits=subreddits,
                    keywords=keywords,
                    request_limit=request.limit,
                    max_candidates=max_candidates,
                    time_filter=time_filter,
                )
                if posts:
                    new_posts = [p for p in posts if p.id not in seen]
                    all_posts.extend(new_posts)
                    if len(all_posts) >= request.limit:
                        break
                    # Not enough new results — widen the time window
                    continue

            posts = await self._fetch_with_public_search(
                subreddits=subreddits,
                keywords=keywords,
                request_limit=request.limit,
                max_candidates=max_candidates,
                time_filter=time_filter,
            )
            new_posts = [p for p in posts if p.id not in seen]
            all_posts.extend(new_posts)
            if len(all_posts) >= request.limit:
                break

        # Remove duplicates introduced by multi-pass while preserving rank order
        seen_ids: set[str] = set()
        unique_posts: list[CandidatePost] = []
        for post in all_posts:
            if post.id not in seen_ids:
                seen_ids.add(post.id)
                unique_posts.append(post)

        if unique_posts:
            return unique_posts[:max_candidates]

        # Last-resort: return sample posts that are not already seen
        sample = self._sample_posts(request)
        return [p for p in sample if p.id not in seen] or sample

    async def _fetch_with_authenticated_api(
        self,
        subreddits: list[str],
        keywords: list[str],
        request_limit: int,
        max_candidates: int,
        time_filter: str = "month",
    ) -> list[CandidatePost]:
        if not self._has_credentials() or asyncpraw is None:
            return []

        reddit = asyncpraw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent
        )

        per_query_limit = self._per_query_limit(request_limit, len(subreddits))

        collected: dict[str, tuple[CandidatePost, float]] = {}

        try:
            for subreddit_name in subreddits:
                subreddit = await reddit.subreddit(subreddit_name)

                for keyword in keywords:
                    async for submission in subreddit.search(
                        keyword,
                        sort="new",          # "new" surfaces recent & varied posts
                        time_filter=time_filter,
                        limit=per_query_limit,
                    ):
                        if getattr(submission, "stickied", False):
                            continue

                        post_id = str(submission.id)
                        author = str(submission.author) if submission.author else "unknown"
                        body = getattr(submission, "selftext", "") or ""
                        title = str(submission.title or "")
                        url = f"https://www.reddit.com{submission.permalink}"

                        if not self._is_valid_post_url(url):
                            continue
                        if not self._is_keyword_match(title, body, keyword):
                            continue

                        score = int(getattr(submission, "score", 0) or 0)
                        num_comments = int(getattr(submission, "num_comments", 0) or 0)

                        candidate = CandidatePost(
                            id=post_id,
                            title=title,
                            body=body,
                            subreddit=subreddit_name,
                            url=url,
                            author=author,
                            created_utc=datetime.fromtimestamp(float(submission.created_utc), tz=timezone.utc),
                            score=score,
                            num_comments=num_comments,
                        )

                        relevance = self._score_keyword_match(
                            title=title,
                            body=body,
                            keyword=keyword,
                            score=score,
                            num_comments=num_comments,
                        )

                        existing = collected.get(post_id)
                        if existing is None or relevance > existing[1]:
                            collected[post_id] = (candidate, relevance)

                        if len(collected) >= max_candidates:
                            return self._rank_collected_posts(collected, max_candidates)

        except Exception as error:
            logger.warning("Authenticated Reddit search failed, using public fallback: %s", error)
            return []
        finally:
            await reddit.close()

        return self._rank_collected_posts(collected, max_candidates)

    async def _fetch_with_public_search(
        self,
        subreddits: list[str],
        keywords: list[str],
        request_limit: int,
        max_candidates: int,
        time_filter: str = "month",
    ) -> list[CandidatePost]:
        if not subreddits:
            return []

        per_query_limit = self._per_query_limit(request_limit, len(subreddits))
        collected: dict[str, tuple[CandidatePost, float]] = {}

        for subreddit_name in subreddits:
            for keyword in keywords:
                listing = await asyncio.to_thread(
                    self._fetch_public_search_listing,
                    subreddit_name,
                    keyword,
                    per_query_limit,
                    time_filter,
                )

                for item in listing:
                    post_data = item.get("data", {})
                    if not post_data or post_data.get("stickied"):
                        continue

                    post_id = str(post_data.get("id") or "")
                    if not post_id:
                        continue

                    title = str(post_data.get("title") or "")
                    body = str(post_data.get("selftext") or "")
                    permalink = str(post_data.get("permalink") or "")
                    fallback_url = str(post_data.get("url") or "")
                    url = f"https://www.reddit.com{permalink}" if permalink else fallback_url
                    if not self._is_valid_post_url(url):
                        continue
                    if not self._is_keyword_match(title, body, keyword):
                        continue

                    created_utc_value = float(post_data.get("created_utc") or 0)
                    created_utc = (
                        datetime.fromtimestamp(created_utc_value, tz=timezone.utc)
                        if created_utc_value > 0
                        else datetime.now(tz=timezone.utc)
                    )

                    score = int(post_data.get("score") or 0)
                    num_comments = int(post_data.get("num_comments") or 0)

                    candidate = CandidatePost(
                        id=post_id,
                        title=title,
                        body=body,
                        subreddit=str(post_data.get("subreddit") or subreddit_name),
                        url=url,
                        author=str(post_data.get("author") or "unknown"),
                        created_utc=created_utc,
                        score=score,
                        num_comments=num_comments,
                    )

                    relevance = self._score_keyword_match(
                        title=title,
                        body=body,
                        keyword=keyword,
                        score=score,
                        num_comments=num_comments,
                    )

                    existing = collected.get(post_id)
                    if existing is None or relevance > existing[1]:
                        collected[post_id] = (candidate, relevance)

                    if len(collected) >= max_candidates:
                        return self._rank_collected_posts(collected, max_candidates)

        return self._rank_collected_posts(collected, max_candidates)

    def _fetch_public_search_listing(
        self,
        subreddit_name: str,
        keyword: str,
        limit: int,
        time_filter: str = "month",
    ) -> list[dict[str, Any]]:
        cache_key = f"{subreddit_name}|{keyword.lower()}|{limit}|{time_filter}"
        now = time.time()
        cached = self._public_search_cache.get(cache_key)
        if cached and (now - cached[0] <= PUBLIC_SEARCH_CACHE_TTL_SECONDS):
            return cached[1]

        encoded_keyword = urllib.parse.quote(keyword)
        url = (
            f"https://www.reddit.com/r/{subreddit_name}/search.json"
            f"?q={encoded_keyword}&restrict_sr=1&sort=new&t={time_filter}&limit={limit}"
        )

        user_agent = self.user_agent or "f1bot-local"
        payload = self._request_json_with_retry(url=url, user_agent=user_agent)
        if not payload:
            return []

        children = payload.get("data", {}).get("children", [])
        if not isinstance(children, list):
            return []

        self._prune_public_cache(now)
        self._public_search_cache[cache_key] = (now, children)
        return children

    def _request_json_with_retry(self, url: str, user_agent: str) -> dict[str, Any] | None:
        request = urllib.request.Request(url, headers={"User-Agent": user_agent})

        for attempt in range(PUBLIC_SEARCH_MAX_RETRIES):
            try:
                with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                    raw = response.read().decode("utf-8")
                return json.loads(raw)
            except urllib.error.HTTPError as error:
                should_retry = error.code in {429, 500, 502, 503, 504} and attempt < PUBLIC_SEARCH_MAX_RETRIES - 1
                if should_retry:
                    retry_after = error.headers.get("Retry-After") if error.headers else None
                    time.sleep(self._retry_delay(attempt, retry_after))
                    continue
                logger.warning("Public Reddit search HTTP error for %s: %s", url, error)
                return None
            except (urllib.error.URLError, TimeoutError) as error:
                if attempt < PUBLIC_SEARCH_MAX_RETRIES - 1:
                    time.sleep(self._retry_delay(attempt, None))
                    continue
                logger.warning("Public Reddit search network error for %s: %s", url, error)
                return None
            except json.JSONDecodeError as error:
                logger.warning("Public Reddit search JSON parse error for %s: %s", url, error)
                return None

        return None

    def _retry_delay(self, attempt: int, retry_after: str | None) -> float:
        if retry_after:
            try:
                return min(float(retry_after), 5.0)
            except ValueError:
                pass
        return min(PUBLIC_SEARCH_BASE_BACKOFF_SECONDS * (2 ** attempt), 5.0)

    def _prune_public_cache(self, now: float) -> None:
        stale_keys = [
            key for key, (created_at, _) in self._public_search_cache.items()
            if now - created_at > PUBLIC_SEARCH_CACHE_TTL_SECONDS
        ]
        for key in stale_keys:
            del self._public_search_cache[key]

    def _rank_collected_posts(
        self,
        collected: dict[str, tuple[CandidatePost, float]],
        max_candidates: int,
    ) -> list[CandidatePost]:
        ranked = sorted(
            collected.values(),
            key=lambda item: (
                item[1],
                item[0].num_comments,
                item[0].score,
                item[0].created_utc,
                item[0].id,
            ),
            reverse=True,
        )

        return [item[0] for item in ranked[:max_candidates]]

    def _is_valid_post_url(self, url: str) -> bool:
        return bool(url and url.startswith("https://www.reddit.com/"))

    def _is_keyword_match(self, title: str, body: str, keyword: str) -> bool:
        content = f"{title} {body}".lower()
        token_hits, phrase_hit = self._keyword_match_stats(content, keyword)
        if phrase_hit:
            return True

        keyword_tokens = [token for token in keyword.lower().split() if token]
        if not keyword_tokens:
            return False

        minimum_hits = 1 if len(keyword_tokens) <= 2 else 2
        if token_hits < minimum_hits:
            return False

        if len(keyword_tokens) >= 3 and token_hits < len(keyword_tokens) and not self._has_intent_signal(title, body):
            return False

        return True

    def _keyword_match_stats(self, content: str, keyword: str) -> tuple[int, bool]:
        normalized_keyword = " ".join(keyword.strip().lower().split())
        if not normalized_keyword:
            return (0, False)

        tokens = {token for token in normalized_keyword.split() if token}
        token_hits = sum(1 for token in tokens if token in content)
        phrase_hit = normalized_keyword in content
        return (token_hits, phrase_hit)

    def _has_intent_signal(self, title: str, body: str) -> bool:
        content = f"{title} {body}".lower()
        if "?" in title or "?" in body:
            return True
        return any(signal in content for signal in INTENT_SIGNALS)

    def _score_keyword_match(
        self,
        title: str,
        body: str,
        keyword: str,
        score: int,
        num_comments: int,
    ) -> float:
        content = f"{title} {body}".lower()
        token_hits, phrase_hit = self._keyword_match_stats(content, keyword)

        intent_bonus = 2.0 if self._has_intent_signal(title, body) else 0.0
        low_intent_penalty = 2.5 if any(signal in content for signal in LOW_INTENT_SIGNALS) else 0.0

        keyword_score = (token_hits * 4.0) + (6.0 if phrase_hit else 0.0)
        engagement_score = (min(num_comments, 80) * 0.02) + (min(max(score, 0), 200) * 0.004)

        return max(0.0, keyword_score + intent_bonus + engagement_score - low_intent_penalty)

    def _per_query_limit(self, request_limit: int, subreddit_count: int) -> int:
        return min(MAX_QUERY_LIMIT, max(MIN_QUERY_LIMIT, request_limit // max(subreddit_count, 1)))

    def _prepare_keywords(self, keywords: list[str]) -> list[str]:
        prepared: list[str] = []
        seen: set[str] = set()

        for raw in keywords:
            for part in re.split(r"[,;|]", str(raw)):
                cleaned = " ".join(part.strip().split())
                if len(cleaned) < 2:
                    continue

                normalized = cleaned.lower()
                if normalized in seen:
                    continue
                seen.add(normalized)
                prepared.append(cleaned)

        if len(prepared) > MAX_KEYWORDS_TO_SEARCH:
            logger.info(
                "Keyword list truncated from %s to %s entries for Reddit search",
                len(prepared),
                MAX_KEYWORDS_TO_SEARCH,
            )

        return prepared[:MAX_KEYWORDS_TO_SEARCH]

    def _normalize_subreddits(self, subreddits: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()

        for raw in subreddits:
            for part in re.split(r"[,;|]", str(raw)):
                cleaned = part.strip().lower()
                if cleaned.startswith("r/"):
                    cleaned = cleaned[2:]
                cleaned = cleaned.replace(" ", "")
                if not cleaned:
                    continue
                if not re.fullmatch(r"[a-z0-9_]{3,32}", cleaned):
                    continue
                if cleaned in seen:
                    continue
                seen.add(cleaned)
                normalized.append(cleaned)

        return normalized[:MAX_SUBREDDITS_TO_SEARCH]

    def _has_credentials(self) -> bool:
        return bool(self.client_id and self.client_secret and self.user_agent)

    def _derive_keywords(self, description: str) -> list[str]:
        words = [word.strip(".,!? ").lower() for word in description.split()]
        unique = []
        seen = set()
        for word in words:
            if len(word) < 4 or word in seen:
                continue
            seen.add(word)
            unique.append(word)
        return unique[:6] or ["need help", "recommendation"]

    def _sample_posts(self, request: LeadScanRequest) -> list[CandidatePost]:
        now = datetime.now(tz=timezone.utc)
        business_hint = request.business_description[:40]

        sample_data: list[dict[str, Any]] = [
            {
                "id": "sample-1",
                "title": "Need better way to find qualified leads for my Shopify brand",
                "body": "Spent money on ads but lead quality is weak. Any practical tools?",
                "subreddit": "smallbusiness",
                "url": "https://www.reddit.com/r/smallbusiness/",
                "author": "founder_01",
                "score": 29,
                "num_comments": 16,
                "hours_ago": 4
            },
            {
                "id": "sample-2",
                "title": "What outreach strategy works in B2B SaaS in 2026?",
                "body": "Looking for workflow to identify warm intent from communities.",
                "subreddit": "sales",
                "url": "https://www.reddit.com/r/sales/",
                "author": "growth_hacker",
                "score": 17,
                "num_comments": 11,
                "hours_ago": 8
            },
            {
                "id": "sample-3",
                "title": "Any AI tool to monitor Reddit for buyer intent?",
                "body": f"Context: {business_hint}. Want a daily qualified lead list.",
                "subreddit": "entrepreneur",
                "url": "https://www.reddit.com/r/entrepreneur/",
                "author": "solofounder",
                "score": 35,
                "num_comments": 22,
                "hours_ago": 2
            },
            {
                "id": "sample-4",
                "title": "Which communities are good for service business lead generation?",
                "body": "Trying Reddit + LinkedIn combo and need a repeatable system.",
                "subreddit": "marketing",
                "url": "https://www.reddit.com/r/marketing/",
                "author": "agency_ops",
                "score": 13,
                "num_comments": 7,
                "hours_ago": 15
            }
        ]

        posts: list[CandidatePost] = []
        for item in sample_data:
            posts.append(
                CandidatePost(
                    id=item["id"],
                    title=item["title"],
                    body=item["body"],
                    subreddit=item["subreddit"],
                    url=item["url"],
                    author=item["author"],
                    created_utc=now - timedelta(hours=item["hours_ago"]),
                    score=item["score"],
                    num_comments=item["num_comments"]
                )
            )

        return posts[: max(1, min(request.limit, len(posts)))]
