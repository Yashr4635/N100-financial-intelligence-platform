"""
Company Profile page.

Interactive, single-company view built from Sprint 1-3 outputs:
    - data/output/company_health_scores.csv   (health score, rating, year)
    - data/output/financial_ratios_calculated.csv (ratio history by year)
    - data/raw/companies.xlsx                 (company_id -> name/sector lookup)
    - reports/radar_charts/{company_name}_radar.png (pre-generated radar image)

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
# src/dashboard/pages/02_profile.py -> project root is 3 levels up
PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
RAW_DIR = PROJECT_ROOT / "data" / "raw"

HEALTH_SCORES_PATH = OUTPUT_DIR / "company_health_scores.csv"
FINANCIAL_RATIOS_PATH = OUTPUT_DIR / "financial_ratios_calculated.csv"
COMPANIES_XLSX_PATH = RAW_DIR / "companies.xlsx"
RADAR_CHARTS_DIR = PROJECT_ROOT / "reports" / "radar_charts"


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

    # Drop fully empty rows/columns that can result from title/blank rows.
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


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
health_df = load_csv(HEALTH_SCORES_PATH)
ratios_df = load_csv(FINANCIAL_RATIOS_PATH)
companies_df = load_companies_workbook(COMPANIES_XLSX_PATH)

# Resolve column names -------------------------------------------------------
health_id_col = find_column(health_df, ["company_id", "id"])
health_year_col = find_column(health_df, ["year"])
health_score_col = find_column(health_df, ["health_score", "score"])
rating_col = find_column(health_df, ["rating"])

ratios_id_col = find_column(ratios_df, ["company_id", "id"])
ratios_year_col = find_column(ratios_df, ["year"])
roe_col = find_column(ratios_df, ["return_on_equity_pct", "roe_pct", "roe"])
npm_col = find_column(ratios_df, ["net_profit_margin_pct", "net_profit_margin"])
opm_col = find_column(
    ratios_df, ["operating_profit_margin_pct", "operating_profit_margin"]
)
de_col = find_column(ratios_df, ["debt_to_equity"])
ic_col = find_column(ratios_df, ["interest_coverage"])
eps_col = find_column(ratios_df, ["earnings_per_share", "eps"])
bvps_col = find_column(ratios_df, ["book_value_per_share", "book_value"])

companies_id_col = find_column(companies_df, ["id", "company_id"])
companies_name_col = find_column(companies_df, ["company_name", "name", "company"])
companies_sector_col = find_column(companies_df, ["sector", "broad_sector", "industry"])

# Build a normalized id -> name / sector lookup from companies.xlsx ----------
id_to_name: dict[str, str] = {}
id_to_sector: dict[str, str] = {}
if companies_id_col and companies_name_col:
    for _, row in companies_df.iterrows():
        key = normalize_id(row[companies_id_col])
        if not key:
            continue
        id_to_name[key] = str(row[companies_name_col]).strip()
        if companies_sector_col:
            sector_val = row[companies_sector_col]
            id_to_sector[key] = str(sector_val).strip() if pd.notna(sector_val) else "N/A"

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("🧾 Company Profile")
st.write(
    "Explore a detailed, single-company view combining health scores, "
    "financial ratios, and the pre-generated radar chart from Sprint 1-3."
)

if health_df.empty and ratios_df.empty:
    st.warning(
        "Could not load health score or financial ratio data. "
        "Please check that Sprint 3 outputs exist under `data/output/`."
    )
    st.stop()

if companies_df.empty:
    st.info(
        f"Could not load `{COMPANIES_XLSX_PATH.relative_to(PROJECT_ROOT)}`. "
        "Company names/sectors will fall back to their raw IDs."
    )

st.divider()

# ---------------------------------------------------------------------------
# 1. Company dropdown
# ---------------------------------------------------------------------------
available_ids: set[str] = set()
if health_id_col:
    available_ids.update(health_df[health_id_col].dropna().map(normalize_id))
if ratios_id_col:
    available_ids.update(ratios_df[ratios_id_col].dropna().map(normalize_id))
available_ids.discard("")

if not available_ids:
    st.error("No companies found in the health score or financial ratio datasets.")
    st.stop()


def display_label(company_id: str) -> str:
    name = id_to_name.get(company_id)
    return name if name else f"Company #{company_id}"


sorted_ids = sorted(available_ids, key=lambda cid: display_label(cid).lower())

selected_id = st.selectbox(
    "Select a company",
    options=sorted_ids,
    format_func=display_label,
)

selected_name = display_label(selected_id)
selected_sector = id_to_sector.get(selected_id, "N/A")

st.divider()

# ---------------------------------------------------------------------------
# Filter data for the selected company
# ---------------------------------------------------------------------------
company_health = pd.DataFrame()
if health_id_col:
    company_health = health_df[
        health_df[health_id_col].map(normalize_id) == selected_id
    ].copy()
    if health_year_col and not company_health.empty:
        company_health = company_health.sort_values(by=health_year_col)

company_ratios = pd.DataFrame()
if ratios_id_col:
    company_ratios = ratios_df[
        ratios_df[ratios_id_col].map(normalize_id) == selected_id
    ].copy()
    if ratios_year_col and not company_ratios.empty:
        company_ratios = company_ratios.sort_values(by=ratios_year_col)

latest_health_row = company_health.iloc[-1] if not company_health.empty else None
latest_ratios_row = company_ratios.iloc[-1] if not company_ratios.empty else None


def safe_metric(row, col, decimals=2, suffix=""):
    if row is None or not col or col not in row or pd.isna(row[col]):
        return "N/A"
    value = row[col]
    if isinstance(value, (int, float)):
        return f"{round(value, decimals)}{suffix}"
    return f"{value}{suffix}"


# ---------------------------------------------------------------------------
# 2. Company overview
# ---------------------------------------------------------------------------
st.subheader("Overview")

overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)

with overview_col1:
    with st.container(border=True):
        st.markdown("**Company Name**")
        st.markdown(f"### {selected_name}")

with overview_col2:
    with st.container(border=True):
        st.markdown("**Sector**")
        st.markdown(f"### {selected_sector}")

with overview_col3:
    with st.container(border=True):
        st.markdown("**Health Score**")
        st.markdown(f"### {safe_metric(latest_health_row, health_score_col, 1)}")

with overview_col4:
    with st.container(border=True):
        st.markdown("**Rating**")
        st.markdown(f"### {safe_metric(latest_health_row, rating_col, suffix='')}")

st.divider()

# ---------------------------------------------------------------------------
# 3. KPI cards
# ---------------------------------------------------------------------------
st.subheader("Key Financial Metrics")

kpi_row1 = st.columns(3)
kpi_row2 = st.columns(3)

with kpi_row1[0]:
    with st.container(border=True):
        st.metric("ROE", safe_metric(latest_ratios_row, roe_col, 2, "%"))

with kpi_row1[1]:
    with st.container(border=True):
        st.metric("Net Profit Margin", safe_metric(latest_ratios_row, npm_col, 2, "%"))

with kpi_row1[2]:
    with st.container(border=True):
        st.metric("Debt to Equity", safe_metric(latest_ratios_row, de_col, 2))

with kpi_row2[0]:
    with st.container(border=True):
        st.metric("Interest Coverage", safe_metric(latest_ratios_row, ic_col, 2))

with kpi_row2[1]:
    with st.container(border=True):
        st.metric("EPS", safe_metric(latest_ratios_row, eps_col, 2))

with kpi_row2[2]:
    with st.container(border=True):
        st.metric("Book Value / Share", safe_metric(latest_ratios_row, bvps_col, 2))

st.divider()

# ---------------------------------------------------------------------------
# 4. Radar chart
# ---------------------------------------------------------------------------
st.subheader("Radar Chart")

radar_path = RADAR_CHARTS_DIR / f"{selected_name}_radar.png"

with st.container(border=True):
    if radar_path.exists():
        st.image(str(radar_path), caption=f"{selected_name} — Financial Radar", width='stretch')
    else:
        st.info(
            f"No radar chart found for **{selected_name}** at "
            f"`reports/radar_charts/{selected_name}_radar.png`. "
            "It may not have been generated yet in Sprint 3."
        )

st.divider()

# ---------------------------------------------------------------------------
# 5. Plotly charts — financial metric trends
# ---------------------------------------------------------------------------
st.subheader("Financial Trends")

if company_ratios.empty or not ratios_year_col:
    st.info("No historical financial ratio data available for this company.")
else:
    trend_col1, trend_col2 = st.columns(2)

    with trend_col1:
        with st.container(border=True):
            st.markdown("**Profitability Trend**")
            profitability_metrics = [c for c in [npm_col, opm_col, roe_col] if c]
            if profitability_metrics:
                melted = company_ratios.melt(
                    id_vars=[ratios_year_col],
                    value_vars=profitability_metrics,
                    var_name="Metric",
                    value_name="Value",
                )
                fig_profit = px.line(
                    melted,
                    x=ratios_year_col,
                    y="Value",
                    color="Metric",
                    markers=True,
                    labels={ratios_year_col: "Year", "Value": "Percent (%)"},
                )
                fig_profit.update_layout(margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_profit, width='stretch')
            else:
                st.info("Profitability metrics not available.")

    with trend_col2:
        with st.container(border=True):
            st.markdown("**Leverage & Coverage Trend**")
            leverage_metrics = [c for c in [de_col, ic_col] if c]
            if leverage_metrics:
                melted = company_ratios.melt(
                    id_vars=[ratios_year_col],
                    value_vars=leverage_metrics,
                    var_name="Metric",
                    value_name="Value",
                )
                fig_leverage = px.bar(
                    melted,
                    x=ratios_year_col,
                    y="Value",
                    color="Metric",
                    barmode="group",
                    facet_col="Metric",
                    labels={ratios_year_col: "Year", "Value": ""},
                )
                fig_leverage.update_yaxes(matches=None, showticklabels=True)
                fig_leverage.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
                fig_leverage.update_layout(margin=dict(l=10, r=10, t=30, b=10), showlegend=False)
                st.plotly_chart(fig_leverage, width='stretch')
            else:
                st.info("Leverage/coverage metrics not available.")

    with st.container(border=True):
        st.markdown("**Per-Share Metrics Trend**")
        per_share_metrics = [c for c in [eps_col, bvps_col] if c]
        if per_share_metrics:
            melted = company_ratios.melt(
                id_vars=[ratios_year_col],
                value_vars=per_share_metrics,
                var_name="Metric",
                value_name="Value",
            )
            fig_per_share = px.bar(
                melted,
                x=ratios_year_col,
                y="Value",
                color="Metric",
                barmode="group",
                facet_col="Metric",
                labels={ratios_year_col: "Year", "Value": ""},
            )
            fig_per_share.update_yaxes(matches=None, showticklabels=True)
            fig_per_share.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
            fig_per_share.update_layout(margin=dict(l=10, r=10, t=30, b=10), showlegend=False)
            st.plotly_chart(fig_per_share, width='stretch')
        else:
            st.info("Per-share metrics not available.")