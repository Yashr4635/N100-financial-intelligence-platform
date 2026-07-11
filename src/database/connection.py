import sqlite3
import pandas as pd
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

        audit = []

        for name, df in datasets.items():

            df.to_sql(
                name,
                self.connection,
                if_exists="replace",
                index=False
            )

            audit.append({
                "dataset": name,
                "rows_loaded": len(df),
                "columns": len(df.columns),
                "status": "SUCCESS"
            })

            print(f"✓ {name:<20} -> {len(df)} rows")

        Path("reports").mkdir(exist_ok=True)

        audit_df = pd.DataFrame(audit)

        audit_df.to_csv(
            "reports/load_audit.csv",
            index=False
        )

        print("=" * 70)
        print("SQLite database created successfully.")
        print("Load audit saved to reports/load_audit.csv")
        print("=" * 70)

    def close(self):
        self.connection.close()