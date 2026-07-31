"""
Sector Analysis Dashboard page.

Built from Sprint 1-3 outputs:
    - data/output/sector_analysis.csv            (sector-level aggregates)
    - data/output/company_health_scores.csv       (per-company health/rating history)
    - data/output/financial_ratios_calculated.csv (per-company ratio history)

Sector-level KPIs, charts, and insights are driven entirely by
sector_analysis.csv. Company-level views (scatter, treemap, top
companies within a sector) additionally need a per-company sector
column; if none of the loaded files provide one, those views degrade
gracefully instead of guessing or showing incorrect groupings.

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
# src/dashboard/pages/06_sectors.py -> project root is 3 levels up
PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"

SECTOR_ANALYSIS_PATH = OUTPUT_DIR / "sector_analysis.csv"
HEALTH_SCORES_PATH = OUTPUT_DIR / "company_health_scores.csv"
FINANCIAL_RATIOS_PATH = OUTPUT_DIR / "financial_ratios_calculated.csv"


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


def format_value(value, decimals=2, suffix=""):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "N/A"
    if isinstance(value, (int, float)):
        return f"{round(value, decimals)}{suffix}"
    return f"{value}{suffix}"


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
sector_df = load_csv(SECTOR_ANALYSIS_PATH)
health_df = load_csv(HEALTH_SCORES_PATH)
ratios_df = load_csv(FINANCIAL_RATIOS_PATH)

# Resolve sector_analysis.csv columns ----------------------------------------
sector_name_col = find_column(sector_df, ["broad_sector", "sector", "sector_name", "industry"])
companies_count_col = find_column(sector_df, ["companies", "company_count", "num_companies"])
avg_health_col = find_column(sector_df, ["avg_health_score", "average_health_score"])
avg_roe_col = find_column(sector_df, ["avg_roe", "average_roe"])
avg_npm_col = find_column(
    sector_df, ["avg_profit_margin", "avg_net_profit_margin", "average_profit_margin"]
)
avg_de_col = find_column(sector_df, ["avg_debt_to_equity", "average_debt_to_equity"])

# Resolve company-level columns ----------------------------------------------
health_id_col = find_column(health_df, ["company_id", "id"])
health_year_col = find_column(health_df, ["year"])
health_score_col = find_column(health_df, ["health_score", "score"])
rating_col = find_column(health_df, ["rating"])
health_sector_col = find_column(health_df, ["sector", "broad_sector", "industry"])

ratios_id_col = find_column(ratios_df, ["company_id", "id"])
ratios_year_col = find_column(ratios_df, ["year"])
roe_col = find_column(ratios_df, ["return_on_equity_pct", "roe_pct", "roe"])
npm_col = find_column(ratios_df, ["net_profit_margin_pct", "net_profit_margin"])
de_col = find_column(ratios_df, ["debt_to_equity"])
ratios_sector_col = find_column(ratios_df, ["sector", "broad_sector", "industry"])

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("🏭 Sectors")
st.write(
    "Sector-level health, profitability, and leverage trends derived from "
    "the Sprint 1-3 analytics outputs."
)

if sector_df.empty or not sector_name_col:
    st.warning(
        "Could not load `data/output/sector_analysis.csv`. "
        "Sector KPIs, charts, and insights cannot be shown without it."
    )
    st.stop()

st.divider()

# ---------------------------------------------------------------------------
# Build a one-row-per-company snapshot (latest year available) from the
# health score and ratio files, for company-level views.
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
    company_timeline = pd.merge(
        ratios_clean,
        health_clean[
            ["_id_key", health_year_col, health_score_col, rating_col]
            + ([health_sector_col] if health_sector_col else [])
        ],
        left_on=["_id_key", ratios_year_col],
        right_on=["_id_key", health_year_col],
        how="outer",
        suffixes=("", "_health"),
    )
    company_timeline["Year"] = company_timeline[ratios_year_col].combine_first(
        company_timeline[health_year_col]
    )
elif not ratios_clean.empty:
    company_timeline = ratios_clean.copy()
    company_timeline["Year"] = company_timeline[ratios_year_col]
elif not health_clean.empty:
    company_timeline = health_clean.copy()
    company_timeline["Year"] = company_timeline[health_year_col]
else:
    company_timeline = pd.DataFrame()

company_snapshot = pd.DataFrame()
if not company_timeline.empty:
    company_snapshot = (
        company_timeline.dropna(subset=["Year"])
        .sort_values(by="Year")
        .drop_duplicates(subset="_id_key", keep="last")
    )

# A per-company sector column, if either source file happens to provide one.
company_sector_col = health_sector_col or ratios_sector_col
company_sector_available = bool(
    company_sector_col and not company_snapshot.empty and company_sector_col in company_snapshot.columns
)

if not company_sector_available:
    st.info(
        "Per-company sector information is not available in "
        "`company_health_scores.csv` or `financial_ratios_calculated.csv`. "
        "Sector-level KPIs, charts, and insights below use "
        "`sector_analysis.csv` directly; company-level views that need a "
        "sector-per-company mapping (scatter plot, treemap, and the top "
        "companies table) will fall back to sector-level or overall views "
        "where noted."
    )

# ---------------------------------------------------------------------------
# 1. Sector Overview KPIs
# ---------------------------------------------------------------------------
st.subheader("Sector Overview")

total_sectors = int(sector_df[sector_name_col].nunique())

if companies_count_col:
    total_companies = int(pd.to_numeric(sector_df[companies_count_col], errors="coerce").sum())
elif company_sector_available:
    total_companies = int(company_snapshot["_id_key"].nunique())
elif not company_snapshot.empty:
    total_companies = int(company_snapshot["_id_key"].nunique())
else:
    total_companies = 0

if avg_health_col:
    best_sector_row = sector_df.loc[sector_df[avg_health_col].idxmax()]
    best_sector_name = str(best_sector_row[sector_name_col])
    avg_sector_health_score = round(sector_df[avg_health_col].mean(), 1)
else:
    best_sector_name = "N/A"
    avg_sector_health_score = None

kpi_cols = st.columns(4)

with kpi_cols[0]:
    with st.container(border=True):
        st.metric("Total Sectors", f"{total_sectors:,}")

with kpi_cols[1]:
    with st.container(border=True):
        st.metric("Total Companies", f"{total_companies:,}" if total_companies else "N/A")

with kpi_cols[2]:
    with st.container(border=True):
        st.metric("Best Performing Sector", best_sector_name)

with kpi_cols[3]:
    with st.container(border=True):
        st.metric(
            "Average Sector Health Score",
            f"{avg_sector_health_score}" if avg_sector_health_score is not None else "N/A",
        )

st.divider()

# ---------------------------------------------------------------------------
# 2. Sector Selector
# ---------------------------------------------------------------------------
st.subheader("Select a Sector")

sector_options = sorted(sector_df[sector_name_col].dropna().unique().tolist())
selected_sector = st.selectbox("Sector", options=sector_options)

selected_sector_row = sector_df[sector_df[sector_name_col] == selected_sector].iloc[0]

st.divider()

# ---------------------------------------------------------------------------
# 3. Sector Metrics for the selected sector
# ---------------------------------------------------------------------------
st.subheader(f"Metrics — {selected_sector}")

metric_cols = st.columns(5)

with metric_cols[0]:
    with st.container(border=True):
        st.metric(
            "Companies",
            format_value(selected_sector_row[companies_count_col], 0)
            if companies_count_col
            else "N/A",
        )

with metric_cols[1]:
    with st.container(border=True):
        st.metric(
            "Average Health Score",
            format_value(selected_sector_row[avg_health_col], 1) if avg_health_col else "N/A",
        )

with metric_cols[2]:
    with st.container(border=True):
        st.metric(
            "Average ROE",
            format_value(selected_sector_row[avg_roe_col], 2, "%") if avg_roe_col else "N/A",
        )

with metric_cols[3]:
    with st.container(border=True):
        st.metric(
            "Average Net Profit Margin",
            format_value(selected_sector_row[avg_npm_col], 2, "%") if avg_npm_col else "N/A",
        )

with metric_cols[4]:
    with st.container(border=True):
        st.metric(
            "Average Debt to Equity",
            format_value(selected_sector_row[avg_de_col], 2) if avg_de_col else "N/A",
        )

st.divider()

# ---------------------------------------------------------------------------
# 4. Interactive Plotly Visualizations
# ---------------------------------------------------------------------------
st.subheader("Visualizations")

chart_row1 = st.columns(2)

with chart_row1[0]:
    with st.container(border=True):
        st.markdown("**Average Health Score by Sector**")
        if avg_health_col:
            plot_df = sector_df[[sector_name_col, avg_health_col]].sort_values(
                by=avg_health_col, ascending=False
            )
            colors = [
                "#EF553B" if s == selected_sector else "#636EFA"
                for s in plot_df[sector_name_col]
            ]
            fig_health = px.bar(
                plot_df,
                x=sector_name_col,
                y=avg_health_col,
                labels={sector_name_col: "Sector", avg_health_col: "Avg Health Score"},
            )
            fig_health.update_traces(marker_color=colors)
            fig_health.update_layout(margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_health, width='stretch')
        else:
            st.info("Average health score data not available.")

with chart_row1[1]:
    with st.container(border=True):
        st.markdown("**Company Count by Sector**")
        if companies_count_col:
            plot_df = sector_df[[sector_name_col, companies_count_col]].sort_values(
                by=companies_count_col, ascending=False
            )
            colors = [
                "#EF553B" if s == selected_sector else "#00CC96"
                for s in plot_df[sector_name_col]
            ]
            fig_count = px.bar(
                plot_df,
                x=sector_name_col,
                y=companies_count_col,
                labels={sector_name_col: "Sector", companies_count_col: "Companies"},
            )
            fig_count.update_traces(marker_color=colors)
            fig_count.update_layout(margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_count, width='stretch')
        else:
            st.info("Company count data not available.")

chart_row2 = st.columns(2)

with chart_row2[0]:
    with st.container(border=True):
        st.markdown("**ROE vs Net Profit Margin**")
        if company_sector_available and roe_col and npm_col:
            scatter_df = company_snapshot.dropna(subset=[roe_col, npm_col])
            fig_scatter = px.scatter(
                scatter_df,
                x=roe_col,
                y=npm_col,
                color=company_sector_col,
                hover_data=["_id_key"],
                labels={roe_col: "ROE (%)", npm_col: "Net Profit Margin (%)"},
            )
            fig_scatter.update_layout(margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_scatter, width='stretch')
        elif avg_roe_col and avg_npm_col:
            st.caption(
                "Company-level sector mapping unavailable — showing "
                "sector-level averages instead (one point per sector)."
            )
            fig_scatter = px.scatter(
                sector_df,
                x=avg_roe_col,
                y=avg_npm_col,
                text=sector_name_col,
                size=companies_count_col if companies_count_col else None,
                labels={avg_roe_col: "Avg ROE (%)", avg_npm_col: "Avg Net Profit Margin (%)"},
            )
            fig_scatter.update_traces(textposition="top center")
            fig_scatter.update_layout(margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_scatter, width='stretch')
        else:
            st.info("ROE / Net Profit Margin data not available.")

with chart_row2[1]:
    with st.container(border=True):
        st.markdown("**Companies by Sector (Treemap)**")
        if company_sector_available and health_score_col:
            treemap_df = company_snapshot.dropna(subset=[company_sector_col])
            fig_treemap = px.treemap(
                treemap_df,
                path=[company_sector_col, "_id_key"],
                values=health_score_col if health_score_col in treemap_df.columns else None,
            )
            fig_treemap.update_layout(margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_treemap, width='stretch')
        elif companies_count_col:
            st.caption(
                "Company-level sector mapping unavailable — showing "
                "sector-level company counts instead."
            )
            fig_treemap = px.treemap(
                sector_df,
                path=[sector_name_col],
                values=companies_count_col,
            )
            fig_treemap.update_layout(margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_treemap, width='stretch')
        else:
            st.info("Not enough data available to build a treemap.")

st.divider()

# ---------------------------------------------------------------------------
# 5. Top Companies Table
# ---------------------------------------------------------------------------
st.subheader(f"Top Companies — {selected_sector}")

with st.container(border=True):
    if company_sector_available:
        sector_companies = company_snapshot[
            company_snapshot[company_sector_col] == selected_sector
        ]
        if sector_companies.empty:
            st.info(f"No companies found for **{selected_sector}** in the company-level data.")
        else:
            display_cols = [c for c in ["_id_key", health_score_col, rating_col, roe_col, npm_col, de_col] if c]
            top_companies = sector_companies[display_cols].rename(
                columns={
                    "_id_key": "Company",
                    health_score_col: "Health Score",
                    rating_col: "Rating",
                    roe_col: "ROE (%)",
                    npm_col: "Net Profit Margin (%)",
                    de_col: "Debt to Equity",
                }
            )
            if "Health Score" in top_companies.columns:
                top_companies = top_companies.sort_values(by="Health Score", ascending=False)
            st.dataframe(top_companies.head(10), width='stretch', hide_index=True)
    elif not company_snapshot.empty and health_score_col:
        st.caption(
            "Company-level sector mapping unavailable — showing the "
            "highest-rated companies overall instead of a sector-specific list."
        )
        display_cols = [c for c in ["_id_key", health_score_col, rating_col, roe_col, npm_col, de_col] if c]
        top_companies = company_snapshot[display_cols].rename(
            columns={
                "_id_key": "Company",
                health_score_col: "Health Score",
                rating_col: "Rating",
                roe_col: "ROE (%)",
                npm_col: "Net Profit Margin (%)",
                de_col: "Debt to Equity",
            }
        ).sort_values(by="Health Score", ascending=False)
        st.dataframe(top_companies.head(10), width='stretch', hide_index=True)
    else:
        st.info("No company-level data available to build a top companies table.")

st.divider()

# ---------------------------------------------------------------------------
# 6. Sector Insights
# ---------------------------------------------------------------------------
st.subheader("Sector Insights")

with st.container(border=True):
    insights = []

    if avg_health_col:
        strongest_row = sector_df.loc[sector_df[avg_health_col].idxmax()]
        weakest_row = sector_df.loc[sector_df[avg_health_col].idxmin()]
        insights.append(
            f"🏆 **Strongest sector**: {strongest_row[sector_name_col]} "
            f"(avg health score {format_value(strongest_row[avg_health_col], 1)})"
        )
        insights.append(
            f"⚠️ **Weakest sector**: {weakest_row[sector_name_col]} "
            f"(avg health score {format_value(weakest_row[avg_health_col], 1)})"
        )

    if avg_npm_col:
        most_profitable_row = sector_df.loc[sector_df[avg_npm_col].idxmax()]
        insights.append(
            f"💰 **Highest profitability**: {most_profitable_row[sector_name_col]} "
            f"(avg net profit margin {format_value(most_profitable_row[avg_npm_col], 2, '%')})"
        )

    if avg_de_col:
        lowest_leverage_row = sector_df.loc[sector_df[avg_de_col].idxmin()]
        insights.append(
            f"🛡️ **Lowest leverage**: {lowest_leverage_row[sector_name_col]} "
            f"(avg debt to equity {format_value(lowest_leverage_row[avg_de_col], 2)})"
        )

    if not insights:
        st.info("Not enough sector data available to generate insights.")
    else:
        for insight in insights:
            st.markdown(f"- {insight}")