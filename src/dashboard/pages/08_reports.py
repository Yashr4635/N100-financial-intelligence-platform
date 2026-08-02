"""
Reports Dashboard page.

Central hub for all Sprint 1–5 output artifacts:
    Sprint 1-4:
    - data/output/executive_summary.csv
    - data/output/analytics_summary.xlsx
    - data/output/company_health_scores.csv
    - data/output/financial_ratios_calculated.csv
    - data/output/investment_screener.csv
    - data/output/peer_comparison.csv
    - data/output/sector_analysis.csv
    - reports/radar_charts/

    Sprint 5:
    - data/output/analysis_parsed.csv
    - data/output/parse_failures.csv
    - data/output/pros_cons_generated.csv
    - data/output/cashflow_intelligence.xlsx
    - data/output/distress_alerts.csv
    - data/output/pattern_changes.csv
    - reports/tearsheets/
    - reports/sector/
    - reports/portfolio/portfolio_summary.pdf

This page only READS pre-computed outputs. No analytics logic is
implemented or modified here.
"""

from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# src/dashboard/pages/08_reports.py -> project root is 3 levels up
PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
RADAR_CHARTS_DIR = PROJECT_ROOT / "reports" / "radar_charts"

# Sprint 5 directories
TEARSHEETS_DIR = PROJECT_ROOT / "reports" / "tearsheets"
SECTOR_REPORTS_DIR = PROJECT_ROOT / "reports" / "sector"
PORTFOLIO_DIR = PROJECT_ROOT / "reports" / "portfolio"

EXEC_SUMMARY_PATH = OUTPUT_DIR / "executive_summary.csv"
ANALYTICS_SUMMARY_PATH = OUTPUT_DIR / "analytics_summary.xlsx"
HEALTH_SCORES_PATH = OUTPUT_DIR / "company_health_scores.csv"
FINANCIAL_RATIOS_PATH = OUTPUT_DIR / "financial_ratios_calculated.csv"
INVESTMENT_SCREENER_PATH = OUTPUT_DIR / "investment_screener.csv"
PEER_COMPARISON_PATH = OUTPUT_DIR / "peer_comparison.csv"
SECTOR_ANALYSIS_PATH = OUTPUT_DIR / "sector_analysis.csv"

# Sprint 5 paths
ANALYSIS_PARSED_PATH = OUTPUT_DIR / "analysis_parsed.csv"
PARSE_FAILURES_PATH = OUTPUT_DIR / "parse_failures.csv"
PROS_CONS_PATH = OUTPUT_DIR / "pros_cons_generated.csv"
CASHFLOW_INTEL_PATH = OUTPUT_DIR / "cashflow_intelligence.xlsx"
DISTRESS_ALERTS_PATH = OUTPUT_DIR / "distress_alerts.csv"
PATTERN_CHANGES_PATH = OUTPUT_DIR / "pattern_changes.csv"
PORTFOLIO_SUMMARY_PATH = PORTFOLIO_DIR / "portfolio_summary.pdf"

# Registry of all downloadable / previewable reports on this page.
REPORTS = [
    # Sprint 1-4
    {"label": "Executive Summary", "path": EXEC_SUMMARY_PATH, "type": "csv"},
    {"label": "Company Health Scores", "path": HEALTH_SCORES_PATH, "type": "csv"},
    {"label": "Financial Ratios", "path": FINANCIAL_RATIOS_PATH, "type": "csv"},
    {"label": "Investment Screener", "path": INVESTMENT_SCREENER_PATH, "type": "csv"},
    {"label": "Peer Comparison", "path": PEER_COMPARISON_PATH, "type": "csv"},
    {"label": "Sector Analysis", "path": SECTOR_ANALYSIS_PATH, "type": "csv"},
    {"label": "Analytics Summary", "path": ANALYTICS_SUMMARY_PATH, "type": "xlsx"},
    # Sprint 5
    {"label": "Analysis Parsed (NLP)", "path": ANALYSIS_PARSED_PATH, "type": "csv"},
    {"label": "Parse Failures (NLP)", "path": PARSE_FAILURES_PATH, "type": "csv"},
    {"label": "Pros & Cons Generated", "path": PROS_CONS_PATH, "type": "csv"},
    {"label": "Cashflow Intelligence", "path": CASHFLOW_INTEL_PATH, "type": "xlsx"},
    {"label": "Distress Alerts", "path": DISTRESS_ALERTS_PATH, "type": "csv"},
    {"label": "Capital Allocation Changes", "path": PATTERN_CHANGES_PATH, "type": "csv"},
    {"label": "Portfolio Summary PDF", "path": PORTFOLIO_SUMMARY_PATH, "type": "pdf"},
]


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> pd.DataFrame:
    """Load a CSV file into a DataFrame, returning an empty DataFrame on failure."""
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_excel_sheet_names(path: Path) -> list[str]:
    if not path.exists():
        return []
    try:
        return pd.ExcelFile(path).sheet_names
    except Exception:
        return []


