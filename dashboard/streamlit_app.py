import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

import streamlit as st
import pandas as pd
from sqlalchemy import text
import plotly.express as px
from etl.db import engine
from datetime import datetime

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(
    page_title="Job Market Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- CUSTOM STYLES ----------------------
st.markdown("""
<style>
    /* Main background */
    .main {
        background: linear-gradient(135deg, #f9fafb 0%, #eef2ff 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
    }

    /* Navbar */
    .navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(90deg, #2563eb, #3b82f6);
        color: white;
        padding: 1rem 2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .navbar h1 {
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0;
    }
    .navbar button {
        background-color: #ffffff22;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.9rem;
        cursor: pointer;
        transition: background 0.3s ease;
    }
    .navbar button:hover {
        background-color: #ffffff44;
    }

    /* Metric cards */
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 700;
    }

    /* Section headers */
    h2, h3 {
        color: #1e3a8a;
        font-weight: 700;
        margin-top: 1rem;
    }

    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        background-color: #fff;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------- NAVBAR ----------------------
navbar_html = f"""
<div class="navbar">
    <h1>📊 Job Market Analytics</h1>
    <div>
        <span style="font-size:0.9rem; margin-right:1rem; opacity:0.8;">
            Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        </span>
        <form action="" method="get">
            <button onclick="window.location.reload()">🔄 Refresh</button>
        </form>
    </div>
</div>
"""
st.markdown(navbar_html, unsafe_allow_html=True)

# ---------------------- LOAD DATA ----------------------
@st.cache_data(ttl=3600)
def load_data(limit=10000):
    query = text("SELECT * FROM job_postings ORDER BY scraped_at DESC LIMIT :limit")
    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn, params={"limit": limit})
    return df

df = load_data()

if df.empty:
    st.warning("⚠️ No data found. Please run the ETL pipeline first.")
    st.stop()

# ---------------------- SIDEBAR ----------------------
st.sidebar.header("🔍 Filters")
title_filter = st.sidebar.text_input("Job Title Contains", value="")
company_filter = st.sidebar.text_input("Company Contains", value="")
remote_filter = st.sidebar.selectbox("Work Type", ["Any", "Remote only", "On-site only"])
top_n = st.sidebar.slider("Top N Roles", min_value=3, max_value=50, value=10)

q = df.copy()
if title_filter:
    q = q[q["job_title"].str.contains(title_filter, case=False, na=False)]
if company_filter:
    q = q[q["company"].str.contains(company_filter, case=False, na=False)]
if remote_filter != "Any":
    q = q[q["remote"] == (remote_filter == "Remote only")]

# ---------------------- METRICS ----------------------
st.markdown("## 📊 Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Total Postings", f"{len(q):,}")
col2.metric("Unique Companies", f"{q['company'].nunique():,}")
col3.metric("Remote %", f"{q['remote'].mean() * 100:.1f}%" if not q.empty else "0%")

st.divider()

# ---------------------- TOP ROLES ----------------------
st.markdown("### 💼 Top Roles")
top_roles = q["job_title"].fillna("Unknown").value_counts().nlargest(top_n).reset_index()
top_roles.columns = ["job_title", "count"]
fig_roles = px.bar(
    top_roles,
    x="count", y="job_title",
    orientation="h",
    color="count",
    color_continuous_scale="Blues",
    title="Most In-Demand Job Titles",
    labels={"count": "Postings", "job_title": "Role"}
)
fig_roles.update_layout(margin=dict(l=0, r=0, t=40, b=0))
st.plotly_chart(fig_roles, use_container_width=True)

# ---------------------- TOP SKILLS ----------------------
st.markdown("### 🧠 Top Skills (Naive Keyword Extraction)")
def extract_skills(series):
    text = " ".join(series.dropna().astype(str).tolist())
    tokens = [t.strip().lower() for t in text.replace(",", " ").split()]
    tokens = [t for t in tokens if len(t) > 1 and t.isalnum()]
    freq = pd.Series(tokens).value_counts().nlargest(25).reset_index()
    freq.columns = ["skill", "count"]
    return freq

skills = extract_skills(q["requirements"])
if not skills.empty:
    fig_skills = px.bar(
        skills,
        x="count", y="skill",
        orientation="h",
        color="count",
        color_continuous_scale="Greens",
        title="Most Mentioned Skills"
    )
    fig_skills.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_skills, use_container_width=True)
else:
    st.info("No skills data available.")

# ---------------------- SALARY DISTRIBUTION ----------------------
st.markdown("### 💰 Salary Distribution (Minimum Salary)")
sal = q[~q["salary_min"].isna()]
if not sal.empty:
    fig_salary = px.histogram(
        sal, x="salary_min",
        nbins=30,
        title="Distribution of Minimum Salaries",
        labels={"salary_min": "Minimum Salary ($)"}
    )
    fig_salary.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_salary, use_container_width=True)
else:
    st.info("No salary data available.")

# ---------------------- DATA TABLE ----------------------
st.markdown("### 🧾 Recent Postings")
st.dataframe(
    q[["scraped_at", "job_title", "company", "location", "salary_raw", "remote", "url"]]
    .sort_values("scraped_at", ascending=False)
    .head(100),
    use_container_width=True
)
