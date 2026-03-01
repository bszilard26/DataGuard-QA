# DataGuard-QA Runbook (Enterprise)

## 1) Prerequisites
- Python 3.11+, make, git
- Docker + Docker Compose (for containerized runs and Postgres testcontainers support)
- Allure CLI (optional, for HTML reports): https://docs.qameta.io/allure/

## 2) Local environment setup
```bash
# clone
git clone git@github.com:bszilard26/DataGuard-QA.git
cd DataGuard-QA

# create and activate venv
python3 -m venv venv
source venv/bin/activate

# install deps (tests + tooling)
pip install -r requirements.txt
pip install pre-commit mypy ruff black  # once per machine

# optional: install git hooks
pre-commit install
```

## 3) Quality gates (run before PRs)
```bash
# format
black .

# lint
ruff check .

# type-check
python -m mypy --ignore-missing-imports .
```

## 4) Test suites
- Fast ETL smoke (SQLite):
  ```bash
  PYTHONPATH=. pytest tests/etl/test_etl_data_validation.py
  ```
- Medium dataset (opt-in):
  ```bash
  PYTHONPATH=. RUN_MEDIUM_ETL=1 pytest tests/etl/test_etl_data_validation.py::test_etl_medium_dataset
  ```
- Postgres profile via testcontainers (requires Docker running):
  ```bash
  PYTHONPATH=. RUN_PG_ETL=1 pytest tests/etl/test_etl_postgres.py
  ```
- Full matrix (SQLite + medium + Postgres):
  ```bash
  PYTHONPATH=. RUN_MEDIUM_ETL=1 RUN_PG_ETL=1 pytest tests/etl
  ```
- Shortcuts via Make (venv activated): `make etl`, `make etl-medium`, `make etl-pg`, `make etl-all`

## 5) Allure reports
- Generate results: `make allure` (runs ETL suite with `--alluredir reports/allure-results`)
- View locally (requires Allure CLI): `make allure-serve`

## 6) Cleanup
- One-shot cleanup of caches, DBs, generated data, and Allure outputs:
  ```bash
  make clean
  ```

## 7) Data quality checkpoint (Great Expectations)
```bash
PYTHONPATH=. python scripts/run_etl.py \
  tests/fixtures/etl/tiny/customers_tiny.csv \
  /tmp/etl_gx.db \
  etl/schema_sqlite.sql \
  tests/fixtures/etl/dim_countries.csv
PYTHONPATH=. python expectations/gx_tiny_checkpoint.py /tmp/etl_gx.db
```

## 8) UI and API tests (optional demos)
```bash
PYTHONPATH=. pytest tests/ui
PYTHONPATH=. pytest tests/api
```

## 9) Containerized run
```bash
# build image
docker build -t dataguard-qa .

# run default command (ETL pytest suite)
docker run --rm dataguard-qa
```

## 10) Reports
- Allure results land in `reports/allure-results/`. To view locally:
  ```bash
  allure serve reports/allure-results
  ```

## 11) CI
- GitHub Actions workflow `.github/workflows/ci.yml` runs lint/format/type, ETL (SQLite), GX checkpoint, and Postgres job with service DB.

## 12) Troubleshooting
- Ensure Docker is running before Postgres/testcontainers jobs.
- If mypy complains about missing stubs, ensure venv is active and deps installed.
- Remove stale SQLite artifacts: `rm -f *.db *.db-shm *.db-wal *.sqlite*`.
- Regenerate medium dataset if needed: `python tests/fixtures/etl/medium/generate_medium_dataset.py` (file is git-ignored).
