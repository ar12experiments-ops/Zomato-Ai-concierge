"""
Unit tests for data cleaning and normalization functions in src.data.cleaner.
"""
import pytest
import pandas as pd
from src.data.cleaner import (
    parse_rating,
    parse_cost,
    categorize_budget_tier,
    parse_cuisines,
    clean_zomato_dataframe,
)


class TestDataCleaner:
    def test_parse_rating_valid(self):
        assert parse_rating("4.1/5") == 4.1
        assert parse_rating("3.9 / 5") == 3.9
        assert parse_rating("4.8") == 4.8
        assert parse_rating(4.5) == 4.5

    def test_parse_rating_edge_cases(self):
        assert parse_rating("NEW") == 0.0
        assert parse_rating("-") == 0.0
        assert parse_rating(None) == 0.0
        assert parse_rating(float("nan")) == 0.0
        assert parse_rating("") == 0.0

    def test_parse_cost_valid(self):
        assert parse_cost("800") == 800
        assert parse_cost("₹800 for two") == 800
        assert parse_cost("1,200") == 1200
        assert parse_cost("₹ 2,500 for two people") == 2500

    def test_parse_cost_edge_cases(self):
        assert parse_cost(None) == 0
        assert parse_cost("") == 0
        assert parse_cost("Free") == 0

    def test_categorize_budget_tier(self):
        assert categorize_budget_tier(300) == "Low"
        assert categorize_budget_tier(399) == "Low"
        assert categorize_budget_tier(400) == "Medium"
        assert categorize_budget_tier(800) == "Medium"
        assert categorize_budget_tier(1200) == "Medium"
        assert categorize_budget_tier(1500) == "High"
        assert categorize_budget_tier(0) == "Unknown"

    def test_parse_cuisines(self):
        result = parse_cuisines("North Indian, Chinese, Italian, North Indian")
        assert result == ["North Indian", "Chinese", "Italian"]
        assert parse_cuisines(None) == []
        assert parse_cuisines("") == []

    def test_clean_zomato_dataframe(self):
        raw_data = pd.DataFrame([
            {
                "name": "  Restaurant A  ",
                "location": "Indiranagar",
                "cuisines": "Italian, Pizza",
                "approx_cost(for_two_people)": "₹1,400",
                "rate": "4.5/5",
                "votes": "1200",
                "address": "100ft Road",
            },
            {
                "name": "Restaurant B",
                "location": "Indiranagar",
                "cuisines": "South Indian",
                "approx_cost(for_two_people)": "250",
                "rate": "NEW",
                "votes": "50",
                "address": "Margosa Rd",
            },
            # Duplicate entry to test deduplication
            {
                "name": "Restaurant A",
                "location": "Indiranagar",
                "cuisines": "Italian, Pizza",
                "approx_cost(for_two_people)": "1400",
                "rate": "4.5/5",
                "votes": "500",  # Lower votes
                "address": "100ft Road",
            },
        ])

        cleaned = clean_zomato_dataframe(raw_data)
        assert len(cleaned) == 2  # Deduplicated from 3
        assert cleaned.iloc[0]["name"] == "Restaurant A"
        assert cleaned.iloc[0]["rating"] == 4.5
        assert cleaned.iloc[0]["approx_cost_for_two"] == 1400
        assert cleaned.iloc[0]["budget_tier"] == "High"
        assert cleaned.iloc[0]["votes"] == 1200

        assert cleaned.iloc[1]["name"] == "Restaurant B"
        assert cleaned.iloc[1]["rating"] == 0.0
        assert cleaned.iloc[1]["approx_cost_for_two"] == 250
        assert cleaned.iloc[1]["budget_tier"] == "Low"
