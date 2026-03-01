from pathlib import Path

import pytest

from tests.fixtures.etl.medium.generate_medium_dataset import main as generate_medium
from utils.db_utils import (
    apply_sql_file,
    get_country_codes,
    get_sqlite_connection,
    load_csv,
    truncate_tables,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_SQLITE = REPO_ROOT / "etl" / "schema_sqlite.sql"
DIM_COUNTRIES = REPO_ROOT / "tests" / "fixtures" / "etl" / "dim_countries.csv"
TINY_CUSTOMERS = REPO_ROOT / "tests" / "fixtures" / "etl" / "tiny" / "customers_tiny.csv"


@pytest.fixture
def sqlite_conn(tmp_path):
    db_path = tmp_path / "etl.db"
    conn = get_sqlite_connection(str(db_path))
    apply_sql_file(conn, str(SCHEMA_SQLITE))
    load_csv(conn, "dim_country", str(DIM_COUNTRIES))
    yield conn
    conn.close()


@pytest.fixture
def country_codes(sqlite_conn):
    return get_country_codes(sqlite_conn)


@pytest.fixture
def tiny_csv_path():
    return str(TINY_CUSTOMERS)


@pytest.fixture
def medium_csv_path(tmp_path):
    out_path = tmp_path / "customers_medium.csv"
    generate_medium(rows=1000, out_path=str(out_path))
    return str(out_path)


@pytest.fixture
def sqlite_db_path(tmp_path):
    return str(tmp_path / "etl.db")


@pytest.fixture(autouse=True)
def clean_tables(sqlite_conn):
    yield
    truncate_tables(
        sqlite_conn, ["staging_customers", "target_customers", "rejected_rows", "etl_run_metrics"]
    )
