"""
Replication Script: Hugging Face Zomato Dataset -> Supabase PostgreSQL DB
Dataset Source: ManikaSaini/zomato-restaurant-recommendation
Target Supabase Project: https://qyxksguifghtppubcsts.supabase.co
"""
import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add workspace root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")

import pandas as pd
import numpy as np
from tqdm import tqdm
from supabase import create_client, Client

from src.config import (
    SUPABASE_URL,
    SUPABASE_KEY,
    PROCESSED_DATA_PATH,
)
from src.data.loader import get_restaurant_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("replicate_to_supabase")


def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL", SUPABASE_URL)
    key = os.getenv("SUPABASE_KEY", SUPABASE_KEY)
    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment (.env).")
    return create_client(url, key)


def sanitize_val(val: Any, default: Any = "") -> Any:
    if val is None or pd.isna(val):
        return default
    if isinstance(val, (np.floating, float)):
        if np.isnan(val) or np.isinf(val):
            return default
        return float(val)
    if isinstance(val, (np.integer, int)):
        return int(val)
    return val


def prepare_records_for_supabase(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Transforms DataFrame rows into clean dicts matching the Supabase restaurants table schema.
    """
    records: List[Dict[str, Any]] = []
    seen = set()

    for _, row in df.iterrows():
        name = str(sanitize_val(row.get("name"), "Unknown")).strip()
        location = str(sanitize_val(row.get("location"), "Bangalore")).strip()
        if not name:
            continue

        # Prevent duplicates within the batch
        pair = (name.lower(), location.lower())
        if pair in seen:
            continue
        seen.add(pair)

        # Cuisines list handling
        raw_cuisines = row.get("cuisines_list", [])
        if isinstance(raw_cuisines, (list, np.ndarray, tuple)):
            cui_list = [str(c).strip() for c in raw_cuisines if str(c).strip()]
        else:
            cui_list = [c.strip() for c in str(row.get("cuisines_str", "")).split(",") if c.strip()]

        cuisines_str = ", ".join(cui_list) if cui_list else str(sanitize_val(row.get("cuisines"), ""))

        # Truncate review string to avoid hitting Supabase HTTP body limits
        reviews_str = str(sanitize_val(row.get("reviews_list"), ""))
        if len(reviews_str) > 1500:
            reviews_str = reviews_str[:1500] + "... [truncated]"

        record = {
            "name": name,
            "url": str(sanitize_val(row.get("url"), "")),
            "address": str(sanitize_val(row.get("address"), "")),
            "location": location,
            "online_order": str(sanitize_val(row.get("online_order"), "No")),
            "book_table": str(sanitize_val(row.get("book_table"), "No")),
            "rating": round(float(sanitize_val(row.get("rating"), 0.0)), 2),
            "votes": int(sanitize_val(row.get("votes"), 0)),
            "phone": str(sanitize_val(row.get("phone"), "")),
            "rest_type": str(sanitize_val(row.get("rest_type"), "")),
            "dish_liked": str(sanitize_val(row.get("dish_liked"), "")),
            "cuisines": str(sanitize_val(row.get("cuisines"), cuisines_str)),
            "cuisines_str": cuisines_str,
            "cuisines_list": cui_list,
            "approx_cost_for_two": int(sanitize_val(row.get("approx_cost_for_two"), 600)),
            "budget_tier": str(sanitize_val(row.get("budget_tier"), "Medium")),
            "reviews_list": reviews_str,
            "menu_item": str(sanitize_val(row.get("menu_item"), "[]"))[:500],
            "listed_in_type": str(sanitize_val(row.get("listed_in_type"), "")),
            "listed_in_city": str(sanitize_val(row.get("listed_in_city"), "")),
        }
        records.append(record)

    return records


def replicate_to_supabase(batch_size: int = 250, limit: int = 0):
    """
    Replicates dataset from local cache or Hugging Face into Supabase.
    """
    logger.info("Initializing Supabase client...")
    client = get_supabase_client()

    logger.info("Loading cleaned dataset (source: Hugging Face Zomato / local parquet)...")
    if PROCESSED_DATA_PATH.exists():
        df = pd.read_parquet(PROCESSED_DATA_PATH)
        logger.info("Loaded %d records from %s", len(df), PROCESSED_DATA_PATH)
    else:
        df = get_restaurant_data()
        logger.info("Ingested and cleaned %d records", len(df))

    if limit > 0:
        df = df.head(limit)
        logger.info("Limit specified: replicating only %d records", limit)

    logger.info("Preparing records for schema mapping...")
    records = prepare_records_for_supabase(df)
    total_records = len(records)
    logger.info("Total clean unique records to replicate: %d", total_records)

    total_batches = (total_records + batch_size - 1) // batch_size
    successful_inserts = 0
    failed_batches = 0

    logger.info("Starting upload in %d batches (batch_size=%d)...", total_batches, batch_size)
    start_time = time.time()

    with tqdm(total=total_records, desc="Replicating to Supabase", unit="rows") as pbar:
        for i in range(0, total_records, batch_size):
            batch = records[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            max_retries = 3
            success = False

            for attempt in range(1, max_retries + 1):
                try:
                    # Upsert records using unique constraint on (name, location)
                    res = client.table("restaurants").upsert(
                        batch,
                        on_conflict="name,location"
                    ).execute()
                    success = True
                    successful_inserts += len(batch)
                    pbar.update(len(batch))
                    break
                except Exception as e:
                    err_msg = str(e)
                    if "PGRST205" in err_msg or "Could not find the table" in err_msg:
                        logger.error(
                            "\n\n[FATAL] The 'restaurants' table does not exist in Supabase yet!\n"
                            "Please run the SQL statements in 'supabase_schema.sql' inside your Supabase SQL Editor:\n"
                            "https://supabase.com/dashboard/project/qyxksguifghtppubcsts/sql\n"
                        )
                        return
                    logger.warning(
                        "Batch %d/%d failed on attempt %d/%d: %s. Retrying in 2s...",
                        batch_num, total_batches, attempt, max_retries, err_msg
                    )
                    time.sleep(2)

            if not success:
                logger.error("Batch %d/%d permanently failed after %d attempts.", batch_num, total_batches, max_retries)
                failed_batches += 1

    elapsed = time.time() - start_time
    logger.info(
        "\n======================================================\n"
        "REPLICATION SUMMARY:\n"
        "  Total records processed : %d\n"
        "  Successfully replicated : %d\n"
        "  Failed batches          : %d\n"
        "  Time elapsed            : %.2f seconds\n"
        "======================================================",
        total_records, successful_inserts, failed_batches, elapsed
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Replicate Hugging Face Zomato dataset to Supabase")
    parser.add_argument("--batch-size", type=int, default=250, help="Batch size for Supabase API upserts")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of records to replicate (0 for all)")
    args = parser.parse_args()

    replicate_to_supabase(batch_size=args.batch_size, limit=args.limit)
