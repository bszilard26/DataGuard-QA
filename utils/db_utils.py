from collections.abc import Iterable
from pathlib import Path
import re
import sqlite3

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _ensure_safe_identifier(identifier: str) -> str:
    if not IDENTIFIER_RE.fullmatch(identifier):
        raise ValueError(f"Unsafe identifier: {identifier}")
    return identifier


def get_sqlite_connection(
    db_path: str = ":memory:", enable_foreign_keys: bool = True
) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    if enable_foreign_keys:
        conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_sqlite_engine(db_path: str = ":memory:", enable_foreign_keys: bool = True) -> Engine:
    engine = create_engine(f"sqlite:///{db_path}")
    if enable_foreign_keys:
        with engine.begin() as conn:
            conn.execute(text("PRAGMA foreign_keys = ON"))
    return engine


def apply_sql_file(conn: sqlite3.Connection, sql_path: str) -> None:
    sql_text = Path(sql_path).read_text()
    conn.executescript(sql_text)


def apply_sql_file_engine(engine: Engine, sql_path: str) -> None:
    sql_text = Path(sql_path).read_text()
    statements = [stmt.strip() for stmt in sql_text.split(";") if stmt.strip()]
    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))


def load_csv(
    conn: sqlite3.Connection, table: str, csv_path: str, if_exists: str = "append"
) -> None:
    df = pd.read_csv(csv_path)
    safe_table = _ensure_safe_identifier(table)
    if if_exists == "append":
        conn.execute(f"DELETE FROM {safe_table}")  # noqa: S608
    df.to_sql(safe_table, conn, if_exists=if_exists, index=False)


def load_csv_engine(engine: Engine, table: str, csv_path: str, if_exists: str = "append") -> None:
    df = pd.read_csv(csv_path)
    safe_table = _ensure_safe_identifier(table)
    if if_exists == "append":
        with engine.begin() as conn:
            conn.execute(text(f"DELETE FROM {safe_table}"))  # noqa: S608
    df.to_sql(safe_table, engine, if_exists=if_exists, index=False)


def get_country_codes(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("SELECT code FROM dim_country").fetchall()
    return {row[0] for row in rows}


def get_country_codes_engine(engine: Engine) -> set[str]:
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT code FROM dim_country")).fetchall()
    return {row[0] for row in rows}


def truncate_tables(conn: sqlite3.Connection, tables: Iterable[str]) -> None:
    for table in tables:
        safe_table = _ensure_safe_identifier(table)
        conn.execute(f"DELETE FROM {safe_table}")  # noqa: S608
    conn.commit()


def truncate_tables_engine(engine: Engine, tables: Iterable[str]) -> None:
    with engine.begin() as conn:
        for table in tables:
            safe_table = _ensure_safe_identifier(table)
            conn.execute(text(f"DELETE FROM {safe_table}"))  # noqa: S608
