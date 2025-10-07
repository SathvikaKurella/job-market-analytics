import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from etl.db import engine
import pandas as pd
from sqlalchemy import text
import streamlit as st

# ✅ Ensure job_data is available even if page opened directly
if "job_data" not in st.session_state:
    @st.cache_data(ttl=3600)
    def load_data(limit=10000):
        query = text("SELECT * FROM job_postings ORDER BY scraped_at DESC LIMIT :limit")
        with engine.connect() as conn:
            df = pd.read_sql_query(query, conn, params={"limit": limit})
        return df

    st.session_state.job_data = load_data()

import streamlit as st
import plotly.express as px

st.title("💼 Job Roles Analysis")

df = st.session_state.job_data

top_n = st.sidebar.slider("Top N Roles", 5, 50, 10)
top_roles = df["job_title"].fillna("Unknown").value_counts().nlargest(top_n).reset_index()
top_roles.columns = ["job_title", "count"]

fig = px.bar(top_roles, x="count", y="job_title", orientation="h",
             color="count", color_continuous_scale="Blues",
             title="Top In-Demand Roles")
st.plotly_chart(fig, use_container_width=True)
