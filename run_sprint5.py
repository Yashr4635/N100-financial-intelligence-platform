#!/usr/bin/env python3
"""
run_sprint5.py — Standalone Sprint 5 pipeline runner.
Run from the project root or via absolute path.
"""
import sys
import os

BASE = "/Users/apple/Desktop/N100 FINANCIAL INTELLIGENCE PLATFORM"
sys.path.insert(0, BASE)
os.chdir(BASE)

# Suppress matplotlib warning about non-writable cache dir
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib_cache"
os.makedirs("/tmp/matplotlib_cache", exist_ok=True)

print("=" * 70)
print("SPRINT 5 STANDALONE RUNNER")
print("=" * 70)

# 1. NLP Parser
print("\n[1/6] NLP Parser...")
try:
    from src.analytics.nlp_parser import NLPParser
    parser = NLPParser()
    parsed, failures = parser.run()
    print(f"  ✓ Parsed: {len(parsed)}, Failures: {len(failures)}")
except Exception as e:
    print(f"  ✗ NLP Parser error: {e}")
    import traceback; traceback.print_exc()

# 2. Pros & Cons Generator
print("\n[2/6] Pros & Cons Generator...")
try:
    from src.analytics.pros_cons_generator import ProsConsGenerator
    gen = ProsConsGenerator()
    df = gen.run()
    print(f"  ✓ Generated {len(df)} insights")
except Exception as e:
    print(f"  ✗ Pros & Cons error: {e}")
    import traceback; traceback.print_exc()

# 3. Cash Flow Intelligence Engine
print("\n[3/6] Cash Flow Intelligence Engine...")
try:
    from src.analytics.cashflow_intelligence import CashFlowIntelligenceEngine
    cf = CashFlowIntelligenceEngine()
    cf.run()
    print("  ✓ Cash Flow Intelligence complete")
except Exception as e:
    print(f"  ✗ Cash Flow Intelligence error: {e}")
    import traceback; traceback.print_exc()

# 4. Capital Allocation Analytics
print("\n[4/6] Capital Allocation Analytics...")
try:
    from src.analytics.capital_allocation import CapitalAllocationAnalytics
    ca = CapitalAllocationAnalytics()
    df_ca = ca.run()
    print(f"  ✓ Pattern changes: {len(df_ca)}")
except Exception as e:
    print(f"  ✗ Capital Allocation error: {e}")
    import traceback; traceback.print_exc()

# 5. Sector Reports
print("\n[5/6] Sector Report Generator...")
try:
    from src.reports.sector_report import SectorReportGenerator
    sr = SectorReportGenerator()
    paths = sr.run()
    print(f"  ✓ Generated {len(paths)} sector reports")
except Exception as e:
    print(f"  ✗ Sector Report error: {e}")
    import traceback; traceback.print_exc()

# 6. Portfolio Summary
print("\n[6/6] Portfolio Summary PDF...")
try:
    from src.reports.portfolio_summary import PortfolioSummaryGenerator
    ps = PortfolioSummaryGenerator()
    path = ps.run()
    print(f"  ✓ Portfolio summary: {path}")
except Exception as e:
    print(f"  ✗ Portfolio Summary error: {e}")
    import traceback; traceback.print_exc()

print("\n" + "=" * 70)
print("SPRINT 5 RUN COMPLETE")
print("=" * 70)

# List outputs
import glob
outputs = glob.glob(os.path.join(BASE, "data", "output", "*.csv"))
outputs += glob.glob(os.path.join(BASE, "data", "output", "*.xlsx"))
outputs += glob.glob(os.path.join(BASE, "reports", "**", "*.pdf"), recursive=True)
print(f"\nOutputs generated ({len(outputs)} files):")
for o in sorted(outputs):
    rel = os.path.relpath(o, BASE)
    size_kb = os.path.getsize(o) // 1024
    print(f"  {rel}  ({size_kb} KB)")
