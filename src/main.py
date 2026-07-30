import sqlite3

import pandas as pd

from src.analytics.radar import RadarChartEngine
from src.etl.loader import ExcelLoader
from src.etl.normalizer import DataNormalizer
from src.etl.validator import DataValidator
from src.database.connection import DatabaseManager
from src.analytics.ratio_engine import RatioEngine
from src.analytics.health_score import HealthScoreEngine
from src.analytics.sector_analysis import SectorAnalysis
from src.analytics.screener import InvestmentScreener
from src.analytics.peer import PeerComparisonEngine
from src.analytics.reporting import ReportingEngine
from src.utils.config import DATABASE_PATH


def main():

    db = DatabaseManager()

    try:
        # ---------------- ETL ----------------
        loader = ExcelLoader()
        datasets = loader.load_all()

        normalizer = DataNormalizer(datasets)
        clean_data = normalizer.normalize()

        validator = DataValidator(clean_data)
        validator.validate()

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

        # PeerComparisonEngine needs sector info
        sector_conn = sqlite3.connect(DATABASE_PATH)
        sectors_df = pd.read_sql("SELECT * FROM sectors", sector_conn)
        sector_conn.close()

        peer_input_df = health_df.merge(sectors_df, on="company_id", how="left")

        peer = PeerComparisonEngine(peer_input_df)
        peer.run()

        reporting = ReportingEngine()
        reporting.run()

        radar = RadarChartEngine()
        radar.run()

        print("\nAnalytics Pipeline Completed Successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    main()