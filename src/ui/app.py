"""
Streamlit main application entry point for the AI-Powered Restaurant Recommendation System.
Designed with Ultrahuman Performance Lab aesthetic: deep obsidian dark theme, neon telemetry, and precision AI reasoning.
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
from typing import List

from src.data.loader import get_restaurant_data
from src.engine.schemas import UserPreferenceRequest
from src.engine.filter import filter_candidates
from src.engine.llm_client import get_ai_recommendations
from src.ui.components import (
    inject_custom_css,
    render_performance_lab_hero,
    render_diagnostic_stat_tiles,
    render_summary_banner,
    render_recommendation_card,
)
from src.config import BUDGET_TIERS, GEMINI_MODEL

# Set Page Configuration
st.set_page_config(
    page_title="Zomato | Dining Performance Lab",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def load_dataset():
    """Loads and caches the cleaned restaurant dataset."""
    return get_restaurant_data()


def main():
    inject_custom_css()
    render_performance_lab_hero()

    # Load dataset
    with st.spinner("⚡ Calibrating restaurant telemetry records..."):
        df = load_dataset()

    # Extract unique locations and top cuisines
    unique_locations = sorted(df["location"].dropna().unique().tolist())
    all_cuisines = [c for sublist in df["cuisines_list"].dropna() for c in sublist]
    top_cuisines = pd.Series(all_cuisines).value_counts().head(35).index.tolist()
    top_cuisines = sorted(top_cuisines)

    # =========================================================================
    # SIDEBAR: CONTROL STATION (ULTRAHUMAN PERFORMANCE LAB STYLE)
    # =========================================================================
    st.sidebar.markdown(
        """
        <div style="padding-bottom: 0.8rem;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #00F0FF; letter-spacing: 0.1em; text-transform: uppercase;">
                CONTROL STATION // CONFIG
            </div>
            <h2 style="font-size: 1.4rem; font-weight: 800; margin: 0.2rem 0 0 0; color: #FFFFFF; letter-spacing: -0.02em;">
                DIAGNOSTIC CRITERIA
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Curated Protocol Presets
    preset = st.sidebar.selectbox(
        "⚡ EXPERIENCE PROTOCOLS",
        options=[
            "Custom Diagnostic",
            "🍷 Romantic Date Night Protocol (Italian / Fine Wine)",
            "🍔 Rapid Fast-Food & Street Fuel",
            "👨‍👩‍👧 High-Capacity Family Dining Protocol",
            "💻 Focus & Artisan Roastery Session",
            "🍻 Craft Brew & High-Energy Socializing",
        ],
    )

    default_budget = "Medium"
    default_cuisines = []
    default_rating = 4.0
    default_vibe = ""

    if "Romantic Date" in preset:
        default_budget = "High"
        default_cuisines = [c for c in ["Italian", "Continental", "European"] if c in top_cuisines]
        default_rating = 4.2
        default_vibe = "Intimate candlelit seating, ambient low lighting, fine wine selection, and exquisite pasta"
    elif "Fast-Food" in preset:
        default_budget = "Low"
        default_cuisines = [c for c in ["Fast Food", "South Indian", "Street Food"] if c in top_cuisines]
        default_rating = 4.0
        default_vibe = "High-velocity service, authentic regional flavors, budget friendly intake"
    elif "Family Dining" in preset:
        default_budget = "Medium"
        default_cuisines = [c for c in ["North Indian", "Biryani", "Mughlai"] if c in top_cuisines]
        default_rating = 4.0
        default_vibe = "Spacious seating, family dining ambiance, rich signature gravies and kebabs"
    elif "Artisan Roastery" in preset:
        default_budget = "Medium"
        default_cuisines = [c for c in ["Cafe", "Desserts", "Beverages", "American"] if c in top_cuisines]
        default_rating = 4.0
        default_vibe = "Quiet productive ambiance, single-origin espresso, high-speed WiFi, artisan snacks"
    elif "Craft Brew" in preset:
        default_budget = "High"
        default_cuisines = [c for c in ["Continental", "Pizza", "Finger Food", "Italian"] if c in top_cuisines]
        default_rating = 4.3
        default_vibe = "Lively open-air rooftop microbrewery, craft IPA beers, wood-fired sourdough pizzas"

    # Locality Selector
    location = st.sidebar.selectbox(
        "📍 TARGET LOCALITY",
        options=["All Localities"] + unique_locations,
        index=0,
    )
    if location == "All Localities":
        location = ""

    # Budget Matrix Selector
    st.sidebar.markdown(
        "<label style='font-size: 0.85rem; font-weight: 600; color: #A1A1AA; letter-spacing: 0.05em; text-transform: uppercase;'>💰 BUDGET LEVEL</label>",
        unsafe_allow_html=True,
    )
    budget = st.sidebar.radio(
        "Budget Tier",
        options=["Any", "Low", "Medium", "High"],
        index=["Any", "Low", "Medium", "High"].index(default_budget),
        label_visibility="collapsed",
        help="Low (<₹400 for 2) | Medium (₹400-₹1200 for 2) | High (>₹1200 for 2)",
    )

    # Cuisines Matrix
    cuisines = st.sidebar.multiselect(
        "🍕 FLAVOR BIOMARKERS / CUISINES",
        options=top_cuisines,
        default=default_cuisines,
        placeholder="Filter by cuisine classes...",
    )

    # Rating Matrix Slider
    min_rating = st.sidebar.slider(
        "⭐ QUALITY ACCREDITATION SCORE",
        min_value=3.0,
        max_value=5.0,
        value=default_rating,
        step=0.1,
        help="Filter candidates by minimum Zomato rating threshold",
    )

    # Qualitative Vibe Specs
    additional_preferences = st.sidebar.text_area(
        "✨ VIBE SPECIFICATIONS & OCCASION",
        value=default_vibe,
        placeholder="e.g. Open terrace, acoustic jazz, woodfired oven, quick service lunch...",
        height=90,
    )

    # Primary Action Trigger
    search_clicked = st.sidebar.button("⚡ INITIATE AI REASONING SEQUENCE", type="primary", use_container_width=True)

    # =========================================================================
    # MAIN STAGE: TELEMETRY & REASONING RESULTS
    # =========================================================================
    if search_clicked or "last_recommendation" in st.session_state:
        if search_clicked:
            user_request = UserPreferenceRequest(
                location=location if location else "Bangalore",
                budget=budget,
                cuisines=cuisines,
                min_rating=min_rating,
                additional_preferences=additional_preferences,
            )

            with st.spinner("🤖 Running candidate pruning and LLM qualitative trade-off analysis..."):
                candidates, relaxed, relaxation_note = filter_candidates(df, user_request)

                if not candidates:
                    st.warning("⚠️ No restaurants found matching criteria. Please broaden your diagnostic inputs.")
                    return

                response = get_ai_recommendations(user_request, candidates, relaxed, relaxation_note)
                st.session_state["last_recommendation"] = response
                st.session_state["last_request"] = user_request

        # Render Diagnostics
        response = st.session_state.get("last_recommendation")
        if response:
            render_summary_banner(
                response.summary,
                relaxed=response.relaxed_filters_applied,
                relaxation_note=response.relaxation_note,
            )

            st.markdown(
                f"""
                <div style="margin-bottom: 1.5rem;">
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.76rem; color: #00F0FF; letter-spacing: 0.1em; text-transform: uppercase;">
                        EVALUATION REPORT // TOP RANKED
                    </div>
                    <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; font-weight: 800; margin: 0.2rem 0 0 0; color: #FFFFFF; letter-spacing: -0.03em;">
                        TOP {len(response.recommendations)} OPTIMIZED DINING MATCHES
                    </h2>
                </div>
                """,
                unsafe_allow_html=True,
            )

            for rec in response.recommendations:
                render_recommendation_card(rec)

    else:
        # Default Command Stage: Diagnostics & Curated Telemetry
        render_diagnostic_stat_tiles(
            total_restaurants=len(df),
            total_locations=len(unique_locations),
            total_cuisines=len(set(all_cuisines)),
        )

        st.markdown(
            """
            <div style="margin: 2.5rem 0 1.25rem 0;">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.74rem; color: #E23744; letter-spacing: 0.1em; text-transform: uppercase;">
                    TELEMETRY FEED // TOP ACCREDITED
                </div>
                <h3 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.5rem; font-weight: 800; color: #FFFFFF; margin: 0.2rem 0 0 0; letter-spacing: -0.02em;">
                    BENCHMARK DINING DESTINATIONS
                </h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Benchmark display
        sample_df = df.sort_values(by=["rating", "votes"], ascending=False).head(5)
        for idx, (_, row) in enumerate(sample_df.iterrows(), start=1):
            from src.engine.schemas import RestaurantRecommendation
            raw_cuisines = row.get("cuisines_list", [])
            if isinstance(raw_cuisines, (list, tuple)):
                cuisines_lst = [str(c) for c in raw_cuisines]
            elif hasattr(raw_cuisines, "__iter__") and not isinstance(raw_cuisines, str):
                cuisines_lst = [str(c) for c in raw_cuisines]
            else:
                cuisines_lst = [c.strip() for c in str(row.get("cuisines_str", "")).split(",") if c.strip()]
                
            votes_count = int(row.get("votes", 0))
            sample_rec = RestaurantRecommendation(
                rank=idx,
                restaurant_name=str(row["name"]),
                cuisine=cuisines_lst,
                rating=float(row["rating"]),
                estimated_cost_for_two=int(row["approx_cost_for_two"]),
                price_tier=str(row["budget_tier"]),
                location=str(row["location"]),
                explanation=f"A culinary benchmark in {row['location']} accredited with exceptional {', '.join(cuisines_lst[:3])} execution across {votes_count:,} verified visits.",
                highlight_tags=["Benchmark Match", f"⭐ {row['rating']}", str(row["budget_tier"]) + " Tier"],
            )
            render_recommendation_card(sample_rec)


if __name__ == "__main__":
    main()
