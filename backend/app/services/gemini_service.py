import json
import re
from datetime import datetime, timezone
from typing import Any

from app.models.schemas import CandidatePost, LeadInsight, LeadScanRequest

try:
    from google import genai
except Exception:
    genai = None


class GeminiLeadScorer:
    def __init__(self, api_key: str | None, model_lite: str, model_main: str) -> None:
        self.api_key = api_key
        self.model_lite = model_lite
        self.model_main = model_main

    async def score_posts(self, request: LeadScanRequest, posts: list[CandidatePost]) -> list[LeadInsight]:
        if not posts:
            return []

        heuristic = self._heuristic_rank(request, posts)

        if not self.api_key or genai is None:
            return heuristic[: request.limit]

        refined = self._score_with_gemini(request, posts, heuristic)
        return (refined or heuristic)[: request.limit]

    def _score_with_gemini(
        self,
        request: LeadScanRequest,
        posts: list[CandidatePost],
        heuristic: list[LeadInsight]
    ) -> list[LeadInsight]:
        post_lookup = {post.id: post for post in posts}
        heuristic_lookup = {item.post.id: item for item in heuristic}

        lite_candidates = [
            {
                "post_id": post.id,
                "title": post.title,
                "body": post.body[:400],
                "subreddit": post.subreddit,
                "score": post.score,
                "num_comments": post.num_comments
            }
            for post in posts
        ]

        lite_prompt = (
            "You are selecting high-intent leads from Reddit posts. "
            "Return only a JSON array with objects: {post_id, why}. "
            "Select posts likely showing pain, intent, or tool buying behavior.\n\n"
            f"Business:\n{request.business_description}\n\n"
            f"Keywords: {', '.join(request.keywords)}\n\n"
            f"Posts:\n{json.dumps(lite_candidates, ensure_ascii=False)}"
        )

        lite_response = self._generate_json(self.model_lite, lite_prompt)
        selected_ids = []

        if isinstance(lite_response, list):
            for item in lite_response:
                if isinstance(item, dict) and str(item.get("post_id", "")).strip():
                    selected_ids.append(str(item["post_id"]))

        if not selected_ids:
            selected_ids = [item.post.id for item in heuristic[: min(15, len(heuristic))]]

        selected_posts = [post_lookup[post_id] for post_id in selected_ids if post_id in post_lookup]
        if not selected_posts:
            return heuristic

        flash_payload = [
            {
                "post_id": post.id,
                "title": post.title,
                "body": post.body[:700],
                "subreddit": post.subreddit,
                "score": post.score,
                "num_comments": post.num_comments,
                "baseline_score": heuristic_lookup[post.id].lead_score if post.id in heuristic_lookup else 50
            }
            for post in selected_posts
        ]

        flash_prompt = (
            "You score lead quality for outreach. "
            "Return only a JSON array. "
            "Each object must have: post_id, lead_score (0-100), qualification_reason, suggested_outreach.\n\n"
            f"Business:\n{request.business_description}\n\n"
            f"Posts:\n{json.dumps(flash_payload, ensure_ascii=False)}"
        )

        flash_response = self._generate_json(self.model_main, flash_prompt)
        if not isinstance(flash_response, list):
            return heuristic

        insights: list[LeadInsight] = []

        for row in flash_response:
            if not isinstance(row, dict):
                continue

            post_id = str(row.get("post_id", "")).strip()
            if not post_id or post_id not in post_lookup:
                continue

            try:
                lead_score = max(0.0, min(float(row.get("lead_score", 50)), 100.0))
            except Exception:
                lead_score = heuristic_lookup.get(post_id, heuristic[0]).lead_score

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

        if not insights:
            return heuristic

        insights.sort(key=lambda item: item.lead_score, reverse=True)
        return insights

    def _generate_json(self, model_name: str, prompt: str) -> Any:
        if not self.api_key or genai is None:
            return None

        try:
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(model=model_name, contents=prompt)
            text = getattr(response, "text", None)
            if not text:
                text = str(response)
            return self._extract_json(text)
        except Exception:
            return None

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
