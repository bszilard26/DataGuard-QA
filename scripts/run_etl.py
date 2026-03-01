import argparse
import json
from pathlib import Path

from etl.pipeline import run_customer_etl
from utils.db_utils import apply_sql_file, get_country_codes, get_sqlite_connection, load_csv


def main():
    parser = argparse.ArgumentParser(description="Run customer ETL against a SQLite DB")
    parser.add_argument("csv", help="Path to customer CSV input")
    parser.add_argument("db", help="Path to SQLite db file (will be created if missing)")
    parser.add_argument("schema", help="Path to schema SQL file")
    parser.add_argument("countries", help="Path to dim_country CSV")
    parser.add_argument("--source", default="cli_batch", help="Source name to store in metrics")
    args = parser.parse_args()

    db_path = Path(args.db)
    conn = get_sqlite_connection(str(db_path))
    apply_sql_file(conn, args.schema)
    load_csv(conn, "dim_country", args.countries)

    country_codes = get_country_codes(conn)
    metrics = run_customer_etl(conn, args.csv, country_codes, source_name=args.source)
    result = {
        "source_count": metrics.source_count,
        "target_count": metrics.target_count,
        "rejected_count": metrics.rejected_count,
    }
    print(json.dumps(result, indent=2))
    conn.close()


if __name__ == "__main__":
    main()
