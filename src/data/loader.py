"""
Dataset loader and persistence module for Hugging Face Zomato dataset.
"""
from typing import Optional
from pathlib import Path
import logging
import pandas as pd
from datasets import load_dataset
import json
from src.config import (
    HF_DATASET_ID,
    PROCESSED_DATA_PATH,
    CSV_FALLBACK_PATH,
    RAW_DATA_DIR,
    DATA_SOURCE,
    SUPABASE_URL,
    SUPABASE_KEY,
)
from src.data.cleaner import clean_zomato_dataframe

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Curated fallback seed data in case offline / network unavailable
SEED_RESTAURANT_DATA = [
    {
        "name": "Toscano",
        "location": "UB City, Bangalore",
        "cuisines": "Italian, European, Pizza, Pasta",
        "approx_cost(for_two_people)": "1500",
        "rate": "4.5/5",
        "votes": 2150,
        "rest_type": "Fine Dining",
        "online_order": "Yes",
        "book_table": "Yes",
        "address": "2nd Floor, UB City, Vittal Mallya Road, Bangalore",
    },
    {
        "name": "Empire Restaurant",
        "location": "Indiranagar, Bangalore",
        "cuisines": "North Indian, Mughlai, Biryani, Kebab, Fast Food",
        "approx_cost(for_two_people)": "600",
        "rate": "4.2/5",
        "votes": 5800,
        "rest_type": "Casual Dining",
        "online_order": "Yes",
        "book_table": "No",
        "address": "80 Feet Road, HAL 2nd Stage, Indiranagar, Bangalore",
    },
    {
        "name": "CTR - Shri Sagar",
        "location": "Malleshwaram, Bangalore",
        "cuisines": "South Indian, Fast Food, Street Food",
        "approx_cost(for_two_people)": "200",
        "rate": "4.7/5",
        "votes": 9300,
        "rest_type": "Quick Bites",
        "online_order": "No",
        "book_table": "No",
        "address": "7th Cross, Margosa Road, Malleshwaram, Bangalore",
    },
    {
        "name": "Toit Brewpub",
        "location": "Indiranagar, Bangalore",
        "cuisines": "Italian, Continental, American, Pizza, Craft Beer",
        "approx_cost(for_two_people)": "1800",
        "rate": "4.8/5",
        "votes": 16400,
        "rest_type": "Microbrewery, Pub",
        "online_order": "Yes",
        "book_table": "Yes",
        "address": "100 Feet Road, Indiranagar, Bangalore",
    },
    {
        "name": "Truffles",
        "location": "Koramangala, Bangalore",
        "cuisines": "American, Burgers, Continental, Desserts",
        "approx_cost(for_two_people)": "700",
        "rate": "4.6/5",
        "votes": 14200,
        "rest_type": "Casual Dining, Cafe",
        "online_order": "Yes",
        "book_table": "No",
        "address": "5th Block, Koramangala, Bangalore",
    },
    {
        "name": "Meghana Foods",
        "location": "Koramangala, Bangalore",
        "cuisines": "Biryani, Andhra, North Indian, Seafood",
        "approx_cost(for_two_people)": "650",
        "rate": "4.5/5",
        "votes": 11800,
        "rest_type": "Casual Dining",
        "online_order": "Yes",
        "book_table": "No",
        "address": "1st Block, Koramangala, Bangalore",
    },
    {
        "name": "Corner House Ice Cream",
        "location": "Residency Road, Bangalore",
        "cuisines": "Ice Cream, Desserts",
        "approx_cost(for_two_people)": "300",
        "rate": "4.7/5",
        "votes": 8500,
        "rest_type": "Dessert Parlour",
        "online_order": "Yes",
        "book_table": "No",
        "address": "Residency Road, Bangalore",
    },
    {
        "name": "Vidyarthi Bhavan",
        "location": "Gandhi Bazaar, Bangalore",
        "cuisines": "South Indian",
        "approx_cost(for_two_people)": "150",
        "rate": "4.4/5",
        "votes": 10500,
        "rest_type": "Quick Bites",
        "online_order": "No",
        "book_table": "No",
        "address": "Gandhi Bazaar, Basavanagudi, Bangalore",
    },
    {
        "name": "Mainland China",
        "location": "Church Street, Bangalore",
        "cuisines": "Chinese, Asian, Pan Asian, Dim Sum",
        "approx_cost(for_two_people)": "1700",
        "rate": "4.4/5",
        "votes": 4200,
        "rest_type": "Fine Dining",
        "online_order": "Yes",
        "book_table": "Yes",
        "address": "Church Street, Bangalore",
    },
    {
        "name": "Nagarjuna",
        "location": "Residency Road, Bangalore",
        "cuisines": "Andhra, South Indian, Biryani",
        "approx_cost(for_two_people)": "800",
        "rate": "4.5/5",
        "votes": 7600,
        "rest_type": "Casual Dining",
        "online_order": "Yes",
        "book_table": "Yes",
        "address": "Residency Road, Bangalore",
    },
    {
        "name": "The Fatty Bao",
        "location": "Indiranagar, Bangalore",
        "cuisines": "Asian, Japanese, Chinese, Sushi",
        "approx_cost(for_two_people)": "2200",
        "rate": "4.6/5",
        "votes": 5300,
        "rest_type": "Casual Dining, Bar",
        "online_order": "Yes",
        "book_table": "Yes",
        "address": "12th Main Road, Indiranagar, Bangalore",
    },
    {
        "name": "Brahmins' Coffee Bar",
        "location": "Basavanagudi, Bangalore",
        "cuisines": "South Indian, Beverages",
        "approx_cost(for_two_people)": "100",
        "rate": "4.8/5",
        "votes": 7100,
        "rest_type": "Quick Bites",
        "online_order": "No",
        "book_table": "No",
        "address": "Ranga Rao Road, Near Shankar Mutt, Shankarpuram, Basavanagudi, Bangalore",
    },
    {
        "name": "Buhari Grand",
        "location": "Connaught Place, Delhi",
        "cuisines": "North Indian, Mughlai, Biryani",
        "approx_cost(for_two_people)": "750",
        "rate": "4.3/5",
        "votes": 3400,
        "rest_type": "Casual Dining",
        "online_order": "Yes",
        "book_table": "No",
        "address": "Connaught Place, New Delhi",
    },
    {
        "name": "Saravana Bhavan",
        "location": "Connaught Place, Delhi",
        "cuisines": "South Indian, Vegetarian",
        "approx_cost(for_two_people)": "450",
        "rate": "4.4/5",
        "votes": 6100,
        "rest_type": "Casual Dining",
        "online_order": "Yes",
        "book_table": "No",
        "address": "Janpath, Connaught Place, New Delhi",
    },
    {
        "name": "Bukhara - ITC Maurya",
        "location": "Chanakyapuri, Delhi",
        "cuisines": "North Indian, Kebab, Mughlai, Fine Dining",
        "approx_cost(for_two_people)": "5500",
        "rate": "4.8/5",
        "votes": 7900,
        "rest_type": "Luxury Dining",
        "online_order": "No",
        "book_table": "Yes",
        "address": "Diplomatic Enclave, Chanakyapuri, New Delhi",
    },
    {
        "name": "Karim's",
        "location": "Jama Masjid, Delhi",
        "cuisines": "Mughlai, North Indian, Kebab",
        "approx_cost(for_two_people)": "600",
        "rate": "4.5/5",
        "votes": 12400,
        "rest_type": "Casual Dining",
        "online_order": "Yes",
        "book_table": "No",
        "address": "Gali Kababian, Jama Masjid, Old Delhi",
    }
]


