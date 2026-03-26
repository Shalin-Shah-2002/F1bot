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
        if not self._has_credentials() or asyncpraw is None:
            return self._sample_posts(request)

        reddit = asyncpraw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent
        )

        max_candidates = max(request.limit * 3, 30)
        per_query_limit = max(5, request.limit // max(len(request.subreddits), 1))
        keywords = request.keywords or self._derive_keywords(request.business_description)
        subreddits = request.subreddits or ["entrepreneur", "smallbusiness", "marketing"]

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
            return self._sample_posts(request)
        finally:
            await reddit.close()

        if not collected:
            return self._sample_posts(request)

        return list(collected.values())

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
