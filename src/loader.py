from pathlib import Path
import pandas as pd

from src.config import RAW_DATA_DIR


class ExcelLoader:
    """
    Loads all Excel datasets from the raw data directory.
    """

    def __init__(self):
        self.dataframes = {}

    def load_all(self):
        excel_files = sorted(RAW_DATA_DIR.glob("*.xlsx"))

        if not excel_files:
            raise FileNotFoundError("No Excel files found in data/raw")

        print("\nLoading datasets...\n")

        for file in excel_files:
            try:
                df = pd.read_excel(file)

                self.dataframes[file.stem] = df

                print(
                    f"Loaded {file.name:<25}"
                    f" Rows: {df.shape[0]:>5}"
                    f" Columns: {df.shape[1]:>3}"
                )

            except Exception as e:
                print(f"Failed to load {file.name}: {e}")

        print("\nFinished loading datasets.\n")

        return self.dataframes