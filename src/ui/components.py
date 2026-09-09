"""
Ultrahuman Performance Lab UI styling and components for the AI Restaurant Recommendation System.
Design system features:
- Deep obsidian dark theme (#060608 / #0D0D11) with ambient glowing neon aurora backlights
- High-tech typography ('Space Grotesk', 'Plus Jakarta Sans', 'JetBrains Mono')
- Smoky frosted glassmorphism (backdrop-filter: blur(28px), 1px laser-etched borders)
- Live biometric signal ticker marquee pills
- Precision diagnostic stat counters
- Ultrahuman-style restaurant command cards with AI Diagnostic Verdict and Match Index
"""
from typing import List, Optional
import streamlit as st
from src.engine.schemas import RestaurantRecommendation

ULTRAHUMAN_LAB_CSS = """
<style>
/* ==========================================================================
   1. ULTRAHUMAN PERFORMANCE LAB - GLOBAL TOKENS & TYPOGRAPHY
   ========================================================================== */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --uh-bg: #060608;
    --uh-bg-secondary: #0D0D12;
    --uh-card-bg: rgba(15, 15, 20, 0.78);
    --uh-card-hover: rgba(22, 22, 30, 0.92);
    
    --uh-border: rgba(255, 255, 255, 0.08);
    --uh-border-hover: rgba(0, 240, 255, 0.35);
    --uh-border-red: rgba(226, 55, 68, 0.4);
    
    --uh-cyan: #00F0FF;
    --uh-cyan-glow: rgba(0, 240, 255, 0.22);
    --uh-red: #E23744;
    --uh-red-glow: rgba(226, 55, 68, 0.28);
    --uh-emerald: #10B981;
    --uh-gold: #F59E0B;
    
    --uh-text-primary: #FFFFFF;
    --uh-text-secondary: #A1A1AA;
    --uh-text-muted: #71717A;
    
    --font-heading: 'Space Grotesk', 'Plus Jakarta Sans', sans-serif;
    --font-body: 'Plus Jakarta Sans', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    
    --radius-card: 20px;
    --radius-pill: 9999px;
    --radius-badge: 8px;
}

/* Base Body & App Container */
html, body, [class*="css"] {
    font-family: var(--font-body) !important;
    color: var(--uh-text-primary) !important;
    background-color: var(--uh-bg) !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.stApp {
    background: radial-gradient(circle at 50% -10%, rgba(226, 55, 68, 0.12) 0%, rgba(0, 240, 255, 0.04) 40%, #060608 85%) !important;
}

/* Streamlit Container Layout */
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 4rem;
    max-width: 1200px;
}

/* ==========================================================================
   2. ULTRAHUMAN PERFORMANCE LAB - HERO COMMAND HEADER
   ========================================================================== */
.uh-hero-container {
    background: linear-gradient(180deg, rgba(18, 18, 24, 0.85) 0%, rgba(10, 10, 14, 0.95) 100%);
    backdrop-filter: blur(32px) saturate(190%);
    -webkit-backdrop-filter: blur(32px) saturate(190%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 28px;
    padding: 3rem 2.8rem;
    margin-bottom: 2.2rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8), 0 0 40px rgba(226, 55, 68, 0.08);
}

.uh-hero-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(226, 55, 68, 0.8), rgba(0, 240, 255, 0.8), transparent);
}

.uh-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(0, 240, 255, 0.08);
    border: 1px solid rgba(0, 240, 255, 0.25);
    color: var(--uh-cyan);
    font-family: var(--font-mono);
    font-size: 0.78rem;
    font-weight: 600;
    padding: 5px 14px;
    border-radius: var(--radius-pill);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
}

.uh-pulse-dot {
    width: 7px;
    height: 7px;
    background-color: var(--uh-cyan);
    border-radius: 50%;
    box-shadow: 0 0 10px var(--uh-cyan);
    animation: pulseGlow 2s infinite ease-in-out;
}

@keyframes pulseGlow {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.4); opacity: 0.6; }
}

.uh-hero-title {
    font-family: var(--font-heading);
    font-size: 3.2rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    margin: 0;
    line-height: 1.08;
    color: #FFFFFF;
    text-transform: uppercase;
}

.uh-hero-title-accent {
    background: linear-gradient(90deg, #FFFFFF 0%, #E23744 50%, #00F0FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.uh-hero-subtitle {
    font-size: 1.12rem;
    color: var(--uh-text-secondary);
    margin-top: 1rem;
    margin-bottom: 0;
    max-width: 720px;
    line-height: 1.6;
    font-weight: 400;
}

/* ==========================================================================
   3. SIGNAL STRIP (ULTRAHUMAN MARQUEE TICKER PILLS)
   ========================================================================== */
.uh-signal-band {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 1.6rem;
    padding-top: 1.4rem;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.uh-signal-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.07);
    color: #E4E4E7;
    font-family: var(--font-mono);
    font-size: 0.76rem;
    padding: 4px 11px;
    border-radius: var(--radius-pill);
    letter-spacing: 0.04em;
    transition: all 0.2s ease;
}

.uh-signal-pill:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.2);
    color: #FFFFFF;
}

/* ==========================================================================
   4. DIAGNOSTIC STAT TILES (ULTRAHUMAN LAB STATS)
   ========================================================================== */
.uh-stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 1.25rem;
    margin-bottom: 2.2rem;
}

.uh-stat-card {
    background: var(--uh-card-bg);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid var(--uh-border);
    border-radius: var(--radius-card);
    padding: 1.6rem 1.8rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    position: relative;
    overflow: hidden;
}

.uh-stat-card:hover {
    transform: translateY(-3px);
    border-color: rgba(0, 240, 255, 0.3);
    box-shadow: 0 14px 36px rgba(0, 0, 0, 0.6), 0 0 20px rgba(0, 240, 255, 0.08);
}

.uh-stat-code {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--uh-text-muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

.uh-stat-number {
    font-family: var(--font-heading);
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #FFFFFF;
    line-height: 1;
    margin-bottom: 0.35rem;
}

.uh-stat-label {
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--uh-text-secondary);
    letter-spacing: 0.02em;
}

/* ==========================================================================
   5. PERFORMANCE LAB RESTAURANT CARDS
   ========================================================================== */
.uh-restaurant-card {
    background: var(--uh-card-bg);
    backdrop-filter: blur(28px) saturate(180%);
    -webkit-backdrop-filter: blur(28px) saturate(180%);
    border: 1px solid var(--uh-border);
    border-radius: 24px;
    padding: 2rem 2.2rem;
    margin-bottom: 2rem;
    box-shadow: 0 14px 40px rgba(0, 0, 0, 0.5);
    transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.3s ease, box-shadow 0.3s ease;
    position: relative;
    overflow: hidden;
}

.uh-restaurant-card:hover {
    transform: translateY(-4px) scale(1.005);
    border-color: rgba(226, 55, 68, 0.35);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7), 0 0 30px rgba(226, 55, 68, 0.1);
}

.uh-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1.5rem;
}

.uh-spec-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: var(--font-mono);
    font-size: 0.76rem;
    font-weight: 600;
    color: var(--uh-red);
    background: rgba(226, 55, 68, 0.1);
    border: 1px solid rgba(226, 55, 68, 0.25);
    padding: 4px 12px;
    border-radius: var(--radius-pill);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}

.uh-restaurant-name {
    font-family: var(--font-heading);
    font-size: 1.85rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #FFFFFF;
    margin: 0;
    line-height: 1.2;
}

.uh-locality {
    font-size: 0.92rem;
    color: var(--uh-text-secondary);
    margin-top: 0.4rem;
    display: flex;
    align-items: center;
    gap: 5px;
}

/* Rating Metric Box */
.uh-rating-box {
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.35);
    color: var(--uh-emerald);
    font-family: var(--font-mono);
    font-weight: 700;
    font-size: 1.15rem;
    padding: 8px 16px;
    border-radius: 12px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    letter-spacing: 0.02em;
    box-shadow: 0 0 20px rgba(16, 185, 129, 0.15);
}

.uh-cost-metric {
    font-family: var(--font-mono);
    font-size: 0.85rem;
    color: var(--uh-text-secondary);
    margin-top: 8px;
    text-align: right;
    letter-spacing: 0.04em;
}

/* Biomarker / Cuisine Chips */
.uh-cuisine-chip {
    display: inline-flex;
    align-items: center;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.09);
    color: #F4F4F5;
    font-size: 0.82rem;
    font-weight: 500;
    padding: 5px 13px;
    border-radius: var(--radius-pill);
    margin-right: 7px;
    margin-bottom: 7px;
    letter-spacing: 0.02em;
}

.uh-tag-chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(0, 240, 255, 0.06);
    border: 1px solid rgba(0, 240, 255, 0.22);
    color: var(--uh-cyan);
    font-family: var(--font-mono);
    font-size: 0.78rem;
    font-weight: 500;
    padding: 4px 12px;
    border-radius: var(--radius-pill);
    margin-right: 7px;
    margin-top: 8px;
    letter-spacing: 0.03em;
}

/* AI Diagnostic Verdict Box (Terminal Aesthetic) */
.uh-verdict-box {
    background: linear-gradient(135deg, rgba(226, 55, 68, 0.06) 0%, rgba(0, 240, 255, 0.04) 100%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-left: 4px solid var(--uh-red);
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    margin-top: 1.2rem;
    position: relative;
}

.uh-verdict-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: var(--font-mono);
    font-size: 0.8rem;
    font-weight: 700;
    color: var(--uh-red);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.5rem;
}

.uh-verdict-text {
    font-size: 0.96rem;
    color: #E4E4E7;
    line-height: 1.6;
    margin: 0;
    font-weight: 400;
}

/* ==========================================================================
   6. SUMMARY CALLOUT & SIDEBAR STYLING
   ========================================================================== */
.uh-summary-card {
    background: rgba(18, 18, 24, 0.85);
    backdrop-filter: blur(28px);
    border: 1px solid var(--uh-border);
    border-left: 5px solid var(--uh-cyan);
    border-radius: 20px;
    padding: 1.75rem 2rem;
    margin-bottom: 2.2rem;
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.5);
}

.uh-summary-title {
    font-family: var(--font-heading);
    font-size: 1.2rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 8px;
}

.uh-summary-body {
    font-size: 1rem;
    color: var(--uh-text-secondary);
    line-height: 1.6;
    margin: 0;
}

/* Dark Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0A0A0E !important;
    border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
}

section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
    color: #FFFFFF !important;
    font-family: var(--font-heading) !important;
    letter-spacing: -0.02em;
}

/* High-Tech Primary Action Button */
div.stButton > button[kind="primary"], div.stButton > button {
    background: linear-gradient(135deg, #E23744 0%, #B91422 100%) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    border-radius: var(--radius-pill) !important;
    padding: 0.85rem 1.6rem !important;
    font-family: var(--font-heading) !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.02em !important;
    text-transform: uppercase !important;
    box-shadow: 0 10px 28px rgba(226, 55, 68, 0.35) !important;
    transition: all 0.25s ease !important;
    width: 100%;
}

div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 14px 34px rgba(226, 55, 68, 0.5), 0 0 20px rgba(0, 240, 255, 0.2) !important;
    border-color: var(--uh-cyan) !important;
}

div.stButton > button:active {
    transform: scale(0.98) !important;
}
</style>
"""


