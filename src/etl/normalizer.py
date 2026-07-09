import pandas as pd


class DataNormalizer:
    """
    Cleans and standardizes all datasets.
    """

    def __init__(self, datasets: dict):
        self.datasets = datasets

    @staticmethod
    def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("-", "_")
        )
        return df

    @staticmethod
    def clean_company_id(df: pd.DataFrame) -> pd.DataFrame:

        if "company_id" in df.columns:
            df["company_id"] = (
                df["company_id"]
                .astype(str)
                .str.strip()
                .str.upper()
            )

        if "id" in df.columns:
            df["id"] = (
                df["id"]
                .astype(str)
                .str.strip()
                .str.upper()
            )

        return df

    @staticmethod
    def clean_year(df: pd.DataFrame) -> pd.DataFrame:

        if "year" not in df.columns:
            return df

        df["year"] = (
            df["year"]
            .astype(str)
            .str.extract(r'(\d{2,4})')[0]
        )

        return df

    @staticmethod
    def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
        return df.drop_duplicates()

    def normalize(self):

        cleaned = {}

        print("\n" + "=" * 70)
        print("NORMALIZING DATASETS")
        print("=" * 70)

        for name, df in self.datasets.items():

            original_rows = len(df)

            df = self.clean_column_names(df)
            df = self.clean_company_id(df)
            df = self.clean_year(df)
            df = self.remove_duplicates(df)

            cleaned_rows = len(df)

            print(
                f"{name:<20}"
                f"Rows: {original_rows:>5} -> {cleaned_rows:<5}"
                f" Columns: {len(df.columns)}"
            )

            cleaned[name] = df

        print("=" * 70)

        return cleaned