"""
Unit tests for deterministic filtering, ranking, and progressive relaxation in src.engine.filter.
"""
import pytest
import pandas as pd
from src.engine.schemas import UserPreferenceRequest
from src.engine.filter import apply_hard_filters, filter_candidates, compute_candidate_score


@pytest.fixture
def sample_df():
    return pd.DataFrame([
        {
            "name": "Toscano",
            "location": "UB City, Bangalore",
            "address": "Vittal Mallya Road",
            "cuisines": "Italian, European",
            "cuisines_list": ["Italian", "European"],
            "cuisines_str": "Italian, European",
            "approx_cost_for_two": 1500,
            "budget_tier": "High",
            "rating": 4.5,
            "votes": 2000,
        },
        {
            "name": "CTR",
            "location": "Malleshwaram, Bangalore",
            "address": "Margosa Road",
            "cuisines": "South Indian, Fast Food",
            "cuisines_list": ["South Indian", "Fast Food"],
            "cuisines_str": "South Indian, Fast Food",
            "approx_cost_for_two": 200,
            "budget_tier": "Low",
            "rating": 4.7,
            "votes": 9000,
        },
        {
            "name": "Empire Restaurant",
            "location": "Indiranagar, Bangalore",
            "address": "80ft Road",
            "cuisines": "North Indian, Biryani",
            "cuisines_list": ["North Indian", "Biryani"],
            "cuisines_str": "North Indian, Biryani",
            "approx_cost_for_two": 600,
            "budget_tier": "Medium",
            "rating": 4.2,
            "votes": 5000,
        },
        {
            "name": "Delhi Darbar",
            "location": "Connaught Place, Delhi",
            "address": "Connaught Place",
            "cuisines": "North Indian, Mughlai",
            "cuisines_list": ["North Indian", "Mughlai"],
            "cuisines_str": "North Indian, Mughlai",
            "approx_cost_for_two": 700,
            "budget_tier": "Medium",
            "rating": 4.3,
            "votes": 3000,
        },
    ])


class TestFilterEngine:
    def test_apply_hard_filters_location_and_budget(self, sample_df):
        res = apply_hard_filters(sample_df, location="Bangalore", cuisines=[], budget="High", min_rating=4.0)
        assert len(res) == 1
        assert res.iloc[0]["name"] == "Toscano"

    def test_apply_hard_filters_cuisine(self, sample_df):
        res = apply_hard_filters(sample_df, location="", cuisines=["South Indian"], budget="Low", min_rating=4.0)
        assert len(res) == 1
        assert res.iloc[0]["name"] == "CTR"

    def test_progressive_relaxation_on_zero_matches(self, sample_df):
        # Impossible criteria: Rating >= 4.9 in UB City
        req = UserPreferenceRequest(
            location="UB City",
            budget="Low",
            cuisines=["Italian"],
            min_rating=4.9,
        )
        candidates, relaxed, note = filter_candidates(sample_df, req)
        assert len(candidates) > 0
        assert relaxed is True
        assert note is not None

    def test_compute_candidate_score(self, sample_df):
        row = sample_df.iloc[0]
        score = compute_candidate_score(row, target_cuisines=["Italian"])
        assert score > 0
