import pandas as pd
from pathlib import Path


class DataValidator:

    def __init__(self, datasets):
        self.datasets = datasets
        self.failures = []

    def log_failure(self, dataset, rule, message):
        self.failures.append({"dataset": dataset, "rule": rule, "message": message})

    def validate(self):

        print("\n" + "=" * 70)
        print("DATA VALIDATION")
        print("=" * 70)

        for name, df in self.datasets.items():

            print(f"\n{name}")

            try:
                # Rule 1: empty dataset
                if df.empty:
                    self.log_failure(name, "DQ-01", "Dataset is empty")

                # Rule 2: duplicate rows
                dup_rows = df.duplicated().sum()
                if dup_rows > 0:
                    self.log_failure(name, "DQ-02", f"{dup_rows} duplicate rows")

                # Rule 3: duplicate columns
                dup_cols = df.columns.duplicated().sum()
                if dup_cols > 0:
                    self.log_failure(name, "DQ-03", f"{dup_cols} duplicate columns")

                # Rule 4: blank column names
                blank_cols = sum(str(c).strip() == "" for c in df.columns)
                if blank_cols > 0:
                    self.log_failure(name, "DQ-04", f"{blank_cols} blank columns")

                # Rule 5: missing values
                missing = df.isna().sum().sum()
                if missing > 0:
                    self.log_failure(name, "DQ-05", f"{missing} missing values")

                # Rule 6: duplicate company_id
                if "company_id" in df.columns:
                    dup = df["company_id"].duplicated().sum()
                    if dup > 0:
                        self.log_failure(name, "DQ-06", f"{dup} duplicate company ids")

                # Rule 7: duplicate company_id/year combo
                if "company_id" in df.columns and "year" in df.columns:
                    dup = df.duplicated(subset=["company_id", "year"]).sum()
                    if dup > 0:
                        self.log_failure(name, "DQ-07", f"{dup} duplicate company/year")

                # Rule 8: invalid year range
                if "year" in df.columns:
                    years = pd.to_numeric(df["year"], errors="coerce")
                    bad = years[(years < 1990) | (years > 2035)]
                    if len(bad) > 0:
                        self.log_failure(name, "DQ-08", f"{len(bad)} invalid years")

                # Rule 9: mandatory company_id
                if "company_id" in df.columns:
                    missing_ids = df["company_id"].isna().sum()
                    if missing_ids > 0:
                        self.log_failure(
                            name, "DQ-09", f"{missing_ids} missing company_id"
                        )

                # Rule 10: mandatory year
                if "year" in df.columns:
                    missing_years = df["year"].isna().sum()
                    if missing_years > 0:
                        self.log_failure(
                            name, "DQ-10", f"{missing_years} missing years"
                        )

                # Rule 11: negative sales
                if "sales" in df.columns:
                    sales = pd.to_numeric(df["sales"], errors="coerce")
                    bad = (sales < 0).sum()
                    if bad > 0:
                        self.log_failure(name, "DQ-11", f"{bad} negative sales")

                # Rule 12: negative assets
                if "total_assets" in df.columns:
                    assets = pd.to_numeric(df["total_assets"], errors="coerce")
                    bad = (assets < 0).sum()
                    if bad > 0:
                        self.log_failure(name, "DQ-12", f"{bad} negative assets")

                # Rule 13: negative liabilities
                if "total_liabilities" in df.columns:
                    liab = pd.to_numeric(df["total_liabilities"], errors="coerce")
                    bad = (liab < 0).sum()
                    if bad > 0:
                        self.log_failure(name, "DQ-13", f"{bad} negative liabilities")

                # Rule 14: negative close price
                if "close_price" in df.columns:
                    close = pd.to_numeric(df["close_price"], errors="coerce")
                    bad = (close < 0).sum()
                    if bad > 0:
                        self.log_failure(name, "DQ-14", f"{bad} negative close prices")

                # Rule 15: negative volume
                if "volume" in df.columns:
                    volume = pd.to_numeric(df["volume"], errors="coerce")
                    bad = (volume < 0).sum()
                    if bad > 0:
                        self.log_failure(name, "DQ-15", f"{bad} negative volume")

                # Rule 16: duplicate primary id
                if "id" in df.columns:
                    dup = df["id"].duplicated().sum()
                    if dup > 0:
                        self.log_failure(name, "DQ-16", f"{dup} duplicate ids")

            except Exception as e:
                self.log_failure(name, "SYSTEM", str(e))

        self.save_report()

    def save_report(self):
        try:
            report = pd.DataFrame(self.failures)

            Path("reports").mkdir(exist_ok=True)

            report.to_csv("reports/validation_failures.csv", index=False)

            print("\nValidation report saved.")
        except Exception as e:
            raise RuntimeError(f"Validation failed: {e}")
