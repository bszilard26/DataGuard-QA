CREATE TABLE IF NOT EXISTS dim_country (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS staging_customers (
    full_name TEXT,
    email TEXT,
    age INTEGER,
    status TEXT,
    country_code TEXT,
    updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS target_customers (
    customer_id SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    age INTEGER NOT NULL CHECK (age BETWEEN 18 AND 120),
    status TEXT NOT NULL CHECK (status IN ('active','inactive','pending')),
    country_code TEXT NOT NULL REFERENCES dim_country(code),
    updated_at TIMESTAMPTZ NOT NULL,
    source_file TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rejected_rows (
    reject_id SERIAL PRIMARY KEY,
    source_table TEXT NOT NULL,
    raw_full_name TEXT,
    raw_email TEXT,
    raw_age TEXT,
    raw_status TEXT,
    raw_country_code TEXT,
    raw_updated_at TEXT,
    reason TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS etl_run_metrics (
    run_id SERIAL PRIMARY KEY,
    run_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_count INTEGER,
    target_count INTEGER,
    rejected_count INTEGER,
    notes TEXT
);
