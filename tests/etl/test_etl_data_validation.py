import sqlite3

def test_data_transformation():
    conn = sqlite3.connect("etl_sample.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM target_table")
    count = cursor.fetchone()[0]
    assert count > 0
    conn.close()
