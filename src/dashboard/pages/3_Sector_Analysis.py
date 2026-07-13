"""
Sector Analysis — N100 Financial Intelligence Platform

Reads directly from data/output/sector_analysis.csv.

NOTES / KNOWN RISKS (see comments inline for detail):
- Column names are resolved defensively via find_col() because this
  project's CSVs have repeatedly shipped with inconsistent naming
  (e.g. "roe" vs "return_on_equity_pct") across pages. If a chart or
  KPI shows "N/A" / "Column not found", the real column name in your
  CSV doesn't match any of the candidates listed — add it to the
  candidate list rather than guessing.
- Rows are deduped on load. This dashboard has repeatedly received
  CSVs with duplicate (sector[, year]) rows from the upstream ETL job.
  This is a band-aid, not a fix — the pipeline should not emit dupes.
- fillcolor values use rgba(), never "#RRGGBB" + alpha-suffix string
  concatenation — that pattern is invalid and has crashed this project
  before (Plotly does not accept 8-digit hex).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Sector Analysis | N100 Financial Intelligence Platform",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================
# THEME
# =====================================================

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

SECTOR_PALETTE = [EMERALD, BLUE, VIOLET, AMBER, "#EC4899", "#14B8A6", RED, "#F97316", "#06B6D4", "#A855F7"]


def hex_to_rgba(hex_color: str, alpha: float = 0.12) -> str:
    """Convert '#RRGGBB' to a Plotly-safe 'rgba(r,g,b,a)' string.
    Plotly's color validators reject 8-digit hex (#RRGGBBAA)."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


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
DATA_FILE = OUTPUT / "sector_analysis.csv"


@st.cache_data
def load_data(path: Path, mtime: float) -> pd.DataFrame:
    """mtime busts the cache whenever the underlying CSV changes on disk."""
    return pd.read_csv(path)


try:
    file_mtime = DATA_FILE.stat().st_mtime if DATA_FILE.exists() else 0
    raw = load_data(DATA_FILE, file_mtime)
except Exception as e:
    st.error(f"Unable to load sector data from {DATA_FILE}.\n\n{e}")
    st.stop()

if raw.empty:
    st.warning("sector_analysis.csv loaded but contains no rows.")
    st.stop()

# =====================================================
# COLUMN RESOLUTION (defensive — see module docstring)
# =====================================================


