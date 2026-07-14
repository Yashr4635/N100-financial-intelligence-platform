"""
Overview — N100 Financial Intelligence Platform

Reads from:
  data/output/company_health_scores.csv
  data/output/sector_analysis.csv
  data/output/investment_screener.csv

NOTES / KNOWN RISKS (consistent with the rest of this project):
- Column names resolved defensively via find_col(). Confirmed real
  column names as of the last working version of this project:
  health -> company_id, health_score, rating
  sector -> broad_sector, avg_health_score, companies
  screener -> company_id, health_score, rating, financial_quality_score
  If your CSVs drift from this, find_col() falls back through the
  candidate lists below instead of crashing.
- Rows deduped on load — recurring upstream ETL bug in this project has
  produced duplicate company rows in every source CSV so far. This is a
  band-aid, not a fix. Fix the pipeline.
- Cache keys off each file's mtime so edits to the CSVs are picked up
  without needing to clear Streamlit's cache manually.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Overview | N100 Financial Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================
# THEME (consistent with app.py / Company_Analysis.py / Sector_Analysis.py / Investment_Screener.py)
# =====================================================

NAVY_BG = "#0B1220"
NAVY_CARD = "#141C2B"
NAVY_BORDER = "#232E45"
EMERALD = "#10B981"
AMBER = "#F59E0B"
RED = "#EF4444"
BLUE = "#3B82F6"
VIOLET = "#8B5CF6"
TEXT_PRIMARY = "#E5E9F0"
TEXT_MUTED = "#8B96AB"

RATING_COLORS = {
    "excellent": EMERALD,
    "strong": EMERALD,
    "good": BLUE,
    "moderate": AMBER,
    "average": AMBER,
    "weak": RED,
    "poor": RED,
}
CATEGORY_PALETTE = [
    EMERALD,
    BLUE,
    VIOLET,
    AMBER,
    "#EC4899",
    "#14B8A6",
    RED,
    "#F97316",
    "#06B6D4",
    "#A855F7",
]

CUSTOM_CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    .stApp {{ background-color: {NAVY_BG}; color: {TEXT_PRIMARY}; }}
    section[data-testid="stSidebar"] {{ background-color: {NAVY_CARD}; border-right: 1px solid {NAVY_BORDER}; }}

    .hero {{
        padding: 28px 32px;
        background: linear-gradient(135deg, {NAVY_CARD} 0%, #0F1830 100%);
        border: 1px solid {NAVY_BORDER};
        border-radius: 16px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }}
    .hero h1 {{ font-size: 32px; font-weight: 800; margin: 0 0 4px 0; }}
    .hero p {{ font-size: 15px; color: {TEXT_MUTED}; margin: 0; }}
    .hero-badge {{
        font-size: 12px; font-weight: 700; padding: 6px 14px; border-radius: 999px;
        background: rgba(16,185,129,0.12); color: {EMERALD}; border: 1px solid rgba(16,185,129,0.3);
        white-space: nowrap;
    }}

    .kpi-card {{
        background: {NAVY_CARD};
        border: 1px solid {NAVY_BORDER};
        border-radius: 14px;
        padding: 18px 20px;
        height: 100%;
        transition: border-color 0.15s ease;
    }}
    .kpi-card:hover {{ border-color: {EMERALD}44; }}
    .kpi-label {{
        font-size: 12px; color: {TEXT_MUTED}; text-transform: uppercase;
        letter-spacing: 0.6px; font-weight: 600; margin-bottom: 6px;
    }}
    .kpi-value {{ font-size: 26px; font-weight: 800; color: {TEXT_PRIMARY}; line-height: 1.15; }}
    .kpi-sub {{ font-size: 12.5px; color: {TEXT_MUTED}; margin-top: 6px; }}

    .section-header {{
        font-size: 19px; font-weight: 700; color: {TEXT_PRIMARY};
        margin: 26px 0 14px 0; padding-bottom: 8px; border-bottom: 1px solid {NAVY_BORDER};
    }}

    div[data-testid="stDataFrame"] {{ border: 1px solid {NAVY_BORDER}; border-radius: 10px; overflow: hidden; }}

    .data-warning {{
        background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.3);
        border-radius: 10px; padding: 10px 16px; font-size: 13px; color: {AMBER};
        margin-bottom: 16px;
    }}

    .footer-note {{
        text-align: center; color: {TEXT_MUTED}; font-size: 12.5px;
        padding-top: 20px; border-top: 1px solid {NAVY_BORDER}; margin-top: 30px;
    }}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =====================================================
# DATA LOADING
# =====================================================

OUTPUT = Path("data/output")
HEALTH_FILE = OUTPUT / "company_health_scores.csv"
SECTOR_FILE = OUTPUT / "sector_analysis.csv"
SCREENER_FILE = OUTPUT / "investment_screener.csv"


@st.cache_data
def load_csv(path: Path, mtime: float) -> pd.DataFrame:
    """mtime busts the cache whenever the underlying CSV changes on disk."""
    return pd.read_csv(path)


def safe_mtime(path: Path) -> float:
    return path.stat().st_mtime if path.exists() else 0


try:
    health_raw = load_csv(HEALTH_FILE, safe_mtime(HEALTH_FILE))
    sector_raw = load_csv(SECTOR_FILE, safe_mtime(SECTOR_FILE))
    screener_raw = load_csv(SCREENER_FILE, safe_mtime(SCREENER_FILE))
except Exception as e:
    st.error(f"Unable to load dashboard data.\n\n{e}")
    st.stop()

for name, frame in [
    ("company_health_scores.csv", health_raw),
    ("sector_analysis.csv", sector_raw),
    ("investment_screener.csv", screener_raw),
]:
    if frame.empty:
        st.warning(f"{name} loaded but contains no rows.")

# =====================================================
# COLUMN RESOLUTION (defensive — see module docstring)
# =====================================================


def find_col(df: pd.DataFrame, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


# health.csv
h_company = find_col(health_raw, ["company_id", "company", "symbol", "ticker"])
h_health = find_col(health_raw, ["health_score", "health"])
h_rating = find_col(health_raw, ["rating"])
h_year = find_col(health_raw, ["year", "fiscal_year", "fy"])
h_id = find_col(health_raw, ["id"])

# sector_analysis.csv
s_sector = find_col(sector_raw, ["broad_sector", "sector", "sector_name"])
s_avg_health = find_col(
    sector_raw, ["avg_health_score", "health_score", "average_health_score"]
)
s_companies = find_col(
    sector_raw, ["companies", "company_count", "num_companies", "n_companies"]
)
s_year = find_col(sector_raw, ["year", "fiscal_year", "fy"])
s_id = find_col(sector_raw, ["id"])

# investment_screener.csv
sc_company = find_col(screener_raw, ["company_id", "company", "symbol", "ticker"])
sc_health = find_col(screener_raw, ["health_score", "health"])
sc_rating = find_col(screener_raw, ["rating"])
sc_fqs = find_col(
    screener_raw, ["financial_quality_score", "quality_score", "fin_quality_score"]
)
sc_year = find_col(screener_raw, ["year", "fiscal_year", "fy"])
sc_id = find_col(screener_raw, ["id"])

if h_company is None:
    st.error(
        f"No company identifier column found in company_health_scores.csv (found: {list(health_raw.columns)})."
    )
    st.stop()

# =====================================================
# DEDUPE — band-aid for recurring upstream ETL duplicate rows.
# =====================================================


def dedupe(
    df: pd.DataFrame, subset_candidates, id_col=None
) -> tuple[pd.DataFrame, int]:
    subset = [c for c in subset_candidates if c is not None]
    if not subset:
        return df, 0
    before = len(df)
    sort_col = id_col if id_col else df.columns[0]
    deduped = df.sort_values(sort_col).drop_duplicates(subset=subset, keep="last")
    return deduped, before - len(deduped)


health, health_dupes = dedupe(health_raw, [h_company, h_year], h_id)
sector, sector_dupes = dedupe(sector_raw, [s_sector, s_year], s_id)
screener, screener_dupes = dedupe(screener_raw, [sc_company, sc_year], sc_id)

total_dupes = health_dupes + sector_dupes + screener_dupes

# =====================================================
# HERO
# =====================================================

st.markdown(
    f"""
    <div class="hero">
        <div>
            <h1>📊 Analytics Overview</h1>
            <p>Platform-wide snapshot across health, sector, and investment data — N100 Financial Intelligence Platform</p>
        </div>
        <div class="hero-badge">{health[h_company].nunique()} Companies Tracked</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if total_dupes > 0:
    st.markdown(
        f'<div class="data-warning">⚠️ Removed {total_dupes} duplicate record(s) across the '
        f"source files ({health_dupes} health, {sector_dupes} sector, {screener_dupes} screener). "
        f"This is a data pipeline issue — check your ETL job.</div>",
        unsafe_allow_html=True,
    )

