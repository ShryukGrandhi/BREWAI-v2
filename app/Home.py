"""
Brew.AI - Main Dashboard (Home Page)
"""
import streamlit as st
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
load_dotenv()

# Page config
st.set_page_config(
    page_title="Brew.AI - Dashboard",
    page_icon="🍺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stMetric { 
        background-color: #1e2127;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #2e3137;
    }
    .big-metric {
        background-color: #1e2127;
        padding: 25px;
        border-radius: 12px;
        border: 2px solid #FF6B35;
        text-align: center;
    }
    .simulation-btn {
        background-color: #FF6B35 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'simulation_mode' not in st.session_state:
    st.session_state.simulation_mode = None
if 'simulation_date' not in st.session_state:
    st.session_state.simulation_date = datetime.now()
if 'current_orders' not in st.session_state:
    st.session_state.current_orders = 30
if 'current_revenue' not in st.session_state:
    st.session_state.current_revenue = 1000.0

# Header
st.title("🍺 Brew.AI - Restaurant Operations Platform")
st.caption(f"📍 Burger Queen • {st.session_state.simulation_date.strftime('%A, %B %d, %Y • %I:%M %p')}")

# Simulation Controls at Top
st.markdown("### ⚡ Quick Actions & Simulation")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    if st.button("📅 Plan Tomorrow", use_container_width=True):
        st.switch_page("pages/1_Planning.py")

with col2:
    if st.button("📆 Plan Week", use_container_width=True):
        st.switch_page("pages/1_Planning.py")

with col3:
    if st.button("⏩ Simulate 1 Day", use_container_width=True):
        st.session_state.simulation_date += timedelta(days=1)
        st.session_state.simulation_mode = "1_day"
        st.rerun()

with col4:
    if st.button("⏩ Simulate 1 Week", use_container_width=True):
        st.session_state.simulation_date += timedelta(weeks=1)
        st.session_state.simulation_mode = "1_week"
        st.rerun()

with col5:
    if st.button("⏩ Simulate 1 Month", use_container_width=True):
        st.session_state.simulation_date += timedelta(days=30)
        st.session_state.simulation_mode = "1_month"
        st.rerun()

with col6:
    if st.button("⏩ Simulate 1 Year", use_container_width=True):
        st.session_state.simulation_date += timedelta(days=365)
        st.session_state.simulation_mode = "1_year"
        st.rerun()

# Show simulation banner if active
if st.session_state.simulation_mode:
    st.success(f"✅ Simulated {st.session_state.simulation_mode.replace('_', ' ')} forward! Now at: {st.session_state.simulation_date.strftime('%B %d, %Y')}")
    if st.button("🔄 Reset to Today"):
        st.session_state.simulation_date = datetime.now()
        st.session_state.simulation_mode = None
        st.rerun()

st.markdown("---")

# Real-Time Dashboard
st.markdown("### 📊 Today's Performance")

col1, col2, col3, col4 = st.columns(4)

# Simulate real-time updates based on time
current_hour = st.session_state.simulation_date.hour
orders_filled = st.session_state.current_orders + (current_hour - 9) * 5
revenue_current = orders_filled * 33.33

with col1:
    st.markdown(f"""
    <div class="big-metric">
        <h3 style="color: #FF6B35; margin: 0;">Orders Filled</h3>
        <h1 style="color: white; margin: 10px 0;">{int(orders_filled)}</h1>
        <p style="color: #10B981; margin: 0;">↑ 12 vs yesterday</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="big-metric">
        <h3 style="color: #FF6B35; margin: 0;">Revenue</h3>
        <h1 style="color: white; margin: 10px 0;">${revenue_current:,.0f}</h1>
        <p style="color: #10B981; margin: 0;">↑ $200 today</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="big-metric">
        <h3 style="color: #FF6B35; margin: 0;">EOD Forecast</h3>
        <h1 style="color: white; margin: 10px 0;">193</h1>
        <p style="color: #4A90E2; margin: 0;">orders predicted</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="big-metric">
        <h3 style="color: #FF6B35; margin: 0;">EOD Revenue</h3>
        <h1 style="color: white; margin: 10px 0;">$6,400</h1>
        <p style="color: #4A90E2; margin: 0;">predicted</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Quick Navigation
st.markdown("### 🧭 Navigate to:")

nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

with nav_col1:
    if st.button("🤖 AI Chatbot", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Chatbot.py")

with nav_col2:
    if st.button("📈 Forecasting & Analytics", use_container_width=True):
        st.switch_page("pages/3_Analytics.py")

with nav_col3:
    if st.button("👥 Staffing & Operations", use_container_width=True):
        st.switch_page("pages/4_Staffing.py")

with nav_col4:
    if st.button("🗺️ Expansion Insights", use_container_width=True):
        st.switch_page("pages/5_Expansion.py")

# Recent Activity
st.markdown("### 📋 Recent Activity")

recent_activities = [
    {"time": "9:05 AM", "event": "Morning prep completed", "status": "✅"},
    {"time": "9:14 AM", "event": "First lunch order received", "status": "🔔"},
    {"time": "9:20 AM", "event": "Weather forecast updated - Rain expected", "status": "☔"},
    {"time": "9:25 AM", "event": "LSTM model predicted peak at 6 PM", "status": "📈"},
]

for activity in recent_activities:
    st.markdown(f"""
    <div style="background-color: #1e2127; padding: 12px; margin: 5px 0; border-radius: 6px; border-left: 3px solid #FF6B35;">
        <b>{activity['status']} {activity['time']}</b> - {activity['event']}
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("Powered by Brew.AI | Captain RAG + LSTM + BrowserUse | Multi-Agent Orchestration")

