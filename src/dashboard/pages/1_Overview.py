import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("📊 Platform Overview")

companies = pd.read_excel("data/raw/companies.xlsx")
health = pd.read_csv("data/output/company_health_scores.csv")
sector = pd.read_csv("data/output/sector_analysis.csv")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Companies", companies["company_name"].nunique())
col2.metric("Records", len(health))
col3.metric("Average Health", round(health["health_score"].mean(), 2))
col4.metric("Sectors", sector["broad_sector"].nunique())

st.divider()

st.subheader("Health Score Distribution")

st.bar_chart(
    health["rating"].value_counts()
)

st.subheader("Top 10 Healthy Companies")

top = health.sort_values(
    by="health_score",
    ascending=False
).head(10)

st.dataframe(
    top[
        [
            "company_id",
            "health_score",
            "rating"
        ]
    ],
    use_container_width=True
)