from src.etl.loader import ExcelLoader
from src.etl.normalizer import DataNormalizer
from src.etl.validator import DataValidator
from src.database.connection import DatabaseManager
from src.analytics.ratio_engine import RatioEngine
from src.analytics.health_score import HealthScoreEngine
from src.analytics.sector_analysis import SectorAnalysis
from src.analytics.screener import InvestmentScreener


def main():

    # ---------------- ETL ----------------
    loader = ExcelLoader()
    datasets = loader.load_all()

    normalizer = DataNormalizer(datasets)
    clean_data = normalizer.normalize()

    validator = DataValidator(clean_data)
    validator.validate()

    db = DatabaseManager()
    db.save_datasets(clean_data)

    print("\nETL Pipeline Completed Successfully!")

    # ---------------- Analytics ----------------
    ratio = RatioEngine()
    ratio.run()

    health = HealthScoreEngine()
    health_df = health.calculate_score()

    sector = SectorAnalysis()
    sector.run()

    screener = InvestmentScreener(health_df)
    screener.run()

    print("\nAnalytics Pipeline Completed Successfully!")

    db.close()


if __name__ == "__main__":
    main()
