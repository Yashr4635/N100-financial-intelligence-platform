import logging
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

# Sprint 5 imports
from src.analytics.nlp_parser import NLPParser
from src.analytics.pros_cons_generator import ProsConsGenerator
from src.analytics.cashflow_intelligence import CashFlowIntelligenceEngine
from src.analytics.capital_allocation import CapitalAllocationAnalytics
from src.reports.pdf_tearsheet import PDFTearsheetGenerator
from src.reports.sector_report import SectorReportGenerator
from src.reports.portfolio_summary import PortfolioSummaryGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


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

        # ---------------- Analytics (Sprint 1-4) ----------------
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

        print("\nAnalytics Pipeline (Sprint 1-4) Completed Successfully!")

        # ============================================================
        # Sprint 5 Pipeline
        # ============================================================

        print("\n" + "=" * 70)
        print("SPRINT 5 PIPELINE")
        print("=" * 70)

        # 1. NLP Parser
        try:
            nlp = NLPParser()
            nlp.run()
        except Exception as exc:
            logger.error("NLP Parser failed: %s", exc)

        # 2. Pros & Cons Generator
        try:
            pros_cons = ProsConsGenerator()
            pros_cons.run()
        except Exception as exc:
            logger.error("Pros & Cons Generator failed: %s", exc)

        # 3. Cash Flow Intelligence Engine
        try:
            cf_intel = CashFlowIntelligenceEngine()
            cf_intel.run()
        except Exception as exc:
            logger.error("Cash Flow Intelligence Engine failed: %s", exc)

        # 4. Capital Allocation Analytics
        try:
            cap_alloc = CapitalAllocationAnalytics()
            cap_alloc.run()
        except Exception as exc:
            logger.error("Capital Allocation Analytics failed: %s", exc)

        # 5. PDF Tearsheet Generator
        try:
            tearsheet = PDFTearsheetGenerator()
            tearsheet.run()
        except Exception as exc:
            logger.error("PDF Tearsheet Generator failed: %s", exc)

        # 6. Sector Report Generator
        try:
            sector_report = SectorReportGenerator()
            sector_report.run()
        except Exception as exc:
            logger.error("Sector Report Generator failed: %s", exc)

        # 7. Portfolio Summary PDF
        try:
            portfolio = PortfolioSummaryGenerator()
            portfolio.run()
        except Exception as exc:
            logger.error("Portfolio Summary Generator failed: %s", exc)

        print("\n" + "=" * 70)
        print("SPRINT 5 PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 70)

    finally:
        db.close()


if __name__ == "__main__":
    main()