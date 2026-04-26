import asyncio
import json
import re
from datetime import datetime, timezone
from typing import Any

from app.core.constants import (
    AI_SCORE_WEIGHT,
    HEURISTIC_SCORE_WEIGHT,
    LEAD_SCAN_AI_CANDIDATE_MULTIPLIER,
    LEAD_SCAN_MAX_AI_CANDIDATES,
    LEAD_SCAN_MIN_AI_CANDIDATES,
    NON_REFINED_MAX_SCORE,
    PROMPT_MAX_BUSINESS_CHARS,
    PROMPT_MAX_COMMENT_CHARS,
    PROMPT_MAX_KEYWORD_CHARS,
    PROMPT_MAX_KEYWORDS,
    PROMPT_MAX_SNIPPET_CHARS,
    PROMPT_MAX_TITLE_CHARS,
)
from app.models.schemas import CandidatePost, LeadInsight, LeadScanRequest

try:
    from google import genai
except Exception:
    genai = None


class GeminiLeadScorer:
    def __init__(self, api_key: str | None, model_lite: str) -> None:
        self.api_key = api_key
        self.model_lite = model_lite
        self.client = None
        if self.api_key and genai is not None:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None

    async def score_posts(self, request: LeadScanRequest, posts: list[CandidatePost]) -> list[LeadInsight]:
        if not posts:
            return []

        heuristic = self._heuristic_rank(request, posts)

        if self.client is None:
            return heuristic[: request.limit]

        refined = await self._score_with_flash_lite(request, heuristic)
        ranked = self._merge_rankings(heuristic, refined)
        return ranked[: request.limit]

    async def _score_with_flash_lite(
        self,
        request: LeadScanRequest,
        heuristic: list[LeadInsight]
    ) -> list[LeadInsight]:
        candidate_count = min(
            max(request.limit * LEAD_SCAN_AI_CANDIDATE_MULTIPLIER, LEAD_SCAN_MIN_AI_CANDIDATES),
            len(heuristic),
            LEAD_SCAN_MAX_AI_CANDIDATES,
        )
        candidates = heuristic[:candidate_count]

        post_lookup = {item.post.id: item.post for item in candidates}
        baseline_lookup = {item.post.id: item.lead_score for item in candidates}
        refined_ids: set[str] = set()

        payload = [
            {
                "post_id": item.post.id,
                "title": self._compact(item.post.title, PROMPT_MAX_TITLE_CHARS),
                "snippet": self._compact(item.post.body, PROMPT_MAX_SNIPPET_CHARS),
                "subreddit": item.post.subreddit,
                "upvotes": item.post.score,
                "comments": item.post.num_comments,
                "baseline_score": round(item.lead_score, 2),
                # Include truncated comment snippets so the model can detect
                # buyer-intent signals that only surface in comment threads.
                "top_comment_snippets": [
                    self._compact(c, PROMPT_MAX_COMMENT_CHARS)
                    for c in item.post.top_comments[:3]
                ],
            }
            for item in candidates
        ]

        keywords = [
            self._compact(keyword, PROMPT_MAX_KEYWORD_CHARS)
            for keyword in request.keywords
            if keyword.strip()
        ][:PROMPT_MAX_KEYWORDS]
        compact_business = self._compact(request.business_description, PROMPT_MAX_BUSINESS_CHARS)

        prompt = (
            "You are an expert lead qualifier for startup outreach across B2B and B2C products. "
            "Score each Reddit post for fit with the business below.\n"
            "Return ONLY a JSON array sorted by lead_score descending. No markdown, no explanation text.\n"
            "Each row schema: {post_id, lead_score, qualification_reason, suggested_outreach}.\n"
            "Scoring rubric: ICP fit 40, explicit pain/intent 30, urgency 15, engagement signal 15.\n"
            "Critical rule: prioritize posts where the author is seeking help, recommendations, hiring support, or a solution.\n"
            "Critical rule: heavily down-score (0-20) posts where the author is advertising their own services, availability, or portfolio.\n"
            "qualification_reason: <= 160 chars and specific.\n"
            "suggested_outreach: <= 220 chars, actionable, personalized, no hype.\n"
            f"Business: {compact_business}\n"
            f"Keywords: {', '.join(keywords) if keywords else 'n/a'}\n"
            f"Posts: {json.dumps(payload, ensure_ascii=False, separators=(',', ':'))}"
        )

        response = await self._generate_json(self.model_lite, prompt)
        if not isinstance(response, list):
            return []

        insights: list[LeadInsight] = []

        for row in response:
            if not isinstance(row, dict):
                continue

            post_id = str(row.get("post_id", "")).strip()
            if not post_id or post_id not in post_lookup:
                continue

            try:
                lead_score = max(0.0, min(float(row.get("lead_score", 50)), 100.0))
            except Exception:
                lead_score = baseline_lookup.get(post_id, 50.0)

            reason = str(row.get("qualification_reason", "Likely buyer intent based on discussion context.")).strip()
            outreach = str(
                row.get(
                    "suggested_outreach",
                    "Share a concise solution and ask one clarifying question to qualify urgency."
                )
            ).strip()

            insights.append(
                LeadInsight(
                    post=post_lookup[post_id],
                    lead_score=round(lead_score, 2),
                    qualification_reason=reason,
                    suggested_outreach=outreach
                )
            )
            refined_ids.add(post_id)

        # Blend AI and heuristic to keep scoring stable while preferring model-refined rows.
        for item in insights:
            baseline = baseline_lookup.get(item.post.id, item.lead_score)
            blended = (item.lead_score * AI_SCORE_WEIGHT) + (baseline * HEURISTIC_SCORE_WEIGHT)
            item.lead_score = round(max(0.0, min(blended, 100.0)), 2)

        insights.sort(
            key=lambda item: (item.post.id in refined_ids, item.lead_score, item.post.num_comments),
            reverse=True,
        )
        return insights

    def _merge_rankings(
        self,
        heuristic: list[LeadInsight],
        ai_ranked: list[LeadInsight],
    ) -> list[LeadInsight]:
        if not ai_ranked:
            return heuristic

        ai_ids = {item.post.id for item in ai_ranked}
        merged: dict[str, LeadInsight] = {}
        for item in heuristic:
            if item.post.id in ai_ids:
                continue
            # Keep non-refined fallback rows below refined AI rows.
            item.lead_score = round(min(item.lead_score, NON_REFINED_MAX_SCORE), 2)
            merged[item.post.id] = item

        for item in ai_ranked:
            merged[item.post.id] = item

        ranked = list(merged.values())
        ranked.sort(key=lambda item: item.lead_score, reverse=True)
        return ranked

    async def _generate_json(self, model_name: str, prompt: str) -> Any:
        if self.client is None:
            return None

        return await asyncio.to_thread(self._generate_json_sync, model_name, prompt)

    def _generate_json_sync(self, model_name: str, prompt: str) -> Any:
        if self.client is None:
            return None

        try:
            response = self.client.models.generate_content(model=model_name, contents=prompt)
            text = getattr(response, "text", None)
            if not text:
                text = str(response)
            return self._extract_json(text)
        except Exception:
            return None

    def _compact(self, text: str, max_chars: int) -> str:
        compact = re.sub(r"\s+", " ", text).strip()
        if len(compact) <= max_chars:
            return compact
        if max_chars <= 3:
            return compact[:max_chars]
        return f"{compact[: max_chars - 3]}..."

    def _extract_json(self, text: str) -> Any:
        candidates = []

        array_start = text.find("[")
        array_end = text.rfind("]")
        if array_start != -1 and array_end != -1 and array_end > array_start:
            candidates.append(text[array_start : array_end + 1])

        object_start = text.find("{")
        object_end = text.rfind("}")
        if object_start != -1 and object_end != -1 and object_end > object_start:
            candidates.append(text[object_start : object_end + 1])

        for candidate in candidates:
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict) and "items" in parsed and isinstance(parsed["items"], list):
                    return parsed["items"]
                return parsed
            except Exception:
                continue

        return None

    def _heuristic_rank(self, request: LeadScanRequest, posts: list[CandidatePost]) -> list[LeadInsight]:
        terms = set(self._tokenize(request.business_description))
        terms.update(self._tokenize(" ".join(request.keywords)))

        ranked: list[LeadInsight] = []
        for post in posts:
            text = f"{post.title} {post.body}".lower()
            hit_count = sum(1 for term in terms if term and term in text)

            engagement_score = min(post.num_comments, 80) * 0.35
            vote_score = min(max(post.score, 0), 300) * 0.08
            urgency_bonus = 8 if re.search(r"need|help|looking|recommend|struggling", text) else 0
            age_bonus = self._age_score(post.created_utc)

            score = 25 + (hit_count * 8) + engagement_score + vote_score + urgency_bonus + age_bonus
            normalized = max(0.0, min(score, 100.0))

            reason = (
                f"Matched {hit_count} business/keyword terms with {post.num_comments} comments and "
                f"{post.score} upvotes."
            )
            outreach = (
                "Start by acknowledging their exact problem, then offer one practical fix and "
                "invite a short DM conversation."
            )

            ranked.append(
                LeadInsight(
                    post=post,
                    lead_score=round(normalized, 2),
                    qualification_reason=reason,
                    suggested_outreach=outreach
                )
            )

        ranked.sort(key=lambda item: item.lead_score, reverse=True)
        return ranked

    def _tokenize(self, text: str) -> list[str]:
        return [word for word in re.findall(r"[a-zA-Z0-9]+", text.lower()) if len(word) > 2]

    def _age_score(self, created_at: datetime) -> float:
        now = datetime.now(tz=timezone.utc)
        age_hours = max((now - created_at).total_seconds() / 3600, 0)
        if age_hours <= 6:
            return 10
        if age_hours <= 24:
            return 6
        if age_hours <= 72:
            return 3
        return 0