def load_raw_dataset_from_hf() -> pd.DataFrame:
    """
    Downloads and loads the Zomato dataset from Hugging Face.
    Attempts direct CSV download first, then `datasets` library, then falls back to seed data.
    """
    raw_csv_path = RAW_DATA_DIR / "zomato.csv"

    # 1. Check if raw CSV already exists locally
    if raw_csv_path.exists():
        logger.info("Found local raw CSV dataset at %s", raw_csv_path)
        try:
            return pd.read_csv(raw_csv_path, encoding="utf-8")
        except UnicodeDecodeError:
            return pd.read_csv(raw_csv_path, encoding="latin-1")

    # 2. Try direct streaming download from Hugging Face resolve URL
    direct_url = f"https://huggingface.co/datasets/{HF_DATASET_ID}/resolve/main/zomato.csv"
    logger.info("Downloading raw dataset directly from %s...", direct_url)
    try:
        import requests
        resp = requests.get(direct_url, timeout=30, stream=True)
        if resp.status_code == 200:
            with open(raw_csv_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
            logger.info("Saved raw dataset to %s", raw_csv_path)
            try:
                return pd.read_csv(raw_csv_path, encoding="utf-8")
            except UnicodeDecodeError:
                return pd.read_csv(raw_csv_path, encoding="latin-1")
    except Exception as e:
        logger.warning("Direct download failed (%s). Trying `datasets` library...", e)

    # 3. Try datasets library
    try:
        ds = load_dataset(HF_DATASET_ID, split="train")
        df = ds.to_pandas()
        logger.info("Successfully fetched %d records from Hugging Face via datasets library.", len(df))
        return df
    except Exception as e:
        logger.warning("Could not fetch from Hugging Face (%s). Using comprehensive seed dataset.", e)
        return pd.DataFrame(SEED_RESTAURANT_DATA)


def load_restaurants_from_supabase(batch_size: int = 1000) -> Optional[pd.DataFrame]:
    """
    Loads all restaurant records directly from the Supabase PostgreSQL database.
    Paginates across batches of `batch_size` to handle PostgREST row limits.
    """
    from src.data.supabase_client import get_supabase_client
    client = get_supabase_client()
    if not client:
        logger.warning("Supabase client unavailable. Skipping Supabase ingestion.")
        return None

    try:
        logger.info("Connecting to Supabase Cloud DB (%s) to fetch restaurants...", SUPABASE_URL)
        all_rows = []
        offset = 0

        while True:
            res = (
                client.table("restaurants")
                .select("*")
                .order("id")
                .range(offset, offset + batch_size - 1)
                .execute()
            )
            data = res.data or []
            if not data:
                break
            all_rows.extend(data)
            logger.info("Fetched %d rows from Supabase (total so far: %d)...", len(data), len(all_rows))
            if len(data) < batch_size:
                break
            offset += batch_size

        if not all_rows:
            logger.warning("Supabase returned 0 restaurant records.")
            return None

        df = pd.DataFrame(all_rows)
        logger.info("Successfully loaded %d records from Supabase!", len(df))

        # Ensure correct data types and list parsing
        if "cuisines_list" in df.columns:
            def parse_cui_list(val):
                if isinstance(val, (list, tuple)):
                    return [str(c) for c in val if str(c).strip()]
                if pd.isna(val) or val is None:
                    return []
                if isinstance(val, str):
                    try:
                        parsed = json.loads(val)
                        if isinstance(parsed, list):
                            return parsed
                    except Exception:
                        pass
                    return [c.strip() for c in val.split(",") if c.strip()]
                return []

            df["cuisines_list"] = df["cuisines_list"].apply(parse_cui_list)

        if "rating" in df.columns:
            df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0.0)
        if "votes" in df.columns:
            df["votes"] = pd.to_numeric(df["votes"], errors="coerce").fillna(0).astype(int)
        if "approx_cost_for_two" in df.columns:
            df["approx_cost_for_two"] = pd.to_numeric(df["approx_cost_for_two"], errors="coerce").fillna(600).astype(int)

        # Sync local cache with freshly fetched Supabase data for fast re-reads & offline resilience
        try:
            df.to_parquet(PROCESSED_DATA_PATH, index=False)
            logger.info("Synchronized local parquet cache from Supabase (%d records)", len(df))
        except Exception as e:
            logger.warning("Could not cache Supabase dataframe to parquet: %s", e)

        return df
    except Exception as e:
        logger.warning("Error fetching restaurants from Supabase (%s). Proceeding to fallback.", e)
        return None


