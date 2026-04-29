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

from app.core.constants import COMMENT_INTENT_FETCH_THRESHOLD
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

MAX_QUERY_COMBINATIONS_PER_SCAN = 42
MAX_COMMENT_FETCHES_PER_SCAN = 24
SCAN_TIME_BUDGET_SECONDS = 45
PUBLIC_SEARCH_LISTING_TIMEOUT_SECONDS = 8
PUBLIC_SEARCH_LISTING_MAX_RETRIES = 2
COMMENT_FETCH_TIMEOUT_SECONDS = 4
COMMENT_FETCH_MAX_RETRIES = 1
COMMENT_MORECHILDREN_BATCH_SIZE = 100

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

# Stronger buyer-intent phrases that predominantly surface in comment threads.
# These are high-precision — matching even one is a reliable purchase-intent signal.
COMMENT_INTENT_SIGNALS = (
    "looking for exactly this",
    "this is exactly what i need",
    "anyone recommend",
    "can anyone recommend",
    "can someone recommend",
    "what do you recommend",
    "does anyone know a tool",
    "anyone know of a good",
    "is there a tool that",
    "is there an app that",
    "is there a service that",
    "what tool should i use",
    "which tool should i use",
    "need a tool for",
    "need software for",
    "need an app for",
    "have you tried",
    "i would pay for",
    "i'd pay for",
    "happy to pay for",
    "willing to pay",
    "paid tool for",
    "looking to buy",
    "ready to buy",
    "where can i find",
    "how do i find",
    "any good alternatives",
    "what do you use for",
    "what's the best way to",
    "what is the best way to",
)

# Signals that usually indicate the author is promoting themselves/services,
# not seeking help. These should be excluded from lead capture.
SELLER_PROMO_SIGNALS = (
    "available for hire",
    "open for work",
    "open to work",
    "for hire",
    "hire me",
    "dm me",
    "message me",
    "inbox me",
    "reach out to me",
    "contact me",
    "freelancer here",
    "i am a freelancer",
    "i'm a freelancer",
    "developer here",
    "i am a developer",
    "i'm a developer",
    "my services",
    "my portfolio",
)

LOW_INTENT_SIGNALS = (
    "progress pic",
    "before and after",
    "my journey",
    "nsv",
    "weigh-in",
)


def _normalize_promo_text(text: str) -> str:
    lowered = text.lower().replace("'", "")
    normalized = re.sub(r"[^a-z0-9\s]", " ", lowered)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


_SELLER_PROMO_CONTEXT_PHRASES = (
    "for hire",
    "open to work",
    "open for work",
)
_SELLER_PROMO_EXACT_PHRASES = tuple(
    signal for signal in SELLER_PROMO_SIGNALS if signal not in _SELLER_PROMO_CONTEXT_PHRASES
)
_SELLER_PROMO_EXACT_PATTERNS = tuple(
    re.compile(rf"\b{re.escape(_normalize_promo_text(signal))}\b")
    for signal in _SELLER_PROMO_EXACT_PHRASES
    if _normalize_promo_text(signal)
)
_SELLER_PROMO_CONTEXT_TOKENS = {"i", "im", "me"}
_SELLER_PROMO_CONTEXT_WINDOW = 3
_SELLER_PROMO_CONTEXT_PHRASE_TOKENS = tuple(
    tuple(_normalize_promo_text(phrase).split())
    for phrase in _SELLER_PROMO_CONTEXT_PHRASES
    if _normalize_promo_text(phrase)
)




