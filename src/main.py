from src.etl.loader import ExcelLoader
from src.etl.normalizer import DataNormalizer
from src.etl.validator import DataValidator
from src.database.connection import DatabaseManager
from src.analytics.health_score import HealthScoreEngine
from src.analytics.ratio_engine import RatioEngine
from src.analytics.sector_analysis import SectorAnalysis

def main():
    # Step 1: Load datasets
    loader = ExcelLoader()
    datasets = loader.load_all()

    # Step 2: Normalize datasets
    normalizer = DataNormalizer(datasets)
    clean_data = normalizer.normalize()

    # Step 3: Validate datasets
    validator = DataValidator(clean_data)
    validator.validate()

    # Step 4: Save to SQLite
    db = DatabaseManager()
    db.save_datasets(clean_data)
    db.close()

    print("\nETL Pipeline Completed Successfully!")


if __name__ == "__main__":
    main()

    

engine = RatioEngine()
engine.run()

health = HealthScoreEngine()
health.calculate_score()

sector = SectorAnalysis()
sector.run()
