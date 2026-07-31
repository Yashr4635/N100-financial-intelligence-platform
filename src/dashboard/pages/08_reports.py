"""
Reports Dashboard page.

Central hub for all Sprint 1-3 output artifacts:
    - data/output/executive_summary.csv
    - data/output/analytics_summary.xlsx
    - data/output/company_health_scores.csv
    - data/output/financial_ratios_calculated.csv
    - data/output/investment_screener.csv
    - data/output/peer_comparison.csv
    - data/output/sector_analysis.csv
    - reports/radar_charts/

This page only READS the pre-computed Sprint 1-3 outputs. No analytics
logic is implemented or modified here.
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

EXEC_SUMMARY_PATH = OUTPUT_DIR / "executive_summary.csv"
ANALYTICS_SUMMARY_PATH = OUTPUT_DIR / "analytics_summary.xlsx"
HEALTH_SCORES_PATH = OUTPUT_DIR / "company_health_scores.csv"
FINANCIAL_RATIOS_PATH = OUTPUT_DIR / "financial_ratios_calculated.csv"
INVESTMENT_SCREENER_PATH = OUTPUT_DIR / "investment_screener.csv"
PEER_COMPARISON_PATH = OUTPUT_DIR / "peer_comparison.csv"
SECTOR_ANALYSIS_PATH = OUTPUT_DIR / "sector_analysis.csv"

# Registry of all downloadable / previewable reports on this page.
REPORTS = [
    {"label": "Executive Summary", "path": EXEC_SUMMARY_PATH, "type": "csv"},
    {"label": "Company Health Scores", "path": HEALTH_SCORES_PATH, "type": "csv"},
    {"label": "Financial Ratios", "path": FINANCIAL_RATIOS_PATH, "type": "csv"},
    {"label": "Investment Screener", "path": INVESTMENT_SCREENER_PATH, "type": "csv"},
    {"label": "Peer Comparison", "path": PEER_COMPARISON_PATH, "type": "csv"},
    {"label": "Sector Analysis", "path": SECTOR_ANALYSIS_PATH, "type": "csv"},
    {"label": "Analytics Summary", "path": ANALYTICS_SUMMARY_PATH, "type": "xlsx"},
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