# Maximum number of comments to keep per post during scan-time intent checks.
_MAX_COMMENTS_TO_FETCH = 10
# Per-comment character limit stored on CandidatePost.
_MAX_COMMENT_BODY_CHARS = 500


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
        self._comment_cache: dict[str, list[str]] = {}

    async def fetch_candidate_posts(
        self,
        request: LeadScanRequest,
        seen_post_ids: set[str] | None = None,
        allow_sample_fallback: bool = True,
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

        scan_deadline = time.monotonic() + SCAN_TIME_BUDGET_SECONDS
        scan_budget = {
            "queries": MAX_QUERY_COMBINATIONS_PER_SCAN,
            "comments": MAX_COMMENT_FETCHES_PER_SCAN,
        }

        # Try progressively wider time windows so repeat scans surface fresh posts.
        time_filters = ["week", "month", "year", "all"]
        all_posts: list[CandidatePost] = []
        all_live_posts: list[CandidatePost] = []

        for time_filter in time_filters:
            if self._scan_deadline_exceeded(scan_deadline):
                logger.info(
                    "Stopping Reddit scan after %ss time budget.",
                    SCAN_TIME_BUDGET_SECONDS,
                )
                break
            if not self._has_query_budget(scan_budget):
                logger.info(
                    "Stopping Reddit scan after reaching query budget (%s combinations).",
                    MAX_QUERY_COMBINATIONS_PER_SCAN,
                )
                break

            if self._has_credentials() and asyncpraw is not None:
                posts = await self._fetch_with_authenticated_api(
                    subreddits=subreddits,
                    keywords=keywords,
                    request_limit=request.limit,
                    max_candidates=max_candidates,
                    time_filter=time_filter,
                    scan_budget=scan_budget,
                    scan_deadline=scan_deadline,
                )
                if posts:
                    all_live_posts.extend(posts)
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
                scan_budget=scan_budget,
                scan_deadline=scan_deadline,
            )
            all_live_posts.extend(posts)
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

        # We found live Reddit results, but all were already shown to this user.
        # Return those live posts instead of synthetic sample data.
        seen_live_ids: set[str] = set()
        unique_live_posts: list[CandidatePost] = []
        for post in all_live_posts:
            if post.id not in seen_live_ids:
                seen_live_ids.add(post.id)
                unique_live_posts.append(post)

        if unique_live_posts:
            logger.info(
                "No fresh Reddit posts found after deduplication; returning previously seen live posts."
            )
            return unique_live_posts[:max_candidates]

        if not allow_sample_fallback:
            logger.warning("No Reddit posts found from live search; sample fallback is disabled.")
            return []

        logger.warning("No Reddit posts found from live search; returning sample fallback posts.")
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
        scan_budget: dict[str, int] | None = None,
        scan_deadline: float | None = None,
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
                if self._scan_deadline_exceeded(scan_deadline):
                    return self._rank_collected_posts(collected, max_candidates)

                subreddit = await reddit.subreddit(subreddit_name)

                for keyword in keywords:
                    if self._scan_deadline_exceeded(scan_deadline):
                        return self._rank_collected_posts(collected, max_candidates)
                    if not self._consume_query_budget(scan_budget):
                        return self._rank_collected_posts(collected, max_candidates)

                    async for submission in subreddit.search(
                        keyword,
                        sort="new",          # "new" surfaces recent & varied posts
                        time_filter=time_filter,
                        limit=per_query_limit,
                    ):
                        if self._scan_deadline_exceeded(scan_deadline):
                            return self._rank_collected_posts(collected, max_candidates)

                        if getattr(submission, "stickied", False):
                            continue

                        post_id = str(submission.id)
                        author = str(submission.author) if submission.author else "unknown"
                        body = getattr(submission, "selftext", "") or ""
                        title = str(submission.title or "")
                        url = f"https://www.reddit.com{submission.permalink}"

                        if not self._is_valid_post_url(url):
                            continue

                        score = int(getattr(submission, "score", 0) or 0)
                        num_comments = int(getattr(submission, "num_comments", 0) or 0)

                        # Fetch comments before the keyword gate so intent-only
                        # comment leads still pass through.
                        top_comments: list[str] = []
                        if self._should_fetch_comments(
                            num_comments=num_comments,
                            scan_budget=scan_budget,
                            scan_deadline=scan_deadline,
                        ):
                            self._consume_comment_budget(scan_budget)
                            top_comments = await self._fetch_comments_for_post(
                                post_id=post_id,
                                post_url=url,
                                num_comments=num_comments,
                                timeout_seconds=COMMENT_FETCH_TIMEOUT_SECONDS,
                                max_retries=COMMENT_FETCH_MAX_RETRIES,
                            )

                        if not self._is_keyword_match(title, body, keyword, top_comments):
                            continue

                        match_source = self._determine_match_source(
                            title=title,
                            body=body,
                            keyword=keyword,
                            top_comments=top_comments,
                        )

                        candidate = CandidatePost(
                            id=post_id,
                            title=title,
                            body=body,
                            match_source=match_source,
                            subreddit=subreddit_name,
                            url=url,
                            author=author,
                            created_utc=datetime.fromtimestamp(float(submission.created_utc), tz=timezone.utc),
                            score=score,
                            num_comments=num_comments,
                            top_comments=top_comments,
                        )

                        relevance = self._score_keyword_match(
                            title=title,
                            body=body,
                            keyword=keyword,
                            score=score,
                            num_comments=num_comments,
                            top_comments=top_comments,
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
        scan_budget: dict[str, int] | None = None,
        scan_deadline: float | None = None,
    ) -> list[CandidatePost]:
        if not subreddits:
            return []

        per_query_limit = self._per_query_limit(request_limit, len(subreddits))
        collected: dict[str, tuple[CandidatePost, float]] = {}

        for subreddit_name in subreddits:
            if self._scan_deadline_exceeded(scan_deadline):
                return self._rank_collected_posts(collected, max_candidates)

            for keyword in keywords:
                if self._scan_deadline_exceeded(scan_deadline):
                    return self._rank_collected_posts(collected, max_candidates)
                if not self._consume_query_budget(scan_budget):
                    return self._rank_collected_posts(collected, max_candidates)

                listing = await asyncio.to_thread(
                    self._fetch_public_search_listing,
                    subreddit_name,
                    keyword,
                    per_query_limit,
                    time_filter,
                    PUBLIC_SEARCH_LISTING_MAX_RETRIES,
                    PUBLIC_SEARCH_LISTING_TIMEOUT_SECONDS,
                )

                for item in listing:
                    if self._scan_deadline_exceeded(scan_deadline):
                        return self._rank_collected_posts(collected, max_candidates)

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

                    score = int(post_data.get("score") or 0)
                    num_comments = int(post_data.get("num_comments") or 0)

                    # Fetch comments before the keyword gate so intent-only
                    # comment leads still pass through.
                    top_comments: list[str] = []
                    if self._should_fetch_comments(
                        num_comments=num_comments,
                        scan_budget=scan_budget,
                        scan_deadline=scan_deadline,
                    ):
                        self._consume_comment_budget(scan_budget)
                        top_comments = await self._fetch_comments_for_post(
                            post_id=post_id,
                            post_url=url,
                            num_comments=num_comments,
                            timeout_seconds=COMMENT_FETCH_TIMEOUT_SECONDS,
                            max_retries=COMMENT_FETCH_MAX_RETRIES,
                        )

                    if not self._is_keyword_match(title, body, keyword, top_comments):
                        continue

                    match_source = self._determine_match_source(
                        title=title,
                        body=body,
                        keyword=keyword,
                        top_comments=top_comments,
                    )

                    created_utc_value = float(post_data.get("created_utc") or 0)
                    created_utc = (
                        datetime.fromtimestamp(created_utc_value, tz=timezone.utc)
                        if created_utc_value > 0
                        else datetime.now(tz=timezone.utc)
                    )

                    candidate = CandidatePost(
                        id=post_id,
                        title=title,
                        body=body,
                        match_source=match_source,
                        subreddit=str(post_data.get("subreddit") or subreddit_name),
                        url=url,
                        author=str(post_data.get("author") or "unknown"),
                        created_utc=created_utc,
                        score=score,
                        num_comments=num_comments,
                        top_comments=top_comments,
                    )

                    relevance = self._score_keyword_match(
                        title=title,
                        body=body,
                        keyword=keyword,
                        score=score,
                        num_comments=num_comments,
                        top_comments=top_comments,
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
        max_retries: int = PUBLIC_SEARCH_MAX_RETRIES,
        timeout_seconds: float = REQUEST_TIMEOUT_SECONDS,
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
        payload = self._request_json_with_retry(
            url=url,
            user_agent=user_agent,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
        )
        if not isinstance(payload, dict):
            return []

        children = payload.get("data", {}).get("children", [])
        if not isinstance(children, list):
            return []

        self._prune_public_cache(now)
        self._public_search_cache[cache_key] = (now, children)
        return children

    def _request_json_with_retry(
        self,
        url: str,
        user_agent: str,
        max_retries: int = PUBLIC_SEARCH_MAX_RETRIES,
        timeout_seconds: float = REQUEST_TIMEOUT_SECONDS,
    ) -> dict[str, Any] | list[Any] | None:
        request = urllib.request.Request(url, headers={"User-Agent": user_agent})
        attempts = max(1, max_retries)
        request_timeout = max(1.0, timeout_seconds)

        for attempt in range(attempts):
            try:
                with urllib.request.urlopen(request, timeout=request_timeout) as response:
                    raw = response.read().decode("utf-8")
                return json.loads(raw)
            except urllib.error.HTTPError as error:
                should_retry = error.code in {429, 500, 502, 503, 504} and attempt < attempts - 1
                if should_retry:
                    retry_after = error.headers.get("Retry-After") if error.headers else None
                    time.sleep(self._retry_delay(attempt, retry_after))
                    continue
                logger.warning("Public Reddit search HTTP error for %s: %s", url, error)
                return None
            except (urllib.error.URLError, TimeoutError) as error:
                if attempt < attempts - 1:
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

    # ------------------------------------------------------------------
    # Comment fetching
    # ------------------------------------------------------------------

    async def _fetch_comments_for_post(
        self,
        post_id: str,
        post_url: str,
        num_comments: int,
        timeout_seconds: float,
        max_retries: int,
    ) -> list[str]:
        cached = self._comment_cache.get(post_id)
        if cached is not None:
            return cached

        comments = await self._fetch_top_comments(
            post_url=post_url,
            num_comments=num_comments,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )
        self._comment_cache[post_id] = comments
        return comments

    async def _fetch_top_comments(
        self,
        post_url: str,
        num_comments: int,
        timeout_seconds: float = COMMENT_FETCH_TIMEOUT_SECONDS,
        max_retries: int = COMMENT_FETCH_MAX_RETRIES,
    ) -> list[str]:
        """Async wrapper — runs the blocking HTTP call on a thread so the event
        loop stays free during the network round-trip."""
        if num_comments < COMMENT_INTENT_FETCH_THRESHOLD:
            return []
        return await asyncio.to_thread(
            self._fetch_top_comments_sync,
            post_url,
            num_comments,
            timeout_seconds,
            max_retries,
        )

    def _fetch_top_comments_sync(
        self,
        post_url: str,
        num_comments: int,
        timeout_seconds: float = COMMENT_FETCH_TIMEOUT_SECONDS,
        max_retries: int = COMMENT_FETCH_MAX_RETRIES,
    ) -> list[str]:
        """Fetch the full available comment tree for a post.

        Uses Reddit's public `<post_url>.json` endpoint (no auth required) so it
        works regardless of whether OAuth credentials are configured.  Falls back
        to an empty list on any network or parse failure so the lead pipeline is
        never blocked by a comment-fetch error.
        """
        if num_comments < COMMENT_INTENT_FETCH_THRESHOLD:
            return []

        json_url = post_url.rstrip("/") + ".json?limit=500&depth=10&raw_json=1"
        user_agent = self.user_agent or "f1bot-local"

        try:
            payload = self._request_json_with_retry(
                url=json_url,
                user_agent=user_agent,
                max_retries=max_retries,
                timeout_seconds=timeout_seconds,
            )
        except Exception:
            return []

        # Reddit returns a 2-element array: [post_listing, comment_listing]
        if not isinstance(payload, list) or len(payload) < 2:
            return []

        post_fullname = self._extract_post_fullname(payload[0], post_url)
        comment_listing = payload[1]
        children = (
            comment_listing.get("data", {}).get("children", [])
            if isinstance(comment_listing, dict)
            else []
        )

        comments: list[str] = []
        pending_more: list[str] = []
        seen_comment_ids: set[str] = set()
        seen_more_ids: set[str] = set()
        hit_comment_limit = self._collect_comments_from_nodes(
            nodes=children,
            comments=comments,
            pending_more=pending_more,
            seen_comment_ids=seen_comment_ids,
            seen_more_ids=seen_more_ids,
        )

        if hit_comment_limit or not post_fullname or not pending_more:
            return comments

        deadline = time.monotonic() + max(1.0, timeout_seconds)
        while (
            pending_more
            and len(comments) < _MAX_COMMENTS_TO_FETCH
            and time.monotonic() < deadline
        ):
            batch = self._next_more_batch(pending_more)
            if not batch:
                break

            extra_nodes = self._fetch_morechildren_sync(
                user_agent=user_agent,
                post_fullname=post_fullname,
                child_ids=batch,
                timeout_seconds=timeout_seconds,
                max_retries=max_retries,
            )
            if not extra_nodes:
                continue

            hit_comment_limit = self._collect_comments_from_nodes(
                nodes=extra_nodes,
                comments=comments,
                pending_more=pending_more,
                seen_comment_ids=seen_comment_ids,
                seen_more_ids=seen_more_ids,
            )
            if hit_comment_limit:
                break

        return comments

    def _collect_comments_from_nodes(
        self,
        nodes: list[dict[str, Any]],
        comments: list[str],
        pending_more: list[str],
        seen_comment_ids: set[str],
        seen_more_ids: set[str],
    ) -> bool:
        queue: list[dict[str, Any]] = [node for node in nodes if isinstance(node, dict)]
        cursor = 0

        while cursor < len(queue):
            if len(comments) >= _MAX_COMMENTS_TO_FETCH:
                return True

            node = queue[cursor]
            cursor += 1
            kind = str(node.get("kind") or "")
            data = node.get("data", {})
            if not isinstance(data, dict):
                continue

            if kind == "t1":
                comment_id = str(data.get("id") or "")
                if comment_id:
                    if comment_id in seen_comment_ids:
                        continue
                    seen_comment_ids.add(comment_id)

                body = str(data.get("body") or "").strip()
                if body and body not in {"[deleted]", "[removed]"}:
                    comments.append(body[:_MAX_COMMENT_BODY_CHARS])
                    if len(comments) >= _MAX_COMMENTS_TO_FETCH:
                        return True

                replies = data.get("replies")
                if isinstance(replies, dict):
                    reply_children = replies.get("data", {}).get("children", [])
                    if isinstance(reply_children, list):
                        queue.extend(child for child in reply_children if isinstance(child, dict))
                continue

            if kind == "more":
                child_ids = data.get("children", [])
                if not isinstance(child_ids, list):
                    continue

                for child_id in child_ids:
                    normalized = str(child_id or "").strip()
                    if not normalized or normalized in seen_more_ids:
                        continue
                    seen_more_ids.add(normalized)
                    pending_more.append(normalized)

        return len(comments) >= _MAX_COMMENTS_TO_FETCH

    def _next_more_batch(self, pending_more: list[str]) -> list[str]:
        if not pending_more:
            return []

        batch_size = min(COMMENT_MORECHILDREN_BATCH_SIZE, len(pending_more))
        batch = pending_more[:batch_size]
        del pending_more[:batch_size]
        return batch

    def _fetch_morechildren_sync(
        self,
        user_agent: str,
        post_fullname: str,
        child_ids: list[str],
        timeout_seconds: float,
        max_retries: int,
    ) -> list[dict[str, Any]]:
        if not child_ids:
            return []

        encoded_children = urllib.parse.quote(",".join(child_ids), safe=",")
        url = (
            "https://www.reddit.com/api/morechildren.json"
            f"?link_id={post_fullname}&children={encoded_children}"
            "&api_type=json&raw_json=1"
        )

        payload = self._request_json_with_retry(
            url=url,
            user_agent=user_agent,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
        )
        if not isinstance(payload, dict):
            return []

        things = payload.get("json", {}).get("data", {}).get("things", [])
        if not isinstance(things, list):
            return []
        return [node for node in things if isinstance(node, dict)]

    def _extract_post_fullname(self, post_listing: Any, post_url: str) -> str | None:
        if isinstance(post_listing, dict):
            children = post_listing.get("data", {}).get("children", [])
            if isinstance(children, list):
                for child in children:
                    if not isinstance(child, dict):
                        continue
                    post_id = str(child.get("data", {}).get("id") or "").strip()
                    if post_id:
                        return f"t3_{post_id}"

        match = re.search(r"/comments/([a-z0-9]+)/", post_url, flags=re.IGNORECASE)
        if match:
            return f"t3_{match.group(1)}"

        return None

    def _prune_public_cache(self, now: float) -> None:
        stale_keys = [
            key for key, (created_at, _) in self._public_search_cache.items()
            if now - created_at > PUBLIC_SEARCH_CACHE_TTL_SECONDS
        ]
        for key in stale_keys:
            del self._public_search_cache[key]

    def _scan_deadline_exceeded(self, scan_deadline: float | None) -> bool:
        if scan_deadline is None:
            return False
        return time.monotonic() >= scan_deadline

    def _has_query_budget(self, scan_budget: dict[str, int] | None) -> bool:
        if scan_budget is None:
            return True
        return scan_budget.get("queries", 0) > 0

    def _consume_query_budget(self, scan_budget: dict[str, int] | None) -> bool:
        if scan_budget is None:
            return True

        remaining = scan_budget.get("queries", 0)
        if remaining <= 0:
            return False

        scan_budget["queries"] = remaining - 1
        return True

    def _should_fetch_comments(
        self,
        num_comments: int,
        scan_budget: dict[str, int] | None,
        scan_deadline: float | None,
    ) -> bool:
        if num_comments < COMMENT_INTENT_FETCH_THRESHOLD:
            return False
        if self._scan_deadline_exceeded(scan_deadline):
            return False
        if scan_budget is None:
            return True
        return scan_budget.get("comments", 0) > 0

    def _consume_comment_budget(self, scan_budget: dict[str, int] | None) -> None:
        if scan_budget is None:
            return

        remaining = scan_budget.get("comments", 0)
        if remaining <= 0:
            return

        scan_budget["comments"] = remaining - 1

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

    def _is_keyword_match(
        self, title: str, body: str, keyword: str, top_comments: list[str] | None = None
    ) -> bool:
        if self._has_seller_promo_signal(title, body):
            return False

        content = f"{title} {body}".lower()
        token_hits, phrase_hit = self._keyword_match_stats(content, keyword)
        if phrase_hit:
            return True

        # A strong comment-level intent signal alone is sufficient to surface the post.
        if top_comments and self._has_comment_intent_signal(top_comments):
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

    def _has_comment_intent_signal(self, top_comments: list[str]) -> bool:
        """Return True if any comment contains a strong buyer-intent phrase.

        Checks both the general INTENT_SIGNALS and the higher-specificity
        COMMENT_INTENT_SIGNALS so nothing is double-counted.
        """
        for comment in top_comments:
            lowered = comment.lower()
            if any(signal in lowered for signal in COMMENT_INTENT_SIGNALS):
                return True
            if any(signal in lowered for signal in INTENT_SIGNALS):
                return True
        return False

    def _has_seller_promo_signal(self, title: str, body: str) -> bool:
        content = _normalize_promo_text(f"{title} {body}")
        if not content:
            return False

        for pattern in _SELLER_PROMO_EXACT_PATTERNS:
            if pattern.search(content):
                return True

        tokens = content.split()
        token_count = len(tokens)
        if not tokens:
            return False

        for phrase_tokens in _SELLER_PROMO_CONTEXT_PHRASE_TOKENS:
            if not phrase_tokens:
                continue
            phrase_len = len(phrase_tokens)
            if phrase_len == 0 or phrase_len > token_count:
                continue
            for index in range(token_count - phrase_len + 1):
                if tokens[index:index + phrase_len] != list(phrase_tokens):
                    continue
                window_start = max(0, index - _SELLER_PROMO_CONTEXT_WINDOW)
                window_end = min(token_count, index + phrase_len + _SELLER_PROMO_CONTEXT_WINDOW)
                if any(token in _SELLER_PROMO_CONTEXT_TOKENS for token in tokens[window_start:window_end]):
                    return True

        return False

    def _determine_match_source(
        self,
        title: str,
        body: str,
        keyword: str,
        top_comments: list[str] | None = None,
    ) -> str:
        post_match = self._is_keyword_match(title, body, keyword)
        comment_match = bool(top_comments) and self._has_comment_intent_signal(top_comments)

        if comment_match and not post_match:
            return "comment"
        return "post"

    def _score_keyword_match(
        self,
        title: str,
        body: str,
        keyword: str,
        score: int,
        num_comments: int,
        top_comments: list[str] | None = None,
    ) -> float:
        content = f"{title} {body}".lower()
        token_hits, phrase_hit = self._keyword_match_stats(content, keyword)

        intent_bonus = 2.0 if self._has_intent_signal(title, body) else 0.0
        low_intent_penalty = 2.5 if any(signal in content for signal in LOW_INTENT_SIGNALS) else 0.0
        seller_promo_penalty = 9.0 if self._has_seller_promo_signal(title, body) else 0.0

        # Extra relevance boost when a high-specificity buyer-intent phrase is
        # detected in the comment thread.  Kept intentionally modest (3.5) so it
        # lifts qualifying comment-intent posts without dominating the ranking.
        comment_intent_bonus = 0.0
        if top_comments:
            for comment in top_comments:
                lowered = comment.lower()
                if any(signal in lowered for signal in COMMENT_INTENT_SIGNALS):
                    comment_intent_bonus = 3.5
                    break
                if any(signal in lowered for signal in INTENT_SIGNALS):
                    comment_intent_bonus = max(comment_intent_bonus, 1.5)

        keyword_score = (token_hits * 4.0) + (6.0 if phrase_hit else 0.0)
        engagement_score = (min(num_comments, 80) * 0.02) + (min(max(score, 0), 200) * 0.004)

        return max(
            0.0,
            keyword_score + intent_bonus + comment_intent_bonus + engagement_score - low_intent_penalty - seller_promo_penalty,
        )

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