def get_restaurant_data(force_reload: bool = False) -> pd.DataFrame:
    """
    Retrieves the cleaned restaurant dataset.
    Prioritizes Supabase Cloud DB as primary source when configured.
    Falls back cleanly to local Parquet/CSV cache or Hugging Face.
    """
    # 1. Primary Source: Supabase Cloud Database (if configured or forced)
    if DATA_SOURCE.lower() == "supabase" and SUPABASE_KEY:
        supabase_df = load_restaurants_from_supabase()
        if supabase_df is not None and not supabase_df.empty:
            logger.info("Using Supabase Cloud Database as PRIMARY restaurant data source (%d records)", len(supabase_df))
            return supabase_df
        logger.warning("Supabase Cloud DB was not ready or empty. Falling back to local cache / Hugging Face...")

    # 2. Try Parquet cache
    if not force_reload and PROCESSED_DATA_PATH.exists():
        try:
            logger.info("Loading cached processed dataset from %s", PROCESSED_DATA_PATH)
            return pd.read_parquet(PROCESSED_DATA_PATH)
        except Exception as e:
            logger.warning("Error reading parquet cache: %s. Re-ingesting...", e)

    # 3. Try CSV fallback cache
    if not force_reload and CSV_FALLBACK_PATH.exists():
        try:
            logger.info("Loading cached CSV dataset from %s", CSV_FALLBACK_PATH)
            df = pd.read_csv(CSV_FALLBACK_PATH)
            # Restore list type for cuisines
            df["cuisines_list"] = df["cuisines_str"].apply(lambda s: [c.strip() for c in str(s).split(",") if c.strip()])
            return df
        except Exception as e:
            logger.warning("Error reading CSV cache: %s", e)

    # 4. Ingest and Clean from Hugging Face / Seed
    raw_df = load_raw_dataset_from_hf()
    cleaned_df = clean_zomato_dataframe(raw_df)

    # 5. Save to cache
    try:
        cleaned_df.to_parquet(PROCESSED_DATA_PATH, index=False)
        logger.info("Saved cleaned dataset to parquet at %s (%d records)", PROCESSED_DATA_PATH, len(cleaned_df))
    except Exception as e:
        logger.warning("Could not save to parquet (%s). Saving to CSV...", e)
        cleaned_df.to_csv(CSV_FALLBACK_PATH, index=False)

    return cleaned_df

