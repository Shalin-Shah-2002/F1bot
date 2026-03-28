import asyncio
import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any

from app.models.schemas import CandidatePost, LeadScanRequest

try:
    import asyncpraw
except Exception:
    asyncpraw = None


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

    async def fetch_candidate_posts(self, request: LeadScanRequest) -> list[CandidatePost]:
        max_candidates = max(request.limit * 3, 30)
        keywords = request.keywords or self._derive_keywords(request.business_description)
        subreddits = request.subreddits or ["entrepreneur", "smallbusiness", "marketing"]

        if self._has_credentials() and asyncpraw is not None:
            posts = await self._fetch_with_authenticated_api(
                subreddits=subreddits,
                keywords=keywords,
                request_limit=request.limit,
                max_candidates=max_candidates,
            )
            if posts:
                return posts

        posts = await self._fetch_with_public_search(
            subreddits=subreddits,
            keywords=keywords,
            request_limit=request.limit,
            max_candidates=max_candidates,
        )
        if posts:
            return posts

        return self._sample_posts(request)

    async def _fetch_with_authenticated_api(
        self,
        subreddits: list[str],
        keywords: list[str],
        request_limit: int,
        max_candidates: int,
    ) -> list[CandidatePost]:
        if not self._has_credentials() or asyncpraw is None:
            return []

        reddit = asyncpraw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent
        )

        per_query_limit = max(5, request_limit // max(len(subreddits), 1))

        collected: dict[str, CandidatePost] = {}

        try:
            for subreddit_name in subreddits:
                subreddit = await reddit.subreddit(subreddit_name)

                for keyword in keywords[:6]:
                    async for submission in subreddit.search(keyword, sort="new", limit=per_query_limit):
                        if getattr(submission, "stickied", False):
                            continue

                        post_id = str(submission.id)
                        if post_id in collected:
                            continue

                        author = str(submission.author) if submission.author else "unknown"
                        body = getattr(submission, "selftext", "") or ""

                        collected[post_id] = CandidatePost(
                            id=post_id,
                            title=submission.title,
                            body=body,
                            subreddit=subreddit_name,
                            url=f"https://www.reddit.com{submission.permalink}",
                            author=author,
                            created_utc=datetime.fromtimestamp(float(submission.created_utc), tz=timezone.utc),
                            score=int(getattr(submission, "score", 0) or 0),
                            num_comments=int(getattr(submission, "num_comments", 0) or 0)
                        )

                        if len(collected) >= max_candidates:
                            break

                    if len(collected) >= max_candidates:
                        break

                if len(collected) >= max_candidates:
                    break
        except Exception:
            return []
        finally:
            await reddit.close()

        return list(collected.values())

    async def _fetch_with_public_search(
        self,
        subreddits: list[str],
        keywords: list[str],
        request_limit: int,
        max_candidates: int,
    ) -> list[CandidatePost]:
        if not subreddits:
            return []

        per_query_limit = min(25, max(5, request_limit // max(len(subreddits), 1)))
        collected: dict[str, tuple[CandidatePost, float]] = {}

        for subreddit_name in subreddits:
            for keyword in keywords[:6]:
                listing = await asyncio.to_thread(
                    self._fetch_public_search_listing,
                    subreddit_name,
                    keyword,
                    per_query_limit,
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
                    if not url:
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
                        break

                if len(collected) >= max_candidates:
                    break

            if len(collected) >= max_candidates:
                break

        ranked = sorted(
            collected.values(),
            key=lambda item: (item[1], item[0].num_comments, item[0].score, item[0].created_utc),
            reverse=True,
        )

        return [item[0] for item in ranked[:max_candidates]]

    def _fetch_public_search_listing(
        self,
        subreddit_name: str,
        keyword: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        encoded_keyword = urllib.parse.quote(keyword)
        url = (
            f"https://www.reddit.com/r/{subreddit_name}/search.json"
            f"?q={encoded_keyword}&restrict_sr=1&sort=new&t=month&limit={limit}"
        )

        user_agent = self.user_agent or "f1bot-local"
        request = urllib.request.Request(url, headers={"User-Agent": user_agent})

        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8", errors="replace"))
        except Exception:
            return []

        return payload.get("data", {}).get("children", [])

    def _score_keyword_match(
        self,
        title: str,
        body: str,
        keyword: str,
        score: int,
        num_comments: int,
    ) -> float:
        normalized_keyword = keyword.strip().lower()
        content = f"{title} {body}".lower()

        token_hits = sum(
            1 for token in normalized_keyword.split() if token and token in content
        )
        phrase_hit = 1 if normalized_keyword and normalized_keyword in content else 0

        return (
            token_hits
            + (2 * phrase_hit)
            + (min(num_comments, 60) * 0.04)
            + (min(score, 120) * 0.015)
        )

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
