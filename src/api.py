"""
FastAPI application backend for the AI-Powered Restaurant Recommendation System.
Ready for local execution and deployment on Render.com.
"""
from pathlib import Path
import logging
from typing import Dict, Any, List
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.config import DATA_SOURCE, SUPABASE_URL
from src.data.loader import get_restaurant_data
from src.data.supabase_client import test_supabase_connection
from src.engine.schemas import (
    UserPreferenceRequest,
    RestaurantRecommendation,
    RecommendationResponse,
)
from src.engine.filter import filter_candidates
from src.engine.llm_client import get_ai_recommendations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Zomato | AI Dining Concierge",
    description="Ultrahuman-inspired Glassmorphic AI Restaurant Recommendation API",
    version="2.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global dataset cache
_df: pd.DataFrame = None


def get_dataframe() -> pd.DataFrame:
    global _df
    if _df is None:
        logger.info("Initializing restaurant dataset cache...")
        _df = get_restaurant_data()
    return _df


@app.on_event("startup")
async def startup_event():
    """Preloads dataset on startup to ensure instant responses."""
    get_dataframe()


@app.get("/health")
async def health_check():
    """Health check endpoint with data source diagnostics."""
    return {
        "status": "healthy",
        "service": "zomato-ai-concierge",
        "version": "2.0.0",
        "data_source": DATA_SOURCE,
        "supabase_url": SUPABASE_URL,
    }


@app.get("/api/supabase/status")
async def get_supabase_status():
    """Returns real-time Supabase connection diagnostics."""
    return test_supabase_connection()


@app.post("/api/sync-data")
async def trigger_sync():
    """Forces reload of restaurant data from primary source."""
    global _df
    _df = get_restaurant_data(force_reload=True)
    return {
        "status": "success",
        "total_records": len(_df),
        "data_source": DATA_SOURCE,
    }


@app.get("/api/metadata")
async def get_metadata():
    """Returns dataset metadata, unique locations, top cuisines, and statistics."""
    df = get_dataframe()
    unique_locations = sorted(df["location"].dropna().unique().tolist())
    all_cuisines = [c for sublist in df["cuisines_list"].dropna() for c in sublist]
    top_cuisines = pd.Series(all_cuisines).value_counts().head(40).index.tolist()
    top_cuisines = sorted(top_cuisines)

    return {
        "total_restaurants": len(df),
        "total_locations": len(unique_locations),
        "total_cuisines": len(set(all_cuisines)),
        "locations": unique_locations,
        "cuisines": top_cuisines,
        "data_source": DATA_SOURCE,
        "supabase_connected": test_supabase_connection().get("table_exists", False),
    }



@app.get("/api/benchmark")
async def get_benchmark_restaurants(limit: int = 6):
    """Returns top-rated featured restaurants for initial showcase."""
    df = get_dataframe()
    sample_df = df.sort_values(by=["rating", "votes"], ascending=False).head(limit)
    benchmarks = []
    for idx, (_, row) in enumerate(sample_df.iterrows(), start=1):
        raw_cuisines = row.get("cuisines_list", [])
        if isinstance(raw_cuisines, (list, tuple)):
            cuisines_lst = [str(c) for c in raw_cuisines]
        elif hasattr(raw_cuisines, "__iter__") and not isinstance(raw_cuisines, str):
            cuisines_lst = [str(c) for c in raw_cuisines]
        else:
            cuisines_lst = [c.strip() for c in str(row.get("cuisines_str", "")).split(",") if c.strip()]

        votes_count = int(row.get("votes", 0))
        benchmarks.append({
            "rank": idx,
            "restaurant_name": str(row["name"]),
            "cuisine": cuisines_lst[:4],
            "rating": float(row["rating"]),
            "estimated_cost_for_two": int(row["approx_cost_for_two"]),
            "price_tier": str(row["budget_tier"]),
            "location": str(row["location"]),
            "explanation": f"A culinary icon in {row['location']} celebrated for its authentic {', '.join(cuisines_lst[:3])} flavors and exceptional dining experience with {votes_count:,} reviews.",
            "highlight_tags": ["Top Rated", f"⭐ {row['rating']}", f"{row['budget_tier']} Budget"],
        })
    return {"benchmarks": benchmarks}


@app.post("/api/recommend", response_model=RecommendationResponse)
async def recommend_restaurants(preferences: UserPreferenceRequest):
    """Generates filtered candidates and calls LLM qualitative reasoning."""
    df = get_dataframe()
    candidates, relaxed, relaxation_note = filter_candidates(df, preferences)
    if not candidates:
        raise HTTPException(
            status_code=404,
            detail="No matching restaurants found even after automated constraint relaxation.",
        )
    response = get_ai_recommendations(preferences, candidates, relaxed, relaxation_note)
    return response


# Mount static frontend files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def serve_index():
    """Serves the main frontend application."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse({"message": "Zomato AI Concierge API active. Static frontend not found."})

