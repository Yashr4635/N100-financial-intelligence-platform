import sqlite3


def test_database_exists():
    import os

    assert os.path.exists("database/nifty100.db")


def test_companies_count():
    conn = sqlite3.connect("database/nifty100.db")

    count = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]

    conn.close()

    assert count == 92
