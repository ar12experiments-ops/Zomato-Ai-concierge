"""
LLM inference client using Google Gemini API with structured JSON output and fallback recommender.
"""
from typing import List, Optional
import json
import logging
import re
import os

from src.config import GEMINI_API_KEY, GEMINI_MODEL, DEFAULT_TOP_RECOMMENDATIONS
from src.engine.schemas import (
    UserPreferenceRequest,
    RestaurantCandidate,
    RestaurantRecommendation,
    RecommendationResponse,
)
from src.engine.prompt import SYSTEM_PROMPT, build_recommendation_prompt

logger = logging.getLogger(__name__)


def generate_heuristic_recommendations(
    preferences: UserPreferenceRequest,
    candidates: List[RestaurantCandidate],
    relaxed: bool = False,
    relaxation_note: Optional[str] = None,
    limit: int = DEFAULT_TOP_RECOMMENDATIONS,
) -> RecommendationResponse:
    """
    Deterministic rule-based fallback recommender when LLM is unavailable or unconfigured.
    Generates intelligent structured explanations using metadata heuristics.
    """
    top_candidates = candidates[:limit]
    recommendations: List[RestaurantRecommendation] = []

    for idx, c in enumerate(top_candidates, start=1):
        # Generate dynamic template-based explanation
        cuisine_str = ", ".join(c.cuisines[:3])
        vibe_str = (
            f" aligning with your preference for '{preferences.additional_preferences}'"
            if preferences.additional_preferences
            else ""
        )
        explanation = (
            f"{c.name} is a premier dining destination in {c.location} specializing in {cuisine_str}. "
            f"With a stellar {c.rating}/5 rating backed by {c.votes:,} customer reviews, "
            f"it offers great value in the {c.budget_tier} budget tier at ~₹{c.approx_cost_for_two} for two{vibe_str}."
        )

        tags = [c.budget_tier + " Budget", f"⭐ {c.rating}"]
        if c.cuisines:
            tags.append(c.cuisines[0])
        if c.votes > 5000:
            tags.append("Crowd Favorite")

        recommendations.append(
            RestaurantRecommendation(
                rank=idx,
                restaurant_name=c.name,
                cuisine=c.cuisines,
                rating=c.rating,
                estimated_cost_for_two=c.approx_cost_for_two,
                price_tier=c.budget_tier,
                location=c.location,
                explanation=explanation,
                highlight_tags=tags,
            )
        )

    summary = (
        f"Selected top {len(recommendations)} restaurants in {preferences.location} based on "
        f"rating, popularity, and {preferences.budget} budget match."
    )

    return RecommendationResponse(
        summary=summary,
        recommendations=recommendations,
        relaxed_filters_applied=relaxed,
        relaxation_note=relaxation_note,
    )


def extract_and_parse_json(raw_text: str) -> dict:
    """
    Strips markdown formatting, extracts JSON object, and parses into Python dict.
    """
    cleaned = raw_text.strip()
    # Strip ```json ... ``` or ``` ... ```
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)
    cleaned = cleaned.strip()

    # Find first { and last }
    json_match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
    if json_match:
        cleaned = json_match.group(1)

    return json.loads(cleaned)


def get_ai_recommendations(
    preferences: UserPreferenceRequest,
    candidates: List[RestaurantCandidate],
    relaxed: bool = False,
    relaxation_note: Optional[str] = None,
) -> RecommendationResponse:
    """
    Calls the Gemini API to reason over candidates and generate recommendations.
    Falls back gracefully to heuristic recommendations on any API error or missing key.
    """
    if not candidates:
        return RecommendationResponse(
            summary="No candidate restaurants available for recommendation.",
            recommendations=[],
            relaxed_filters_applied=relaxed,
            relaxation_note=relaxation_note,
        )

    api_key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY).strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        logger.info("No Gemini API key provided. Using deterministic heuristic recommender.")
        return generate_heuristic_recommendations(
            preferences, candidates, relaxed, relaxation_note
        )

    prompt = build_recommendation_prompt(preferences, candidates)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.3,
            ),
        )

        raw_text = response.text
        parsed_dict = extract_and_parse_json(raw_text)

        # Validate with Pydantic
        recommendation_response = RecommendationResponse.model_validate(parsed_dict)
        recommendation_response.relaxed_filters_applied = relaxed
        recommendation_response.relaxation_note = relaxation_note

        # Candidate pool whitelist verification (anti-hallucination guard)
        candidate_names = {c.name.strip().lower() for c in candidates}
        for rec in recommendation_response.recommendations:
            # If name doesn't match, find closest candidate name
            if rec.restaurant_name.strip().lower() not in candidate_names:
                # Find best fuzzy match or fallback candidate
                for cand in candidates:
                    if cand.name.lower() in rec.restaurant_name.lower() or rec.restaurant_name.lower() in cand.name.lower():
                        rec.restaurant_name = cand.name
                        break

        return recommendation_response

    except Exception as e:
        logger.warning("Gemini API call failed (%s). Falling back to heuristic recommender.", e)
        return generate_heuristic_recommendations(
            preferences, candidates, relaxed, relaxation_note
        )
