import sys
import os

# --- Ensure project root is on the Python path ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --- Now safe to import your modules ---
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
import os
from dotenv import load_dotenv

# 🔧 Load environment variables explicitly (important for Streamlit)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# Now import engine AFTER loading env vars
from etl.db import engine

st.set_page_config(page_title="Job Market Analytics", layout="wide")
st.title("Job Market Analytics Dashboard")


@st.cache_data
def load_data(limit=10000):
    query = text("SELECT * FROM job_postings ORDER BY scraped_at DESC LIMIT :limit")
    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn, params={"limit": limit})
    return df

df = load_data(limit=10000)

if df.empty:
    st.warning("No data found. Run the ETL pipeline first (see README).")
    st.stop()

# Top-level filters
cols = st.columns([2,2,1,1])
with cols[0]:
    title_filter = st.text_input("Job title contains", value="")
with cols[1]:
    company_filter = st.text_input("Company contains", value="")
with cols[2]:
    remote_filter = st.selectbox("Remote", options=["Any","Remote only","On-site only"])
with cols[3]:
    top_n = st.number_input("Show top N roles", min_value=3, max_value=100, value=10)

q = df.copy()
if title_filter:
    q = q[q["job_title"].str.contains(title_filter, case=False, na=False)]
if company_filter:
    q = q[q["company"].str.contains(company_filter, case=False, na=False)]
if remote_filter != "Any":
    if remote_filter == "Remote only":
        q = q[q["remote"]==True]
    else:
        q = q[q["remote"]==False]

st.markdown("## Overview")
c1, c2, c3 = st.columns(3)
c1.metric("Total postings", len(q))
c2.metric("Unique companies", q["company"].nunique())
c3.metric("Remote %", f"{q['remote'].mean()*100:.1f}%")

# Role demand bar chart
st.markdown("### Top roles")
top_roles = q["job_title"].fillna("Unknown").value_counts().nlargest(top_n).reset_index()
top_roles.columns = ["job_title","count"]
fig_roles = px.bar(top_roles, x="count", y="job_title", orientation="h", labels={"count":"Postings", "job_title":"Role"})
st.plotly_chart(fig_roles, use_container_width=True)

# Skills extraction from requirements column (very naive tokenization)
st.markdown("### Top skills (naive)")
def extract_skills(series):
    text = " ".join(series.dropna().astype(str).tolist())
    tokens = [t.strip().lower() for t in text.replace(",", " ").split()]
    # filter tokens that look like skills: length >1 and alnum
    tokens = [t for t in tokens if len(t)>1 and t.isalnum()]
    freq = pd.Series(tokens).value_counts().nlargest(30).reset_index()
    freq.columns = ["skill","count"]
    return freq
skills = extract_skills(q["requirements"])
if not skills.empty:
    fig_skills = px.bar(skills, x="count", y="skill", orientation="h")
    st.plotly_chart(fig_skills, use_container_width=True)
else:
    st.info("No skills data available.")

# Salary distribution
st.markdown("### Salary distribution (salary_min where available)")
sal = q[~q["salary_min"].isna()]
if not sal.empty:
    fig_salary = px.histogram(sal, x="salary_min", nbins=30, labels={"salary_min":"Salary (min)"})
    st.plotly_chart(fig_salary, use_container_width=True)
else:
    st.info("No parsed salary data available.")

# Data table
st.markdown("### Recent postings sample")
st.dataframe(q[["scraped_at","job_title","company","location","salary_raw","remote","url"]].sort_values("scraped_at", ascending=False).head(200))