# =====================================================
# KPI CARDS
# =====================================================

companies_count = health[h_company].nunique()
records_count = len(health)
sectors_count = sector[s_sector].nunique() if s_sector else None
avg_health = (
    round(health[h_health].mean(), 1)
    if h_health and not health[h_health].dropna().empty
    else None
)

kpis = [
    ("Companies", companies_count),
    ("Financial Records", records_count),
    ("Sectors", sectors_count if sectors_count is not None else "N/A"),
    ("Average Health", avg_health if avg_health is not None else "N/A"),
]

kpi_cols = st.columns(4)
for col, (label, value) in zip(kpi_cols, kpis):
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")

# =====================================================
# CHARTS — ROW 1: Health Distribution / Rating Distribution
# =====================================================

row1_left, row1_right = st.columns(2)

with row1_left:
    st.markdown(
        '<div class="section-header">Health Score Distribution</div>',
        unsafe_allow_html=True,
    )
    if h_health:
        hist_df = health.dropna(subset=[h_health])
        if not hist_df.empty:
            fig_hist = px.histogram(
                hist_df,
                x=h_health,
                nbins=20,
                color=h_rating if h_rating else None,
                color_discrete_map=RATING_COLORS if h_rating else None,
            )
            fig_hist.update_traces(marker_line_color=NAVY_BG, marker_line_width=1)
            fig_hist.update_layout(
                plot_bgcolor=NAVY_CARD,
                paper_bgcolor=NAVY_CARD,
                font_color=TEXT_PRIMARY,
                height=380,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(title="Health Score", gridcolor=NAVY_BORDER),
                yaxis=dict(title="Number of Companies", gridcolor=NAVY_BORDER),
                bargap=0.05,
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("No health score data available.")
    else:
        st.info("Health score column not found in company_health_scores.csv.")

with row1_right:
    st.markdown(
        '<div class="section-header">Rating Distribution</div>', unsafe_allow_html=True
    )
    if h_rating:
        rating_counts = health[h_rating].dropna().value_counts()
        if not rating_counts.empty:
            pie_colors = [
                RATING_COLORS.get(str(r).lower(), TEXT_MUTED)
                for r in rating_counts.index
            ]
            fig_pie = px.pie(
                names=rating_counts.index,
                values=rating_counts.values,
                hole=0.55,
                color_discrete_sequence=pie_colors,
            )
            fig_pie.update_layout(
                plot_bgcolor=NAVY_CARD,
                paper_bgcolor=NAVY_CARD,
                font_color=TEXT_PRIMARY,
                height=380,
                margin=dict(l=10, r=10, t=10, b=10),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.3),
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No rating data available.")
    else:
        st.info("Rating column not found in company_health_scores.csv.")

st.write("")

# =====================================================
# CHARTS — ROW 2: Sector Distribution / Avg Health by Sector
# =====================================================

row2_left, row2_right = st.columns(2)

with row2_left:
    st.markdown(
        '<div class="section-header">Sector Distribution</div>', unsafe_allow_html=True
    )
    if s_sector and s_companies:
        sec_dist = sector.dropna(subset=[s_sector, s_companies]).sort_values(
            s_companies, ascending=False
        )
        if not sec_dist.empty:
            fig_bar1 = px.bar(
                sec_dist,
                x=s_sector,
                y=s_companies,
                color_discrete_sequence=[EMERALD],
            )
            fig_bar1.update_layout(
                plot_bgcolor=NAVY_CARD,
                paper_bgcolor=NAVY_CARD,
                font_color=TEXT_PRIMARY,
                height=380,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(title="Sector", gridcolor=NAVY_BORDER, tickangle=-30),
                yaxis=dict(title="Companies", gridcolor=NAVY_BORDER),
            )
            st.plotly_chart(fig_bar1, use_container_width=True)
        else:
            st.info("No sector distribution data available.")
    else:
        st.info(
            "Sector and/or company-count column not found in sector_analysis.csv "
            f"(found: {list(sector_raw.columns)})."
        )

with row2_right:
    st.markdown(
        '<div class="section-header">Average Health by Sector</div>',
        unsafe_allow_html=True,
    )
    if s_sector and s_avg_health:
        sec_health = sector.dropna(subset=[s_sector, s_avg_health]).sort_values(
            s_avg_health, ascending=True
        )
        if not sec_health.empty:
            bar_colors = [
                EMERALD if v >= 70 else AMBER if v >= 40 else RED
                for v in sec_health[s_avg_health]
            ]
            fig_bar2 = px.bar(
                sec_health,
                x=s_avg_health,
                y=s_sector,
                orientation="h",
                color_discrete_sequence=[EMERALD],
            )
            fig_bar2.update_traces(marker_color=bar_colors)
            fig_bar2.update_layout(
                plot_bgcolor=NAVY_CARD,
                paper_bgcolor=NAVY_CARD,
                font_color=TEXT_PRIMARY,
                height=380,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(
                    title="Average Health Score", gridcolor=NAVY_BORDER, range=[0, 100]
                ),
                yaxis=dict(title="", gridcolor=NAVY_BORDER),
            )
            st.plotly_chart(fig_bar2, use_container_width=True)
        else:
            st.info("No average health data available.")
    else:
        st.info(
            "Sector and/or average health column not found in sector_analysis.csv "
            f"(found: {list(sector_raw.columns)})."
        )

st.write("")

# =====================================================
# TOP INVESTMENT OPPORTUNITIES + DOWNLOAD
# =====================================================

st.markdown(
    '<div class="section-header">Top Investment Opportunities</div>',
    unsafe_allow_html=True,
)

display_cols = [c for c in [sc_company, sc_health, sc_rating, sc_fqs] if c]
if not screener.empty and display_cols:
    top_opps = screener.sort_values(
        sc_health if sc_health else display_cols[0], ascending=False
    ).head(20)[display_cols]

    col_config = {}
    if sc_health and sc_health in top_opps.columns:
        col_config[sc_health] = st.column_config.ProgressColumn(
            "Health Score", min_value=0, max_value=100, format="%.1f"
        )
    if sc_fqs and sc_fqs in top_opps.columns:
        col_config[sc_fqs] = st.column_config.ProgressColumn(
            "Financial Quality", min_value=0, max_value=100, format="%.1f"
        )

    st.dataframe(
        top_opps, use_container_width=True, column_config=col_config, hide_index=True
    )
else:
    st.info(
        "Required columns not found in investment_screener.csv "
        f"(found: {list(screener_raw.columns)})."
    )

download_df = (
    screener.drop(columns=[sc_id]) if sc_id and sc_id in screener.columns else screener
)
st.download_button(
    "⬇ Download Investment Screener",
    data=download_df.to_csv(index=False).encode("utf-8"),
    file_name="investment_screener.csv",
    mime="text/csv",
)

# =====================================================
# FOOTER
# =====================================================

st.markdown(
    '<div class="footer-note">N100 Financial Intelligence Platform • Overview • '
    "Python · Pandas · Plotly · Streamlit</div>",
    unsafe_allow_html=True,
)
