import os

import pytest
from sqlalchemy import create_engine
from testcontainers.postgres import PostgresContainer

from etl.pipeline_sa import run_customer_etl_engine
from utils.db_utils import apply_sql_file_engine, get_country_codes_engine, load_csv_engine

RUN_PG = os.getenv("RUN_PG_ETL", "0") == "1"
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCHEMA_PG = os.path.join(REPO_ROOT, "etl", "schema_postgres.sql")
DIM_COUNTRIES = os.path.join(REPO_ROOT, "tests", "fixtures", "etl", "dim_countries.csv")
TINY_CUSTOMERS = os.path.join(REPO_ROOT, "tests", "fixtures", "etl", "tiny", "customers_tiny.csv")


@pytest.mark.skipif(not RUN_PG, reason="set RUN_PG_ETL=1 to enable Postgres ETL tests")
class TestPostgresETL:
    @pytest.fixture(scope="class")
    def pg_engine(self):
        with PostgresContainer("postgres:16-alpine") as pg:
            engine = create_engine(pg.get_connection_url())
            apply_sql_file_engine(engine, SCHEMA_PG)
            load_csv_engine(engine, "dim_country", DIM_COUNTRIES)
            yield engine
            engine.dispose()

    def test_pg_etl_happy(self, pg_engine):
        country_codes = get_country_codes_engine(pg_engine)
        metrics = run_customer_etl_engine(
            pg_engine, TINY_CUSTOMERS, country_codes, source_name="tiny_batch"
        )

        assert metrics.source_count == 10
        assert metrics.target_count == 4
        assert metrics.rejected_count == 6

    def test_pg_idempotent(self, pg_engine):
        country_codes = get_country_codes_engine(pg_engine)
        first_run = run_customer_etl_engine(
            pg_engine, TINY_CUSTOMERS, country_codes, source_name="tiny_batch"
        )
        second_run = run_customer_etl_engine(
            pg_engine, TINY_CUSTOMERS, country_codes, source_name="tiny_batch_repeat"
        )

        assert first_run.target_count == 4
        assert second_run.target_count == 4

        with pg_engine.begin() as conn:
            emails = conn.execute("SELECT email FROM target_customers").fetchall()
        assert len(emails) == 4
        assert len({e[0] for e in emails}) == 4
