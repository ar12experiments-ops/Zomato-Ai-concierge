"""
Unit tests for Supabase client, schema mapping, and fallback resilience.
"""
import pytest
import pandas as pd
from src.config import SUPABASE_URL, SUPABASE_KEY
from src.data.supabase_client import get_supabase_client, test_supabase_connection
from scripts.replicate_to_supabase import prepare_records_for_supabase


def test_supabase_client_initialization():
    client = get_supabase_client()
    assert client is not None


def test_supabase_connection_diagnostics():
    status = test_supabase_connection()
    assert isinstance(status, dict)
    assert "connected" in status
    assert "table_exists" in status


def test_prepare_records_for_supabase():
    sample_data = {
        "name": ["Toit Brewpub", "Empire Restaurant"],
        "location": ["Indiranagar", "Indiranagar"],
        "cuisines_list": [["Brewery", "Pizza"], ["North Indian", "Biryani"]],
        "rating": [4.8, 4.2],
        "votes": [16400, 5800],
        "approx_cost_for_two": [1800, 600],
        "budget_tier": ["High", "Medium"],
        "url": ["http://zomato.com/toit", ""],
        "address": ["100ft Road", "80ft Road"],
    }
    df = pd.DataFrame(sample_data)
    records = prepare_records_for_supabase(df)

    assert len(records) == 2
    assert records[0]["name"] == "Toit Brewpub"
    assert records[0]["location"] == "Indiranagar"
    assert records[0]["rating"] == 4.8
    assert records[0]["approx_cost_for_two"] == 1800
    assert records[0]["cuisines_list"] == ["Brewery", "Pizza"]
