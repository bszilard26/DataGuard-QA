# DataGuard-QA

![CI](https://github.com/bszilard26/DataGuard-QA/actions/workflows/ci.yml/badge.svg)
![Version](https://img.shields.io/badge/version-1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Overview

DataGuard-QA is an end-to-end QA showcase covering UI, API, and data/ETL validation with production-grade tooling, Docker, and CI.

- UI: Selenium + Page Objects
- API: requests + pytest
- ETL/Data QA: pandas + SQLite (Postgres optional), Great Expectations
- Tooling: black, ruff, mypy, pre-commit
- Reporting: Allure
- CI/CD: GitHub Actions + Docker/Compose

## Tech Stack

| Area    | Tools |
|---------|-------|
| UI      | Selenium, WebDriverManager, Pytest |
| API     | requests, Pytest |
| ETL/DB  | pandas, SQLite/Postgres, SQLAlchemy path, Great Expectations |
| CI/CD   | GitHub Actions, Docker, Docker Compose |
| Reports | Allure, allure-pytest plugin |

## ETL Harness Highlights

- SQLite-first schema plus optional Postgres profile (testcontainers)
- Tiny + medium fixtures, golden snapshot, drift metrics guard
- Pandas ETL: clean/validate/dedupe by email, upsert idempotently, capture rejects with reasons
- Validators: row counts, nulls, duplicates, FK integrity, domain/range, email format
- Make targets: install, etl, etl-medium, etl-pg, etl-all, format, lint, type, gx
- CLI runner: `python scripts/run_etl.py <csv> <db> etl/schema_sqlite.sql tests/fixtures/etl/dim_countries.csv`

## Quickstart (TL;DR)

```bash
git clone git@github.com:bszilard26/DataGuard-QA.git
cd DataGuard-QA

python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pip install pre-commit mypy ruff black

# quality gates
black . && ruff check . && python -m mypy --ignore-missing-imports .

# core ETL suite (SQLite)
PYTHONPATH=. pytest tests/etl/test_etl_data_validation.py

# optional: medium & Postgres profiles
PYTHONPATH=. RUN_MEDIUM_ETL=1 pytest tests/etl/test_etl_data_validation.py::test_etl_medium_dataset
PYTHONPATH=. RUN_PG_ETL=1 pytest tests/etl/test_etl_postgres.py

# dockerized run (defaults to ETL pytest suite)
docker build -t dataguard-qa .
docker run --rm dataguard-qa
```

Allure: `make allure` to generate, `make allure-serve` to view (Allure CLI required). Cleanup: `make clean`.

Full enterprise runbook: [docs/RUNBOOK.md](docs/RUNBOOK.md)

## Reports
- Allure results: `reports/allure-results/` -> `allure serve reports/allure-results`
- Great Expectations checkpoint: `make gx` (runs tiny ETL + GX validation)

## CI
GitHub Actions workflow (`.github/workflows/ci.yml`) enforces format/lint/type, runs ETL (SQLite), GX checkpoint, and a Postgres service job.
