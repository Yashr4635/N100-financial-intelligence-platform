"""
Peer Comparison page.

Side-by-side comparison of 2-3 companies built from Sprint 1-3 outputs:
    - data/output/peer_comparison.csv           (primary source: ratios,
      health score, rating, and sector all in one place)
    - data/output/company_health_scores.csv     (fallback source)
    - data/output/financial_ratios_calculated.csv (fallback source)
    - data/raw/companies.xlsx                    (company_id -> full name lookup)
    - reports/radar_charts/{company_id}_radar.png (pre-generated radar image,
      filed under the company's ticker/id)

This page only READS the pre-computed Sprint 1-3 outputs. No analytics
logic is implemented or modified here.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# src/dashboard/pages/04_peer.py -> project root is 3 levels up
PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
RAW_DIR = PROJECT_ROOT / "data" / "raw"

PEER_COMPARISON_PATH = OUTPUT_DIR / "peer_comparison.csv"
HEALTH_SCORES_PATH = OUTPUT_DIR / "company_health_scores.csv"
FINANCIAL_RATIOS_PATH = OUTPUT_DIR / "financial_ratios_calculated.csv"
COMPANIES_XLSX_PATH = RAW_DIR / "companies.xlsx"
RADAR_CHARTS_DIR = PROJECT_ROOT / "reports" / "radar_charts"


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


def format_value(value, decimals=2, suffix=""):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "N/A"
    if isinstance(value, (int, float)):
        return f"{round(value, decimals)}{suffix}"
    return f"{value}{suffix}"


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
peer_df = load_csv(PEER_COMPARISON_PATH)
health_df = load_csv(HEALTH_SCORES_PATH)
ratios_df = load_csv(FINANCIAL_RATIOS_PATH)
companies_df = load_companies_workbook(COMPANIES_XLSX_PATH)

# Prefer the dedicated peer_comparison.csv (it already combines ratios,
# health score, rating, and sector). Fall back to company_health_scores.csv
# if it isn't available.
source_df = peer_df if not peer_df.empty else health_df

# Resolve column names -------------------------------------------------------
id_col = find_column(source_df, ["company_id", "id"])
year_col = find_column(source_df, ["year"])
health_score_col = find_column(source_df, ["health_score", "score"])
rating_col = find_column(source_df, ["rating"])
sector_col = find_column(source_df, ["sector", "broad_sector", "industry"])
roe_col = find_column(source_df, ["return_on_equity_pct", "roe_pct", "roe"])
npm_col = find_column(source_df, ["net_profit_margin_pct", "net_profit_margin"])
de_col = find_column(source_df, ["debt_to_equity"])
ic_col = find_column(source_df, ["interest_coverage"])
eps_col = find_column(source_df, ["earnings_per_share", "eps"])
bvps_col = find_column(source_df, ["book_value_per_share", "book_value"])

companies_id_col = find_column(companies_df, ["id", "company_id"])
companies_name_col = find_column(companies_df, ["company_name", "name", "company"])

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("👥 Peer Comparison")
st.write(
    "Compare two or three companies side by side across health score, "
    "profitability, leverage, and per-share metrics."
)

if source_df.empty or not id_col:
    st.warning(
        "Could not load comparison data. Please check that "
        "`data/output/peer_comparison.csv` or "
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

snapshot_df = snapshot_df.set_index("_id_key", drop=False)

# Name lookup from companies.xlsx --------------------------------------------
id_to_name: dict[str, str] = {}
if companies_id_col and companies_name_col:
    for _, row in companies_df.iterrows():
        key = normalize_id(row[companies_id_col])
        if key:
            id_to_name[key] = str(row[companies_name_col]).strip()


def display_label(company_id: str) -> str:
    return id_to_name.get(company_id, company_id)


available_ids = sorted(snapshot_df["_id_key"].unique().tolist(), key=lambda cid: display_label(cid).lower())

if len(available_ids) < 2:
    st.error("At least two companies with data are required for a comparison.")
    st.stop()

# ---------------------------------------------------------------------------
# 1-3. Company dropdowns
# ---------------------------------------------------------------------------
st.subheader("Select Companies")

dropdown_col1, dropdown_col2, dropdown_col3 = st.columns(3)

with dropdown_col1:
    company_a_id = st.selectbox(
        "Company A",
        options=available_ids,
        format_func=display_label,
        index=0,
        key="peer_company_a",
    )

with dropdown_col2:
    default_b_index = 1 if len(available_ids) > 1 else 0
    company_b_id = st.selectbox(
        "Company B",
        options=available_ids,
        format_func=display_label,
        index=default_b_index,
        key="peer_company_b",
    )

with dropdown_col3:
    optional_options = ["None"] + available_ids
    company_c_choice = st.selectbox(
        "Company C (optional)",
        options=optional_options,
        format_func=lambda v: "None" if v == "None" else display_label(v),
        index=0,
        key="peer_company_c",
    )

selected_ids = [company_a_id, company_b_id]
if company_c_choice != "None":
    selected_ids.append(company_c_choice)

# Keep unique companies only, preserving selection order.
seen = set()
selected_ids = [cid for cid in selected_ids if not (cid in seen or seen.add(cid))]

if len(selected_ids) < 2:
    st.warning("Please select at least two distinct companies to compare.")
    st.stop()

selected_names = [display_label(cid) for cid in selected_ids]
selected_rows = {cid: snapshot_df.loc[cid] for cid in selected_ids}

st.divider()

# ---------------------------------------------------------------------------
# Overview: Health Score & Rating comparison
# ---------------------------------------------------------------------------
st.subheader("Overview")

overview_cols = st.columns(len(selected_ids))
for col, cid, name in zip(overview_cols, selected_ids, selected_names):
    row = selected_rows[cid]
    with col:
        with st.container(border=True):
            st.markdown(f"**{name}**")
            sector_value = row[sector_col] if sector_col else "N/A"
            st.caption(f"Sector: {format_value(sector_value)}")
            st.metric("Health Score", format_value(row[health_score_col], 1) if health_score_col else "N/A")
            st.metric("Rating", format_value(row[rating_col]) if rating_col else "N/A")

st.divider()

# ---------------------------------------------------------------------------
# KPI cards — one row per metric, one column per company
# ---------------------------------------------------------------------------
st.subheader("Key Financial Metrics")

kpi_metrics = [
    ("ROE", roe_col, 2, "%"),
    ("Net Profit Margin", npm_col, 2, "%"),
    ("Debt to Equity", de_col, 2, ""),
    ("Interest Coverage", ic_col, 2, ""),
    ("EPS", eps_col, 2, ""),
    ("Book Value / Share", bvps_col, 2, ""),
]

for label, col_name, decimals, suffix in kpi_metrics:
    with st.container(border=True):
        st.markdown(f"**{label}**")
        metric_cols = st.columns(len(selected_ids))
        for m_col, cid, name in zip(metric_cols, selected_ids, selected_names):
            row = selected_rows[cid]
            value = row[col_name] if col_name and col_name in row else None
            with m_col:
                st.metric(name, format_value(value, decimals, suffix))

st.divider()

# ---------------------------------------------------------------------------
# Comparison dataframe
# ---------------------------------------------------------------------------
st.subheader("Comparison Table")

table_metrics = [
    ("Health Score", health_score_col, 1, ""),
    ("Rating", rating_col, None, ""),
    ("ROE (%)", roe_col, 2, "%"),
    ("Net Profit Margin (%)", npm_col, 2, "%"),
    ("Debt to Equity", de_col, 2, ""),
    ("Interest Coverage", ic_col, 2, ""),
    ("EPS", eps_col, 2, ""),
    ("Book Value / Share", bvps_col, 2, ""),
]

comparison_data = {}
for name, cid in zip(selected_names, selected_ids):
    row = selected_rows[cid]
    comparison_data[name] = [
        format_value(row[col_name], decimals if decimals is not None else 2, suffix)
        if col_name
        else "N/A"
        for _, col_name, decimals, suffix in table_metrics
    ]

comparison_df = pd.DataFrame(
    comparison_data, index=[label for label, *_ in table_metrics]
)

with st.container(border=True):
    st.dataframe(comparison_df, width='stretch')

st.divider()

# ---------------------------------------------------------------------------
# Radar chart comparison
# ---------------------------------------------------------------------------
st.subheader("Radar Chart Comparison")

radar_cols = st.columns(len(selected_ids))
for col, cid, name in zip(radar_cols, selected_ids, selected_names):
    radar_path = RADAR_CHARTS_DIR / f"{cid}_radar.png"
    with col:
        with st.container(border=True):
            st.markdown(f"**{name}**")
            if radar_path.exists():
                st.image(str(radar_path), width='stretch')
            else:
                st.info(
                    f"No radar chart found for **{name}** at "
                    f"`reports/radar_charts/{cid}_radar.png`."
                )

st.divider()

# ---------------------------------------------------------------------------
# Summary: strongest and weakest metrics
# ---------------------------------------------------------------------------
st.subheader("Summary")

# Metrics used for strongest/weakest analysis, with their "better" direction.
summary_metrics = [
    ("Health Score", health_score_col, "higher", "", 1),
    ("ROE", roe_col, "higher", "%", 2),
    ("Net Profit Margin", npm_col, "higher", "%", 2),
    ("Debt to Equity", de_col, "lower", "", 2),
    ("Interest Coverage", ic_col, "higher", "", 2),
    ("EPS", eps_col, "higher", "", 2),
    ("Book Value / Share", bvps_col, "higher", "", 2),
]

# For each metric, rank the selected companies (1 = best).
metric_winners: dict[str, tuple[str, float]] = {}
company_wins: dict[str, list[str]] = {cid: [] for cid in selected_ids}
company_losses: dict[str, list[str]] = {cid: [] for cid in selected_ids}

for label, col_name, direction, suffix, decimals in summary_metrics:
    if not col_name:
        continue
    values = {}
    for cid in selected_ids:
        row = selected_rows[cid]
        val = row[col_name] if col_name in row else None
        if val is not None and not (isinstance(val, float) and pd.isna(val)):
            values[cid] = val

    if len(values) < 2:
        continue

    if direction == "higher":
        best_id = max(values, key=values.get)
        worst_id = min(values, key=values.get)
    else:
        best_id = min(values, key=values.get)
        worst_id = max(values, key=values.get)

    if best_id != worst_id:
        company_wins[best_id].append(f"{label} ({format_value(values[best_id], decimals, suffix)})")
        company_losses[worst_id].append(f"{label} ({format_value(values[worst_id], decimals, suffix)})")

with st.container(border=True):
    any_summary = False
    for cid, name in zip(selected_ids, selected_names):
        wins = company_wins.get(cid, [])
        losses = company_losses.get(cid, [])
        if not wins and not losses:
            continue
        any_summary = True
        st.markdown(f"**{name}**")
        if wins:
            st.markdown(f"- 🏆 Strongest in: {', '.join(wins)}")
        if losses:
            st.markdown(f"- ⚠️ Weakest in: {', '.join(losses)}")

    if not any_summary:
        st.info("Not enough comparable metric data to generate a summary.")