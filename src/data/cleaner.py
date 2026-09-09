"""
Data cleaning, normalization, and transformation module for the Zomato restaurant dataset.
"""
from typing import Any, List, Optional
import re
import pandas as pd
import numpy as np


def parse_rating(val: Any) -> float:
    """
    Parses rating string (e.g., '4.1/5', '3.9 /5', 'NEW', '-') into a float.
    Returns 0.0 for unrated or corrupted records.
    """
    if pd.isna(val) or val is None:
        return 0.0
    val_str = str(val).strip()
    if val_str in ("NEW", "-", "", "nan", "None", "Opening Soon"):
        return 0.0
    # Match pattern like '4.1/5' or '4.1'
    match = re.match(r"^([0-9]+(?:\.[0-9]+)?)(?:\s*/\s*5)?", val_str)
    if match:
        try:
            return round(float(match.group(1)), 2)
        except ValueError:
            return 0.0
    return 0.0


def parse_cost(val: Any) -> int:
    """
    Extracts numeric cost for two from strings like '₹800 for two', '800', '1,200'.
    Returns 0 if cost cannot be extracted.
    """
    if pd.isna(val) or val is None:
        return 0
    val_str = str(val).strip()
    # Remove currency symbols and extract digits
    digits_only = re.sub(r"[^\d]", "", val_str)
    if digits_only:
        try:
            return int(digits_only)
        except ValueError:
            return 0
    return 0


def categorize_budget_tier(cost: int) -> str:
    """
    Categorizes numeric cost for two into Low, Medium, or High budget tier.
    """
    if cost <= 0:
        return "Unknown"
    elif cost < 400:
        return "Low"
    elif cost <= 1200:
        return "Medium"
    else:
        return "High"


def parse_cuisines(val: Any) -> List[str]:
    """
    Parses comma-separated cuisines into a standardized list of title-cased strings.
    """
    if pd.isna(val) or val is None:
        return []
    val_str = str(val).strip()
    if not val_str:
        return []
    items = [c.strip().title() for c in val_str.split(",") if c.strip()]
    return list(dict.fromkeys(items))  # Preserve order, eliminate duplicates


def clean_zomato_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans, deduplicates, and structures the raw Zomato DataFrame.
    """
    cleaned_df = df.copy()

    # Standardize column names to lowercase and strip whitespace
    cleaned_df.columns = [str(c).strip().lower().replace(" ", "_") for c in cleaned_df.columns]

    # Map possible column name variations
    column_mapping = {
        "approx_cost(for_two_people)": "approx_cost_for_two",
        "approx_cost_for_two_people": "approx_cost_for_two",
        "rate": "rating",
        "listed_in(city)": "listed_in_city",
        "listed_in(type)": "listed_in_type",
    }
    cleaned_df.rename(columns=column_mapping, inplace=True)

    # Ensure required columns exist
    for col in ["name", "location", "cuisines"]:
        if col not in cleaned_df.columns:
            cleaned_df[col] = ""

    if "rating" not in cleaned_df.columns and "rate" in cleaned_df.columns:
        cleaned_df["rating"] = cleaned_df["rate"]
    elif "rating" not in cleaned_df.columns:
        cleaned_df["rating"] = 0.0

    if "approx_cost_for_two" not in cleaned_df.columns:
        cleaned_df["approx_cost_for_two"] = 0

    if "votes" not in cleaned_df.columns:
        cleaned_df["votes"] = 0

    # 1. Clean and normalize string fields
    cleaned_df["name"] = cleaned_df["name"].fillna("Unknown Restaurant").astype(str).str.strip()
    cleaned_df["location"] = cleaned_df["location"].fillna("Bangalore").astype(str).str.strip()
    cleaned_df["address"] = cleaned_df.get("address", pd.Series(dtype=str)).fillna("").astype(str).str.strip()

    # 2. Parse ratings to float
    cleaned_df["rating"] = cleaned_df["rating"].apply(parse_rating)

    # 3. Parse approx cost for two to int
    cleaned_df["approx_cost_for_two"] = cleaned_df["approx_cost_for_two"].apply(parse_cost)

    # 4. Impute missing/zero cost with median cost of the locality if available, else 600
    median_cost_overall = int(cleaned_df[cleaned_df["approx_cost_for_two"] > 0]["approx_cost_for_two"].median()) if len(cleaned_df[cleaned_df["approx_cost_for_two"] > 0]) > 0 else 600
    cleaned_df.loc[cleaned_df["approx_cost_for_two"] == 0, "approx_cost_for_two"] = median_cost_overall

    # 5. Add budget tier
    cleaned_df["budget_tier"] = cleaned_df["approx_cost_for_two"].apply(categorize_budget_tier)

    # 6. Parse and standardize cuisines list & cuisine string
    cleaned_df["cuisines_list"] = cleaned_df["cuisines"].apply(parse_cuisines)
    cleaned_df["cuisines_str"] = cleaned_df["cuisines_list"].apply(lambda lst: ", ".join(lst))

    # 7. Clean votes to integer
    def parse_votes(v: Any) -> int:
        if pd.isna(v):
            return 0
        try:
            return int(re.sub(r"[^\d]", "", str(v)))
        except ValueError:
            return 0

    cleaned_df["votes"] = cleaned_df["votes"].apply(parse_votes)

    # 8. Deduplicate records keeping the highest voted one
    cleaned_df.sort_values(by="votes", ascending=False, inplace=True)
    cleaned_df.drop_duplicates(subset=["name", "location"], keep="first", inplace=True)
    cleaned_df.reset_index(drop=True, inplace=True)

    return cleaned_df
