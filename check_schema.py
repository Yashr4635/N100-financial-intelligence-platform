import sqlite3
from src.utils.config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)

tables = [
    "profitandloss",
    "balancesheet",
    "cashflow"
]

for table in tables:
    print("\n" + "=" * 60)
    print(table.upper())
    print("=" * 60)

    cursor = conn.execute(f"PRAGMA table_info({table});")

    for row in cursor.fetchall():
        print(row)

conn.close()