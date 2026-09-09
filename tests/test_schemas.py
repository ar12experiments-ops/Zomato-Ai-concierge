"""
Unit tests for Pydantic schemas, validation, and JSON parsing in src.engine.schemas.
"""
import pytest
from src.engine.schemas import (
    UserPreferenceRequest,
    RestaurantCandidate,
    RestaurantRecommendation,
    RecommendationResponse,
)
from src.engine.llm_client import extract_and_parse_json, generate_heuristic_recommendations


class TestSchemas:
    def test_user_preference_request_defaults(self):
        req = UserPreferenceRequest()
        assert req.location == "Bangalore"
        assert req.budget == "Medium"
        assert req.min_rating == 3.5

    def test_restaurant_recommendation_validation(self):
        rec = RestaurantRecommendation(
            rank=1,
            restaurant_name="Toscano",
            cuisine=["Italian"],
            rating=4.5,
            estimated_cost_for_two=1500,
            price_tier="High",
            location="UB City",
            explanation="Great Italian food with romantic ambiance.",
            highlight_tags=["Romantic Vibe"],
        )
        assert rec.rank == 1
        assert rec.restaurant_name == "Toscano"
        assert rec.rating == 4.5

    def test_extract_and_parse_json(self):
        raw_markdown = """
        ```json
        {
            "summary": "Found great places",
            "recommendations": [
                {
                    "rank": 1,
                    "restaurant_name": "CTR",
                    "cuisine": ["South Indian"],
                    "rating": 4.7,
                    "estimated_cost_for_two": 200,
                    "price_tier": "Low",
                    "location": "Malleshwaram",
                    "explanation": "Famous for crispy benne masala dosa.",
                    "highlight_tags": ["Crispy Dosa"]
                }
            ]
        }
        ```
        """
        parsed = extract_and_parse_json(raw_markdown)
        response = RecommendationResponse.model_validate(parsed)
        assert response.summary == "Found great places"
        assert len(response.recommendations) == 1
        assert response.recommendations[0].restaurant_name == "CTR"

    def test_heuristic_recommender(self):
        req = UserPreferenceRequest(location="Bangalore", budget="Medium")
        candidates = [
            RestaurantCandidate(
                id=1,
                name="CTR",
                location="Malleshwaram",
                cuisines=["South Indian"],
                rating=4.7,
                votes=9000,
                approx_cost_for_two=200,
                budget_tier="Low",
                address="Malleshwaram 7th Cross",
            )
        ]
        res = generate_heuristic_recommendations(req, candidates)
        assert len(res.recommendations) == 1
        assert res.recommendations[0].restaurant_name == "CTR"
        assert "CTR is a premier dining destination" in res.recommendations[0].explanation
