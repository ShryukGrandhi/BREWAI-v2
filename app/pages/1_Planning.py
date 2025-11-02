"""
Planning Page - Run all agents for tomorrow or week
"""
import streamlit as st
import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.scraper_agent import run_scraper_agent
from agents.weather_agent import run_weather_agent
from agents.forecast_agent_lstm import run_forecast_agent_lstm
from agents.staffing_agent import run_staffing_agent
from agents.prep_agent import run_prep_agent
from agents.geo_agent import run_geo_agent
from agents.trace_agent import get_trace_agent

st.set_page_config(page_title="Planning", page_icon="📅", layout="wide")

st.title("📅 AI-Powered Planning")
st.caption("Automated operations planning with 8 intelligent agents")

# Planning controls
col1, col2 = st.columns(2)

with col1:
    planning_mode = st.selectbox(
        "Planning Horizon:",
        ["Tomorrow", "Next Week", "Next Month"]
    )

with col2:
    auto_execute = st.checkbox("Auto-execute all agents", value=True)

st.markdown("---")

# Agent execution controls
st.markdown("### 🤖 Agent Orchestra")

if 'agents_running' not in st.session_state:
    st.session_state.agents_running = False
if 'agent_results' not in st.session_state:
    st.session_state.agent_results = {}

# Progress indicator
steps = [
    ("🔍 Scraper", "scraper"),
    ("🌤️ Weather", "weather"),  
    ("📈 Forecast", "forecast"),
    ("👥 Staffing", "staffing"),
    ("📦 Prep", "prep"),
    ("🗺️ Expansion", "expansion")
]

cols = st.columns(len(steps))
for i, (col, (name, key)) in enumerate(zip(cols, steps)):
    with col:
        if key in st.session_state.agent_results:
            st.success(f"{name} ✅")
        else:
            st.info(name)

# Start button
if st.button(f"▶️ Plan {planning_mode}", type="primary", use_container_width=True):
    st.session_state.agents_running = True
    
    with st.status("🚀 Running agents...", expanded=True) as status:
        # Run agents sequentially
        try:
            # Scraper
            st.write("🔍 ScraperAgent: Collecting reviews...")
            scraper_result = run_scraper_agent("Burger Queen", "123 Main St, NYC")
            st.session_state.agent_results['scraper'] = scraper_result
            st.write(f"✅ Scraped {len(scraper_result.get('gmaps_reviews', []))} reviews")
            
            # Weather
            st.write("🌤️ WeatherAgent: Fetching forecast...")
            weather_result = run_weather_agent("Burger Queen", "123 Main St, NYC")
            st.session_state.agent_results['weather'] = weather_result
            st.write(f"✅ Forecast loaded")
            
            # Forecast
            st.write("📈 ForecastAgent: Running LSTM prediction...")
            forecast_result = run_forecast_agent_lstm()
            st.session_state.agent_results['forecast'] = forecast_result
            st.write(f"✅ Peak: {forecast_result.get('peak_hour')}:00 with {forecast_result.get('peak_orders')} orders")
            
            # Staffing
            if forecast_result.get('success'):
                st.write("👥 StaffingAgent: Calculating needs...")
                staffing_result = run_staffing_agent(
                    ["Alice", "Bob", "Carol", "Dave"],
                    "Burger Queen",
                    forecast_result['peak_hour'],
                    forecast_result['peak_orders']
                )
                st.session_state.agent_results['staffing'] = staffing_result
                st.write(f"✅ {staffing_result.get('required_cooks')} cooks needed")
            
            # Prep
            if forecast_result.get('success') and weather_result.get('success'):
                st.write("📦 PrepAgent: Creating purchase orders...")
                prep_result = run_prep_agent(
                    "Burger Queen",
                    forecast_result['peak_orders'],
                    weather_result.get('summary', {})
                )
                st.session_state.agent_results['prep'] = prep_result
                st.write(f"✅ PO for {prep_result.get('wings_lbs')} lbs")
            
            # Expansion
            st.write("🗺️ GeoAgent: Analyzing expansion...")
            geo_result = run_geo_agent("San Francisco, CA")
            st.session_state.agent_results['expansion'] = geo_result
            st.write(f"✅ Analyzed {len(geo_result.get('locations', []))} locations")
            
            status.update(label="✅ All agents complete!", state="complete")
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            status.update(label="❌ Agent execution failed", state="error")

# Show results
if st.session_state.agent_results:
    st.markdown("---")
    st.markdown("### 📊 Results Summary")
    
    tabs = st.tabs(["Forecast", "Staffing", "Prep", "Expansion"])
    
    with tabs[0]:
        if 'forecast' in st.session_state.agent_results:
            result = st.session_state.agent_results['forecast']
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Peak Hour", f"{result.get('peak_hour')}:00")
            with col2:
                st.metric("Peak Orders", f"{result.get('peak_orders'):.0f}")
            with col3:
                st.metric("Daily Revenue", f"${result.get('total_daily_revenue', 0):,.2f}")
            
            if os.path.exists("artifacts/forecast_plot.png"):
                st.image("artifacts/forecast_plot.png")
    
    with tabs[1]:
        if 'staffing' in st.session_state.agent_results:
            result = st.session_state.agent_results['staffing']
            st.metric("Cooks Needed", result.get('required_cooks', 0))
            
            for shift in result.get('shifts', []):
                st.markdown(f"**{shift['staff']}** - {shift['role']} ({shift['start_time']} - {shift['end_time']})")
    
    with tabs[2]:
        if 'prep' in st.session_state.agent_results:
            result = st.session_state.agent_results['prep']
            po = result.get('po_data', {})
            st.markdown(f"**Item:** {po.get('item')}")
            st.markdown(f"**Quantity:** {po.get('quantity')} {po.get('unit')}")
            st.markdown(f"**Delivery:** {po.get('delivery_date')}")
    
    with tabs[3]:
        if 'expansion' in st.session_state.agent_results:
            result = st.session_state.agent_results['expansion']
            for loc in result.get('locations', [])[:5]:
                st.markdown(f"**{loc['name']}** - ROI: {loc['roi_score']:.2f}")

