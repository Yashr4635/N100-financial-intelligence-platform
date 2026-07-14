"""
Company Analysis — N100 Financial Intelligence Platform

FIXES vs original:
1. Column-matching bug: `find_col()` was searching for `roe`/`net_profit_margin`
   etc. but the real CSV uses `_pct` suffixes (return_on_equity_pct,
   net_profit_margin_pct). That's why ROE / NPM / charts showed N/A —
   the columns existed, the code just wasn't looking for the right names.
2. Duplicate rows: your data has duplicate (company, year) rows (e.g. ABB
   2024 appears twice with different free_cash_flow_cr/capex_cr values).
   Deduped here (keeps latest by id) so KPIs and charts aren't silently
   double-counted or picking the wrong duplicate. This is a BAND-AID —
   fix the actual ETL/ingestion job, don't rely on the dashboard for this.
3. KPIs now show real YoY delta values instead of a static "Strong/
   Moderate/Weak" label with no numeric backing.
4. Caching added — csv was being re-read on every widget interaction.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Company Analysis | N100 Financial Intelligence Platform",
    page_icon="📊",
    layout="wide",
)

# ---------------------------------------------------
# Theme
# ---------------------------------------------------

NAVY_BG = "#0B1220"
NAVY_CARD = "#141C2B"
NAVY_CARD_HOVER = "#182236"
NAVY_BORDER = "#232E45"
EMERALD = "#10B981"
AMBER = "#F59E0B"
RED = "#EF4444"
BLUE = "#3B82F6"
VIOLET = "#8B5CF6"
TEXT_PRIMARY = "#E5E9F0"
TEXT_MUTED = "#8B96AB"


def hex_to_rgba(hex_color: str, alpha: float = 0.09) -> str:
    """Convert a '#RRGGBB' hex string into a Plotly-safe 'rgba(r,g,b,a)' string.
    Plotly's fillcolor validator rejects 8-digit hex (#RRGGBBAA) — it only
    accepts 6-digit hex, rgb(), rgba(), hsl()/hsla(), or named CSS colors.
    """
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
        .stApp {{ background-color: {NAVY_BG}; color: {TEXT_PRIMARY}; }}
        section[data-testid="stSidebar"] {{ background-color: {NAVY_CARD}; border-right: 1px solid {NAVY_BORDER}; }}

        .hero {{
            padding: 26px 30px;
            background: linear-gradient(135deg, {NAVY_CARD} 0%, #0F1830 100%);
            border: 1px solid {NAVY_BORDER};
            border-radius: 16px;
            margin-bottom: 22px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .hero h1 {{ font-size: 30px; font-weight: 800; margin: 0 0 4px 0; }}
        .hero p {{ font-size: 14.5px; color: {TEXT_MUTED}; margin: 0; }}
        .hero-badge {{
            font-size: 12px; font-weight: 700; padding: 6px 14px; border-radius: 999px;
            background: rgba(16,185,129,0.12); color: {EMERALD}; border: 1px solid rgba(16,185,129,0.3);
            white-space: nowrap;
        }}

        .section-header {{
            font-size: 19px; font-weight: 700; color: {TEXT_PRIMARY};
            margin: 26px 0 14px 0; padding-bottom: 8px; border-bottom: 1px solid {NAVY_BORDER};
            display: flex; align-items: center; gap: 8px;
        }}

        div[data-testid="stMetric"] {{
            background: {NAVY_CARD};
            border: 1px solid {NAVY_BORDER};
            border-radius: 14px;
            padding: 16px 18px;
            transition: border-color 0.15s ease;
        }}
        div[data-testid="stMetric"]:hover {{ border-color: {EMERALD}44; }}
        div[data-testid="stMetricLabel"] {{ color: {TEXT_MUTED}; font-weight: 600; }}
        div[data-testid="stMetricDelta"] svg {{ display: none; }}

        div[data-testid="stDataFrame"] {{
            border: 1px solid {NAVY_BORDER}; border-radius: 10px; overflow: hidden;
        }}

        .rating-pill {{
            display: inline-block; padding: 6px 16px; border-radius: 999px;
            font-weight: 700; font-size: 20px;
        }}
        .data-warning {{
            background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.3);
            border-radius: 10px; padding: 10px 16px; font-size: 13px; color: {AMBER};
            margin-bottom: 16px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

OUTPUT = Path("data/output")
DATA_FILE = OUTPUT / "company_health_scores.csv"


@st.cache_data
def load_data(path: Path, mtime: float) -> pd.DataFrame:
    """mtime is passed purely to bust the cache when the file changes on disk."""
    return pd.read_csv(path)


try:
    file_mtime = DATA_FILE.stat().st_mtime if DATA_FILE.exists() else 0
    df = load_data(DATA_FILE, file_mtime)
except Exception as e:
    st.error(f"Unable to load company data.\n\n{e}")
    st.stop()

# ---------------------------------------------------
# Column aliasing — now matches the ACTUAL schema
# (return_on_equity_pct, net_profit_margin_pct, etc.)
# with the old candidates kept as fallback for other
# dataset versions.
# ---------------------------------------------------


def find_col(candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


col_company = find_col(["company_id", "company", "symbol", "ticker"])
col_year = find_col(["year", "fiscal_year", "fy"])
col_health = find_col(["health_score", "health"])
col_rating = find_col(["rating"])
col_roe = find_col(["return_on_equity_pct", "roe", "return_on_equity"])
col_npm = find_col(
    ["net_profit_margin_pct", "net_profit_margin", "npm", "profit_margin"]
)
col_opm = find_col(["operating_profit_margin_pct", "operating_profit_margin", "opm"])
col_de = find_col(["debt_to_equity", "debt_equity_ratio", "de_ratio"])
col_ic = find_col(["interest_coverage"])
col_at = find_col(["asset_turnover"])
col_fcf = find_col(["free_cash_flow_cr", "free_cash_flow"])
col_capex = find_col(["capex_cr", "capex"])
col_eps = find_col(["earnings_per_share", "eps"])
col_id = find_col(["id"])

if col_company is None:
    st.error("No company identifier column found in dataset (expected 'company_id').")
    st.stop()

# ---------------------------------------------------
# Dedup: drop duplicate (company, year) rows. Your source
# data has these (see ABB 2024 x2, 2023 x2, 2022 x2 in the
# raw CSV) — this is an upstream ETL bug, not something a
# dashboard should have to work around. Fix the pipeline.
# ---------------------------------------------------

dedup_subset = [c for c in [col_company, col_year] if c is not None]
duplicates_found = 0
if dedup_subset:
    before = len(df)
    sort_col = col_id if col_id else df.columns[0]
    df = df.sort_values(sort_col).drop_duplicates(subset=dedup_subset, keep="last")
    duplicates_found = before - len(df)

# ---------------------------------------------------
# Hero
# ---------------------------------------------------

st.markdown(
    f"""
    <div class="hero">
        <div>
            <h1>📊 Company Analysis</h1>
            <p>Deep-dive into individual company financial performance — N100 Financial Intelligence Platform</p>
        </div>
        <div class="hero-badge">{df[col_company].nunique()} Companies Tracked</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if duplicates_found > 0:
    st.markdown(
        f'<div class="data-warning">⚠️ Removed {duplicates_found} duplicate (company, year) '
        f"record(s) from the source data. This is a data pipeline issue — check your ETL job.</div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------
# Company selector
# ---------------------------------------------------

companies = sorted(df[col_company].dropna().unique().tolist())
if not companies:
    st.warning("No companies available in the dataset.")
    st.stop()

sel_col, _ = st.columns([1, 2])
with sel_col:
    selected_company = st.selectbox("Select Company", companies)

company_df = df[df[col_company] == selected_company].copy()

if col_year and col_year in company_df.columns:
    company_df = company_df.sort_values(col_year)

if company_df.empty:
    st.warning("No records found for the selected company.")
    st.stop()

latest_row = company_df.iloc[-1]
prior_row = company_df.iloc[-2] if len(company_df) > 1 else None


def safe_value(row, col, decimals=2, suffix=""):
    if col is None or col not in row.index:
        return "N/A"
    val = row[col]
    if pd.isna(val):
        return "N/A"
    try:
        return f"{round(float(val), decimals)}{suffix}"
    except (TypeError, ValueError):
        return str(val)


def yoy_delta(col, decimals=2, suffix=""):
    """Real numeric YoY delta, not a canned label."""
    if col is None or prior_row is None:
        return None
    if col not in latest_row.index or col not in prior_row.index:
        return None
    try:
        curr, prev = float(latest_row[col]), float(prior_row[col])
        if pd.isna(curr) or pd.isna(prev):
            return None
        diff = round(curr - prev, decimals)
        sign = "+" if diff >= 0 else ""
        return f"{sign}{diff}{suffix} YoY"
    except (TypeError, ValueError):
        return None


RATING_COLORS = {
    "excellent": EMERALD,
    "strong": EMERALD,
    "good": BLUE,
    "moderate": AMBER,
    "average": AMBER,
    "weak": RED,
    "poor": RED,
}

# ---------------------------------------------------
# KPI Row
# ---------------------------------------------------

period_label = (
    f" ({int(latest_row[col_year])})"
    if col_year and not pd.isna(latest_row.get(col_year, None))
    else ""
)
st.markdown(
    f'<div class="section-header">Key Performance Indicators{period_label}</div>',
    unsafe_allow_html=True,
)

k1, k2, k3, k4, k5, k6 = st.columns(6)

with k1:
    st.metric(
        "Health Score",
        safe_value(latest_row, col_health, decimals=1),
        delta=yoy_delta(col_health, decimals=1),
    )

with k2:
    rating_val = safe_value(latest_row, col_rating, decimals=0) if col_rating else "N/A"
    color = RATING_COLORS.get(str(rating_val).lower(), TEXT_PRIMARY)
    st.markdown(
        f'<div style="background:{NAVY_CARD};border:1px solid {NAVY_BORDER};border-radius:14px;'
        f'padding:16px 18px;">'
        f'<div style="color:{TEXT_MUTED};font-weight:600;font-size:14px;margin-bottom:6px;">Rating</div>'
        f'<div class="rating-pill" style="color:{color};">{rating_val}</div></div>',
        unsafe_allow_html=True,
    )

with k3:
    st.metric(
        "ROE",
        safe_value(latest_row, col_roe, suffix="%"),
        delta=yoy_delta(col_roe, suffix="%"),
    )

with k4:
    st.metric(
        "Net Profit Margin",
        safe_value(latest_row, col_npm, suffix="%"),
        delta=yoy_delta(col_npm, suffix="%"),
    )

with k5:
    st.metric(
        "Debt to Equity",
        safe_value(latest_row, col_de, decimals=3),
        delta=yoy_delta(col_de, decimals=3),
    )

with k6:
    st.metric("EPS", safe_value(latest_row, col_eps), delta=yoy_delta(col_eps))

st.write("")

# ---------------------------------------------------
# Trend charts
# ---------------------------------------------------

st.markdown(
    '<div class="section-header">Historical Trends</div>', unsafe_allow_html=True
)

if col_year is None:
    st.info(
        "No year/fiscal-period column found — trend charts require a time dimension."
    )
elif len(company_df) < 2:
    st.info(
        "Only one historical record for this company — trends require at least two periods."
    )
else:
    chart_specs = [
        ("ROE", col_roe, EMERALD, "%"),
        ("Net Profit Margin", col_npm, AMBER, "%"),
        ("EPS", col_eps, BLUE, ""),
        ("Debt to Equity", col_de, VIOLET, ""),
        ("Operating Profit Margin", col_opm, "#EC4899", "%"),
        ("Free Cash Flow (Cr)", col_fcf, "#14B8A6", ""),
    ]
    chart_specs = [
        c
        for c in chart_specs
        if c[1] is not None and not company_df[c[1]].dropna().empty
    ]

    for row_start in range(0, len(chart_specs), 3):
        row_specs = chart_specs[row_start : row_start + 3]
        chart_cols = st.columns(3)
        for chart_col, (title, metric_col, color, suffix) in zip(chart_cols, row_specs):
            with chart_col:
                st.markdown(f"**{title} Over Time**")
                plot_df = company_df.dropna(subset=[metric_col, col_year])

                fig = go.Figure(
                    go.Scatter(
                        x=plot_df[col_year],
                        y=plot_df[metric_col],
                        mode="lines+markers",
                        line=dict(color=color, width=3, shape="spline"),
                        marker=dict(
                            size=7, color=color, line=dict(width=1, color=NAVY_BG)
                        ),
                        fill="tozeroy",
                        fillcolor=hex_to_rgba(color, alpha=0.09),
                        hovertemplate=f"%{{x}}<br>%{{y}}{suffix}<extra></extra>",
                    )
                )
                fig.update_layout(
                    plot_bgcolor=NAVY_CARD,
                    paper_bgcolor=NAVY_CARD,
                    font_color=TEXT_PRIMARY,
                    height=300,
                    margin=dict(l=10, r=10, t=10, b=10),
                    xaxis=dict(title="Year", gridcolor=NAVY_BORDER, type="category"),
                    yaxis=dict(title=title, gridcolor=NAVY_BORDER),
                    hoverlabel=dict(bgcolor=NAVY_CARD_HOVER, font_color=TEXT_PRIMARY),
                )
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{title}")

    if not chart_specs:
        st.info("No metric data available for charting.")

st.write("")

# ---------------------------------------------------
# Full historical table
# ---------------------------------------------------

st.markdown(
    '<div class="section-header">Full Historical Record</div>', unsafe_allow_html=True
)

display_df = company_df.copy()
if col_id and col_id in display_df.columns:
    display_df = display_df.drop(columns=[col_id])
if col_year:
    display_df = display_df.sort_values(col_year, ascending=False)

col_config = {}
if col_health and col_health in display_df.columns:
    col_config[col_health] = st.column_config.ProgressColumn(
        "Health Score", min_value=0, max_value=100, format="%.1f"
    )

st.dataframe(
    display_df.fillna("N/A"),
    use_container_width=True,
    hide_index=True,
    column_config=col_config,
)

table_col1, table_col2 = st.columns([1, 5])
with table_col1:
    st.download_button(
        "⬇ Download CSV",
        data=display_df.to_csv(index=False).encode("utf-8"),
        file_name=f"{selected_company}_historical_record.csv",
        mime="text/csv",
        use_container_width=True,
    )
with table_col2:
    st.caption(f"{len(company_df)} historical record(s) found for {selected_company}.")
