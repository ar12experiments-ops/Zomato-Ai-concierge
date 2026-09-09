-- =============================================================================
-- Supabase Schema: Zomato Restaurant Recommendations
-- Run this script in your Supabase SQL Editor:
-- https://supabase.com/dashboard/project/qyxksguifghtppubcsts/sql
-- =============================================================================

-- 1. Create the restaurants table
CREATE TABLE IF NOT EXISTS public.restaurants (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT,
    address TEXT,
    location TEXT NOT NULL,
    online_order TEXT DEFAULT 'No',
    book_table TEXT DEFAULT 'No',
    rating NUMERIC(3, 2) DEFAULT 0.00,
    votes INTEGER DEFAULT 0,
    phone TEXT,
    rest_type TEXT,
    dish_liked TEXT,
    cuisines TEXT,
    cuisines_str TEXT,
    cuisines_list JSONB DEFAULT '[]'::jsonb,
    approx_cost_for_two INTEGER DEFAULT 0,
    budget_tier TEXT DEFAULT 'Medium',
    reviews_list TEXT,
    menu_item TEXT,
    listed_in_type TEXT,
    listed_in_city TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_restaurant_loc UNIQUE (name, location)
);

-- 2. Performance Indexes for fast filtering & ranking
CREATE INDEX IF NOT EXISTS idx_restaurants_location ON public.restaurants(location);
CREATE INDEX IF NOT EXISTS idx_restaurants_rating ON public.restaurants(rating DESC);
CREATE INDEX IF NOT EXISTS idx_restaurants_votes ON public.restaurants(votes DESC);
CREATE INDEX IF NOT EXISTS idx_restaurants_budget ON public.restaurants(budget_tier);
CREATE INDEX IF NOT EXISTS idx_restaurants_cost ON public.restaurants(approx_cost_for_two);
CREATE INDEX IF NOT EXISTS idx_restaurants_cuisines_trgm ON public.restaurants USING gin (to_tsvector('english', coalesce(cuisines_str, '')));

-- 3. Row-Level Security (RLS) Setup
ALTER TABLE public.restaurants ENABLE ROW LEVEL SECURITY;

-- Allow public read access (for anon and authenticated users)
DROP POLICY IF EXISTS "Allow public read access" ON public.restaurants;
CREATE POLICY "Allow public read access"
    ON public.restaurants
    FOR SELECT
    TO public
    USING (true);

-- Allow full access for service_role
DROP POLICY IF EXISTS "Allow service_role full access" ON public.restaurants;
CREATE POLICY "Allow service_role full access"
    ON public.restaurants
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- 4. Grant permissions to public roles
GRANT SELECT ON public.restaurants TO anon, authenticated;
GRANT ALL ON public.restaurants TO service_role;
GRANT USAGE, SELECT ON SEQUENCE public.restaurants_id_seq TO anon, authenticated, service_role;
