"""
N100 Financial Intelligence Platform
Investment Screener Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --------------------------------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------------------------------
st.set_page_config(
    page_title="Investment Screener | N100 Financial Intelligence",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = "data/output/investment_screener.csv"

# --------------------------------------------------------------------------------
# CUSTOM CSS (matches Home / Company Analysis / Sector Analysis theme)
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
        font-size: 0.8rem;
        color: #8b96a5;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 0.5rem;
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.2;
    }
    .kpi-icon {
        font-size: 1.5rem;
        margin-bottom: 0.4rem;
        display: block;
    }
    .kpi-accent-blue { border-left: 4px solid #4f9dfd; }
    .kpi-accent-green { border-left: 4px solid #34d399; }
    .kpi-accent-orange { border-left: 4px solid #fbbf24; }
    .kpi-accent-purple { border-left: 4px solid #a78bfa; }
    .kpi-accent-pink { border-left: 4px solid #f472b6; }

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

    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 700;
        background: rgba(52,211,153,0.15);
        color: #34d399;
        border: 1px solid rgba(52,211,153,0.3);
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

    rename_map = {
        "company": "company_name",
        "name": "company_name",
        "symbol": "ticker",
        "stock_symbol": "ticker",
        "industry": "sector",
        "sector_name": "sector",
        "health_score": "health_score",
        "financial_quality": "financial_quality_score",
        "quality_score": "financial_quality_score",
        "rating_category": "rating",
        "investment_rating": "rating",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    if "company_name" not in df.columns:
        df["company_name"] = df.get("ticker", pd.Series(["Unknown"] * len(df)))
    df["company_name"] = df["company_name"].fillna("Unknown").astype(str).str.strip()

    if "sector" not in df.columns:
        df["sector"] = "Unknown"
    df["sector"] = df["sector"].fillna("Unknown").astype(str).str.strip()

    if "rating" not in df.columns:
        df["rating"] = "Unrated"
    df["rating"] = df["rating"].fillna("Unrated").astype(str).str.strip()

    for col in ["health_score", "financial_quality_score"]:
        if col not in df.columns:
            df[col] = np.nan
        df[col] = pd.to_numeric(df[col], errors="coerce")
        median_val = df[col].median() if df[col].notna().any() else 0
        df[col] = df[col].fillna(median_val)

    return df


df = load_data(DATA_PATH)

# --------------------------------------------------------------------------------
# HERO SECTION
# --------------------------------------------------------------------------------
st.markdown(
    """
<div class="hero-container">
    <div class="hero-title">🧮 Investment Screener</div>
    <div class="hero-subtitle">Screen, filter, and rank N100 companies by health score, financial quality, and investment rating</div>
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
st.sidebar.markdown("## 🔍 Screener Filters")

search_query = st.sidebar.text_input(
    "Company Search", placeholder="Type a company name..."
)

all_sectors = ["All"] + sorted(df["sector"].dropna().unique().tolist())
selected_sector = st.sidebar.selectbox("Sector", options=all_sectors, index=0)

all_ratings = ["All"] + sorted(df["rating"].dropna().unique().tolist())
selected_rating = st.sidebar.selectbox("Rating", options=all_ratings, index=0)

hs_min = float(df["health_score"].min())
hs_max = float(df["health_score"].max())
if hs_min == hs_max:
    hs_max = hs_min + 1
health_score_range = st.sidebar.slider(
    "Health Score Range",
    min_value=float(np.floor(hs_min)),
    max_value=float(np.ceil(hs_max)),
    value=(float(np.floor(hs_min)), float(np.ceil(hs_max))),
    step=0.5,
)

fq_min = float(df["financial_quality_score"].min())
fq_max = float(df["financial_quality_score"].max())
if fq_min == fq_max:
    fq_max = fq_min + 1
fq_score_range = st.sidebar.slider(
    "Financial Quality Score Range",
    min_value=float(np.floor(fq_min)),
    max_value=float(np.ceil(fq_max)),
    value=(float(np.floor(fq_min)), float(np.ceil(fq_max))),
    step=0.5,
)

