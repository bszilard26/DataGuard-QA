PYTHON ?= python
PIP ?= pip
PYTEST ?= pytest

VENV_BIN ?= venv/bin
ACTIVATE = source $(VENV_BIN)/activate

.PHONY: install etl etl-medium etl-pg etl-all

install:
	$(PYTHON) -m venv venv
	$(ACTIVATE) && $(PIP) install -r requirements.txt

etl:
	$(ACTIVATE) && PYTHONPATH=. $(PYTEST) tests/etl/test_etl_data_validation.py

etl-medium:
	$(ACTIVATE) && PYTHONPATH=. RUN_MEDIUM_ETL=1 $(PYTEST) tests/etl/test_etl_data_validation.py::test_etl_medium_dataset

etl-pg:
	$(ACTIVATE) && PYTHONPATH=. RUN_PG_ETL=1 $(PYTEST) tests/etl/test_etl_postgres.py

etl-all:
	$(ACTIVATE) && PYTHONPATH=. RUN_MEDIUM_ETL=1 RUN_PG_ETL=1 $(PYTEST) tests/etl

.PHONY: format lint type gx allure allure-serve clean

format:
	$(ACTIVATE) && black .

lint:
	$(ACTIVATE) && ruff check .

type:
	$(ACTIVATE) && mypy --ignore-missing-imports .

gx:
	$(ACTIVATE) && PYTHONPATH=. python scripts/run_etl.py tests/fixtures/etl/tiny/customers_tiny.csv /tmp/etl_gx.db etl/schema_sqlite.sql tests/fixtures/etl/dim_countries.csv && PYTHONPATH=. python expectations/gx_tiny_checkpoint.py /tmp/etl_gx.db

allure:
	$(ACTIVATE) && PYTHONPATH=. $(PYTEST) tests/etl --alluredir reports/allure-results

allure-serve:
	$(ACTIVATE) && allure serve reports/allure-results

clean:
	rm -rf reports/allure-results reports/allure-report .pytest_cache .ruff_cache .mypy_cache .coverage htmlcov
	rm -f customers_medium.csv *.db *.db-shm *.db-wal *.sqlite *.sqlite3
