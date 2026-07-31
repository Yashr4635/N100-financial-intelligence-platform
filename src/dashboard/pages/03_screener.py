"""
Investment Screener page.

Interactive screener built from Sprint 1-3 outputs:
    - data/output/investment_screener.csv       (primary screening dataset)
    - data/output/company_health_scores.csv     (fallback source)
    - data/output/financial_ratios_calculated.csv (fallback source)
    - data/raw/companies.xlsx                    (company_id -> name/sector lookup)

This page only READS the pre-computed Sprint 1-3 outputs. No analytics
logic is implemented or modified here.
"""

import math
from pathlib import Path

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# src/dashboard/pages/03_screener.py -> project root is 3 levels up
PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
RAW_DIR = PROJECT_ROOT / "data" / "raw"

SCREENER_PATH = OUTPUT_DIR / "investment_screener.csv"
HEALTH_SCORES_PATH = OUTPUT_DIR / "company_health_scores.csv"
FINANCIAL_RATIOS_PATH = OUTPUT_DIR / "financial_ratios_calculated.csv"
COMPANIES_XLSX_PATH = RAW_DIR / "companies.xlsx"


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


@st.cache_data(show_spinner=False)
def load_companies_workbook(path: Path) -> pd.DataFrame:
    """
    Load companies.xlsx defensively.

    The sheet is not a clean table -- there may be a title/blank row
    above the real header row. This scans the first several rows for
    the one that looks like a header (contains an "id"-like cell and a
    "company name"-like cell) and reads the sheet starting from there.
    Falls back to a plain header=0 read if detection fails.
    """
    if not path.exists():
        return pd.DataFrame()

    try:
        preview = pd.read_excel(path, header=None, nrows=10)
    except Exception:
        return pd.DataFrame()

    header_row_idx = 0
    for i in range(len(preview)):
        row_values = [
            str(v).strip().lower() if pd.notna(v) else "" for v in preview.iloc[i].tolist()
        ]
        has_id = any(v == "id" for v in row_values)
        has_name = any("company" in v and "name" in v for v in row_values)
        if has_id and has_name:
            header_row_idx = i
            break

    try:
        df = pd.read_excel(path, header=header_row_idx)
    except Exception:
        return pd.DataFrame()

    df = df.dropna(axis=1, how="all").dropna(axis=0, how="all")
    return df


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


def floor_to(value: float, step: float) -> float:
    return math.floor(value / step) * step


def ceil_to(value: float, step: float) -> float:
    return math.ceil(value / step) * step


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
screener_df = load_csv(SCREENER_PATH)
health_df = load_csv(HEALTH_SCORES_PATH)
companies_df = load_companies_workbook(COMPANIES_XLSX_PATH)

# Fall back to company_health_scores.csv if the dedicated screener output
# isn't available -- both files share the same underlying schema.
source_df = screener_df if not screener_df.empty else health_df
source_label = "investment_screener.csv" if not screener_df.empty else "company_health_scores.csv"

# Resolve column names -------------------------------------------------------
id_col = find_column(source_df, ["company_id", "id"])
year_col = find_column(source_df, ["year"])
health_score_col = find_column(source_df, ["health_score", "score"])
rating_col = find_column(source_df, ["rating"])
roe_col = find_column(source_df, ["return_on_equity_pct", "roe_pct", "roe"])
npm_col = find_column(source_df, ["net_profit_margin_pct", "net_profit_margin"])
de_col = find_column(source_df, ["debt_to_equity"])

companies_id_col = find_column(companies_df, ["id", "company_id"])
companies_name_col = find_column(companies_df, ["company_name", "name", "company"])
companies_sector_col = find_column(companies_df, ["sector", "broad_sector", "industry"])

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("🔍 Screener")
st.write(
    "Filter and rank companies by health score, profitability, and "
    "leverage using the Sprint 1-3 analytics outputs."
)

if source_df.empty or not id_col:
    st.warning(
        "Could not load screening data. Please check that "
        "`data/output/investment_screener.csv` or "
        "`data/output/company_health_scores.csv` is available."
    )
    st.stop()