def inject_custom_css():
    """Injects Ultrahuman Performance Lab dark theme styling."""
    st.markdown(ULTRAHUMAN_LAB_CSS, unsafe_allow_html=True)


def render_performance_lab_hero():
    """Renders the Ultrahuman Performance Lab signature command hero."""
    st.markdown(
        """
        <div class="uh-hero-container">
            <div class="uh-status-pill">
                <span class="uh-pulse-dot"></span>
                <span>SYSTEM ACTIVE // RESTAURANT INTELLIGENCE LAB</span>
            </div>
            <h1 class="uh-hero-title">
                DINING <span class="uh-hero-title-accent">PERFORMANCE LAB</span>
            </h1>
            <p class="uh-hero-subtitle">
                The next-generation command center for culinary discovery. Combining structured Zomato telemetry with Large Language Model qualitative reasoning.
            </p>
            <div class="uh-signal-band">
                <span class="uh-signal-pill">🍕 WOODFIRED CRUST</span>
                <span class="uh-signal-pill">🍷 ACIDITY & WINE TASTE</span>
                <span class="uh-signal-pill">🥘 RICH AROMA</span>
                <span class="uh-signal-pill">🌿 VEGAN & PLANT-BASED</span>
                <span class="uh-signal-pill">⭐ 4.8 ACCREDITED</span>
                <span class="uh-signal-pill">☕ ARTISAN ROASTERY</span>
                <span class="uh-signal-pill">⚡ QUICK INTAKE</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_diagnostic_stat_tiles(total_restaurants: int, total_locations: int, total_cuisines: int):
    """Renders Ultrahuman Performance Lab telemetry stat counters."""
    st.markdown(
        f"""
        <div class="uh-stats-grid">
            <div class="uh-stat-card">
                <div class="uh-stat-code">DATASET_INDEX // 01</div>
                <div class="uh-stat-number">{total_restaurants:,}</div>
                <div class="uh-stat-label">Calibrated Restaurant Nodes</div>
            </div>
            <div class="uh-stat-card">
                <div class="uh-stat-code">GEO_COVERAGE // 02</div>
                <div class="uh-stat-number">{total_locations:,}</div>
                <div class="uh-stat-label">Verified Dining Localities</div>
            </div>
            <div class="uh-stat-card">
                <div class="uh-stat-code">FLAVOR_MATRIX // 03</div>
                <div class="uh-stat-number">{total_cuisines:,}</div>
                <div class="uh-stat-label">Global Cuisine Classes</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_summary_banner(summary: str, relaxed: bool = False, relaxation_note: Optional[str] = None):
    """Renders the executive AI summary in Performance Lab callout style."""
    if relaxed and relaxation_note:
        st.info(f"⚡ **Diagnostic Notice:** {relaxation_note}")

    st.markdown(
        f"""
        <div class="uh-summary-card">
            <div class="uh-summary-title">
                <span>🎯 AI DIAGNOSTIC SYNTHESIS</span>
            </div>
            <p class="uh-summary-body">{summary}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_recommendation_card(rec: RestaurantRecommendation):
    """Renders a high-tech Ultrahuman Performance Lab restaurant recommendation card."""
    # Ensure cuisine is a list
    if isinstance(rec.cuisine, (list, tuple)):
        cuisines_list = [str(c) for c in rec.cuisine]
    elif isinstance(rec.cuisine, str):
        cuisines_list = [c.strip() for c in rec.cuisine.split(",") if c.strip()]
    else:
        cuisines_list = []

    # Ensure tags is a list
    if isinstance(rec.highlight_tags, (list, tuple)):
        tags_list = [str(t) for t in rec.highlight_tags]
    elif isinstance(rec.highlight_tags, str):
        tags_list = [t.strip() for t in rec.highlight_tags.split(",") if t.strip()]
    else:
        tags_list = []

    # Format rating safely
    try:
        rating_formatted = f"{float(rec.rating):.1f}"
    except (ValueError, TypeError):
        rating_formatted = "4.0"

    # Format cost safely
    try:
        cost_formatted = f"₹{int(rec.estimated_cost_for_two):,} FOR TWO"
    except (ValueError, TypeError):
        cost_formatted = "₹600 FOR TWO"

    cuisines_html = "".join([f'<span class="uh-cuisine-chip">{c}</span>' for c in cuisines_list[:5]])
    tags_html = "".join([f'<span class="uh-tag-chip">⚡ {t}</span>' for t in tags_list])

    card_html = f"""
    <div class="uh-restaurant-card">
        <div class="uh-card-header">
            <div>
                <div class="uh-spec-tag">
                    <span>SPEC #{rec.rank:02d} // REASONING MATCH</span>
                </div>
                <h3 class="uh-restaurant-name">{rec.restaurant_name}</h3>
                <div class="uh-locality">
                    <span>📍</span> {rec.location}
                </div>
            </div>
            <div style="text-align: right; flex-shrink: 0;">
                <div class="uh-rating-box">
                    ★ {rating_formatted}
                </div>
                <div class="uh-cost-metric">
                    {cost_formatted}
                </div>
            </div>
        </div>
        
        <div style="margin-top: 0.9rem; margin-bottom: 0.5rem;">
            {cuisines_html}
        </div>
        
        <div class="uh-verdict-box">
            <div class="uh-verdict-header">
                <span>🤖 AI DIAGNOSTIC VERDICT</span>
            </div>
            <p class="uh-verdict-text">{rec.explanation}</p>
        </div>
        
        <div style="margin-top: 0.5rem;">
            {tags_html}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
