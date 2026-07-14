from typing import Dict

import pandas as pd

from src.utils.config import RAW_DATA_DIR

# Files that contain metadata in the first row
CORE_DATASETS = {
    "companies",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "analysis",
    "documents",
    "prosandcons",
}


class ExcelLoader:
    """
    Production-ready Excel Loader
    """

    def __init__(self):
        self.datasets = {}

    def load_all(self) -> Dict[str, pd.DataFrame]:
        excel_files = sorted(RAW_DATA_DIR.glob("*.xlsx"))

        print("\n" + "=" * 70)
        print("N100 FINANCIAL INTELLIGENCE PLATFORM")
        print("Loading datasets...")
        print("=" * 70)

        for file in excel_files:

            header = 1 if file.stem in CORE_DATASETS else 0

            try:
                df = pd.read_excel(file, header=header)
            except FileNotFoundError:
                print(f"[✗] {file.name} -> Dataset not found: {file}")
                continue
            except Exception as e:
                print(f"[✗] {file.name} -> Failed to load: {e}")
                continue

            self.datasets[file.stem] = df

            print(
                f"[✓] {file.name:<25}"
                f" Rows: {df.shape[0]:>5}"
                f" Cols: {df.shape[1]:>3}"
                f" Header={header}"
            )

        print("=" * 70)
        print(f"Loaded {len(self.datasets)} datasets successfully.")
        print("=" * 70)

        return self.datasets
