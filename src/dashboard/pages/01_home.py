"""
Home page.

Executive overview of the analytics produced in Sprints 1-3:
    - KPI cards
    - Plotly charts (health score distribution, sector distribution,
      top 10 companies by health score)
    - Recent insights
    - Alerts (weak health scores, missing values, flagged companies)

This page only READS the pre-computed Sprint 1-3 output CSVs. No
analytics logic is implemented or modified here.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# src/dashboard/pages/01_home.py -> project root is 3 levels up
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data" / "output"

HEALTH_SCORES_PATH = DATA_DIR / "company_health_scores.csv"
FINANCIAL_RATIOS_PATH = DATA_DIR / "financial_ratios_calculated.csv"
SECTOR_ANALYSIS_PATH = DATA_DIR / "sector_analysis.csv"

# Thresholds
WEAK_HEALTH_SCORE_THRESHOLD = 40


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
    Used to stay resilient to minor naming differences in Sprint 1-3
    outputs without changing any analytics code.
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


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
health_df = load_csv(HEALTH_SCORES_PATH)
ratios_df = load_csv(FINANCIAL_RATIOS_PATH)
sector_df = load_csv(SECTOR_ANALYSIS_PATH)

# Resolve likely column names (falls back to None if not found)
# NOTE: company_health_scores.csv identifies companies via `company_id`
# (no company name column exists), and sector membership lives in
# sector_analysis.csv under `broad_sector`.
company_col = find_column(
    health_df, ["company", "company_name", "ticker", "symbol", "company_id", "id"]
)
health_score_col = find_column(health_df, ["health_score", "healthscore", "score"])
sector_col = find_column(
    health_df, ["sector", "sector_name", "industry", "broad_sector"]
) or find_column(sector_df, ["sector", "sector_name", "industry", "broad_sector"])
flag_col = find_column(
    health_df, ["flag", "status", "health_flag", "risk_flag", "classification"]
)

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("🏠 Home")
st.write(
    "Executive overview of company health, sector composition, and key "
    "signals derived from the Sprint 1-3 analytics outputs."
)

if health_df.empty:
    st.warning(
        f"Could not find or load `{HEALTH_SCORES_PATH.relative_to(PROJECT_ROOT)}`. "
        "KPI cards, charts, and alerts below will be limited until this file is available."
    )

st.divider()

# ---------------------------------------------------------------------------
# 1. Executive KPI cards
# ---------------------------------------------------------------------------
st.subheader("Executive Summary")

total_companies = int(health_df[company_col].nunique()) if company_col else 0

if sector_col and sector_col in health_df.columns:
    total_sectors = int(health_df[sector_col].nunique())
elif sector_col and sector_col in sector_df.columns:
    total_sectors = int(sector_df[sector_col].nunique())
else:
    total_sectors = 0

avg_health_score = (
    round(health_df[health_score_col].mean(), 1)
    if health_score_col and not health_df.empty
    else None
)

def format_identifier(value) -> str:
    """Render a company identifier cleanly (avoid '23.0' for numeric IDs)."""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


if company_col and health_score_col and not health_df.empty:
    top_row = health_df.loc[health_df[health_score_col].idxmax()]
    top_company_name = format_identifier(top_row[company_col])
    if company_col.lower() in ("company_id", "id"):
        top_company_name = f"Company #{top_company_name}"
    top_company_score = round(top_row[health_score_col], 1)
else:
    top_company_name = "N/A"
    top_company_score = None

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    with st.container(border=True):
        st.metric("Total Companies", f"{total_companies:,}" if total_companies else "N/A")

with kpi2:
    with st.container(border=True):
        st.metric("Total Sectors", f"{total_sectors:,}" if total_sectors else "N/A")

with kpi3:
    with st.container(border=True):
        st.metric(
            "Average Health Score",
            f"{avg_health_score}" if avg_health_score is not None else "N/A",
        )

with kpi4:
    with st.container(border=True):
        st.metric(
            "Highest Health Score",
            top_company_name,
            delta=f"Score: {top_company_score}" if top_company_score is not None else None,
        )

st.divider()

# ---------------------------------------------------------------------------
# 2. Plotly charts
# ---------------------------------------------------------------------------
st.subheader("Analytics Overview")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    with st.container(border=True):
        st.markdown("**Health Score Distribution**")
        if health_score_col and not health_df.empty:
            fig_dist = px.histogram(
                health_df,
                x=health_score_col,
                nbins=20,
                labels={health_score_col: "Health Score"},
            )
            fig_dist.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                bargap=0.05,
            )
            st.plotly_chart(fig_dist, width='stretch')
        else:
            st.info("Health score data not available.")

with chart_col2:
    with st.container(border=True):
        st.markdown("**Sector Distribution**")
        if sector_col and sector_col in health_df.columns:
            sector_counts = health_df[sector_col].value_counts().reset_index()
            sector_counts.columns = ["Sector", "Count"]
            fig_sector = px.pie(
                sector_counts,
                names="Sector",
                values="Count",
                hole=0.4,
            )
            fig_sector.update_layout(margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_sector, width='stretch')
        elif not sector_df.empty:
            st.dataframe(sector_df, width='stretch', hide_index=True)
        else:
            st.info("Sector data not available.")

with st.container(border=True):
    st.markdown("**Top 10 Companies by Health Score**")
    if company_col and health_score_col and not health_df.empty:
        top10 = (
            health_df[[company_col, health_score_col]]
            .dropna(subset=[health_score_col])
            .sort_values(by=health_score_col, ascending=False)
            .head(10)
        )
        fig_top10 = px.bar(
            top10.sort_values(by=health_score_col, ascending=True),
            x=health_score_col,
            y=company_col,
            orientation="h",
            labels={health_score_col: "Health Score", company_col: "Company"},
        )
        fig_top10.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_top10, width='stretch')
    else:
        st.info("Company health score data not available.")

st.divider()

# ---------------------------------------------------------------------------
# 3. Recent insights
# ---------------------------------------------------------------------------
st.subheader("Recent Insights")

with st.container(border=True):
    insights = []

    if avg_health_score is not None:
        insights.append(f"Average health score across all companies is **{avg_health_score}**.")

    if company_col and health_score_col and not health_df.empty:
        insights.append(
            f"**{top_company_name}** currently holds the highest health score at "
            f"**{top_company_score}**."
        )
        weak_count = int((health_df[health_score_col] < WEAK_HEALTH_SCORE_THRESHOLD).sum())
        if weak_count:
            insights.append(
                f"**{weak_count}** compan{'y' if weak_count == 1 else 'ies'} "
                f"currently score below the weak-health threshold of "
                f"{WEAK_HEALTH_SCORE_THRESHOLD}."
            )

    if sector_col and sector_col in health_df.columns and not health_df.empty:
        top_sector = health_df[sector_col].value_counts().idxmax()
        insights.append(f"**{top_sector}** is the most represented sector in the dataset.")

    if not insights:
        st.info("No insights available yet — analytics outputs could not be loaded.")
    else:
        for insight in insights:
            st.markdown(f"- {insight}")

st.divider()

# ---------------------------------------------------------------------------
# 4. Alerts
# ---------------------------------------------------------------------------
st.subheader("Alerts")

alert_col1, alert_col2, alert_col3 = st.columns(3)

# --- Low health score alert -------------------------------------------------
with alert_col1:
    with st.container(border=True):
        st.markdown("**⚠️ Low Health Score (< 40)**")
        if health_score_col and not health_df.empty:
            low_score_df = health_df[health_df[health_score_col] < WEAK_HEALTH_SCORE_THRESHOLD]
            if not low_score_df.empty:
                st.error(f"{len(low_score_df)} companies below threshold")
                cols_to_show = [c for c in [company_col, health_score_col] if c]
                st.dataframe(
                    low_score_df[cols_to_show].sort_values(by=health_score_col),
                    width='stretch',
                    hide_index=True,
                )
            else:
                st.success("No companies below the threshold.")
        else:
            st.info("Health score data not available.")

# --- Missing values alert ---------------------------------------------------
with alert_col2:
    with st.container(border=True):
        st.markdown("**🧩 Missing Values**")
        missing_summary = []
        for label, df in [
            ("Health Scores", health_df),
            ("Financial Ratios", ratios_df),
            ("Sector Analysis", sector_df),
        ]:
            if not df.empty:
                missing_count = int(df.isna().sum().sum())
                if missing_count:
                    missing_summary.append((label, missing_count))

        if missing_summary:
            st.warning(f"{len(missing_summary)} dataset(s) contain missing values")
            for label, count in missing_summary:
                st.markdown(f"- {label}: **{count}** missing values")
        else:
            st.success("No missing values detected.")

# --- Weak-flagged companies alert -------------------------------------------
with alert_col3:
    with st.container(border=True):
        st.markdown("**🚩 Flagged as Weak**")
        if flag_col and not health_df.empty:
            weak_mask = (
                health_df[flag_col]
                .astype(str)
                .str.strip()
                .str.lower()
                .isin(["weak", "risk", "poor", "at risk", "flagged"])
            )
            weak_df = health_df[weak_mask]
            if not weak_df.empty:
                st.error(f"{len(weak_df)} companies flagged as weak")
                cols_to_show = [c for c in [company_col, flag_col] if c]
                st.dataframe(weak_df[cols_to_show], width='stretch', hide_index=True)
            else:
                st.success("No companies flagged as weak.")
        else:
            st.info("No weak-flag column found in the health scores dataset.")