def find_col(df: pd.DataFrame, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


col_sector = find_col(raw, ["broad_sector", "sector", "sector_name"])
col_health = find_col(raw, ["health_score", "avg_health_score", "average_health_score", "health"])
col_roe = find_col(raw, ["avg_roe", "average_roe", "roe_pct", "return_on_equity_pct", "roe"])
col_de = find_col(raw, ["avg_debt_to_equity", "average_debt_to_equity", "debt_to_equity", "de_ratio"])
col_rating = find_col(raw, ["rating", "avg_rating"])
col_year = find_col(raw, ["year", "fiscal_year", "fy"])
col_company_count = find_col(raw, ["company_count", "num_companies", "n_companies", "companies", "count"])
col_id = find_col(raw, ["id"])

if col_sector is None:
    st.error(
        "No sector identifier column found in sector_analysis.csv "
        f"(looked for broad_sector/sector/sector_name; found columns: {list(raw.columns)})."
    )
    st.stop()

# =====================================================
# DEDUPE — see module docstring. Band-aid for upstream ETL dupes.
# =====================================================

dedup_subset = [c for c in [col_sector, col_year] if c is not None]
df = raw.copy()
duplicates_found = 0
if dedup_subset:
    before = len(df)
    sort_col = col_id if col_id else df.columns[0]
    df = df.sort_values(sort_col).drop_duplicates(subset=dedup_subset, keep="last")
    duplicates_found = before - len(df)

# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.markdown("### 🎛️ Filters")

sector_values = sorted(df[col_sector].dropna().unique().tolist())
selected_sectors = st.sidebar.multiselect("Sector", sector_values, default=sector_values)

min_health_floor, min_health_ceiling = 0, 100
if col_health and not df[col_health].dropna().empty:
    min_health_floor = int(df[col_health].min())
    min_health_ceiling = int(df[col_health].max())

min_health = st.sidebar.slider(
    "Minimum Health Score",
    min_value=0,
    max_value=100,
    value=min_health_floor if col_health else 0,
)

st.sidebar.divider()
st.sidebar.caption("N100 Financial Intelligence Platform")

filtered = df.copy()
if selected_sectors:
    filtered = filtered[filtered[col_sector].isin(selected_sectors)]
else:
    filtered = filtered.iloc[0:0]

if col_health:
    filtered = filtered[filtered[col_health].fillna(-1) >= min_health]

# =====================================================
# HERO
# =====================================================

st.markdown(
    f"""
    <div class="hero">
        <div>
            <h1>🏭 Sector Analysis</h1>
            <p>Cross-sector financial health, profitability, and leverage — N100 Financial Intelligence Platform</p>
        </div>
        <div class="hero-badge">{df[col_sector].nunique()} Sectors Tracked</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if duplicates_found > 0:
    st.markdown(
        f'<div class="data-warning">⚠️ Removed {duplicates_found} duplicate sector record(s) '
        f'from the source data. This is a data pipeline issue — check your ETL job.</div>',
        unsafe_allow_html=True,
    )

# =====================================================
# KPI CARDS
# =====================================================

# Total Sectors
total_sectors = df[col_sector].nunique()

# Best Sector (highest average health score)
if col_health and not df[col_health].dropna().empty:
    best_sector_row = df.groupby(col_sector)[col_health].mean().sort_values(ascending=False)
    best_sector_name = best_sector_row.index[0]
    best_sector_score = round(best_sector_row.iloc[0], 1)
else:
    best_sector_name, best_sector_score = "N/A", None

# Average Health Score (across all sectors)
avg_health_all = round(df[col_health].mean(), 1) if col_health and not df[col_health].dropna().empty else None

# Highest ROE Sector
if col_roe and not df[col_roe].dropna().empty:
    roe_by_sector = df.groupby(col_sector)[col_roe].mean().sort_values(ascending=False)
    highest_roe_sector = roe_by_sector.index[0]
    highest_roe_value = round(roe_by_sector.iloc[0], 2)
else:
    highest_roe_sector, highest_roe_value = "N/A", None

kpis = [
    ("Total Sectors", total_sectors, None),
    ("Best Sector", best_sector_name, f"Health Score {best_sector_score}" if best_sector_score is not None else None),
    ("Average Health Score", avg_health_all if avg_health_all is not None else "N/A", None),
    ("Highest ROE Sector", highest_roe_sector, f"ROE {highest_roe_value}%" if highest_roe_value is not None else None),
]

kpi_cols = st.columns(4)
for col, (label, value, sub) in zip(kpi_cols, kpis):
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                {sub_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")

# =====================================================
# CHARTS
# =====================================================

if filtered.empty:
    st.info("No sectors match the current filters. Widen the health score range or select more sectors.")
else:
    chart_row1_left, chart_row1_right = st.columns([1.3, 1])

    # ---- Average Health Score by Sector (Horizontal Bar) ----
    with chart_row1_left:
        st.markdown('<div class="section-header">Average Health Score by Sector</div>', unsafe_allow_html=True)
        if col_health:
            health_by_sector = (
                filtered.groupby(col_sector)[col_health].mean().dropna().sort_values(ascending=True)
            )
            if not health_by_sector.empty:
                bar_colors = [
                    EMERALD if v >= 70 else AMBER if v >= 40 else RED for v in health_by_sector.values
                ]
                fig_health = go.Figure(
                    go.Bar(
                        x=health_by_sector.values,
                        y=health_by_sector.index,
                        orientation="h",
                        marker_color=bar_colors,
                        text=[round(v, 1) for v in health_by_sector.values],
                        textposition="outside",
                    )
                )
                fig_health.update_layout(
                    plot_bgcolor=NAVY_CARD,
                    paper_bgcolor=NAVY_CARD,
                    font_color=TEXT_PRIMARY,
                    height=420,
                    margin=dict(l=10, r=10, t=10, b=10),
                    xaxis=dict(title="Health Score", gridcolor=NAVY_BORDER, range=[0, 100]),
                    yaxis=dict(gridcolor=NAVY_BORDER),
                )
                st.plotly_chart(fig_health, use_container_width=True)
            else:
                st.info("No health score data available for the current filter selection.")
        else:
            st.info("No health score column found in sector_analysis.csv.")

    # ---- Sector Distribution (Pie) ----
    with chart_row1_right:
        st.markdown('<div class="section-header">Sector Distribution</div>', unsafe_allow_html=True)
        if col_company_count:
            dist = filtered.groupby(col_sector)[col_company_count].sum().dropna()
        else:
            # NOTE: no company-count column was found in the CSV, so this
            # falls back to counting rows per sector. If sector_analysis.csv
            # is already one row per sector, every slice will be equal size
            # and this chart will not carry real information — verify
            # against your actual schema.
            dist = filtered[col_sector].value_counts()

        if not dist.empty:
            fig_pie = px.pie(
                names=dist.index,
                values=dist.values,
                hole=0.55,
                color_discrete_sequence=SECTOR_PALETTE,
            )
            fig_pie.update_layout(
                plot_bgcolor=NAVY_CARD,
                paper_bgcolor=NAVY_CARD,
                font_color=TEXT_PRIMARY,
                height=420,
                margin=dict(l=10, r=10, t=10, b=10),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.3),
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No data available to build sector distribution.")

    chart_row2_left, chart_row2_right = st.columns(2)

    # ---- Average ROE by Sector (Bar) ----
    with chart_row2_left:
        st.markdown('<div class="section-header">Average ROE by Sector</div>', unsafe_allow_html=True)
        if col_roe:
            roe_by_sector_f = filtered.groupby(col_sector)[col_roe].mean().dropna().sort_values(ascending=False)
            if not roe_by_sector_f.empty:
                fig_roe = go.Figure(
                    go.Bar(
                        x=roe_by_sector_f.index,
                        y=roe_by_sector_f.values,
                        marker_color=BLUE,
                        text=[round(v, 2) for v in roe_by_sector_f.values],
                        textposition="outside",
                    )
                )
                fig_roe.update_layout(
                    plot_bgcolor=NAVY_CARD,
                    paper_bgcolor=NAVY_CARD,
                    font_color=TEXT_PRIMARY,
                    height=380,
                    margin=dict(l=10, r=10, t=10, b=10),
                    xaxis=dict(title="Sector", gridcolor=NAVY_BORDER, tickangle=-30),
                    yaxis=dict(title="Average ROE (%)", gridcolor=NAVY_BORDER),
                )
                st.plotly_chart(fig_roe, use_container_width=True)
            else:
                st.info("No ROE data available for the current filter selection.")
        else:
            st.info("No ROE column found in sector_analysis.csv.")

    # ---- Average Debt to Equity by Sector (Bar) ----
    with chart_row2_right:
        st.markdown('<div class="section-header">Average Debt to Equity by Sector</div>', unsafe_allow_html=True)
        if col_de:
            de_by_sector = filtered.groupby(col_sector)[col_de].mean().dropna().sort_values(ascending=False)
            if not de_by_sector.empty:
                fig_de = go.Figure(
                    go.Bar(
                        x=de_by_sector.index,
                        y=de_by_sector.values,
                        marker_color=VIOLET,
                        text=[round(v, 2) for v in de_by_sector.values],
                        textposition="outside",
                    )
                )
                fig_de.update_layout(
                    plot_bgcolor=NAVY_CARD,
                    paper_bgcolor=NAVY_CARD,
                    font_color=TEXT_PRIMARY,
                    height=380,
                    margin=dict(l=10, r=10, t=10, b=10),
                    xaxis=dict(title="Sector", gridcolor=NAVY_BORDER, tickangle=-30),
                    yaxis=dict(title="Debt to Equity", gridcolor=NAVY_BORDER),
                )
                st.plotly_chart(fig_de, use_container_width=True)
            else:
                st.info("No debt-to-equity data available for the current filter selection.")
        else:
            st.info("No debt-to-equity column found in sector_analysis.csv.")

    # ---- Treemap by Health Score ----
    st.markdown('<div class="section-header">Sector Treemap — Health Score</div>', unsafe_allow_html=True)
    if col_health:
        treemap_data = filtered.groupby(col_sector)[col_health].mean().dropna().reset_index()
        if not treemap_data.empty:
            fig_treemap = px.treemap(
                treemap_data,
                path=[col_sector],
                values=col_health,
                color=col_health,
                color_continuous_scale=[RED, AMBER, EMERALD],
                range_color=[0, 100],
            )
            fig_treemap.update_layout(
                paper_bgcolor=NAVY_CARD,
                font_color=TEXT_PRIMARY,
                height=440,
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig_treemap, use_container_width=True)
        else:
            st.info("No health score data available to build the treemap.")
    else:
        st.info("No health score column found in sector_analysis.csv.")

st.write("")

# =====================================================
# INTERACTIVE TABLE + DOWNLOAD
# =====================================================

st.markdown('<div class="section-header">Sector Data Table</div>', unsafe_allow_html=True)

if filtered.empty:
    st.info("No rows to display for the current filters.")
else:
    display_df = filtered.copy()
    if col_id and col_id in display_df.columns:
        display_df = display_df.drop(columns=[col_id])
    if col_health:
        display_df = display_df.sort_values(col_health, ascending=False)

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
        height=420,
    )

    table_col1, table_col2 = st.columns([1, 5])
    with table_col1:
        st.download_button(
            "⬇ Download CSV",
            data=display_df.to_csv(index=False).encode("utf-8"),
            file_name="sector_analysis_filtered.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with table_col2:
        st.caption(f"Showing {len(filtered)} of {len(df)} sector record(s) based on active filters.")

# =====================================================
# FOOTER
# =====================================================

st.markdown(
    '<div class="footer-note">N100 Financial Intelligence Platform • Sector Analysis • '
    'Python · Pandas · Plotly · Streamlit</div>',
    unsafe_allow_html=True,
)