"""
Trends Dashboard page.

Historical trend analysis for a single company, built from Sprint 1-3
outputs:
    - data/output/financial_ratios_calculated.csv (ratio history by year)
    - data/output/company_health_scores.csv       (health score & rating history)
    - data/raw/companies.xlsx                     (company_id -> full name lookup)

This page only READS the pre-computed Sprint 1-3 outputs. No analytics
logic is implemented or modified here.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# src/dashboard/pages/05_trends.py -> project root is 3 levels up
PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
RAW_DIR = PROJECT_ROOT / "data" / "raw"

FINANCIAL_RATIOS_PATH = OUTPUT_DIR / "financial_ratios_calculated.csv"
HEALTH_SCORES_PATH = OUTPUT_DIR / "company_health_scores.csv"
COMPANIES_XLSX_PATH = RAW_DIR / "companies.xlsx"


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
def load_companies_workbook(path: Path) -> pd.DataFrame:
    """
    Load companies.xlsx defensively.

    The sheet is not a clean table -- there may be a title/blank row
    above the real header row. This scans the first several rows for
    the one that looks like a header (contains an "id"-like cell and a
    "company name"-like cell) and reads the sheet starting from there.
    Falls back to a plain header=0 read if detection fails.
    """
    if not path.exists():
        return pd.DataFrame()

    try:
        preview = pd.read_excel(path, header=None, nrows=10)
    except Exception:
        return pd.DataFrame()

    header_row_idx = 0
    for i in range(len(preview)):
        row_values = [
            str(v).strip().lower() if pd.notna(v) else "" for v in preview.iloc[i].tolist()
        ]
        has_id = any(v == "id" for v in row_values)
        has_name = any("company" in v and "name" in v for v in row_values)
        if has_id and has_name:
            header_row_idx = i
            break

    try:
        df = pd.read_excel(path, header=header_row_idx)
    except Exception:
        return pd.DataFrame()

    df = df.dropna(axis=1, how="all").dropna(axis=0, how="all")
    return df


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


def normalize_id(value) -> str:
    """Normalize an identifier for matching across files (int-like -> plain string)."""
    if pd.isna(value):
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def format_value(value, decimals=2, suffix=""):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "N/A"
    if isinstance(value, (int, float)):
        return f"{round(value, decimals)}{suffix}"
    return f"{value}{suffix}"


def format_delta(value, decimals=2, suffix=""):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    sign = "+" if value >= 0 else ""
    return f"{sign}{round(value, decimals)}{suffix}"


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
ratios_df = load_csv(FINANCIAL_RATIOS_PATH)
health_df = load_csv(HEALTH_SCORES_PATH)
companies_df = load_companies_workbook(COMPANIES_XLSX_PATH)

# Resolve column names -------------------------------------------------------
ratios_id_col = find_column(ratios_df, ["company_id", "id"])
ratios_year_col = find_column(ratios_df, ["year"])
roe_col = find_column(ratios_df, ["return_on_equity_pct", "roe_pct", "roe"])
npm_col = find_column(ratios_df, ["net_profit_margin_pct", "net_profit_margin"])
de_col = find_column(ratios_df, ["debt_to_equity"])
ic_col = find_column(ratios_df, ["interest_coverage"])
eps_col = find_column(ratios_df, ["earnings_per_share", "eps"])
bvps_col = find_column(ratios_df, ["book_value_per_share", "book_value"])

health_id_col = find_column(health_df, ["company_id", "id"])
health_year_col = find_column(health_df, ["year"])
health_score_col = find_column(health_df, ["health_score", "score"])
rating_col = find_column(health_df, ["rating"])

companies_id_col = find_column(companies_df, ["id", "company_id"])
companies_name_col = find_column(companies_df, ["company_name", "name", "company"])

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("📈 Trends")
st.write(
    "Explore how a company's health score and key financial ratios have "
    "evolved over time."
)

if ratios_df.empty and health_df.empty:
    st.warning(
        "Could not load trend data. Please check that "
        "`data/output/financial_ratios_calculated.csv` and "
        "`data/output/company_health_scores.csv` are available."
    )
    st.stop()

if not ratios_id_col and not health_id_col:
    st.error("Neither dataset contains a recognizable company identifier column.")
    st.stop()

st.divider()

# ---------------------------------------------------------------------------
# Build a full per-year timeline per company (outer merge so a year
# missing from one file doesn't drop data from the other).
# ---------------------------------------------------------------------------
ratios_clean = pd.DataFrame()
if ratios_id_col and ratios_year_col:
    ratios_clean = ratios_df.copy()
    ratios_clean["_id_key"] = ratios_clean[ratios_id_col].map(normalize_id)
    ratios_clean = ratios_clean[ratios_clean["_id_key"] != ""]

health_clean = pd.DataFrame()
if health_id_col and health_year_col:
    health_clean = health_df.copy()
    health_clean["_id_key"] = health_clean[health_id_col].map(normalize_id)
    health_clean = health_clean[health_clean["_id_key"] != ""]

if not ratios_clean.empty and not health_clean.empty:
    timeline_df = pd.merge(
        ratios_clean,
        health_clean[["_id_key", health_year_col, health_score_col, rating_col]],
        left_on=["_id_key", ratios_year_col],
        right_on=["_id_key", health_year_col],
        how="outer",
        suffixes=("", "_health"),
    )
    # Reconcile the two year columns from the outer merge into one.
    timeline_df["Year"] = timeline_df[ratios_year_col].combine_first(
        timeline_df[health_year_col]
    )
elif not ratios_clean.empty:
    timeline_df = ratios_clean.copy()
    timeline_df["Year"] = timeline_df[ratios_year_col]
elif not health_clean.empty:
    timeline_df = health_clean.copy()
    timeline_df["Year"] = timeline_df[health_year_col]
else:
    timeline_df = pd.DataFrame()

if timeline_df.empty:
    st.warning("No company identifier / year combination could be built from the source data.")
    st.stop()

# Name lookup from companies.xlsx --------------------------------------------
id_to_name: dict[str, str] = {}
if companies_id_col and companies_name_col:
    for _, row in companies_df.iterrows():
        key = normalize_id(row[companies_id_col])
        if key:
            id_to_name[key] = str(row[companies_name_col]).strip()


def display_label(company_id: str) -> str:
    return id_to_name.get(company_id, company_id)


available_ids = sorted(
    timeline_df["_id_key"].dropna().unique().tolist(), key=lambda cid: display_label(cid).lower()
)

if not available_ids:
    st.error("No companies found in the trend datasets.")
    st.stop()

# ---------------------------------------------------------------------------
# 1. Company selector
# ---------------------------------------------------------------------------
st.subheader("Select a Company")

selected_id = st.selectbox(
    "Company",
    options=available_ids,
    format_func=display_label,
)

selected_name = display_label(selected_id)

company_timeline = timeline_df[timeline_df["_id_key"] == selected_id].copy()
company_timeline = company_timeline.dropna(subset=["Year"])
company_timeline["Year"] = company_timeline["Year"].astype(int)
company_timeline = company_timeline.sort_values(by="Year")

st.divider()

# ---------------------------------------------------------------------------
# 4. KPI summary
# ---------------------------------------------------------------------------
st.subheader("KPI Summary")


def first_last(df: pd.DataFrame, col: str | None):
    """Return (first_available_value, last_available_value) for a metric,
    handling missing years/values gracefully."""
    if not col or col not in df.columns:
        return None, None
    series = df[["Year", col]].dropna(subset=[col]).sort_values(by="Year")
    if series.empty:
        return None, None
    first_val = series.iloc[0][col]
    last_val = series.iloc[-1][col]
    return first_val, last_val


hs_first, hs_last = first_last(company_timeline, health_score_col)
roe_first, roe_last = first_last(company_timeline, roe_col)
npm_first, npm_last = first_last(company_timeline, npm_col)

hs_change = (hs_last - hs_first) if hs_first is not None and hs_last is not None else None
roe_change = (roe_last - roe_first) if roe_first is not None and roe_last is not None else None
npm_change = (npm_last - npm_first) if npm_first is not None and npm_last is not None else None

kpi_cols = st.columns(4)

with kpi_cols[0]:
    with st.container(border=True):
        st.metric("Latest Health Score", format_value(hs_last, 1))

with kpi_cols[1]:
    with st.container(border=True):
        st.metric(
            "Health Score Change",
            format_value(hs_last, 1) if hs_last is not None else "N/A",
            delta=format_delta(hs_change, 1),
        )

with kpi_cols[2]:
    with st.container(border=True):
        st.metric(
            "ROE Change",
            format_value(roe_last, 2, "%") if roe_last is not None else "N/A",
            delta=format_delta(roe_change, 2, "%"),
        )

with kpi_cols[3]:
    with st.container(border=True):
        st.metric(
            "Profit Margin Change",
            format_value(npm_last, 2, "%") if npm_last is not None else "N/A",
            delta=format_delta(npm_change, 2, "%"),
        )

st.caption(
    f"Change is measured from the earliest to the latest recorded year "
    f"available for **{selected_name}**."
)

st.divider()

# ---------------------------------------------------------------------------
# 2. Historical line charts (one per metric)
# ---------------------------------------------------------------------------
st.subheader("Historical Trends")

trend_specs = [
    ("Health Score", health_score_col, ""),
    ("ROE", roe_col, "%"),
    ("Net Profit Margin", npm_col, "%"),
    ("Debt to Equity", de_col, ""),
    ("Interest Coverage", ic_col, ""),
    ("EPS", eps_col, ""),
    ("Book Value", bvps_col, ""),
]

available_specs = [(label, col, suffix) for label, col, suffix in trend_specs if col]

if not available_specs:
    st.info("None of the expected trend metrics were found in the source data.")
else:
    # Lay charts out two per row.
    for i in range(0, len(available_specs), 2):
        row_specs = available_specs[i : i + 2]
        row_cols = st.columns(2)
        for col_widget, (label, metric_col, suffix) in zip(row_cols, row_specs):
            with col_widget:
                with st.container(border=True):
                    st.markdown(f"**{label} Over Time**")
                    metric_series = company_timeline[["Year", metric_col]].dropna(
                        subset=[metric_col]
                    )
                    if metric_series.empty:
                        st.info(f"No historical {label.lower()} data available for this company.")
                    elif len(metric_series) == 1:
                        st.info(
                            f"Only one data point available for {label.lower()} "
                            f"({int(metric_series.iloc[0]['Year'])}: "
                            f"{format_value(metric_series.iloc[0][metric_col], 2, suffix)})."
                        )
                    else:
                        fig = px.line(
                            metric_series,
                            x="Year",
                            y=metric_col,
                            markers=True,
                            labels={metric_col: f"{label}{f' ({suffix})' if suffix else ''}"},
                        )
                        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
                        fig.update_xaxes(dtick=1)
                        st.plotly_chart(fig, width='stretch')

st.divider()

# ---------------------------------------------------------------------------
# 3. Multi-metric comparison chart
# ---------------------------------------------------------------------------
st.subheader("Multi-Metric Comparison")

with st.container(border=True):
    st.markdown("**Indexed Trend (First Available Year = 100)**")
    st.caption(
        "Each metric is rescaled to its own first recorded year so metrics "
        "with very different units (e.g. Health Score vs. EPS) can be "
        "compared on a single chart."
    )

    indexed_frames = []
    for label, metric_col, _ in available_specs:
        series = company_timeline[["Year", metric_col]].dropna(subset=[metric_col]).sort_values(
            by="Year"
        )
        if len(series) < 2:
            continue
        base_value = series.iloc[0][metric_col]
        if base_value in (0, None) or pd.isna(base_value):
            continue
        series = series.copy()
        series["Indexed Value"] = (series[metric_col] / base_value) * 100
        series["Metric"] = label
        indexed_frames.append(series[["Year", "Metric", "Indexed Value"]])

    if not indexed_frames:
        st.info(
            "Not enough multi-year data across metrics to build a comparison chart "
            "for this company."
        )
    else:
        combined = pd.concat(indexed_frames, ignore_index=True)
        fig_multi = px.line(
            combined,
            x="Year",
            y="Indexed Value",
            color="Metric",
            markers=True,
            labels={"Indexed Value": "Indexed Value (First Year = 100)"},
        )
        fig_multi.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        fig_multi.update_xaxes(dtick=1)
        fig_multi.add_hline(y=100, line_dash="dot", line_color="gray")
        st.plotly_chart(fig_multi, width='stretch')