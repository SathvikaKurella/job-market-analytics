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



st.title("🧠 Skills Analysis")

df = st.session_state.job_data

def extract_skills(series):
    text = " ".join(series.dropna().astype(str).tolist())
    tokens = [t.strip().lower() for t in text.replace(",", " ").split()]
    tokens = [t for t in tokens if len(t) > 1 and t.isalnum()]
    freq = pd.Series(tokens).value_counts().nlargest(25).reset_index()
    freq.columns = ["skill", "count"]
    return freq

skills = extract_skills(df["requirements"])

if skills.empty:
    st.info("No skill data available.")
else:
    fig = px.bar(skills, x="count", y="skill", orientation="h",
                 color="count", color_continuous_scale="Greens",
                 title="Most Mentioned Skills")
    st.plotly_chart(fig, use_container_width=True)
