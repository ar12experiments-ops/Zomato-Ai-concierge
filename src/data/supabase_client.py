"""
Supabase client provider and health checker.
"""
import logging
from typing import Optional
from supabase import create_client, Client
from src.config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

_supabase_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """
    Returns a cached Supabase client singleton, or None if credentials are missing.
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("Supabase credentials not configured (SUPABASE_URL or SUPABASE_KEY empty).")
        return None

    try:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client successfully initialized for project: %s", SUPABASE_URL)
        return _supabase_client
    except Exception as e:
        logger.error("Failed to initialize Supabase client: %s", e)
        return None


def test_supabase_connection() -> dict:
    """
    Tests connectivity to Supabase and checks if 'restaurants' table is available.
    """
    client = get_supabase_client()
    if not client:
        return {"connected": False, "table_exists": False, "error": "Supabase client not initialized."}

    try:
        res = client.table("restaurants").select("count", count="exact").limit(0).execute()
        count = res.count if hasattr(res, "count") and res.count is not None else 0
        return {"connected": True, "table_exists": True, "count": count, "error": None}
    except Exception as e:
        err_str = str(e)
        table_exists = not ("PGRST205" in err_str or "Could not find the table" in err_str)
        return {"connected": True if table_exists else False, "table_exists": table_exists, "error": err_str}
