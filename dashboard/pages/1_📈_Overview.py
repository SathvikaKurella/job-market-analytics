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


st.title("📈 Overview")

df = st.session_state.job_data

if df.empty:
    st.warning("No data found. Please run the ETL pipeline.")
    st.stop()

# Summary metrics
st.markdown("### Key Insights")
col1, col2, col3 = st.columns(3)
col1.metric("Total Postings", f"{len(df):,}")
col2.metric("Unique Companies", f"{df['company'].nunique():,}")
col3.metric("Remote %", f"{df['remote'].mean() * 100:.1f}%" if not df.empty else "0%")

st.divider()

# Time trend
df["scraped_date"] = pd.to_datetime(df["scraped_at"]).dt.date
trend = df.groupby("scraped_date").size().reset_index(name="count")
fig_trend = px.line(trend, x="scraped_date", y="count", markers=True,
                    title="Job Posting Trend Over Time")
st.plotly_chart(fig_trend, use_container_width=True)
