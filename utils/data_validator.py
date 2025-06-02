# utils/data_validator.py

import sqlite3

class DataValidator:

    def __init__(self, db_path="etl_sample.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def compare_row_counts(self, table1, table2):
        self.cursor.execute(f"SELECT COUNT(*) FROM {table1}")
        count1 = self.cursor.fetchone()[0]
        self.cursor.execute(f"SELECT COUNT(*) FROM {table2}")
        count2 = self.cursor.fetchone()[0]
        return count1 == count2

    def check_nulls(self, table, column):
        self.cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} IS NULL")
        return self.cursor.fetchone()[0] == 0

    def check_duplicates(self, table, column):
        self.cursor.execute(f"""
            SELECT {column}, COUNT(*) 
            FROM {table} 
            GROUP BY {column} 
            HAVING COUNT(*) > 1
        """)
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
