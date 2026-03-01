import json
import os

import allure
import pandas as pd
import pandas.testing as pdt
import pytest

from etl.pipeline import ALLOWED_STATUS, run_customer_etl
from utils.data_validator import DataValidator

RUN_MEDIUM = os.getenv("RUN_MEDIUM_ETL", "0") == "1"


def test_etl_happy_path_and_rejections(sqlite_conn, sqlite_db_path, country_codes, tiny_csv_path):
    with allure.step("Run ETL for tiny batch"):
        metrics = run_customer_etl(
            sqlite_conn, tiny_csv_path, country_codes, source_name="tiny_batch"
        )

    assert metrics.source_count == 10
    assert metrics.target_count == 4
    assert metrics.rejected_count == 6

    john_age, john_first = sqlite_conn.execute(
        "SELECT age, first_name FROM target_customers WHERE email = ?",
        ("john.doe@example.com",),
    ).fetchone()
    assert john_age == 36
    assert john_first == "Duplicate"

    reject_reasons = {
        row[0] for row in sqlite_conn.execute("SELECT reason FROM rejected_rows").fetchall()
    }
    expected_reasons = {
        "duplicate_email_newer_record_kept",
        "missing_email",
        "full_name_incomplete",
        "age_out_of_range",
        "invalid_email_format",
        "invalid_country_code",
    }
    assert expected_reasons.issubset(reject_reasons)

    # Attach samples for reporting
    target_df = pd.read_sql_query("SELECT * FROM target_customers", sqlite_conn)
    rejects_df = pd.read_sql_query("SELECT * FROM rejected_rows", sqlite_conn)
    allure.attach(
        target_df.to_csv(index=False),
        name="target_customers.csv",
        attachment_type=allure.attachment_type.CSV,
    )
    allure.attach(
        rejects_df.to_csv(index=False),
        name="rejected_rows.csv",
        attachment_type=allure.attachment_type.CSV,
    )

    with allure.step("Validate target table quality rules"):
        validator = DataValidator(sqlite_db_path)
        assert validator.check_nulls(
            "target_customers",
            [
                "email",
                "first_name",
                "last_name",
                "age",
                "status",
                "country_code",
            ],
        ).passed
        assert validator.check_domain("target_customers", "status", ALLOWED_STATUS).passed
        assert validator.check_range("target_customers", "age", 18, 120).passed
        assert validator.check_fk_integrity(
            "target_customers", "country_code", "dim_country", "code"
        ).passed
        validator.close()


def test_etl_golden_snapshot(sqlite_conn, sqlite_db_path, country_codes, tiny_csv_path):
    run_customer_etl(sqlite_conn, tiny_csv_path, country_codes, source_name="tiny_batch")

    target_df = pd.read_sql_query(
        (
            "SELECT email, first_name, last_name, age, status, country_code, updated_at, "
            "source_file FROM target_customers ORDER BY email"
        ),
        sqlite_conn,
    )
    golden_df = (
        pd.read_csv("tests/fixtures/etl/golden/target_tiny.csv")
        .sort_values("email")
        .reset_index(drop=True)
    )

    allure.attach(
        target_df.to_csv(index=False),
        name="target_after_run.csv",
        attachment_type=allure.attachment_type.CSV,
    )
    pdt.assert_frame_equal(target_df.reset_index(drop=True), golden_df)

    validator = DataValidator(sqlite_db_path)
    fk_ok = validator.check_fk_integrity("target_customers", "country_code", "dim_country", "code")
    assert fk_ok.passed
    validator.close()


def test_etl_drift_metrics(sqlite_conn, country_codes, tiny_csv_path):
    run_customer_etl(sqlite_conn, tiny_csv_path, country_codes, source_name="tiny_batch")

    target_count = sqlite_conn.execute("SELECT COUNT(*) FROM target_customers").fetchone()[0]
    rejected_count = sqlite_conn.execute("SELECT COUNT(*) FROM rejected_rows").fetchone()[0]
    status_counts = dict(
        sqlite_conn.execute(
            "SELECT status, COUNT(*) FROM target_customers GROUP BY status"
        ).fetchall()
    )
    reject_reasons = dict(
        sqlite_conn.execute("SELECT reason, COUNT(*) FROM rejected_rows GROUP BY reason").fetchall()
    )

    with open("tests/fixtures/etl/golden/metrics_tiny.json") as f:
        baseline = json.load(f)

    allure.attach(
        json.dumps(
            {
                "target_row_count": target_count,
                "rejected_row_count": rejected_count,
                "status_counts": status_counts,
                "reject_reasons": reject_reasons,
            },
            indent=2,
        ),
        name="drift_metrics.json",
        attachment_type=allure.attachment_type.JSON,
    )

    assert target_count == baseline["target_row_count"]
    assert rejected_count == baseline["rejected_row_count"]
    assert status_counts == baseline["status_counts"]
    assert reject_reasons == baseline["reject_reasons"]


def test_fk_orphan_detection(sqlite_conn, sqlite_db_path, country_codes, tiny_csv_path):
    run_customer_etl(sqlite_conn, tiny_csv_path, country_codes, source_name="tiny_batch")

    # simulate orphan by temporarily disabling FK checks, then re-enabling
    sqlite_conn.execute("PRAGMA foreign_keys = OFF")
    sqlite_conn.execute("DELETE FROM dim_country WHERE code = 'US'")
    sqlite_conn.execute("PRAGMA foreign_keys = ON")
    sqlite_conn.commit()

    validator = DataValidator(sqlite_db_path)
    fk_result = validator.check_fk_integrity(
        "target_customers", "country_code", "dim_country", "code"
    )
    assert not fk_result.passed
    validator.close()


def test_etl_idempotent(sqlite_conn, sqlite_db_path, country_codes, tiny_csv_path):
    first_run = run_customer_etl(
        sqlite_conn, tiny_csv_path, country_codes, source_name="tiny_batch"
    )
    second_run = run_customer_etl(
        sqlite_conn, tiny_csv_path, country_codes, source_name="tiny_batch_repeat"
    )

    assert first_run.target_count == 4
    assert second_run.target_count == 4

    target_rows = sqlite_conn.execute("SELECT email FROM target_customers").fetchall()
    assert len(target_rows) == 4
    assert len({email for (email,) in target_rows}) == 4


@pytest.mark.skipif(not RUN_MEDIUM, reason="set RUN_MEDIUM_ETL=1 to run medium dataset")
def test_etl_medium_dataset(sqlite_conn, sqlite_db_path, country_codes, medium_csv_path):
    metrics = run_customer_etl(
        sqlite_conn, medium_csv_path, country_codes, source_name="medium_batch"
    )

    assert metrics.target_count >= 700
    assert metrics.rejected_count > 0

    validator = DataValidator(sqlite_db_path)
    assert validator.check_domain("target_customers", "status", ALLOWED_STATUS).passed
    assert validator.check_range("target_customers", "age", 18, 120).passed
    validator.close()
