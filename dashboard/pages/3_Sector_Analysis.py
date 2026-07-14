"""
N100 Financial Intelligence Platform
Sector Analysis Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --------------------------------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------------------------------
st.set_page_config(
    page_title="Sector Analysis | N100 Financial Intelligence",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = "data/output/sector_analysis.csv"

# --------------------------------------------------------------------------------
# CUSTOM CSS (matches Home / Company Analysis theme)
# --------------------------------------------------------------------------------
st.markdown(
    """
<style>
    .stApp {
        background: linear-gradient(180deg, #0e1117 0%, #12161f 100%);
    }

    /* Hero Section */
    .hero-container {
        padding: 2.2rem 2rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #1a1f2e 0%, #232a3d 100%);
        border: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.35);
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #9aa4b2;
        font-weight: 400;
    }

    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(145deg, #1a1f2e, #1f2536);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 16px;
        padding: 1.4rem 1.3rem;
        text-align: left;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        box-shadow: 0 4px 18px rgba(0,0,0,0.25);
        height: 100%;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 28px rgba(0,0,0,0.4);
        border-color: rgba(99,179,237,0.35);
    }
    .kpi-label {
        font-size: 0.82rem;
        color: #8b96a5;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 0.5rem;
    }
    .kpi-value {
        font-size: 1.7rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.2;
    }
    .kpi-icon {
        font-size: 1.6rem;
        margin-bottom: 0.4rem;
        display: block;
    }
    .kpi-accent-blue { border-left: 4px solid #4f9dfd; }
    .kpi-accent-green { border-left: 4px solid #34d399; }
    .kpi-accent-orange { border-left: 4px solid #fbbf24; }
    .kpi-accent-purple { border-left: 4px solid #a78bfa; }

    /* Section headers */
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #ffffff;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.08);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0e1117;
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    /* Dataframe container */
    .dataframe-container {
        background: #1a1f2e;
        border-radius: 14px;
        padding: 1rem;
        border: 1px solid rgba(255,255,255,0.06);
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff;
    }

    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #0e1117; }
    ::-webkit-scrollbar-thumb { background: #3a4152; border-radius: 4px; }
</style>
""",
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------------
# DATA LOADING
# --------------------------------------------------------------------------------
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        return pd.DataFrame()

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Normalize expected columns with safe fallbacks
    rename_map = {
        "sector_name": "sector",
        "industry": "sector",
        "health_score": "avg_health_score",
        "roe": "avg_roe",
        "return_on_equity": "avg_roe",
        "profit_margin": "avg_profit_margin",
        "net_profit_margin": "avg_profit_margin",
        "debt_to_equity": "avg_debt_to_equity",
        "de_ratio": "avg_debt_to_equity",
        "company_count": "num_companies",
        "companies": "num_companies",
        "num_of_companies": "num_companies",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    required_numeric = [
        "avg_health_score",
        "avg_roe",
        "avg_profit_margin",
        "avg_debt_to_equity",
    ]
    for col in required_numeric:
        if col not in df.columns:
            df[col] = np.nan
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if "sector" not in df.columns:
        df["sector"] = "Unknown"
    df["sector"] = df["sector"].fillna("Unknown").astype(str).str.strip()

    if "num_companies" not in df.columns:
        df["num_companies"] = 1
    df["num_companies"] = pd.to_numeric(df["num_companies"], errors="coerce").fillna(1)

    # Fill remaining NaNs safely
    for col in required_numeric:
        df[col] = df[col].fillna(df[col].median() if df[col].notna().any() else 0)

    return df


df = load_data(DATA_PATH)

# --------------------------------------------------------------------------------
# HERO SECTION
# --------------------------------------------------------------------------------
st.markdown(
    """
<div class="hero-container">
    <div class="hero-title">🏭 Sector Analysis Dashboard</div>
    <div class="hero-subtitle">Comparative performance, profitability, and risk metrics across sectors — N100 Financial Intelligence Platform</div>
</div>
""",
    unsafe_allow_html=True,
)

if df.empty:
    st.error(
        f"⚠️ Data file not found or empty at `{DATA_PATH}`. Please verify the file path."
    )
    st.stop()

# --------------------------------------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------------------------------------
st.sidebar.markdown("## 🔍 Filters")

all_sectors = sorted(df["sector"].dropna().unique().tolist())
selected_sectors = st.sidebar.multiselect(
    "Select Sector(s)", options=all_sectors, default=all_sectors
)

min_health = (
    float(df["avg_health_score"].min()) if df["avg_health_score"].notna().any() else 0.0
)
max_health = (
    float(df["avg_health_score"].max())
    if df["avg_health_score"].notna().any()
    else 100.0
)
if min_health == max_health:
    max_health = min_health + 1

min_health_score = st.sidebar.slider(
    "Minimum Health Score",
    min_value=float(np.floor(min_health)),
    max_value=float(np.ceil(max_health)),
    value=float(np.floor(min_health)),
    step=0.5,
)

st.sidebar.markdown("---")
st.sidebar.caption("Data source: `sector_analysis.csv`")

# Apply filters
filtered_df = df[
    (df["sector"].isin(selected_sectors)) & (df["avg_health_score"] >= min_health_score)
].copy()

if filtered_df.empty:
    st.warning(
        "No sectors match the selected filters. Try adjusting the sidebar options."
    )
    st.stop()

# --------------------------------------------------------------------------------
# KPI CARDS
# --------------------------------------------------------------------------------
total_sectors = filtered_df["sector"].nunique()

best_sector_row = filtered_df.loc[filtered_df["avg_health_score"].idxmax()]
best_sector = best_sector_row["sector"]

avg_health_score = filtered_df["avg_health_score"].mean()

highest_roe_row = filtered_df.loc[filtered_df["avg_roe"].idxmax()]
highest_roe_sector = highest_roe_row["sector"]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
    <div class="kpi-card kpi-accent-blue">
        <span class="kpi-icon">🏢</span>
        <div class="kpi-label">Total Sectors</div>
        <div class="kpi-value">{total_sectors}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
    <div class="kpi-card kpi-accent-green">
        <span class="kpi-icon">🏆</span>
        <div class="kpi-label">Best Performing Sector</div>
        <div class="kpi-value" style="font-size:1.25rem;">{best_sector}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
    <div class="kpi-card kpi-accent-purple">
        <span class="kpi-icon">💠</span>
        <div class="kpi-label">Average Health Score</div>
        <div class="kpi-value">{avg_health_score:.2f}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
    <div class="kpi-card kpi-accent-orange">
        <span class="kpi-icon">📈</span>
        <div class="kpi-label">Highest ROE Sector</div>
        <div class="kpi-value" style="font-size:1.25rem;">{highest_roe_sector}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# --------------------------------------------------------------------------------
# PLOTLY THEME HELPERS
# --------------------------------------------------------------------------------
PLOTLY_TEMPLATE = "plotly_dark"
PAPER_BG = "rgba(0,0,0,0)"
PLOT_BG = "rgba(0,0,0,0)"
COLOR_SEQ = px.colors.sequential.Tealgrn + px.colors.sequential.Sunset


def style_fig(fig, height=420):
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color="#e5e9f0", size=13),
        margin=dict(l=20, r=20, t=60, b=20),
        height=height,
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.06)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.06)")
    return fig


# --------------------------------------------------------------------------------
# CHARTS ROW 1: Health Score (H-Bar) & ROE (Bar)
# --------------------------------------------------------------------------------
st.markdown(
    '<div class="section-header">📊 Sector Performance Metrics</div>',
    unsafe_allow_html=True,
)

c1, c2 = st.columns(2)

with c1:
    health_sorted = filtered_df.sort_values("avg_health_score", ascending=True)
    fig_health = px.bar(
        health_sorted,
        x="avg_health_score",
        y="sector",
        orientation="h",
        color="avg_health_score",
        color_continuous_scale="Tealgrn",
        title="Average Health Score by Sector",
        labels={"avg_health_score": "Avg Health Score", "sector": "Sector"},
    )
    fig_health.update_coloraxes(showscale=False)
    st.plotly_chart(style_fig(fig_health), use_container_width=True)

with c2:
    roe_sorted = filtered_df.sort_values("avg_roe", ascending=False)
    fig_roe = px.bar(
        roe_sorted,
        x="sector",
        y="avg_roe",
        color="avg_roe",
        color_continuous_scale="Sunset",
        title="Average ROE by Sector",
        labels={"avg_roe": "Avg ROE (%)", "sector": "Sector"},
    )
    fig_roe.update_coloraxes(showscale=False)
    fig_roe.update_xaxes(tickangle=-35)
    st.plotly_chart(style_fig(fig_roe), use_container_width=True)

# --------------------------------------------------------------------------------
# CHARTS ROW 2: Profit Margin & Debt to Equity
# --------------------------------------------------------------------------------
c3, c4 = st.columns(2)

with c3:
    margin_sorted = filtered_df.sort_values("avg_profit_margin", ascending=False)
    fig_margin = px.bar(
        margin_sorted,
        x="sector",
        y="avg_profit_margin",
        color="avg_profit_margin",
        color_continuous_scale="Blues",
        title="Average Profit Margin by Sector",
        labels={"avg_profit_margin": "Avg Profit Margin (%)", "sector": "Sector"},
    )
    fig_margin.update_coloraxes(showscale=False)
    fig_margin.update_xaxes(tickangle=-35)
    st.plotly_chart(style_fig(fig_margin), use_container_width=True)

with c4:
    de_sorted = filtered_df.sort_values("avg_debt_to_equity", ascending=False)
    fig_de = px.bar(
        de_sorted,
        x="sector",
        y="avg_debt_to_equity",
        color="avg_debt_to_equity",
        color_continuous_scale="Oranges",
        title="Average Debt to Equity by Sector",
        labels={"avg_debt_to_equity": "Avg Debt/Equity", "sector": "Sector"},
    )
    fig_de.update_coloraxes(showscale=False)
    fig_de.update_xaxes(tickangle=-35)
    st.plotly_chart(style_fig(fig_de), use_container_width=True)

# --------------------------------------------------------------------------------
# CHARTS ROW 3: Distribution (Pie) & Treemap
# --------------------------------------------------------------------------------
st.markdown(
    '<div class="section-header">🧭 Sector Composition</div>', unsafe_allow_html=True
)

c5, c6 = st.columns(2)

with c5:
    fig_pie = px.pie(
        filtered_df,
        names="sector",
        values="num_companies",
        title="Sector Distribution (by Company Count)",
        color_discrete_sequence=COLOR_SEQ,
        hole=0.45,
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(style_fig(fig_pie), use_container_width=True)

with c6:
    fig_tree = px.treemap(
        filtered_df,
        path=[px.Constant("All Sectors"), "sector"],
        values="num_companies",
        color="avg_health_score",
        color_continuous_scale="Tealgrn",
        title="Sector Treemap (Size = Companies, Color = Health Score)",
    )
    fig_tree.update_traces(root_color="#1a1f2e")
    st.plotly_chart(style_fig(fig_tree), use_container_width=True)

# --------------------------------------------------------------------------------
# DATA TABLE
# --------------------------------------------------------------------------------
st.markdown(
    '<div class="section-header">📋 Sector Data Table</div>', unsafe_allow_html=True
)

display_cols = [
    "sector",
    "num_companies",
    "avg_health_score",
    "avg_roe",
    "avg_profit_margin",
    "avg_debt_to_equity",
]
display_cols = [c for c in display_cols if c in filtered_df.columns]

st.dataframe(
    filtered_df[display_cols].sort_values("avg_health_score", ascending=False),
    use_container_width=True,
    height=420,
    hide_index=True,
)

# --------------------------------------------------------------------------------
# DOWNLOAD BUTTON
# --------------------------------------------------------------------------------
csv_data = filtered_df[display_cols].to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Sector Data (CSV)",
    data=csv_data,
    file_name="filtered_sector_analysis.csv",
    mime="text/csv",
    use_container_width=False,
)

st.markdown("<br>", unsafe_allow_html=True)
st.caption("N100 Financial Intelligence Platform · Sector Analysis Module")
