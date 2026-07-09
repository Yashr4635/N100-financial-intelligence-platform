import sqlite3
from pathlib import Path

from src.utils.config import DATABASE_PATH


class DatabaseManager:
    """
    Handles SQLite database operations.
    """

    def __init__(self):
        self.connection = sqlite3.connect(DATABASE_PATH)

    def save_datasets(self, datasets: dict):

        print("\n" + "=" * 70)
        print("LOADING DATA INTO SQLITE")
        print("=" * 70)

        for name, df in datasets.items():

            df.to_sql(
                name,
                self.connection,
                if_exists="replace",
                index=False
            )

            print(f"✓ {name:<20} -> {len(df)} rows")

        print("=" * 70)
        print("SQLite database created successfully.")
        print("=" * 70)

    def close(self):
        self.connection.close()