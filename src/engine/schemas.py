"""
Pydantic data schemas and contracts for request and recommendation response validation.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class UserPreferenceRequest(BaseModel):
    """
    Structured payload capturing user preferences.
    """
    location: str = Field(default="Bangalore", description="Target city or neighborhood")
    budget: str = Field(default="Medium", description="Budget tier: Low, Medium, High, or Any")
    cuisines: List[str] = Field(default_factory=list, description="List of preferred cuisine types")
    min_rating: float = Field(default=3.5, ge=0.0, le=5.0, description="Minimum rating threshold")
    additional_preferences: Optional[str] = Field(
        default="", description="Free-text preferences, ambiance, dietary needs, or vibe"
    )


class RestaurantCandidate(BaseModel):
    """
    Structured restaurant candidate metadata passed to the LLM.
    """
    id: int = Field(description="Temporary candidate index")
    name: str = Field(description="Restaurant name")
    location: str = Field(description="Locality / Neighborhood")
    cuisines: List[str] = Field(description="Cuisine specialties")
    rating: float = Field(description="Aggregate rating out of 5")
    votes: int = Field(default=0, description="Total review votes")
    approx_cost_for_two: int = Field(description="Approximate cost in INR for two persons")
    budget_tier: str = Field(description="Budget tier category")
    address: Optional[str] = Field(default="", description="Full address")


class RestaurantRecommendation(BaseModel):
    """
    Single AI-generated restaurant recommendation card.
    """
    rank: int = Field(description="Ranking position (1 to N)")
    restaurant_name: str = Field(description="Exact restaurant name from candidate list")
    cuisine: List[str] = Field(description="Primary cuisine tags")
    rating: float = Field(description="Aggregate rating score")
    estimated_cost_for_two: int = Field(description="Estimated cost in INR for two")
    price_tier: str = Field(description="Budget tier (Low, Medium, High)")
    location: str = Field(description="Locality or address")
    explanation: str = Field(
        description="Personalized 2-3 sentence rationale detailing why this restaurant matches the user's specific preferences"
    )
    highlight_tags: List[str] = Field(
        default_factory=list, description="Key highlight tags, e.g. ['Romantic Vibe', 'Great Pasta']"
    )


class RecommendationResponse(BaseModel):
    """
    Complete recommendation response payload from the LLM engine.
    """
    summary: str = Field(
        description="Concise executive summary highlighting the choices and trade-offs"
    )
    recommendations: List[RestaurantRecommendation] = Field(
        description="Ranked list of top recommendations"
    )
    relaxed_filters_applied: bool = Field(
        default=False, description="True if constraint relaxation was needed"
    )
    relaxation_note: Optional[str] = Field(
        default=None, description="Explanation if filters were relaxed"
    )
