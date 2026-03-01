PRAGMA foreign_keys = ON;

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
	updated_at TEXT,
	_source_file TEXT
);

CREATE TABLE IF NOT EXISTS target_customers (
	customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
	email TEXT NOT NULL UNIQUE,
	first_name TEXT NOT NULL,
	last_name TEXT NOT NULL,
	age INTEGER NOT NULL CHECK (age BETWEEN 18 AND 120),
	status TEXT NOT NULL CHECK (status IN ('active','inactive','pending')),
	country_code TEXT NOT NULL,
	updated_at TEXT NOT NULL,
	source_file TEXT,
	created_at TEXT DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (country_code) REFERENCES dim_country(code)
);

CREATE TABLE IF NOT EXISTS rejected_rows (
	reject_id INTEGER PRIMARY KEY AUTOINCREMENT,
	source_table TEXT NOT NULL,
	raw_full_name TEXT,
	raw_email TEXT,
	raw_age TEXT,
	raw_status TEXT,
	raw_country_code TEXT,
	raw_updated_at TEXT,
	reason TEXT NOT NULL,
	created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS etl_run_metrics (
	run_id INTEGER PRIMARY KEY AUTOINCREMENT,
	run_at TEXT NOT NULL,
	source_count INTEGER,
	target_count INTEGER,
	rejected_count INTEGER,
	notes TEXT
);
