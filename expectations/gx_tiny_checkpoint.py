import argparse
import sqlite3

import great_expectations as gx

REQUIRED_COLUMNS = [
    "email",
    "first_name",
    "last_name",
    "age",
    "status",
    "country_code",
    "updated_at",
]

ALLOWED_STATUS = {"active", "inactive", "pending"}


def build_dataset(conn: sqlite3.Connection):
    df = gx.from_pandas(
        __import__("pandas").read_sql_query(
            (
                "SELECT email, first_name, last_name, age, status, country_code, updated_at "
                "FROM target_customers"
            ),
            conn,
        )
    )
    return df


def run_checkpoint(db_path: str) -> bool:
    conn = sqlite3.connect(db_path)
    ds = build_dataset(conn)

    for col in REQUIRED_COLUMNS:
        ds.expect_column_values_to_not_be_null(col)
    ds.expect_column_values_to_be_unique("email")
    ds.expect_column_values_to_be_in_set("status", list(ALLOWED_STATUS))
    ds.expect_column_values_to_be_between("age", min_value=18, max_value=120)

    res = ds.validate()
    conn.close()
    return res.success


def main():
    parser = argparse.ArgumentParser(
        description="Run Great Expectations checks on target_customers"
    )
    parser.add_argument("db", help="Path to SQLite db")
    args = parser.parse_args()
    ok = run_checkpoint(args.db)
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
