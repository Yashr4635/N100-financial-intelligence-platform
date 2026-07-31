"""
Streamlit dashboard entrypoint.

Run with:
    streamlit run src/dashboard/app.py

This milestone only scaffolds the app: page configuration, sidebar
navigation, and registration of all 8 pages. No analytics, charts, or
KPI logic is implemented here.
"""

from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGES_DIR = Path(__file__).parent / "pages"

# ---------------------------------------------------------------------------
# Page registration
# ---------------------------------------------------------------------------
# Each entry maps to one of the scaffolded page files in src/dashboard/pages/
home = st.Page(
    str(PAGES_DIR / "01_home.py"),
    title="Home",
    icon="🏠",
    default=True,
)
profile = st.Page(
    str(PAGES_DIR / "02_profile.py"),
    title="Profile",
    icon="🧾",
)
screener = st.Page(
    str(PAGES_DIR / "03_screener.py"),
    title="Screener",
    icon="🔍",
)
peer = st.Page(
    str(PAGES_DIR / "04_peer.py"),
    title="Peer Comparison",
    icon="👥",
)
trends = st.Page(
    str(PAGES_DIR / "05_trends.py"),
    title="Trends",
    icon="📈",
)
sectors = st.Page(
    str(PAGES_DIR / "06_sectors.py"),
    title="Sectors",
    icon="🏭",
)
capital = st.Page(
    str(PAGES_DIR / "07_capital.py"),
    title="Capital",
    icon="💰",
)
reports = st.Page(
    str(PAGES_DIR / "08_reports.py"),
    title="Reports",
    icon="📄",
)

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("📊 Analytics Dashboard")
    st.caption("Sprint 4 · Milestone 1 — Scaffold")
    st.divider()

nav = st.navigation(
    {
        "Overview": [home, profile],
        "Analysis": [screener, peer, trends, sectors],
        "Finance": [capital],
        "Output": [reports],
    }
)

nav.run()