st.divider()

# ---------------------------------------------------------------------------
# Build a one-row-per-company snapshot (latest year available)
# ---------------------------------------------------------------------------
snapshot_df = source_df.copy()
snapshot_df["_id_key"] = snapshot_df[id_col].map(normalize_id)
snapshot_df = snapshot_df[snapshot_df["_id_key"] != ""]

if year_col and year_col in snapshot_df.columns:
    snapshot_df = snapshot_df.sort_values(by=year_col).drop_duplicates(
        subset="_id_key", keep="last"
    )
else:
    snapshot_df = snapshot_df.drop_duplicates(subset="_id_key", keep="last")

# Attach company name / sector from companies.xlsx --------------------------
id_to_name: dict[str, str] = {}
id_to_sector: dict[str, str] = {}
if companies_id_col and companies_name_col:
    for _, row in companies_df.iterrows():
        key = normalize_id(row[companies_id_col])
        if not key:
            continue
        id_to_name[key] = str(row[companies_name_col]).strip()
        if companies_sector_col:
            sector_val = row[companies_sector_col]
            id_to_sector[key] = str(sector_val).strip() if pd.notna(sector_val) else "Unknown"

snapshot_df["Company"] = snapshot_df["_id_key"].map(
    lambda k: id_to_name.get(k, f"Company #{k}")
)

sector_available = bool(id_to_sector)
if sector_available:
    snapshot_df["Sector"] = snapshot_df["_id_key"].map(lambda k: id_to_sector.get(k, "Unknown"))
else:
    st.info(
        f"`{COMPANIES_XLSX_PATH.relative_to(PROJECT_ROOT)}` does not contain a "
        "sector/industry column, so the sector filter is unavailable for this dataset."
    )

# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------
st.subheader("Screening Filters")

with st.container(border=True):
    if sector_available:
        search_col, sector_col_filter = st.columns([2, 2])
    else:
        search_col = st.container()
        sector_col_filter = None

    with search_col:
        search_term = st.text_input(
            "Search by company name",
            placeholder="e.g. INDIGO, TRENT...",
        )

    selected_sectors = None
    if sector_col_filter is not None:
        with sector_col_filter:
            sector_options = sorted(snapshot_df["Sector"].dropna().unique().tolist())
            selected_sectors = st.multiselect(
                "Sector",
                options=sector_options,
                default=sector_options,
            )

    slider_cols = st.columns(4)

    # --- Health Score slider -------------------------------------------
    with slider_cols[0]:
        if health_score_col and snapshot_df[health_score_col].notna().any():
            hs_min = float(snapshot_df[health_score_col].min())
            hs_max = float(snapshot_df[health_score_col].max())
            hs_range = st.slider(
                "Health Score",
                min_value=floor_to(hs_min, 1),
                max_value=ceil_to(hs_max, 1),
                value=(floor_to(hs_min, 1), ceil_to(hs_max, 1)),
            )
        else:
            hs_range = None
            st.caption("Health Score data not available.")

    # --- ROE slider ------------------------------------------------------
    with slider_cols[1]:
        if roe_col and snapshot_df[roe_col].notna().any():
            roe_min = float(snapshot_df[roe_col].min())
            roe_max = float(snapshot_df[roe_col].max())
            roe_range = st.slider(
                "ROE (%)",
                min_value=floor_to(roe_min, 1.0),
                max_value=ceil_to(roe_max, 1.0),
                value=(floor_to(roe_min, 1.0), ceil_to(roe_max, 1.0)),
            )
        else:
            roe_range = None
            st.caption("ROE data not available.")

    # --- Debt to Equity slider -------------------------------------------
    with slider_cols[2]:
        if de_col and snapshot_df[de_col].notna().any():
            de_min = float(snapshot_df[de_col].min())
            de_max = float(snapshot_df[de_col].max())
            de_range = st.slider(
                "Debt to Equity",
                min_value=floor_to(de_min, 0.1),
                max_value=ceil_to(de_max, 0.1),
                value=(floor_to(de_min, 0.1), ceil_to(de_max, 0.1)),
            )
        else:
            de_range = None
            st.caption("Debt to Equity data not available.")

    # --- Net Profit Margin slider -----------------------------------------
    with slider_cols[3]:
        if npm_col and snapshot_df[npm_col].notna().any():
            npm_min = float(snapshot_df[npm_col].min())
            npm_max = float(snapshot_df[npm_col].max())
            npm_range = st.slider(
                "Net Profit Margin (%)",
                min_value=floor_to(npm_min, 1.0),
                max_value=ceil_to(npm_max, 1.0),
                value=(floor_to(npm_min, 1.0), ceil_to(npm_max, 1.0)),
            )
        else:
            npm_range = None
            st.caption("Net Profit Margin data not available.")

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
filtered_df = snapshot_df.copy()