@st.cache_data(show_spinner=False)
def load_excel_sheet(path: Path, sheet_name: str) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_excel(path, sheet_name=sheet_name)
    except Exception:
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def read_file_bytes(path: Path) -> bytes | None:
    if not path.exists():
        return None
    try:
        return path.read_bytes()
    except Exception:
        return None


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """
    Return the first column in `df` that matches (case-insensitively,
    ignoring underscores/spaces) one of the candidate names.
    """
    if df.empty:
        return None
    normalized = {
        c.lower().replace("_", "").replace(" ", ""): c for c in df.columns
    }
    for candidate in candidates:
        key = candidate.lower().replace("_", "").replace(" ", "")
        if key in normalized:
            return normalized[key]
    return None


def format_metric_value(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "N/A"
    if isinstance(value, (int, float)):
        if float(value).is_integer():
            return f"{int(value):,}"
        return f"{round(value, 2):,}"
    return str(value)


# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("📄 Reports")
st.write(
    "Central hub for all Sprint 1-3 analytics outputs — executive "
    "summary, downloadable reports, previews, and radar charts."
)

st.divider()

# ---------------------------------------------------------------------------
# 1. Executive Summary
# ---------------------------------------------------------------------------
st.subheader("Executive Summary")

exec_df = load_csv(EXEC_SUMMARY_PATH)
metric_col = find_column(exec_df, ["metric", "name"])
value_col = find_column(exec_df, ["value"])

if exec_df.empty or not metric_col or not value_col:
    st.info(
        f"Could not load `{EXEC_SUMMARY_PATH.relative_to(PROJECT_ROOT)}`. "
        "Executive summary metrics are unavailable."
    )
    exec_lookup: dict[str, float] = {}
else:
    exec_lookup = dict(zip(exec_df[metric_col], exec_df[value_col]))
    records = exec_df[[metric_col, value_col]].to_dict("records")
    for i in range(0, len(records), 3):
        row_records = records[i : i + 3]
        row_cols = st.columns(3)
        for col_widget, record in zip(row_cols, row_records):
            with col_widget:
                with st.container(border=True):
                    st.metric(
                        str(record[metric_col]),
                        format_metric_value(record[value_col]),
                    )

st.divider()

# ---------------------------------------------------------------------------
# 2. Available Reports (download buttons)
# ---------------------------------------------------------------------------
st.subheader("Available Reports")

report_cols = st.columns(2)
for i, report in enumerate(REPORTS):
    with report_cols[i % 2]:
        with st.container(border=True):
            st.markdown(f"**{report['label']}** ({report['type'].upper()})")
            file_bytes = read_file_bytes(report["path"])
            if file_bytes is None:
                st.caption(
                    f"⚠️ Not found: `{report['path'].relative_to(PROJECT_ROOT)}`"
                )
            else:
                mime = (
                    "text/csv"
                    if report["type"] == "csv"
                    else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.download_button(
                    label=f"⬇️ Download {report['label']}",
                    data=file_bytes,
                    file_name=report["path"].name,
                    mime=mime,
                    key=f"download_{report['label']}",
                )

st.divider()

# ---------------------------------------------------------------------------
# 3. Report Preview
# ---------------------------------------------------------------------------
st.subheader("Report Preview")

with st.container(border=True):
    available_reports = [r for r in REPORTS if r["path"].exists()]

    if not available_reports:
        st.info("No report files are currently available to preview.")
    else:
        preview_labels = [r["label"] for r in available_reports]
        selected_label = st.selectbox("Select a report to preview", options=preview_labels)
        selected_report = next(r for r in available_reports if r["label"] == selected_label)

        if selected_report["type"] == "csv":
            preview_df = load_csv(selected_report["path"])
            if preview_df.empty:
                st.info("This report has no rows to preview.")
            else:
                st.dataframe(preview_df.head(20), width='stretch', hide_index=True)
                st.caption(f"Showing first {min(20, len(preview_df))} of {len(preview_df):,} rows.")
        else:
            sheet_names = load_excel_sheet_names(selected_report["path"])
            if not sheet_names:
                st.info("Could not read sheets from this workbook.")
            else:
                selected_sheet = st.selectbox("Select a sheet", options=sheet_names)
                sheet_df = load_excel_sheet(selected_report["path"], selected_sheet)
                if sheet_df.empty:
                    st.info("This sheet has no rows to preview.")
                else:
                    st.dataframe(sheet_df.head(20), width='stretch', hide_index=True)
                    st.caption(
                        f"Showing first {min(20, len(sheet_df))} of {len(sheet_df):,} rows "
                        f"from sheet '{selected_sheet}'."
                    )

st.divider()

# ---------------------------------------------------------------------------
# 4. Radar Chart Gallery
# ---------------------------------------------------------------------------
st.subheader("Radar Chart Gallery")

radar_files = []
if RADAR_CHARTS_DIR.exists():
    radar_files = sorted(RADAR_CHARTS_DIR.glob("*_radar.png"))

if not radar_files:
    st.info(
        f"No radar charts found in "
        f"`{RADAR_CHARTS_DIR.relative_to(PROJECT_ROOT)}`."
    )
else:
    tickers = [f.stem.replace("_radar", "") for f in radar_files]
    ticker_to_path = dict(zip(tickers, radar_files))

    with st.container(border=True):
        st.markdown("**View a Specific Company**")
        selected_ticker = st.selectbox("Select a company", options=sorted(tickers))
        st.image(
            str(ticker_to_path[selected_ticker]),
            caption=f"{selected_ticker} — Radar Chart",
            width='stretch',
        )

    st.markdown("**All Available Radar Charts**")
    gallery_cols_per_row = 4
    for i in range(0, len(radar_files), gallery_cols_per_row):
        row_files = radar_files[i : i + gallery_cols_per_row]
        row_cols = st.columns(gallery_cols_per_row)
        for col_widget, file_path in zip(row_cols, row_files):
            with col_widget:
                with st.container(border=True):
                    st.image(str(file_path), width='stretch')
                    st.caption(file_path.stem.replace("_radar", ""))

st.divider()

# ---------------------------------------------------------------------------
# 5. Report Statistics
# ---------------------------------------------------------------------------
st.subheader("Report Statistics")

number_of_reports = sum(1 for r in REPORTS if r["path"].exists())

health_df = load_csv(HEALTH_SCORES_PATH)
health_id_col = find_column(health_df, ["company_id", "id"])

if "Total Companies" in exec_lookup:
    total_companies = format_metric_value(exec_lookup["Total Companies"])
elif health_id_col:
    total_companies = f"{health_df[health_id_col].nunique():,}"
else:
    total_companies = "N/A"

sector_df = load_csv(SECTOR_ANALYSIS_PATH)
sector_name_col = find_column(sector_df, ["broad_sector", "sector", "sector_name", "industry"])

if "Number of Sectors" in exec_lookup:
    total_sectors = format_metric_value(exec_lookup["Number of Sectors"])
elif sector_name_col:
    total_sectors = f"{sector_df[sector_name_col].nunique():,}"
else:
    total_sectors = "N/A"

existing_paths = [r["path"] for r in REPORTS if r["path"].exists()] + [
    f for f in radar_files
]
if existing_paths:
    last_updated_ts = max(p.stat().st_mtime for p in existing_paths)
    last_updated = datetime.fromtimestamp(last_updated_ts).strftime("%Y-%m-%d %H:%M:%S")
else:
    last_updated = "N/A"

stat_cols = st.columns(4)

with stat_cols[0]:
    with st.container(border=True):
        st.metric("Number of Reports", f"{number_of_reports} / {len(REPORTS)}")

with stat_cols[1]:
    with st.container(border=True):
        st.metric("Total Companies", total_companies)

with stat_cols[2]:
    with st.container(border=True):
        st.metric("Total Sectors", total_sectors)

with stat_cols[3]:
    with st.container(border=True):
        st.metric("Last Updated", last_updated)

st.divider()

# ===========================================================================
# Sprint 5 Sections
# ===========================================================================
st.header("🚀 Sprint 5 Intelligence Outputs")

# ---------------------------------------------------------------------------
# S5.1 – Pros & Cons Viewer
# ---------------------------------------------------------------------------
st.subheader("✅⚠️ Pros & Cons by Company")
pros_cons_df = load_csv(PROS_CONS_PATH)

if pros_cons_df.empty:
    st.info("Pros & Cons not yet generated. Run the pipeline to generate `pros_cons_generated.csv`.")
else:
    company_ids_pc = sorted(pros_cons_df["company_id"].dropna().unique().tolist()) \
        if "company_id" in pros_cons_df.columns else []
    if company_ids_pc:
        selected_pc = st.selectbox("Select company for Pros & Cons", options=company_ids_pc,
                                   key="pc_company_select")
        company_pc = pros_cons_df[pros_cons_df["company_id"] == selected_pc]
        pros = company_pc[company_pc["type"] == "Pro"] if "type" in company_pc.columns else company_pc
        cons = company_pc[company_pc["type"] == "Con"] if "type" in company_pc.columns else company_pc

        col_pros, col_cons = st.columns(2)
        with col_pros:
            with st.container(border=True):
                st.markdown("**✅ Pros**")
                if pros.empty:
                    st.caption("No pros generated for this company.")
                else:
                    for _, row in pros.iterrows():
                        conf = row.get("confidence", "")
                        conf_str = f" *(confidence: {conf:.0%})*" if isinstance(conf, float) else ""
                        st.markdown(f"- {row.get('insight', '')}{conf_str}")
        with col_cons:
            with st.container(border=True):
                st.markdown("**⚠️ Cons**")
                if cons.empty:
                    st.caption("No cons generated for this company.")
                else:
                    for _, row in cons.iterrows():
                        conf = row.get("confidence", "")
                        conf_str = f" *(confidence: {conf:.0%})*" if isinstance(conf, float) else ""
                        st.markdown(f"- {row.get('insight', '')}{conf_str}")

st.divider()

# ---------------------------------------------------------------------------
# S5.2 – Distress Alerts
# ---------------------------------------------------------------------------
st.subheader("🚨 Distress Alerts")
distress_df = load_csv(DISTRESS_ALERTS_PATH)
if distress_df.empty:
    st.success("✅ No distress alerts found — all companies appear financially stable.")
else:
    st.error(f"⚠️ {len(distress_df)} distress record(s) detected.")
    st.dataframe(distress_df, hide_index=True, use_container_width=True)
    file_bytes_distress = read_file_bytes(DISTRESS_ALERTS_PATH)
    if file_bytes_distress:
        st.download_button(
            "⬇️ Download Distress Alerts CSV",
            data=file_bytes_distress,
            file_name="distress_alerts.csv",
            mime="text/csv",
            key="download_distress_alerts",
        )

st.divider()

# ---------------------------------------------------------------------------
# S5.3 – Capital Allocation Pattern Changes
# ---------------------------------------------------------------------------
st.subheader("📊 Capital Allocation Pattern Changes")
pattern_df = load_csv(PATTERN_CHANGES_PATH)
if pattern_df.empty:
    st.info("No capital allocation pattern changes detected yet.")
else:
    st.dataframe(pattern_df, hide_index=True, use_container_width=True)
    file_bytes_pattern = read_file_bytes(PATTERN_CHANGES_PATH)
    if file_bytes_pattern:
        st.download_button(
            "⬇️ Download Pattern Changes CSV",
            data=file_bytes_pattern,
            file_name="pattern_changes.csv",
            mime="text/csv",
            key="download_pattern_changes",
        )

st.divider()

# ---------------------------------------------------------------------------
# S5.4 – NLP Parse Results
# ---------------------------------------------------------------------------
st.subheader("🔍 NLP Parse Results")
parsed_col, failures_col = st.columns(2)

with parsed_col:
    with st.container(border=True):
        parsed_df = load_csv(ANALYSIS_PARSED_PATH)
        st.markdown(f"**Parsed Records: {len(parsed_df):,}**")
        if not parsed_df.empty:
            st.dataframe(parsed_df.head(10), hide_index=True, use_container_width=True)
            fb = read_file_bytes(ANALYSIS_PARSED_PATH)
            if fb:
                st.download_button("⬇️ Download Parsed CSV", fb,
                                   "analysis_parsed.csv", "text/csv",
                                   key="dl_parsed")

with failures_col:
    with st.container(border=True):
        failures_df = load_csv(PARSE_FAILURES_PATH)
        st.markdown(f"**Parse Failures: {len(failures_df):,}**")
        if not failures_df.empty:
            st.dataframe(failures_df.head(10), hide_index=True, use_container_width=True)
            fb2 = read_file_bytes(PARSE_FAILURES_PATH)
            if fb2:
                st.download_button("⬇️ Download Failures CSV", fb2,
                                   "parse_failures.csv", "text/csv",
                                   key="dl_failures")

st.divider()

# ---------------------------------------------------------------------------
# S5.5 – Company Tearsheets Gallery
# ---------------------------------------------------------------------------
st.subheader("📑 Company Tearsheets")
tearsheet_files = sorted(TEARSHEETS_DIR.glob("*_tearsheet.pdf")) if TEARSHEETS_DIR.exists() else []
if not tearsheet_files:
    st.info("No tearsheets generated yet. Run the pipeline to generate tearsheet PDFs.")
else:
    st.success(f"✅ {len(tearsheet_files)} tearsheets available.")
    tickers_ts = [f.stem.replace("_tearsheet", "") for f in tearsheet_files]
    selected_ts = st.selectbox("Select company tearsheet", options=sorted(tickers_ts),
                               key="ts_select")
    selected_ts_path = TEARSHEETS_DIR / f"{selected_ts}_tearsheet.pdf"
    ts_bytes = read_file_bytes(selected_ts_path)
    if ts_bytes:
        st.download_button(
            f"⬇️ Download {selected_ts} Tearsheet PDF",
            data=ts_bytes,
            file_name=f"{selected_ts}_tearsheet.pdf",
            mime="application/pdf",
            key=f"dl_ts_{selected_ts}",
        )

st.divider()

# ---------------------------------------------------------------------------
# S5.6 – Sector Reports
# ---------------------------------------------------------------------------
st.subheader("🏭 Sector Reports")
sector_pdfs = sorted(SECTOR_REPORTS_DIR.glob("*.pdf")) if SECTOR_REPORTS_DIR.exists() else []
if not sector_pdfs:
    st.info("No sector reports generated yet. Run the pipeline to generate sector PDFs.")
else:
    st.success(f"✅ {len(sector_pdfs)} sector reports available.")
    sector_names = [f.stem.replace("_report", "").replace("_", " ") for f in sector_pdfs]
    selected_sr = st.selectbox("Select sector report", options=sector_names, key="sr_select")
    selected_sr_path = sector_pdfs[sector_names.index(selected_sr)]
    sr_bytes = read_file_bytes(selected_sr_path)
    if sr_bytes:
        st.download_button(
            f"⬇️ Download {selected_sr} Sector Report",
            data=sr_bytes,
            file_name=selected_sr_path.name,
            mime="application/pdf",
            key=f"dl_sr_{selected_sr}",
        )

st.divider()

# ---------------------------------------------------------------------------
# S5.7 – Portfolio Summary PDF
# ---------------------------------------------------------------------------
st.subheader("📋 Portfolio Summary")
portfolio_bytes = read_file_bytes(PORTFOLIO_SUMMARY_PATH)
if portfolio_bytes:
    st.success("✅ Portfolio summary PDF ready.")
    st.download_button(
        "⬇️ Download Portfolio Summary PDF",
        data=portfolio_bytes,
        file_name="portfolio_summary.pdf",
        mime="application/pdf",
        key="dl_portfolio",
    )
else:
    st.info("Portfolio summary PDF not yet generated. Run the pipeline to generate it.")