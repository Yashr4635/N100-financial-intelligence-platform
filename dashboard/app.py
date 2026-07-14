import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="N100 Financial Intelligence Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================
# THEME / COLOR SYSTEM
# Palette: Deep navy (#0B1220 / #101826) + Emerald (#10B981) accent
# Navy signals trust/institutional finance, emerald signals growth/positive
# performance without tipping into "casino green". Amber/red reserved
# strictly for score-based status, never decorative.
# =====================================================

NAVY_BG = "#0B1220"
NAVY_CARD = "#141C2B"
NAVY_BORDER = "#232E45"
EMERALD = "#10B981"
AMBER = "#F59E0B"
RED = "#EF4444"
TEXT_PRIMARY = "#E5E9F0"
TEXT_MUTED = "#8B96AB"

CUSTOM_CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .stApp {{
        background-color: {NAVY_BG};
        color: {TEXT_PRIMARY};
    }}

    section[data-testid="stSidebar"] {{
        background-color: {NAVY_CARD};
        border-right: 1px solid {NAVY_BORDER};
    }}

    /* Hero section */
    .hero {{
        padding: 28px 32px;
        background: linear-gradient(135deg, {NAVY_CARD} 0%, #0F1830 100%);
        border: 1px solid {NAVY_BORDER};
        border-radius: 16px;
        margin-bottom: 24px;
    }}
    .hero h1 {{
        font-size: 32px;
        font-weight: 800;
        margin: 0 0 4px 0;
        color: {TEXT_PRIMARY};
    }}
    .hero p {{
        font-size: 15px;
        color: {TEXT_MUTED};
        margin: 0;
    }}
    .hero .tag {{
        display: inline-block;
        background: rgba(16,185,129,0.12);
        color: {EMERALD};
        border: 1px solid rgba(16,185,129,0.3);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 10px;
        letter-spacing: 0.3px;
    }}

    /* KPI cards */
    .kpi-card {{
        background: {NAVY_CARD};
        border: 1px solid {NAVY_BORDER};
        border-radius: 14px;
        padding: 18px 20px;
        height: 100%;
    }}
    .kpi-label {{
        font-size: 12px;
        color: {TEXT_MUTED};
        text-transform: uppercase;
        letter-spacing: 0.6px;
        font-weight: 600;
        margin-bottom: 6px;
    }}
    .kpi-value {{
        font-size: 28px;
        font-weight: 800;
        color: {TEXT_PRIMARY};
        line-height: 1.1;
    }}
    .kpi-delta {{
        font-size: 12.5px;
        font-weight: 600;
        margin-top: 6px;
    }}

    /* Section headers */
    .section-header {{
        font-size: 20px;
        font-weight: 700;
        color: {TEXT_PRIMARY};
        margin: 8px 0 14px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid {NAVY_BORDER};
    }}

    /* Generic card wrapper */
    .card {{
        background: {NAVY_CARD};
        border: 1px solid {NAVY_BORDER};
        border-radius: 14px;
        padding: 20px;
    }}

    div[data-testid="stDataFrame"] {{
        border: 1px solid {NAVY_BORDER};
        border-radius: 10px;
        overflow: hidden;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        background-color: {NAVY_CARD};
        padding: 6px;
        border-radius: 12px;
        border: 1px solid {NAVY_BORDER};
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        color: {TEXT_MUTED};
        font-weight: 600;
        padding: 8px 18px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {EMERALD} !important;
        color: #05130D !important;
    }}

    .footer-note {{
        text-align: center;
        color: {TEXT_MUTED};
        font-size: 12.5px;
        padding-top: 20px;
        border-top: 1px solid {NAVY_BORDER};
        margin-top: 30px;
    }}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =====================================================
# LOAD DATA
# =====================================================

OUTPUT = Path("data/output")

health_file = OUTPUT / "company_health_scores.csv"
sector_file = OUTPUT / "sector_analysis.csv"
screener_file = OUTPUT / "investment_screener.csv"

try:
    health = pd.read_csv(health_file)
    sectors = pd.read_csv(sector_file)
    screener = pd.read_csv(screener_file)
except Exception as e:
    st.error(f"Unable to load dashboard data.\n\n{e}")
    st.stop()

# ---------------------------------------------------
# FIX: dedupe. Same upstream ETL bug as Company_Analysis.py
# (duplicate company_id rows — e.g. TECHM x6, INDIGO x2 in
# the screener). This was band-aided on one page and not the
# other, which is why "Top Investment Opportunities" showed
# the same company repeated. Fix the ETL job — this dedupe
# is a stopgap so the dashboard doesn't lie in the meantime.
# ---------------------------------------------------


def dedupe(df: pd.DataFrame, subset_candidates) -> pd.DataFrame:
    subset = [c for c in subset_candidates if c in df.columns]
    if not subset:
        return df
    sort_col = "id" if "id" in df.columns else df.columns[0]
    return df.sort_values(sort_col).drop_duplicates(subset=subset, keep="last")


health = dedupe(health, ["company_id", "year", "fiscal_year"])
screener = dedupe(screener, ["company_id", "year", "fiscal_year"])
sectors = dedupe(sectors, ["broad_sector", "year", "fiscal_year"])


def find_col(df: pd.DataFrame, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


# Screener's quality-score column — schema drift risk, same class of bug
# that broke ROE/NPM on Company_Analysis.py. Resolve it once, here, instead
# of assuming the literal string "financial_quality_score" always exists.
col_fqs = find_col(screener, ["financial_quality_score", "quality_score", "fin_quality_score"])


def status_color(score):
    if pd.isna(score):
        return TEXT_MUTED
    if score >= 70:
        return EMERALD
    elif score >= 40:
        return AMBER
    else:
        return RED


def status_label(score):
    if pd.isna(score):
        return "N/A"
    if score >= 70:
        return "Strong"
    elif score >= 40:
        return "Moderate"
    else:
        return "Weak"


# =====================================================
# SIDEBAR — FUNCTIONAL FILTERS
# =====================================================

st.sidebar.markdown("### 🎛️ Filters")

sector_options = ["All Sectors"]
if "broad_sector" in sectors.columns:
    sector_options += sorted(sectors["broad_sector"].dropna().unique().tolist())

selected_sector = st.sidebar.selectbox("Sector", sector_options)

rating_options = ["All Ratings"]
if "rating" in health.columns:
    rating_options += sorted(health["rating"].dropna().unique().tolist())

selected_rating = st.sidebar.selectbox("Rating", rating_options)

min_score, max_score = 0, 100
if "health_score" in health.columns and not health["health_score"].dropna().empty:
    min_score = int(health["health_score"].min())
    max_score = int(health["health_score"].max())

score_range = st.sidebar.slider(
    "Health Score Range",
    min_value=0,
    max_value=100,
    value=(min_score, max_score),
)

st.sidebar.divider()
st.sidebar.markdown("### ⚙️ Pipeline Status")
st.sidebar.markdown(f"🟢 ETL Pipeline")
st.sidebar.markdown(f"🟢 SQLite Database")
st.sidebar.markdown(f"🟢 Analytics Engine")
st.sidebar.markdown(f"🟢 Health Scoring")
st.sidebar.markdown(f"🟢 Investment Screener")

st.sidebar.divider()
st.sidebar.caption("Bluestock Internship Project")

# ---- apply filters to a working copy ----
filtered = health.copy()

if "health_score" in filtered.columns:
    filtered = filtered[
        (filtered["health_score"] >= score_range[0])
        & (filtered["health_score"] <= score_range[1])
    ]

if selected_rating != "All Ratings" and "rating" in filtered.columns:
    filtered = filtered[filtered["rating"] == selected_rating]

filtered_screener = screener.copy()
if "health_score" in filtered_screener.columns:
    filtered_screener = filtered_screener[
        (filtered_screener["health_score"] >= score_range[0])
        & (filtered_screener["health_score"] <= score_range[1])
    ]
if selected_rating != "All Ratings" and "rating" in filtered_screener.columns:
    filtered_screener = filtered_screener[filtered_screener["rating"] == selected_rating]

filtered_sectors = sectors.copy()
if selected_sector != "All Sectors" and "broad_sector" in filtered_sectors.columns:
    filtered_sectors = filtered_sectors[filtered_sectors["broad_sector"] == selected_sector]

# =====================================================
# HERO SECTION
# =====================================================

st.markdown(
    f"""
    <div class="hero">
        <div class="tag">LIVE ANALYTICS</div>
        <h1>📈 N100 Financial Intelligence Platform</h1>
        <p>End-to-end financial data engineering, health scoring, and investment screening across Nifty100 companies.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# =====================================================
# KPI STRIP
# =====================================================

avg_health = round(health["health_score"].mean(), 1) if "health_score" in health.columns else 0
excellent_count = (health["rating"] == "Excellent").sum() if "rating" in health.columns else 0
excellent_pct = round((excellent_count / len(health)) * 100, 1) if len(health) else 0

kpis = [
    ("Companies Tracked", health["company_id"].nunique() if "company_id" in health.columns else len(health), None, None),
    ("Financial Records", len(health), None, None),
    ("Sectors Covered", sectors["broad_sector"].nunique() if "broad_sector" in sectors.columns else "—", None, None),
    ("Average Health Score", avg_health, status_color(avg_health), status_label(avg_health)),
    ("Excellent-Rated Cos.", f"{excellent_count} ({excellent_pct}%)", EMERALD if excellent_pct > 20 else AMBER, None),
]

cols = st.columns(5)
for col, (label, value, color, tag) in zip(cols, kpis):
    delta_html = ""
    if color and tag:
        delta_html = f'<div class="kpi-delta" style="color:{color};">● {tag}</div>'
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                {delta_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")

# =====================================================
# TABS — Overview / Company Deep Dive / Sector Analysis
# =====================================================

tab_overview, tab_companies, tab_sectors = st.tabs(
    ["📊 Overview", "🔎 Company Deep Dive", "🏭 Sector Analysis"]
)

# -----------------------------------------------------
# TAB 1 — OVERVIEW
# -----------------------------------------------------
with tab_overview:

    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        st.markdown('<div class="section-header">Health Score Distribution — Top 15 Companies</div>', unsafe_allow_html=True)
        if "health_score" in filtered.columns and "company_id" in filtered.columns and not filtered.empty:
            top15 = filtered.sort_values("health_score", ascending=False).head(15)
            colors = [status_color(s) for s in top15["health_score"]]
            fig = go.Figure(
                go.Bar(
                    x=top15["health_score"],
                    y=top15["company_id"].astype(str),
                    orientation="h",
                    marker_color=colors,
                    text=top15["health_score"].round(1),
                    textposition="outside",
                )
            )
            fig.update_layout(
                plot_bgcolor=NAVY_CARD,
                paper_bgcolor=NAVY_CARD,
                font_color=TEXT_PRIMARY,
                height=460,
                margin=dict(l=10, r=10, t=10, b=10),
                yaxis=dict(autorange="reversed", gridcolor=NAVY_BORDER),
                xaxis=dict(title="Health Score", gridcolor=NAVY_BORDER, range=[0, 100]),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the current filter selection.")

    with col_right:
        st.markdown('<div class="section-header">Sector Composition</div>', unsafe_allow_html=True)
        if "broad_sector" in sectors.columns:
            sector_counts = sectors["broad_sector"].value_counts().reset_index()
            sector_counts.columns = ["sector", "count"]
            fig2 = px.pie(
                sector_counts,
                names="sector",
                values="count",
                hole=0.55,
                color_discrete_sequence=px.colors.sequential.Emrld[::-1],
            )
            fig2.update_layout(
                plot_bgcolor=NAVY_CARD,
                paper_bgcolor=NAVY_CARD,
                font_color=TEXT_PRIMARY,
                height=460,
                margin=dict(l=10, r=10, t=10, b=10),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.25),
            )
            st.plotly_chart(fig2, width="stretch")
        else:
            st.info("Sector column not found in dataset.")

    st.markdown('<div class="section-header">Top Investment Opportunities</div>', unsafe_allow_html=True)
    display_cols = [c for c in ["company_id", "health_score", "rating", col_fqs] if c and c in filtered_screener.columns]
    if not filtered_screener.empty and display_cols:
        top_opps = filtered_screener.sort_values(
            "health_score" if "health_score" in filtered_screener.columns else display_cols[0],
            ascending=False,
        ).head(10)[display_cols]

        col_config = {}
        if "health_score" in top_opps.columns:
            col_config["health_score"] = st.column_config.ProgressColumn(
                "Health Score", min_value=0, max_value=100, format="%.1f"
            )
        if col_fqs and col_fqs in top_opps.columns:
            col_config[col_fqs] = st.column_config.ProgressColumn(
                "Financial Quality", min_value=0, max_value=100, format="%.1f"
            )

        st.dataframe(top_opps, use_container_width=True, column_config=col_config, hide_index=True)
    else:
        st.info("No investment opportunities match the current filters.")

# -----------------------------------------------------
# TAB 2 — COMPANY DEEP DIVE
# -----------------------------------------------------
with tab_companies:

    st.markdown('<div class="section-header">Health Score vs. Financial Quality</div>', unsafe_allow_html=True)

    # FIX #2: col_fqs (e.g. "financial_quality_score") exists in BOTH
    # health.csv and screener.csv. Merging two frames that share a column
    # name outside the join key makes pandas silently rename both to
    # "<col>_x" / "<col>_y" — so col_fqs was resolved correctly, the merge
    # "succeeded", but the plain column name dropna() asked for no longer
    # existed. Fix: if filtered (health) already has the column, use it
    # directly and skip the merge entirely. Only merge from screener if
    # health doesn't have it.
    if col_fqs and "health_score" in filtered.columns and "company_id" in filtered.columns:
        if col_fqs in filtered.columns:
            scatter_df = filtered.copy()
        else:
            merge_cols = ["company_id", col_fqs]
            scatter_df = filtered.merge(screener[merge_cols], on="company_id", how="left")
        scatter_df = scatter_df.dropna(subset=["health_score", col_fqs])

        if not scatter_df.empty:
            fig3 = px.scatter(
                scatter_df,
                x=col_fqs,
                y="health_score",
                color="rating" if "rating" in scatter_df.columns else None,
                hover_name="company_id",
                color_discrete_sequence=[EMERALD, AMBER, RED, "#3B82F6", "#A855F7"],
            )
            fig3.update_traces(marker=dict(size=11, line=dict(width=1, color=NAVY_BG)))
            fig3.update_layout(
                plot_bgcolor=NAVY_CARD,
                paper_bgcolor=NAVY_CARD,
                font_color=TEXT_PRIMARY,
                height=420,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(title="Financial Quality Score", gridcolor=NAVY_BORDER),
                yaxis=dict(title="Health Score", gridcolor=NAVY_BORDER),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Not enough overlapping data to plot.")
    else:
        st.info(
            "Required columns not found for this chart "
            f"(looked for financial_quality_score / quality_score in investment_screener.csv, found: "
            f"{list(screener.columns)})."
        )

    st.markdown('<div class="section-header">Full Company Table (Filtered)</div>', unsafe_allow_html=True)

    table_cols = [c for c in ["company_id", "health_score", "rating"] if c in filtered.columns]
    if not filtered.empty and table_cols:
        col_config2 = {}
        if "health_score" in table_cols:
            col_config2["health_score"] = st.column_config.ProgressColumn(
                "Health Score", min_value=0, max_value=100, format="%.1f"
            )
        st.dataframe(
            filtered[table_cols].sort_values(table_cols[1] if len(table_cols) > 1 else table_cols[0], ascending=False),
            use_container_width=True,
            column_config=col_config2,
            hide_index=True,
            height=420,
        )
        st.caption(f"Showing {len(filtered)} of {len(health)} companies based on active filters.")
    else:
        st.info("No companies match the current filters. Try widening the score range.")

# -----------------------------------------------------
# TAB 3 — SECTOR ANALYSIS
# -----------------------------------------------------
with tab_sectors:

    st.markdown('<div class="section-header">Sector Breakdown</div>', unsafe_allow_html=True)

    numeric_sector_cols = [c for c in sectors.select_dtypes(include="number").columns if c != "broad_sector"]

    if "broad_sector" in filtered_sectors.columns and numeric_sector_cols:
        metric_choice = st.selectbox("Metric", numeric_sector_cols, index=0)

        agg = filtered_sectors.groupby("broad_sector")[metric_choice].mean().reset_index().sort_values(metric_choice, ascending=False)

        fig4 = px.treemap(
            agg,
            path=["broad_sector"],
            values=metric_choice,
            color=metric_choice,
            color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"],
        )
        fig4.update_layout(
            paper_bgcolor=NAVY_CARD,
            font_color=TEXT_PRIMARY,
            height=440,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No numeric sector metrics available for visualization.")

    st.markdown('<div class="section-header">Sector Data Table</div>', unsafe_allow_html=True)
    if not filtered_sectors.empty:
        st.dataframe(filtered_sectors, use_container_width=True, hide_index=True)
    else:
        st.info("No sector data for the current selection.")

# =====================================================
# FOOTER
# =====================================================

st.markdown(
    '<div class="footer-note">Developed by Yash • Bluestock Internship • Python · Pandas · SQLite · Streamlit · Plotly</div>',
    unsafe_allow_html=True,
)