st.sidebar.markdown("---")
st.sidebar.caption("Data source: `investment_screener.csv`")

# --------------------------------------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------------------------------------
filtered_df = df.copy()

if search_query.strip():
    filtered_df = filtered_df[
        filtered_df["company_name"].str.contains(
            search_query.strip(), case=False, na=False
        )
    ]

if selected_sector != "All":
    filtered_df = filtered_df[filtered_df["sector"] == selected_sector]

if selected_rating != "All":
    filtered_df = filtered_df[filtered_df["rating"] == selected_rating]

filtered_df = filtered_df[
    (filtered_df["health_score"] >= health_score_range[0])
    & (filtered_df["health_score"] <= health_score_range[1])
    & (filtered_df["financial_quality_score"] >= fq_score_range[0])
    & (filtered_df["financial_quality_score"] <= fq_score_range[1])
]

# --------------------------------------------------------------------------------
# KPI CARDS
# --------------------------------------------------------------------------------
total_companies = len(df)
filtered_count = len(filtered_df)

if filtered_count > 0:
    avg_health_score = filtered_df["health_score"].mean()
    excellent_companies = filtered_df[
        filtered_df["rating"].str.contains("Excellent", case=False, na=False)
    ].shape[0]
    top_company_row = filtered_df.loc[filtered_df["health_score"].idxmax()]
    top_company = top_company_row["company_name"]
