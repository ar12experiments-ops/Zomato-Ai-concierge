"""
Deterministic filtering engine and candidate pruner with progressive relaxation.
"""
from typing import List, Tuple, Optional
import math
import logging
import pandas as pd
import numpy as np

from src.engine.schemas import UserPreferenceRequest, RestaurantCandidate
from src.config import MAX_CANDIDATES_FOR_LLM, BUDGET_TIERS

logger = logging.getLogger(__name__)


def compute_candidate_score(row: pd.Series, target_cuisines: List[str]) -> float:
    """
    Computes a composite heuristic ranking score for pruning candidate pools:
    Score = (Rating * log10(Votes + 10)) + (Cuisine Match Overlap * 0.5)
    """
    rating = float(row.get("rating", 0.0))
    votes = int(row.get("votes", 0))
    cuisines_val = row.get("cuisines_list", [])

    # Log-scaled vote multiplier
    vote_factor = math.log10(max(votes, 1) + 10)
    base_score = rating * vote_factor

    # Cuisine overlap bonus
    if target_cuisines:
        target_lower = {c.strip().lower() for c in target_cuisines if c.strip()}
        if isinstance(cuisines_val, (list, np.ndarray, tuple)):
            row_cuisines_lower = {str(c).strip().lower() for c in cuisines_val}
        else:
            row_cuisines_lower = {c.strip().lower() for c in str(cuisines_val).split(",") if c.strip()}
        overlap = len(target_lower.intersection(row_cuisines_lower))
        base_score += overlap * 0.5

    return round(base_score, 3)


def apply_hard_filters(
    df: pd.DataFrame,
    location: str,
    cuisines: List[str],
    budget: str,
    min_rating: float,
) -> pd.DataFrame:
    """
    Applies exact deterministic filters on location, cuisines, budget, and rating.
    """
    filtered = df.copy()

    # 1. Location Filter (Case-insensitive substring match)
    if location and location.strip() and location.strip().lower() != "all":
        loc_clean = location.strip().lower()
        mask = (
            filtered["location"].str.lower().str.contains(loc_clean, na=False)
            | filtered["address"].str.lower().str.contains(loc_clean, na=False)
        )
        filtered = filtered[mask]

    # 2. Rating Filter
    if min_rating > 0.0:
        filtered = filtered[filtered["rating"] >= min_rating]

    # 3. Budget Filter
    if budget and budget.capitalize() in BUDGET_TIERS:
        tier = budget.capitalize()
        tier_bounds = BUDGET_TIERS[tier]
        cost_mask = (filtered["approx_cost_for_two"] >= tier_bounds["min"]) & (
            filtered["approx_cost_for_two"] <= tier_bounds["max"]
        )
        filtered = filtered[cost_mask]

    # 4. Cuisine Filter (Any matching cuisine)
    if cuisines:
        target_cuisines_clean = [c.strip().lower() for c in cuisines if c.strip()]
        if target_cuisines_clean:
            def matches_cuisine(row_cuisines) -> bool:
                if isinstance(row_cuisines, (list, np.ndarray, tuple)):
                    row_lower = [str(c).strip().lower() for c in row_cuisines]
                    return any(tc in item for tc in target_cuisines_clean for item in row_lower)
                else:
                    row_str = str(row_cuisines).lower()
                    return any(tc in row_str for tc in target_cuisines_clean)

            filtered = filtered[filtered["cuisines_list"].apply(matches_cuisine)]

    return filtered


def filter_candidates(
    df: pd.DataFrame,
    preferences: UserPreferenceRequest,
    top_k: int = MAX_CANDIDATES_FOR_LLM,
) -> Tuple[List[RestaurantCandidate], bool, Optional[str]]:
    """
    Filters restaurant dataframe based on user preferences.
    If 0 matches are found, executes progressive relaxation hierarchy.
    Returns: (list_of_candidates, relaxed_flag, relaxation_note)
    """
    target_cuisines = preferences.cuisines
    location = preferences.location
    budget = preferences.budget
    min_rating = preferences.min_rating

    # Attempt 1: Exact hard filters
    filtered_df = apply_hard_filters(df, location, target_cuisines, budget, min_rating)
    relaxed = False
    relaxation_note = None

    # Progressive Relaxation Hierarchy
    if len(filtered_df) == 0:
        logger.info("Zero exact matches. Initiating relaxation Step 1 (Relax Rating)...")
        relaxed = True
        relaxed_rating = max(0.0, min_rating - 0.5)
        filtered_df = apply_hard_filters(df, location, target_cuisines, budget, relaxed_rating)
        relaxation_note = f"Relaxed minimum rating threshold from {min_rating} to {relaxed_rating}+"

    if len(filtered_df) == 0:
        logger.info("Zero matches in Step 1. Initiating relaxation Step 2 (Relax Budget)...")
        filtered_df = apply_hard_filters(df, location, target_cuisines, "Any", max(0.0, min_rating - 0.5))
        relaxation_note = f"Expanded budget criteria across all tiers in {location}."

    if len(filtered_df) == 0:
        logger.info("Zero matches in Step 2. Initiating relaxation Step 3 (Relax Location & Cuisines)...")
        filtered_df = apply_hard_filters(df, "", target_cuisines, "Any", 0.0)
        if len(filtered_df) == 0:
            # Absolute fallback: Top rated overall
            filtered_df = df.sort_values(by=["rating", "votes"], ascending=False).head(top_k)
            relaxation_note = "Showing top-rated dining spots across the region matching general popularity."
        else:
            relaxation_note = f"Showing top-rated {', '.join(target_cuisines)} restaurants in neighboring areas."

    # Compute composite heuristic score and rank
    filtered_df = filtered_df.copy()
    filtered_df["composite_score"] = filtered_df.apply(
        lambda r: compute_candidate_score(r, target_cuisines), axis=1
    )
    ranked_df = filtered_df.sort_values(by="composite_score", ascending=False).head(top_k)

    # Convert to Pydantic RestaurantCandidate objects
    candidates: List[RestaurantCandidate] = []
    for idx, (_, row) in enumerate(ranked_df.iterrows(), start=1):
        candidates.append(
            RestaurantCandidate(
                id=idx,
                name=str(row["name"]),
                location=str(row["location"]),
                cuisines=row["cuisines_list"] if isinstance(row["cuisines_list"], list) else [str(row["cuisines_str"])],
                rating=float(row["rating"]),
                votes=int(row["votes"]),
                approx_cost_for_two=int(row["approx_cost_for_two"]),
                budget_tier=str(row["budget_tier"]),
                address=str(row.get("address", "")),
            )
        )

    return candidates, relaxed, relaxation_note
