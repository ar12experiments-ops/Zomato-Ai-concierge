"""
Prompt engineering and context assembly module for LLM recommendation reasoning.
"""
from typing import List
import json
from src.engine.schemas import UserPreferenceRequest, RestaurantCandidate

SYSTEM_PROMPT = """You are an expert AI Food Critic and Dining Concierge inspired by Zomato.
Your task is to analyze a curated candidate list of restaurants and user dining preferences, then select, rank, and provide personalized recommendations.

RULES & CONSTRAINTS:
1. STRICT GROUNDING: Recommend ONLY restaurants that appear in the provided candidate list. Never invent or hallucinate restaurants.
2. RANKING: Select and rank the top 3 to 5 best matching restaurants.
3. PERSONALIZED JUSTIFICATIONS: Write a compelling, informative, 2-3 sentence explanation for each recommended restaurant. Explicitly explain WHY this spot matches the user's cuisine, budget, locality, and any subjective notes (e.g. ambiance, vibe, occasion).
4. HIGHLIGHT TAGS: Provide 2 to 4 concise tags per restaurant (e.g. 'Rooftop Ambiance', 'Must-Try Biryani', 'Budget Friendly').
5. EXECUTIVE SUMMARY: Write a warm, 1-2 sentence executive summary outlining the selections and trade-offs.
6. OUTPUT FORMAT: Output STRICT, VALID JSON adhering directly to the required schema. Do not include markdown code block backticks (```json) outside the JSON.
"""


def build_candidate_context_json(candidates: List[RestaurantCandidate]) -> str:
    """
    Serializes candidate restaurant list into structured JSON context for the LLM prompt.
    """
    candidate_dicts = [
        {
            "id": c.id,
            "name": c.name,
            "location": c.location,
            "cuisines": c.cuisines,
            "rating": c.rating,
            "votes": c.votes,
            "cost_for_two_inr": c.approx_cost_for_two,
            "budget_tier": c.budget_tier,
            "address": c.address,
        }
        for c in candidates
    ]
    return json.dumps(candidate_dicts, indent=2)


def build_recommendation_prompt(
    preferences: UserPreferenceRequest,
    candidates: List[RestaurantCandidate],
) -> str:
    """
    Assembles the complete user prompt combining preference payload and candidate context.
    Sandboxes free-text user notes in XML tags to defend against prompt injection.
    """
    candidate_context_str = build_candidate_context_json(candidates)
    
    # Sanitize user notes
    safe_user_notes = (preferences.additional_preferences or "None provided").strip()

    prompt = f"""### USER DINING PREFERENCES:
- Target Location: {preferences.location}
- Budget Tier: {preferences.budget}
- Preferred Cuisines: {', '.join(preferences.cuisines) if preferences.cuisines else 'Any / Flexible'}
- Minimum Rating Threshold: {preferences.min_rating}+
<user_notes>
{safe_user_notes}
</user_notes>

### CANDIDATE RESTAURANTS POOL:
{candidate_context_str}

### REQUIRED OUTPUT JSON SCHEMA:
{{
  "summary": "Executive summary string",
  "recommendations": [
    {{
      "rank": 1,
      "restaurant_name": "Exact Name from Candidates",
      "cuisine": ["Cuisine1", "Cuisine2"],
      "rating": 4.5,
      "estimated_cost_for_two": 800,
      "price_tier": "Medium",
      "location": "Locality Name",
      "explanation": "2-3 sentence tailored rationale connecting features with user preference.",
      "highlight_tags": ["Tag1", "Tag2"]
    }}
  ]
}}

Generate the JSON response now:"""
    return prompt
