"""Tests for comment-level buyer-intent detection.

These tests verify that strong purchase-intent signals appearing only in
Reddit comment threads are detected and used to surface leads that would
otherwise be missed by title/body-only matching.
"""
from __future__ import annotations

import asyncio
import json
from unittest.mock import MagicMock, patch

import pytest

from app.services.reddit_service import (
    COMMENT_INTENT_SIGNALS,
    INTENT_SIGNALS,
    RedditLeadCollector,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _collector() -> RedditLeadCollector:
    return RedditLeadCollector(client_id=None, client_secret=None, user_agent="test-agent")


# ---------------------------------------------------------------------------
# COMMENT_INTENT_SIGNALS sanity checks
# ---------------------------------------------------------------------------

class TestCommentIntentSignalsList:
    def test_signals_list_is_non_empty(self) -> None:
        assert len(COMMENT_INTENT_SIGNALS) > 0

    def test_high_specificity_phrases_present(self) -> None:
        """Key buyer-intent phrases must be in the list."""
        must_contain = [
            "anyone recommend",
            "looking for exactly this",
            "i would pay for",
            "willing to pay",
            "is there a tool that",
        ]
        for phrase in must_contain:
            assert phrase in COMMENT_INTENT_SIGNALS, f"Expected '{phrase}' in COMMENT_INTENT_SIGNALS"

    def test_all_signals_are_lowercase(self) -> None:
        """Signals must be lowercase so `.lower()` comparisons work correctly."""
        for sig in COMMENT_INTENT_SIGNALS:
            assert sig == sig.lower(), f"Signal not lowercase: {sig!r}"


# ---------------------------------------------------------------------------
# _has_comment_intent_signal
# ---------------------------------------------------------------------------

class TestHasCommentIntentSignal:
    def test_returns_false_for_empty_list(self) -> None:
        c = _collector()
        assert c._has_comment_intent_signal([]) is False

    def test_detects_comment_intent_phrase(self) -> None:
        c = _collector()
        comments = [
            "Has anyone dealt with this before?",
            "I would pay for a tool that does this automatically.",
        ]
        assert c._has_comment_intent_signal(comments) is True

    def test_detects_general_intent_signal_in_comment(self) -> None:
        c = _collector()
        comments = ["Any recommendation for a good CRM?"]
        assert c._has_comment_intent_signal(comments) is True

    def test_returns_false_when_no_signals_present(self) -> None:
        c = _collector()
        comments = [
            "Great post, thanks for sharing.",
            "I tried this yesterday and it worked.",
        ]
        assert c._has_comment_intent_signal(comments) is False

    def test_case_insensitive_detection(self) -> None:
        c = _collector()
        comments = ["ANYONE RECOMMEND a good email tool?"]
        assert c._has_comment_intent_signal(comments) is True

    def test_detects_signal_in_mixed_batch(self) -> None:
        c = _collector()
        comments = [
            "Interesting approach.",
            "Where can I find something like this?",
            "Nice writeup.",
        ]
        assert c._has_comment_intent_signal(comments) is True


# ---------------------------------------------------------------------------
# _is_keyword_match with top_comments
# ---------------------------------------------------------------------------

class TestIsKeywordMatchWithComments:
    def test_comment_intent_alone_passes_when_body_is_weak(self) -> None:
        """A post whose title/body barely matches the keyword should still
        pass _is_keyword_match when comments contain a strong intent signal."""
        c = _collector()
        # "automation" is the keyword; title/body only has "auto" (no direct hit)
        result = c._is_keyword_match(
            title="Just sharing my workflow",
            body="I use a couple of tools.",
            keyword="automation software",
            top_comments=["Looking for exactly this kind of automation software!"],
        )
        assert result is True

    def test_no_comments_still_matches_on_phrase(self) -> None:
        c = _collector()
        result = c._is_keyword_match(
            title="Need automation software for my team",
            body="",
            keyword="automation software",
            top_comments=[],
        )
        assert result is True

    def test_weak_title_body_and_no_intent_in_comments_fails(self) -> None:
        c = _collector()
        result = c._is_keyword_match(
            title="Random post about cooking",
            body="Here is my recipe.",
            keyword="automation software",
            top_comments=["Nice recipe!", "Thanks for sharing."],
        )
        assert result is False

    def test_backward_compatible_no_comments_arg(self) -> None:
        """Calling without top_comments must still work (defaults to None)."""
        c = _collector()
        result = c._is_keyword_match(
            title="Looking for lead generation software",
            body="Any recommendations?",
            keyword="lead generation",
        )
        assert result is True


# ---------------------------------------------------------------------------
# _score_keyword_match with top_comments
# ---------------------------------------------------------------------------

class TestScoreKeywordMatchWithComments:
    def test_comment_intent_signals_increase_relevance_score(self) -> None:
        c = _collector()
        base = c._score_keyword_match(
            title="Lead generation tips",
            body="Check out these strategies.",
            keyword="lead generation",
            score=10,
            num_comments=5,
            top_comments=[],
        )
        boosted = c._score_keyword_match(
            title="Lead generation tips",
            body="Check out these strategies.",
            keyword="lead generation",
            score=10,
            num_comments=5,
            top_comments=["Anyone recommend a good lead generation tool?"],
        )
        assert boosted > base

    def test_high_specificity_comment_gives_larger_boost_than_general(self) -> None:
        c = _collector()

        general_boost = c._score_keyword_match(
            title="Lead gen",
            body="",
            keyword="lead generation",
            score=5,
            num_comments=4,
            top_comments=["Any recommendation?"],
        )
        high_specificity_boost = c._score_keyword_match(
            title="Lead gen",
            body="",
            keyword="lead generation",
            score=5,
            num_comments=4,
            top_comments=["I would pay for a tool that does this automatically."],
        )
        assert high_specificity_boost >= general_boost

    def test_score_is_non_negative(self) -> None:
        c = _collector()
        result = c._score_keyword_match(
            title="Progress pic",
            body="Before and after my journey.",
            keyword="fitness",
            score=0,
            num_comments=0,
            top_comments=[],
        )
        assert result >= 0.0

    def test_no_comments_kwarg_is_backward_compatible(self) -> None:
        c = _collector()
        result = c._score_keyword_match(
            title="Lead generation tips",
            body="Here are my tips.",
            keyword="lead generation",
            score=5,
            num_comments=3,
        )
        assert result >= 0.0


# ---------------------------------------------------------------------------
# _fetch_top_comments_sync
# ---------------------------------------------------------------------------

class TestFetchTopCommentsSync:
    def _make_reddit_comment_payload(self, bodies: list[str]) -> list[dict]:
        """Build a minimal Reddit `.json` payload for comment fetching."""
        children = [
            {
                "kind": "t1",
                "data": {"body": body},
            }
            for body in bodies
        ]
        return [
            {"kind": "Listing", "data": {"children": []}},  # post listing
            {"kind": "Listing", "data": {"children": children}},  # comment listing
        ]

    def test_returns_empty_when_below_threshold(self) -> None:
        c = _collector()
        result = c._fetch_top_comments_sync("https://www.reddit.com/r/test/comments/abc/", num_comments=1)
        assert result == []

    def test_parses_comment_bodies_correctly(self) -> None:
        c = _collector()
        payload = self._make_reddit_comment_payload(["Anyone recommend a CRM?", "I'd pay for this."])

        with patch.object(c, "_request_json_with_retry", return_value=payload):
            result = c._fetch_top_comments_sync(
                "https://www.reddit.com/r/test/comments/abc/", num_comments=5
            )

        assert result == ["Anyone recommend a CRM?", "I'd pay for this."]

    def test_skips_deleted_comments(self) -> None:
        c = _collector()
        payload = self._make_reddit_comment_payload(["[deleted]", "Real comment here."])

        with patch.object(c, "_request_json_with_retry", return_value=payload):
            result = c._fetch_top_comments_sync(
                "https://www.reddit.com/r/test/comments/abc/", num_comments=5
            )

        assert "[deleted]" not in result
        assert "Real comment here." in result

    def test_skips_more_stubs(self) -> None:
        c = _collector()
        stub = {"kind": "more", "data": {"children": ["t1_xyz"]}}
        payload = [
            {"kind": "Listing", "data": {"children": []}},
            {"kind": "Listing", "data": {"children": [stub]}},
        ]

        with patch.object(c, "_request_json_with_retry", return_value=payload):
            result = c._fetch_top_comments_sync(
                "https://www.reddit.com/r/test/comments/abc/", num_comments=5
            )

        assert result == []

    def test_returns_empty_on_network_error(self) -> None:
        c = _collector()

        with patch.object(c, "_request_json_with_retry", side_effect=Exception("timeout")):
            result = c._fetch_top_comments_sync(
                "https://www.reddit.com/r/test/comments/abc/", num_comments=5
            )

        assert result == []

    def test_returns_empty_when_payload_is_none(self) -> None:
        c = _collector()

        with patch.object(c, "_request_json_with_retry", return_value=None):
            result = c._fetch_top_comments_sync(
                "https://www.reddit.com/r/test/comments/abc/", num_comments=5
            )

        assert result == []

    def test_truncates_long_comment_bodies(self) -> None:
        c = _collector()
        long_body = "x" * 1000
        payload = self._make_reddit_comment_payload([long_body])

        with patch.object(c, "_request_json_with_retry", return_value=payload):
            result = c._fetch_top_comments_sync(
                "https://www.reddit.com/r/test/comments/abc/", num_comments=5
            )

        assert len(result) == 1
        assert len(result[0]) <= 500  # _MAX_COMMENT_BODY_CHARS


# ---------------------------------------------------------------------------
# Async wrapper: _fetch_top_comments
# ---------------------------------------------------------------------------

class TestFetchTopCommentsAsync:
    def test_returns_empty_below_threshold(self) -> None:
        c = _collector()
        result = asyncio.run(
            c._fetch_top_comments("https://www.reddit.com/r/test/comments/abc/", num_comments=2)
        )
        assert result == []

    def test_delegates_to_sync_above_threshold(self) -> None:
        c = _collector()
        expected = ["Buyer comment here"]

        with patch.object(c, "_fetch_top_comments_sync", return_value=expected):
            result = asyncio.run(
                c._fetch_top_comments(
                    "https://www.reddit.com/r/test/comments/abc/", num_comments=5
                )
            )

        assert result == expected
