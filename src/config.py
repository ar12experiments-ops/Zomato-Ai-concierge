"""
Configuration and constants for the AI-Powered Restaurant Recommendation System.
"""
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = Path(os.getenv("RAW_DATA_DIR", str(DATA_DIR / "raw")))
PROCESSED_DATA_DIR = Path(os.getenv("CACHE_DIR", str(DATA_DIR / "processed")))

# Ensure required directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Processed dataset file path
PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "zomato_cleaned.parquet"
CSV_FALLBACK_PATH = PROCESSED_DATA_DIR / "zomato_cleaned.csv"

# Hugging Face Dataset identifier
HF_DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Supabase Cloud Database Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qyxksguifghtppubcsts.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
DATA_SOURCE = os.getenv("DATA_SOURCE", "supabase" if os.getenv("SUPABASE_KEY") else "local")

# Candidate retrieval settings
MAX_CANDIDATES_FOR_LLM = int(os.getenv("MAX_CANDIDATES_FOR_LLM", "15"))
DEFAULT_TOP_RECOMMENDATIONS = 5

# Budget Tier Thresholds (in INR for two persons)
BUDGET_TIERS = {
    "Low": {"min": 0, "max": 400, "label": "Low (Under ₹400 for two)"},
    "Medium": {"min": 400, "max": 1200, "label": "Medium (₹400 - ₹1200 for two)"},
    "High": {"min": 1200, "max": 100000, "label": "High (Above ₹1200 for two)"},
}

