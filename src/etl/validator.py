import pandas as pd
from pathlib import Path


class DataValidator:

    def __init__(self, datasets):
        self.datasets = datasets
        self.failures = []

    def log_failure(self, dataset, rule, message):
        self.failures.append({
            "dataset": dataset,
            "rule": rule,
            "message": message
        })

    def validate(self):

        print("\n" + "=" * 70)
        print("DATA VALIDATION")
        print("=" * 70)

        for name, df in self.datasets.items():

            print(f"\n{name}")

            try:
                # -------------------------
                # Rule 1
                # -------------------------
                if df.empty:
                    self.log_failure(name, "DQ-01", "Dataset is empty")

                # -------------------------
                # Rule 2
                # -------------------------
                dup_rows = df.duplicated().sum()

                if dup_rows > 0:
                    self.log_failure(
                        name,
                        "DQ-02",
                        f"{dup_rows} duplicate rows"
                    )

                # -------------------------
                # Rule 3
                # -------------------------
                dup_cols = df.columns.duplicated().sum()

                if dup_cols > 0:
                    self.log_failure(
                        name,
                        "DQ-03",
                        f"{dup_cols} duplicate columns"
                    )

                # -------------------------
                # Rule 4
                # -------------------------
                blank_cols = sum(
                    str(c).strip() == ""
                    for c in df.columns
                )

                if blank_cols > 0:
                    self.log_failure(
                        name,
                        "DQ-04",
                        f"{blank_cols} blank columns"
                    )

                # -------------------------
                # Rule 5
                # -------------------------
                missing = df.isna().sum().sum()

                if missing > 0:
                    self.log_failure(
                        name,
                        "DQ-05",
                        f"{missing} missing values"
                    )

                # -------------------------
                # Rule 6
                # -------------------------
                if "company_id" in df.columns:

                    dup = df["company_id"].duplicated().sum()

                    if dup > 0:
                        self.log_failure(
                            name,
                            "DQ-06",
                            f"{dup} duplicate company ids"
                        )

                # -------------------------
                # Rule 7
                # -------------------------
                if (
                    "company_id" in df.columns
                    and
                    "year" in df.columns
                ):

                    dup = df.duplicated(
                        subset=["company_id", "year"]
                    ).sum()

                    if dup > 0:
                        self.log_failure(
                            name,
                            "DQ-07",
                            f"{dup} duplicate company/year"
                        )

                # -------------------------
                # Rule 8
                # -------------------------
                if "year" in df.columns:

                    years = pd.to_numeric(
                        df["year"],
                        errors="coerce"
                    )

                    bad = years[
                        (years < 1990) |
                        (years > 2035)
                    ]

                    if len(bad) > 0:
                        self.log_failure(
                            name,
                            "DQ-08",
                            f"{len(bad)} invalid years"
                        )

            except Exception as e:

                self.log_failure(
                    name,
                    "SYSTEM",
                    str(e)
                )

        self.save_report()

    def save_report(self):

        report = pd.DataFrame(self.failures)

        Path("reports").mkdir(exist_ok=True)

        report.to_csv(
            "reports/validation_failures.csv",
            index=False
        )

        print("\nValidation report saved.")