else:
    avg_health_score = 0
    excellent_companies = 0
    top_company = "N/A"

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(
        f"""
    <div class="kpi-card kpi-accent-blue">
        <span class="kpi-icon">🏢</span>
        <div class="kpi-label">Total Companies</div>
        <div class="kpi-value">{total_companies}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
    <div class="kpi-card kpi-accent-purple">
        <span class="kpi-icon">🧾</span>
        <div class="kpi-label">Filtered Companies</div>
        <div class="kpi-value">{filtered_count}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
    <div class="kpi-card kpi-accent-green">
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
        <span class="kpi-icon">⭐</span>
        <div class="kpi-label">Excellent Companies</div>
        <div class="kpi-value">{excellent_companies}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col5:
    st.markdown(
        f"""
    <div class="kpi-card kpi-accent-pink">
        <span class="kpi-icon">🏆</span>
        <div class="kpi-label">Top Company</div>
        <div class="kpi-value" style="font-size:1.15rem;">{top_company}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# --------------------------------------------------------------------------------
# HANDLE EMPTY FILTER RESULTS
# --------------------------------------------------------------------------------
if filtered_df.empty:
    st.warning(
        "⚠️ No companies match the selected filters. Try adjusting the sidebar options."
    )
    st.stop()

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
# CHARTS ROW 1: Health Score Histogram & Rating Pie
# --------------------------------------------------------------------------------
st.markdown(
    '<div class="section-header">📊 Score Distributions</div>', unsafe_allow_html=True
)

c1, c2 = st.columns(2)

with c1:
    fig_hist = px.histogram(
        filtered_df,
        x="health_score",
        nbins=25,
        color_discrete_sequence=["#4f9dfd"],
        title="Health Score Distribution",
    )
    fig_hist.update_layout(bargap=0.05)
    st.plotly_chart(style_fig(fig_hist), use_container_width=True)

with c2:
    rating_counts = filtered_df["rating"].value_counts().reset_index()
    rating_counts.columns = ["rating", "count"]
    fig_pie = px.pie(
        rating_counts,
        names="rating",
        values="count",
        title="Rating Distribution",
        color_discrete_sequence=COLOR_SEQ,
        hole=0.45,
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(style_fig(fig_pie), use_container_width=True)

# --------------------------------------------------------------------------------
# CHARTS ROW 2: Financial Quality Distribution & Scatter
# --------------------------------------------------------------------------------
c3, c4 = st.columns(2)

with c3:
    fig_fq = px.histogram(
        filtered_df,
        x="financial_quality_score",
        nbins=25,
        color_discrete_sequence=["#a78bfa"],
        title="Financial Quality Score Distribution",
    )
    fig_fq.update_layout(bargap=0.05)
    st.plotly_chart(style_fig(fig_fq), use_container_width=True)

with c4:
    fig_scatter = px.scatter(
        filtered_df,
        x="health_score",
        y="financial_quality_score",
        color="rating",
        hover_name="company_name",
        title="Health Score vs Financial Quality Score",
        color_discrete_sequence=COLOR_SEQ,
    )
    fig_scatter.update_traces(
        marker=dict(size=9, opacity=0.8, line=dict(width=0.5, color="#0e1117"))
    )
    st.plotly_chart(style_fig(fig_scatter), use_container_width=True)

# --------------------------------------------------------------------------------
# CHARTS ROW 3: Bubble Chart & Treemap
# --------------------------------------------------------------------------------
st.markdown(
    '<div class="section-header">🧭 Multi-Dimensional Analysis</div>',
    unsafe_allow_html=True,
)

c5, c6 = st.columns(2)

with c5:
    fig_bubble = px.scatter(
        filtered_df,
        x="health_score",
        y="financial_quality_score",
        size="health_score",
        color="sector",
        hover_name="company_name",
        title="Bubble Chart: Health vs Quality (Size = Health Score)",
        color_discrete_sequence=COLOR_SEQ,
        size_max=40,
    )
    fig_bubble.update_traces(
        marker=dict(opacity=0.75, line=dict(width=0.5, color="#0e1117"))
    )
    st.plotly_chart(style_fig(fig_bubble), use_container_width=True)

with c6:
    fig_tree = px.treemap(
        filtered_df,
        path=[px.Constant("All Companies"), "sector", "company_name"],
        values="health_score",
        color="financial_quality_score",
        color_continuous_scale="Tealgrn",
        title="Treemap: Sector → Company (Color = Financial Quality)",
    )
    fig_tree.update_traces(root_color="#1a1f2e")
    st.plotly_chart(style_fig(fig_tree, height=460), use_container_width=True)

# --------------------------------------------------------------------------------
# TOP 20 COMPANIES BAR CHART
# --------------------------------------------------------------------------------
st.markdown(
    '<div class="section-header">🏅 Top 20 Companies</div>', unsafe_allow_html=True
)

top20 = filtered_df.sort_values("health_score", ascending=False).head(20)
fig_top20 = px.bar(
    top20.sort_values("health_score", ascending=True),
    x="health_score",
    y="company_name",
    orientation="h",
    color="health_score",
    color_continuous_scale="Tealgrn",
    title="Top 20 Companies by Health Score",
    labels={"health_score": "Health Score", "company_name": "Company"},
)
fig_top20.update_coloraxes(showscale=False)
st.plotly_chart(style_fig(fig_top20, height=600), use_container_width=True)

# --------------------------------------------------------------------------------
# DATA TABLE
# --------------------------------------------------------------------------------
st.markdown(
    '<div class="section-header">📋 Screener Results</div>', unsafe_allow_html=True
)

preferred_cols = [
    "company_name",
    "ticker",
    "sector",
    "rating",
    "health_score",
    "financial_quality_score",
]
display_cols = [c for c in preferred_cols if c in filtered_df.columns]
remaining_cols = [c for c in filtered_df.columns if c not in display_cols]
final_cols = display_cols + remaining_cols

st.dataframe(
    filtered_df[final_cols].sort_values("health_score", ascending=False),
    use_container_width=True,
    height=440,
    hide_index=True,
)

# --------------------------------------------------------------------------------
# DOWNLOAD BUTTON
# --------------------------------------------------------------------------------
csv_data = filtered_df[final_cols].to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Screener Results (CSV)",
    data=csv_data,
    file_name="filtered_investment_screener.csv",
    mime="text/csv",
    use_container_width=False,
)

st.markdown("<br>", unsafe_allow_html=True)
st.caption("N100 Financial Intelligence Platform · Investment Screener Module")
