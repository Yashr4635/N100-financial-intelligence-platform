import pandas as pd
import yaml
from pathlib import Path


class InvestmentScreener:
    """
    Filters fundamentally strong companies based on
    health score and financial quality.
    """

    def __init__(self, health_df: pd.DataFrame):
        self.df = health_df.copy()
        config_path = Path("config") / "screener_config.yaml"
        with config_path.open("r", encoding="utf-8") as config_file:
            self.config = yaml.safe_load(config_file) or {}

    def run(self, preset_name: str | None = None) -> pd.DataFrame:

        print("\n" + "=" * 70)
        print("INVESTMENT SCREENER")
        print("=" * 70)

        if preset_name is None:
            screen = self.df[
                (self.df["health_score"] >= 80) & (self.df["financial_quality_score"] >= 4)
            ].copy()

            screen = screen.sort_values(by="health_score", ascending=False)
        else:
            try:
                screen = self.apply_filters(preset_name)
            except ValueError as error:
                print(str(error))
                return pd.DataFrame()

            if "health_score" in screen.columns:
                screen = screen.sort_values(by="health_score", ascending=False)

            print(f"Preset Used: {preset_name}")

        Path("data/output").mkdir(parents=True, exist_ok=True)

        output_path = "data/output/investment_screener.csv"

        screen.to_csv(output_path, index=False)

        print(f"Selected {len(screen)} companies")
        print(f"Saved to {output_path}")

        return screen

    def apply_filters(self, preset_name: str) -> pd.DataFrame:
        """
        Apply a named preset of min/max filters to the dataframe.

        Reads self.config["presets"][preset_name], a mapping of
        rule names to threshold values. Each rule name must end in
        either "_min" or "_max" to indicate the comparison direction;
        the corresponding dataframe column is found by stripping that
        suffix. Rules referencing columns that are not present in the
        dataframe are silently skipped rather than raising an error,
        since not all financial metrics are available yet.

        Args:
            preset_name: Key identifying the preset under
                self.config["presets"].

        Returns:
            A filtered copy of self.df with all applicable rules
            from the preset applied.
        """
        filtered_df = self.df.copy()

        presets = self.config.get("presets", {})
        if preset_name not in presets:
            raise ValueError(f"Unknown screener preset: {preset_name}")
        preset = presets[preset_name]

        for rule_name, threshold in preset.items():
            if rule_name.endswith("_min"):
                column = rule_name[: -len("_min")]
                if column in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df[column] >= threshold]
            elif rule_name.endswith("_max"):
                column = rule_name[: -len("_max")]
                if column in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df[column] <= threshold]

        return filtered_df