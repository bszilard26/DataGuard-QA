# utils/data_validator.py
# ruff: noqa: S608

from collections.abc import Iterable
from dataclasses import dataclass
import re
import sqlite3
from typing import Any

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass
class ValidationResult:
    passed: bool
    details: Any


class DataValidator:
    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn.cursor()

    def _ensure_safe_identifier(self, identifier: str) -> str:
        if not IDENTIFIER_RE.fullmatch(identifier):
            raise ValueError(f"Unsafe identifier: {identifier}")
        return identifier

    def compare_row_counts(self, table1: str, table2: str) -> ValidationResult:
        safe_table1 = self._ensure_safe_identifier(table1)
        safe_table2 = self._ensure_safe_identifier(table2)
        count1 = self._scalar(f"SELECT COUNT(*) FROM {safe_table1}")  # noqa: S608
        count2 = self._scalar(f"SELECT COUNT(*) FROM {safe_table2}")  # noqa: S608
        return ValidationResult(
            passed=count1 == count2, details={"table1": count1, "table2": count2}
        )

    def check_nulls(self, table: str, columns: Iterable[str]) -> ValidationResult:
        safe_table = self._ensure_safe_identifier(table)
        results = {}
        for col in columns:
            safe_col = self._ensure_safe_identifier(col)
            count = self._scalar(
                f"SELECT COUNT(*) FROM {safe_table} WHERE {safe_col} IS NULL"  # noqa: S608
            )
            results[col] = count
        passed = all(count == 0 for count in results.values())
        return ValidationResult(passed=passed, details=results)

    def check_duplicates(self, table: str, column: str) -> ValidationResult:
        safe_table = self._ensure_safe_identifier(table)
        safe_column = self._ensure_safe_identifier(column)
        rows = self.cursor.execute(  # noqa: S608
            f"""
            SELECT {safe_column}, COUNT(*) as dupes
            FROM {safe_table}
            GROUP BY {safe_column}
            HAVING dupes > 1
            """
        ).fetchall()
        return ValidationResult(passed=len(rows) == 0, details=rows)

    def check_fk_integrity(
        self, table: str, fk_column: str, ref_table: str, ref_column: str
    ) -> ValidationResult:
        safe_table = self._ensure_safe_identifier(table)
        safe_fk = self._ensure_safe_identifier(fk_column)
        safe_ref_table = self._ensure_safe_identifier(ref_table)
        safe_ref_col = self._ensure_safe_identifier(ref_column)
        rows = self.cursor.execute(  # noqa: S608
            f"""
            SELECT t.{safe_fk}
            FROM {safe_table} t
            LEFT JOIN {safe_ref_table} r ON t.{safe_fk} = r.{safe_ref_col}
            WHERE r.{safe_ref_col} IS NULL
            """
        ).fetchall()
        return ValidationResult(passed=len(rows) == 0, details=rows)

    def check_domain(self, table: str, column: str, allowed: Iterable[str]) -> ValidationResult:
        safe_table = self._ensure_safe_identifier(table)
        safe_column = self._ensure_safe_identifier(column)
        allowed_list = list(allowed)
        placeholder = ",".join(["?"] * len(allowed_list))
        rows = self.cursor.execute(
            (
                f"SELECT DISTINCT {safe_column} FROM {safe_table} "  # noqa: S608
                f"WHERE {safe_column} NOT IN ({placeholder})"
            ),
            allowed_list,
        ).fetchall()
        return ValidationResult(passed=len(rows) == 0, details=rows)

    def check_range(
        self, table: str, column: str, min_value: int, max_value: int
    ) -> ValidationResult:
        safe_table = self._ensure_safe_identifier(table)
        safe_column = self._ensure_safe_identifier(column)
        rows = self.cursor.execute(
            f"SELECT {safe_column} FROM {safe_table} WHERE {safe_column} < ? OR {safe_column} > ?",  # noqa: S608
            (min_value, max_value),
        ).fetchall()
        return ValidationResult(passed=len(rows) == 0, details=rows)

    def check_email_format(self, table: str, column: str) -> ValidationResult:
        safe_table = self._ensure_safe_identifier(table)
        safe_column = self._ensure_safe_identifier(column)
        rows = self.cursor.execute(
            f"SELECT {safe_column} FROM {safe_table}"  # noqa: S608
        ).fetchall()
        invalid = [
            email for (email,) in rows if not isinstance(email, str) or not EMAIL_RE.match(email)
        ]
        return ValidationResult(passed=len(invalid) == 0, details=invalid)

    def close(self) -> None:
        self.conn.close()

    def _scalar(self, query: str, params: tuple | list | None = None) -> int:
        return int(self.cursor.execute(query, params or ()).fetchone()[0])
