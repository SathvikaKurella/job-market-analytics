import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from etl.db import engine
import pandas as pd
from sqlalchemy import text
import streamlit as st
import plotly.express as px


# ✅ Ensure job_data is available even if page opened directly
if "job_data" not in st.session_state:
    @st.cache_data(ttl=3600)
    def load_data(limit=10000):
        query = text("SELECT * FROM job_postings ORDER BY scraped_at DESC LIMIT :limit")
        with engine.connect() as conn:
            df = pd.read_sql_query(query, conn, params={"limit": limit})
        return df

    st.session_state.job_data = load_data()


st.title("💰 Salary Insights")

df = st.session_state.job_data
df = df[~df["salary_min"].isna()]

if df.empty:
    st.info("No salary data available.")
    st.stop()

fig = px.histogram(df, x="salary_min", nbins=30,
                   title="Distribution of Minimum Salaries",
                   labels={"salary_min": "Minimum Salary ($)"})
st.plotly_chart(fig, use_container_width=True)
