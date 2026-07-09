import pandas as pd


class DataValidator:
    """
    Performs basic data quality validation.
    """

    def __init__(self, datasets: dict):
        self.datasets = datasets

    def validate(self):
        print("\n" + "=" * 70)
        print("DATA VALIDATION REPORT")
        print("=" * 70)

        for name, df in self.datasets.items():

            duplicate_rows = df.duplicated().sum()
            missing_values = df.isna().sum().sum()
            duplicate_columns = df.columns.duplicated().sum()
            blank_columns = sum(
                str(col).strip() == "" for col in df.columns
            )

            print(f"\n{name.upper()}")
            print("-" * 40)
            print(f"Rows               : {len(df)}")
            print(f"Columns            : {len(df.columns)}")
            print(f"Duplicate Rows     : {duplicate_rows}")
            print(f"Missing Values     : {missing_values}")
            print(f"Duplicate Columns  : {duplicate_columns}")
            print(f"Blank Columns      : {blank_columns}")

        print("\n" + "=" * 70)