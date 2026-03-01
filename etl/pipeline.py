from dataclasses import dataclass
from datetime import UTC, datetime
import re
from typing import Any

import pandas as pd

ALLOWED_STATUS = {"active", "inactive", "pending"}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class ETLMetrics:
    source_count: int
    target_count: int
    rejected_count: int
    notes: str | None = None


def split_full_name(full_name: str) -> tuple[str | None, str | None]:
    if not isinstance(full_name, str):
        return None, None
    parts = full_name.strip().split()
    if len(parts) < 2:
        return None, None
    return parts[0], " ".join(parts[1:])


def normalize_email(email: str | None) -> str | None:
    if email is None or pd.isna(email):
        return None
    cleaned = str(email).strip().lower()
    return cleaned if cleaned else None


def validate_and_clean(
    df: pd.DataFrame, country_codes: set[str]
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    rejects: list[dict[str, Any]] = []

    if df.empty:
        return df, rejects

    df = df.copy()
    df["email"] = df["email"].apply(normalize_email)
    df["updated_at_ts"] = pd.to_datetime(df["updated_at"], errors="coerce", utc=True)

    df_sorted = df.sort_values(["updated_at_ts"], ascending=False)
    duplicate_mask = df_sorted.duplicated(subset=["email"], keep="first")
    duplicate_rows = df_sorted[duplicate_mask]
    base_df = df_sorted[~duplicate_mask]

    for _, row in duplicate_rows.iterrows():
        rejects.append(_reject_record(row, "duplicate_email_newer_record_kept"))

    cleaned_rows = []
    for _, row in base_df.iterrows():
        email = row.get("email")
        full_name = row.get("full_name")
        age = row.get("age")
        status = row.get("status")
        country_code = row.get("country_code")
        updated_at_ts = row.get("updated_at_ts")

        if not isinstance(email, str) or not email:
            rejects.append(_reject_record(row, "missing_email"))
            continue
        if not EMAIL_RE.match(email):
            rejects.append(_reject_record(row, "invalid_email_format"))
            continue

        first_name, last_name = split_full_name(full_name)
        if not first_name or not last_name:
            rejects.append(_reject_record(row, "full_name_incomplete"))
            continue

        try:
            age_int = int(age)
        except (TypeError, ValueError):
            rejects.append(_reject_record(row, "invalid_age_value"))
            continue
        if age_int < 18 or age_int > 120:
            rejects.append(_reject_record(row, "age_out_of_range"))
            continue

        if status not in ALLOWED_STATUS:
            rejects.append(_reject_record(row, "invalid_status"))
            continue

        if country_code not in country_codes:
            rejects.append(_reject_record(row, "invalid_country_code"))
            continue

        if pd.isna(updated_at_ts):
            rejects.append(_reject_record(row, "invalid_updated_at"))
            continue

        cleaned_rows.append(
            {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "age": age_int,
                "status": status,
                "country_code": country_code,
                "updated_at": updated_at_ts.isoformat(),
                "source_file": row.get("_source_file"),
            }
        )

    return pd.DataFrame(cleaned_rows), rejects


def _reject_record(row: pd.Series, reason: str) -> dict[str, Any]:
    return {
        "source_table": "staging_customers",
        "raw_full_name": row.get("full_name"),
        "raw_email": row.get("email"),
        "raw_age": row.get("age"),
        "raw_status": row.get("status"),
        "raw_country_code": row.get("country_code"),
        "raw_updated_at": row.get("updated_at"),
        "reason": reason,
    }


def upsert_clean_rows(conn, cleaned_df: pd.DataFrame) -> int:
    if cleaned_df.empty:
        return 0
    rows_inserted = 0
    sql = """
        INSERT INTO target_customers (
            email, first_name, last_name, age, status, country_code, updated_at, source_file
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET
            first_name=excluded.first_name,
            last_name=excluded.last_name,
            age=excluded.age,
            status=excluded.status,
            country_code=excluded.country_code,
            updated_at=excluded.updated_at,
            source_file=excluded.source_file
        WHERE excluded.updated_at > target_customers.updated_at
        """
    for _, row in cleaned_df.iterrows():
        conn.execute(
            sql,
            (
                row["email"],
                row["first_name"],
                row["last_name"],
                row["age"],
                row["status"],
                row["country_code"],
                row["updated_at"],
                row.get("source_file"),
            ),
        )
        rows_inserted += 1
    conn.commit()
    return rows_inserted


def persist_rejects(conn, rejects: list[dict[str, Any]]) -> int:
    if not rejects:
        return 0
    conn.executemany(
        """
        INSERT INTO rejected_rows (
            source_table,
            raw_full_name,
            raw_email,
            raw_age,
            raw_status,
            raw_country_code,
            raw_updated_at,
            reason
        ) VALUES (
            :source_table,
            :raw_full_name,
            :raw_email,
            :raw_age,
            :raw_status,
            :raw_country_code,
            :raw_updated_at,
            :reason
        )
        """,
        rejects,
    )
    conn.commit()
    return len(rejects)


def load_staging_from_csv(conn, csv_path: str, source_file: str | None = None) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["_source_file"] = source_file or csv_path
    conn.execute("DELETE FROM staging_customers")
    df.to_sql("staging_customers", conn, if_exists="append", index=False)
    return df


def run_customer_etl(
    conn, csv_path: str, country_codes: set[str], source_name: str = "batch"
) -> ETLMetrics:
    staging_df = load_staging_from_csv(conn, csv_path, source_file=source_name)
    cleaned_df, rejects = validate_and_clean(staging_df, country_codes)

    upsert_clean_rows(conn, cleaned_df)
    rejected = persist_rejects(conn, rejects)

    target_count = _scalar(conn, "SELECT COUNT(*) FROM target_customers")
    conn.execute(
        """
        INSERT INTO etl_run_metrics (
            run_at,
            source_count,
            target_count,
            rejected_count,
            notes
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            datetime.now(UTC).isoformat(),
            len(staging_df),
            target_count,
            rejected,
            source_name,
        ),
    )
    conn.commit()
    return ETLMetrics(
        source_count=len(staging_df),
        target_count=target_count,
        rejected_count=rejected,
        notes=source_name,
    )


def _scalar(conn, query: str) -> int:
    return int(conn.execute(query).fetchone()[0])
