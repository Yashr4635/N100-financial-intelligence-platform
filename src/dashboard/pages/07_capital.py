"""
Capital Allocation Dashboard page.

Built from Sprint 1-3 outputs:
    - data/output/financial_ratios_calculated.csv (FCF, CapEx, CFO, Debt history)
    - data/output/company_health_scores.csv        (fallback source for the
      same metrics, and the company's overall rating for context)

This page only READS the pre-computed Sprint 1-3 outputs. The "Capital
Allocation Health" status below is a simple, transparent rule-of-thumb
computed here for display purposes only (based on FCF, debt, and cash
flow trends) -- it does not modify or replace any Sprint 1-3 analytics.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# src/dashboard/pages/07_capital.py -> project root is 3 levels up
PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"

FINANCIAL_RATIOS_PATH = OUTPUT_DIR / "financial_ratios_calculated.csv"
HEALTH_SCORES_PATH = OUTPUT_DIR / "company_health_scores.csv"


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


def format_value(value, decimals=2, suffix="", prefix=""):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "N/A"
    if isinstance(value, (int, float)):
        return f"{prefix}{round(value, decimals):,}{suffix}"
    return f"{prefix}{value}{suffix}"


def first_last(df: pd.DataFrame, col: str | None):
    """Return (first_available_value, last_available_value) for a metric,
    handling missing years/values gracefully."""
    if not col or col not in df.columns:
        return None, None
    series = df[["Year", col]].dropna(subset=[col]).sort_values(by="Year")
    if series.empty:
        return None, None
    return series.iloc[0][col], series.iloc[-1][col]


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
ratios_df = load_csv(FINANCIAL_RATIOS_PATH)
health_df = load_csv(HEALTH_SCORES_PATH)

# Resolve column names -------------------------------------------------------
ratios_id_col = find_column(ratios_df, ["company_id", "id"])
ratios_year_col = find_column(ratios_df, ["year"])
fcf_col = find_column(ratios_df, ["free_cash_flow_cr", "free_cash_flow"])
capex_col = find_column(ratios_df, ["capex_cr", "capex"])
cfo_col = find_column(ratios_df, ["cash_from_operations_cr", "cash_from_operations"])
debt_col = find_column(ratios_df, ["total_debt_cr", "total_debt"])
fcf_to_debt_col = find_column(ratios_df, ["fcf_to_debt"])

health_id_col = find_column(health_df, ["company_id", "id"])
health_year_col = find_column(health_df, ["year"])
rating_col = find_column(health_df, ["rating"])
health_score_col = find_column(health_df, ["health_score", "score"])
# Fallback lookups in case financial_ratios_calculated.csv is unavailable but
# company_health_scores.csv carries the same capital metrics.
fcf_col = fcf_col or find_column(health_df, ["free_cash_flow_cr", "free_cash_flow"])
capex_col = capex_col or find_column(health_df, ["capex_cr", "capex"])
cfo_col = cfo_col or find_column(health_df, ["cash_from_operations_cr", "cash_from_operations"])
debt_col = debt_col or find_column(health_df, ["total_debt_cr", "total_debt"])
fcf_to_debt_col = fcf_to_debt_col or find_column(health_df, ["fcf_to_debt"])

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("💰 Capital")
st.write(
    "Free cash flow, capital expenditure, operating cash flow, and debt "
    "trends for a selected company."
)

if ratios_df.empty and health_df.empty:
    st.warning(
        "Could not load capital data. Please check that "
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
    health_extra_cols = [c for c in [rating_col, health_score_col] if c and c not in ratios_clean.columns]
    timeline_df = pd.merge(
        ratios_clean,
        health_clean[["_id_key", health_year_col] + health_extra_cols],
        left_on=["_id_key", ratios_year_col],
        right_on=["_id_key", health_year_col],
        how="outer",
        suffixes=("", "_health"),
    )
    timeline_df["Year"] = timeline_df[ratios_year_col].combine_first(timeline_df[health_year_col])
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

available_ids = sorted(timeline_df["_id_key"].dropna().unique().tolist())

if not available_ids:
    st.error("No companies found in the capital allocation datasets.")
    st.stop()

# ---------------------------------------------------------------------------
# 1. Company Selector
# ---------------------------------------------------------------------------
st.subheader("Select a Company")

selected_id = st.selectbox("Company", options=available_ids)

company_timeline = timeline_df[timeline_df["_id_key"] == selected_id].copy()
company_timeline = company_timeline.dropna(subset=["Year"])
company_timeline["Year"] = company_timeline["Year"].astype(int)
company_timeline = company_timeline.sort_values(by="Year")

latest_row = company_timeline.iloc[-1] if not company_timeline.empty else None

st.divider()

# ---------------------------------------------------------------------------
# 2. KPI Cards (latest available values)
# ---------------------------------------------------------------------------
st.subheader("Key Capital Metrics (Latest Available Year)")

kpi_cols = st.columns(5)

with kpi_cols[0]:
    with st.container(border=True):
        st.metric(
            "Free Cash Flow (₹ Cr)",
            format_value(latest_row[fcf_col], 1) if latest_row is not None and fcf_col else "N/A",
        )

with kpi_cols[1]:
    with st.container(border=True):
        st.metric(
            "CapEx (₹ Cr)",
            format_value(latest_row[capex_col], 1) if latest_row is not None and capex_col else "N/A",
        )

with kpi_cols[2]:
    with st.container(border=True):
        st.metric(
            "Cash From Operations (₹ Cr)",
            format_value(latest_row[cfo_col], 1) if latest_row is not None and cfo_col else "N/A",
        )

with kpi_cols[3]:
    with st.container(border=True):
        st.metric(
            "Total Debt (₹ Cr)",
            format_value(latest_row[debt_col], 1) if latest_row is not None and debt_col else "N/A",
        )

with kpi_cols[4]:
    with st.container(border=True):
        st.metric(
            "FCF to Debt Ratio",
            format_value(latest_row[fcf_to_debt_col], 3)
            if latest_row is not None and fcf_to_debt_col
            else "N/A",
        )

st.divider()

# ---------------------------------------------------------------------------
# 3. Interactive Plotly Charts
# ---------------------------------------------------------------------------
st.subheader("Trends")

trend_specs = [
    ("Free Cash Flow Trend", fcf_col, "₹ Cr"),
    ("CapEx Trend", capex_col, "₹ Cr"),
    ("Cash From Operations Trend", cfo_col, "₹ Cr"),
    ("Total Debt Trend", debt_col, "₹ Cr"),
]

available_trend_specs = [(label, col, unit) for label, col, unit in trend_specs if col]

if not available_trend_specs:
    st.info("None of the expected capital metrics were found in the source data.")
else:
    for i in range(0, len(available_trend_specs), 2):
        row_specs = available_trend_specs[i : i + 2]
        row_cols = st.columns(2)
        for col_widget, (label, metric_col, unit) in zip(row_cols, row_specs):
            with col_widget:
                with st.container(border=True):
                    st.markdown(f"**{label}**")
                    series = company_timeline[["Year", metric_col]].dropna(subset=[metric_col])
                    if series.empty:
                        st.info(f"No historical data available for {label.lower()}.")
                    elif len(series) == 1:
                        st.info(
                            f"Only one data point available "
                            f"({int(series.iloc[0]['Year'])}: "
                            f"{format_value(series.iloc[0][metric_col], 1)} {unit})."
                        )
                    else:
                        fig = px.line(
                            series,
                            x="Year",
                            y=metric_col,
                            markers=True,
                            labels={metric_col: f"{label.replace(' Trend', '')} ({unit})"},
                        )
                        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
                        fig.update_xaxes(dtick=1)
                        st.plotly_chart(fig, width='stretch')

# --- FCF vs Debt Comparison --------------------------------------------------
with st.container(border=True):
    st.markdown("**FCF vs Debt Comparison**")
    if fcf_col and debt_col:
        combo_df = company_timeline[["Year", fcf_col, debt_col]].dropna(
            subset=[fcf_col, debt_col], how="all"
        )
        if combo_df.empty:
            st.info("No overlapping FCF / Debt data available for this company.")
        elif len(combo_df) == 1:
            st.info(
                f"Only one data point available "
                f"({int(combo_df.iloc[0]['Year'])}: "
                f"FCF {format_value(combo_df.iloc[0][fcf_col], 1)}, "
                f"Debt {format_value(combo_df.iloc[0][debt_col], 1)})."
            )
        else:
            fig_combo = make_subplots(specs=[[{"secondary_y": True}]])
            fig_combo.add_trace(
                go.Bar(x=combo_df["Year"], y=combo_df[fcf_col], name="Free Cash Flow (₹ Cr)"),
                secondary_y=False,
            )
            fig_combo.add_trace(
                go.Scatter(
                    x=combo_df["Year"],
                    y=combo_df[debt_col],
                    name="Total Debt (₹ Cr)",
                    mode="lines+markers",
                    line=dict(color="#EF553B"),
                ),
                secondary_y=True,
            )
            fig_combo.update_yaxes(title_text="Free Cash Flow (₹ Cr)", secondary_y=False)
            fig_combo.update_yaxes(title_text="Total Debt (₹ Cr)", secondary_y=True)
            fig_combo.update_xaxes(title_text="Year", dtick=1)
            fig_combo.update_layout(margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_combo, width='stretch')
    else:
        st.info("FCF and/or Total Debt data not available for this comparison.")

st.divider()

# ---------------------------------------------------------------------------
# 4. Capital Allocation Health
# ---------------------------------------------------------------------------
st.subheader("Capital Allocation Health")

fcf_first, fcf_last = first_last(company_timeline, fcf_col)
capex_first, capex_last = first_last(company_timeline, capex_col)
cfo_first, cfo_last = first_last(company_timeline, cfo_col)
debt_first, debt_last = first_last(company_timeline, debt_col)
fcf_to_debt_first, fcf_to_debt_last = first_last(company_timeline, fcf_to_debt_col)

# A simple, transparent rule-of-thumb score for display purposes only.
# It does not replace or modify the underlying Sprint 1-3 analytics.
score = 0
scoring_notes = []

if fcf_last is not None:
    if fcf_last > 0:
        score += 2
    else:
        score -= 1

if fcf_first is not None and fcf_last is not None and fcf_first != 0:
    if fcf_last > fcf_first:
        score += 1

if cfo_last is not None:
    if cfo_last > 0:
        score += 2
    else:
        score -= 1

if fcf_to_debt_last is not None:
    if fcf_to_debt_last >= 0.15:
        score += 2
    elif fcf_to_debt_last >= 0.05:
        score += 1
    elif fcf_to_debt_last < 0:
        score -= 2

if debt_first is not None and debt_last is not None and debt_first > 0:
    debt_growth = (debt_last - debt_first) / debt_first
    if debt_growth > 0.5:
        score -= 2
    elif debt_growth < 0:
        score += 1

has_enough_data = any(
    v is not None for v in [fcf_last, cfo_last, fcf_to_debt_last, debt_last]
)

if not has_enough_data:
    status = "Unavailable"
elif score >= 5:
    status = "Excellent"
elif score >= 2:
    status = "Good"
elif score >= 0:
    status = "Moderate"
else:
    status = "Weak"

status_display = {
    "Excellent": ("🟢", "success"),
    "Good": ("🔵", "info"),
    "Moderate": ("🟠", "warning"),
    "Weak": ("🔴", "error"),
    "Unavailable": ("⚪", "info"),
}

with st.container(border=True):
    icon, box_type = status_display[status]
    message = f"{icon} **Capital Allocation Health: {status}**"
    if status == "Unavailable":
        st.info(f"{message} — not enough FCF/Debt/Cash Flow data to assess.")
    elif box_type == "success":
        st.success(message)
    elif box_type == "warning":
        st.warning(message)
    elif box_type == "error":
        st.error(message)
    else:
        st.info(message)

st.divider()

# ---------------------------------------------------------------------------
# 5. Insights Section
# ---------------------------------------------------------------------------
st.subheader("Insights")

with st.container(border=True):
    insights = []

    if cfo_last is not None and cfo_last > 0:
        insights.append("💵 **Strong cash generation** — cash from operations is currently positive.")
    elif cfo_last is not None and cfo_last <= 0:
        insights.append("⚠️ **Weak cash generation** — cash from operations is currently negative or zero.")

    if debt_first is not None and debt_last is not None and debt_first > 0:
        debt_growth_pct = ((debt_last - debt_first) / debt_first) * 100
        if debt_growth_pct > 30:
            insights.append(
                f"📈 **High debt burden** — total debt has grown by "
                f"{format_value(debt_growth_pct, 1)}% since the earliest recorded year."
            )
        elif debt_growth_pct < -10:
            insights.append(
                f"📉 **Deleveraging** — total debt has fallen by "
                f"{format_value(abs(debt_growth_pct), 1)}% since the earliest recorded year."
            )

    if fcf_first is not None and fcf_last is not None:
        if fcf_last > fcf_first:
            insights.append("📈 **Improving FCF** — free cash flow has increased over the observed period.")
        elif fcf_last < fcf_first:
            insights.append("📉 **Declining FCF** — free cash flow has decreased over the observed period.")

    if capex_first is not None and capex_last is not None:
        if capex_last < capex_first:
            insights.append("📉 **Declining CapEx** — capital expenditure has decreased over the observed period.")
        elif capex_last > capex_first:
            insights.append("📈 **Rising CapEx** — capital expenditure has increased over the observed period.")

    if fcf_to_debt_last is not None:
        if fcf_to_debt_last >= 0.15:
            insights.append("✅ **Healthy FCF-to-Debt ratio** — cash flow comfortably covers outstanding debt.")
        elif fcf_to_debt_last < 0:
            insights.append("⚠️ **Negative FCF-to-Debt ratio** — free cash flow is not covering debt obligations.")

    if not insights:
        st.info("Not enough data available to generate capital allocation insights.")
    else:
        for insight in insights:
            st.markdown(f"- {insight}")