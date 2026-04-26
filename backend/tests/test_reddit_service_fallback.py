from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from app.models.schemas import CandidatePost, LeadScanRequest
from app.services.reddit_service import RedditLeadCollector


def _scan_request() -> LeadScanRequest:
    return LeadScanRequest(
        business_description="We help founders find qualified Reddit leads with repeatable workflows.",
        keywords=["lead generation"],
        subreddits=["entrepreneur"],
        limit=3,
    )


def test_fetch_candidate_posts_returns_empty_when_sample_fallback_disabled() -> None:
    collector = RedditLeadCollector(client_id=None, client_secret=None, user_agent="f1bot-test")

    async def _empty_public_search(*_: object, **__: object) -> list[object]:
        return []

    collector._fetch_with_public_search = _empty_public_search  # type: ignore[method-assign]

    posts = asyncio.run(
        collector.fetch_candidate_posts(
            _scan_request(),
            seen_post_ids=set(),
            allow_sample_fallback=False,
        )
    )

    assert posts == []


def test_fetch_candidate_posts_returns_sample_when_sample_fallback_enabled() -> None:
    collector = RedditLeadCollector(client_id=None, client_secret=None, user_agent="f1bot-test")

    async def _empty_public_search(*_: object, **__: object) -> list[object]:
        return []

    collector._fetch_with_public_search = _empty_public_search  # type: ignore[method-assign]

    posts = asyncio.run(
        collector.fetch_candidate_posts(
            _scan_request(),
            seen_post_ids=set(),
            allow_sample_fallback=True,
        )
    )

    assert posts
    assert posts[0].id.startswith("sample-")


def test_fetch_candidate_posts_returns_live_posts_when_only_seen_results_exist() -> None:
    collector = RedditLeadCollector(client_id=None, client_secret=None, user_agent="f1bot-test")

    async def _seen_only_public_search(*_: object, **__: object) -> list[CandidatePost]:
        return [
            CandidatePost(
                id="live-1",
                title="Need help choosing lead-gen tooling",
                body="Trying to evaluate practical options.",
                subreddit="entrepreneur",
                url="https://www.reddit.com/r/entrepreneur/comments/live1/test/",
                author="founder-live",
                created_utc=datetime.now(tz=timezone.utc),
                score=12,
                num_comments=4,
            )
        ]

    collector._fetch_with_public_search = _seen_only_public_search  # type: ignore[method-assign]

    posts = asyncio.run(
        collector.fetch_candidate_posts(
            _scan_request(),
            seen_post_ids={"live-1"},
            allow_sample_fallback=True,
        )
    )

    assert posts
    assert posts[0].id == "live-1"
    assert not posts[0].id.startswith("sample-")