if search_term:
    filtered_df = filtered_df[
        filtered_df["Company"].str.contains(search_term, case=False, na=False)
    ]

if sector_available:
    if selected_sectors:
        filtered_df = filtered_df[filtered_df["Sector"].isin(selected_sectors)]
    else:
        filtered_df = filtered_df.iloc[0:0]

if hs_range and health_score_col:
    filtered_df = filtered_df[
        filtered_df[health_score_col].between(hs_range[0], hs_range[1])
    ]

if roe_range and roe_col:
    filtered_df = filtered_df[filtered_df[roe_col].between(roe_range[0], roe_range[1])]

if de_range and de_col:
    filtered_df = filtered_df[filtered_df[de_col].between(de_range[0], de_range[1])]

if npm_range and npm_col:
    filtered_df = filtered_df[filtered_df[npm_col].between(npm_range[0], npm_range[1])]

st.divider()

# ---------------------------------------------------------------------------
# KPI cards
# ---------------------------------------------------------------------------
st.subheader("Results Summary")

companies_found = len(filtered_df)

avg_health = (
    round(filtered_df[health_score_col].mean(), 1)
    if health_score_col and companies_found
    else None
)

if health_score_col and companies_found:
    best_row = filtered_df.loc[filtered_df[health_score_col].idxmax()]
    best_company = f"{best_row['Company']} ({round(best_row[health_score_col], 1)})"
else:
    best_company = "N/A"

kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    with st.container(border=True):
        st.metric("Companies Found", f"{companies_found:,}")

with kpi2:
    with st.container(border=True):
        st.metric("Average Health Score", f"{avg_health}" if avg_health is not None else "N/A")

with kpi3:
    with st.container(border=True):
        st.metric("Best Company", best_company)

st.divider()

# ---------------------------------------------------------------------------
# Interactive filtered dataframe
# ---------------------------------------------------------------------------
st.subheader("Filtered Companies")

display_cols = [
    c
    for c in [
        "Company",
        "Sector",
        health_score_col,
        rating_col,
        roe_col,
        npm_col,
        de_col,
        year_col,
    ]
    if c and c in filtered_df.columns
]

rename_map = {
    health_score_col: "Health Score",
    rating_col: "Rating",
    roe_col: "ROE (%)",
    npm_col: "Net Profit Margin (%)",
    de_col: "Debt to Equity",
    year_col: "Year",
}

with st.container(border=True):
    if filtered_df.empty:
        st.info("No companies match the current filters. Try widening your criteria.")
    else:
        display_df = (
            filtered_df[display_cols]
            .rename(columns=rename_map)
            .sort_values(by="Health Score", ascending=False)
            if "Health Score" in [rename_map.get(c, c) for c in display_cols]
            else filtered_df[display_cols].rename(columns=rename_map)
        )
        st.dataframe(display_df, width='stretch', hide_index=True)

        # -----------------------------------------------------------------
        # Download CSV button
        # -----------------------------------------------------------------
        csv_bytes = display_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download filtered results as CSV",
            data=csv_bytes,
            file_name="screener_results.csv",
            mime="text/csv",
        )