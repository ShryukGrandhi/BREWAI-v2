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
        with st.spinner("Running 1-day simulation..."):
            from agents.forecast_agent_lstm import run_forecast_agent_lstm
            from agents.weather_agent import run_weather_agent
            
            # Run forecast for tomorrow
            st.session_state.simulation_date += timedelta(days=1)
            weather_result = run_weather_agent("Burger Queen", "123 Main St, NYC")
            forecast_result = run_forecast_agent_lstm()
            
            st.session_state.simulation_results = {
                'weather': weather_result,
                'forecast': forecast_result,
                'period': '1 day'
            }
            st.session_state.simulation_mode = "1_day"
            st.rerun()

with col4:
    if st.button("⏩ Simulate 1 Week", use_container_width=True):
        with st.spinner("Running 7-day simulation..."):
            # Generate week forecast
            weekly_data = []
            for day in range(7):
                target_date = datetime.now() + timedelta(days=day+1)
                daily_orders = np.random.randint(150, 250)
                daily_revenue = daily_orders * 18.5
                weekly_data.append({
                    'date': target_date.strftime('%Y-%m-%d'),
                    'day': target_date.strftime('%A'),
                    'orders': daily_orders,
                    'revenue': daily_revenue
                })
            
            st.session_state.simulation_date += timedelta(weeks=1)
            st.session_state.simulation_results = {
                'weekly_forecast': weekly_data,
                'total_orders': sum(d['orders'] for d in weekly_data),
                'total_revenue': sum(d['revenue'] for d in weekly_data),
                'period': '1 week'
            }
            st.session_state.simulation_mode = "1_week"
            st.rerun()

with col5:
    if st.button("⏩ Simulate 1 Month", use_container_width=True):
        with st.spinner("Running 30-day simulation..."):
            # Generate month forecast
            monthly_data = []
            total_orders = 0
            total_revenue = 0.0
            
            for day in range(30):
                target_date = datetime.now() + timedelta(days=day+1)
                # Weekend boost
                is_weekend = target_date.weekday() >= 5
                base_orders = 200 if is_weekend else 165
                daily_orders = int(base_orders + np.random.normal(0, 20))
                daily_revenue = daily_orders * 18.5
                
                total_orders += daily_orders
                total_revenue += daily_revenue
                
                if day % 7 == 0:  # Weekly summary
                    monthly_data.append({
                        'week': f"Week {day//7 + 1}",
                        'orders': daily_orders * 7,
                        'revenue': daily_revenue * 7
                    })
            
            st.session_state.simulation_date += timedelta(days=30)
            st.session_state.simulation_results = {
                'monthly_summary': monthly_data,
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'avg_daily_orders': total_orders / 30,
                'avg_daily_revenue': total_revenue / 30,
                'period': '1 month'
            }
            st.session_state.simulation_mode = "1_month"
            st.rerun()

with col6:
    if st.button("⏩ Simulate 1 Year", use_container_width=True):
        with st.spinner("Running 365-day simulation..."):
            # Generate year forecast
            yearly_data = []
            total_orders = 0
            total_revenue = 0.0
            
            for month in range(12):
                month_orders = 0
                month_revenue = 0.0
                
                # Days in month
                days_in_month = 30
                
                for day in range(days_in_month):
                    target_date = datetime.now() + timedelta(days=month*30 + day)
                    is_weekend = target_date.weekday() >= 5
                    
                    # Seasonal variations
                    season_factor = 1.0
                    if month in [5, 6, 7]:  # Summer
                        season_factor = 1.2
                    elif month in [11, 0, 1]:  # Winter holidays
                        season_factor = 1.3
                    
                    base_orders = (200 if is_weekend else 165) * season_factor
                    daily_orders = int(base_orders + np.random.normal(0, 25))
                    daily_revenue = daily_orders * 18.5
                    
                    month_orders += daily_orders
                    month_revenue += daily_revenue
                
                total_orders += month_orders
                total_revenue += month_revenue
                
                yearly_data.append({
                    'month': (datetime.now() + timedelta(days=month*30)).strftime('%B %Y'),
                    'orders': month_orders,
                    'revenue': month_revenue
                })
            
            st.session_state.simulation_date += timedelta(days=365)
            st.session_state.simulation_results = {
                'yearly_summary': yearly_data,
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'avg_monthly_orders': total_orders / 12,
                'avg_monthly_revenue': total_revenue / 12,
                'growth_rate': 0.15,  # 15% year-over-year growth
                'period': '1 year'
            }
            st.session_state.simulation_mode = "1_year"
            st.rerun()

# Show simulation results if active
if st.session_state.simulation_mode and 'simulation_results' in st.session_state:
    results = st.session_state.simulation_results
    period = results.get('period')
    
    st.success(f"✅ Simulated {period} forward! Now at: {st.session_state.simulation_date.strftime('%B %d, %Y')}")
    
    # Show simulation summary
    if period == '1 day':
        if 'forecast' in results and results['forecast'].get('success'):
            f = results['forecast']
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tomorrow's Orders", f"{f.get('total_daily_orders', 0):.0f}")
            with col2:
                st.metric("Tomorrow's Revenue", f"${f.get('total_daily_revenue', 0):,.2f}")
            with col3:
                st.metric("Peak Hour", f"{f.get('peak_hour')}:00")
    
    elif period == '1 week':
        st.markdown("**Week Forecast:**")
        for day_data in results.get('weekly_forecast', []):
            st.markdown(f"**{day_data['day']}:** {day_data['orders']} orders, ${day_data['revenue']:,.2f}")
        st.metric("Week Total", f"{results.get('total_orders', 0)} orders | ${results.get('total_revenue', 0):,.2f}")
    
    elif period == '1 month':
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Orders (30 days)", f"{results.get('total_orders', 0):,}")
        with col2:
            st.metric("Total Revenue", f"${results.get('total_revenue', 0):,.2f}")
        with col3:
            st.metric("Avg Daily", f"{results.get('avg_daily_orders', 0):.0f} orders")
    
    elif period == '1 year':
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Orders (365 days)", f"{results.get('total_orders', 0):,}")
        with col2:
            st.metric("Total Revenue", f"${results.get('total_revenue', 0):,.2f}")
        with col3:
            st.metric("Avg Monthly", f"{results.get('avg_monthly_orders', 0):,.0f} orders")
        with col4:
            st.metric("Growth Rate", f"{results.get('growth_rate', 0)*100:.0f}%")
        
        # Show monthly breakdown
        with st.expander("📊 Monthly Breakdown"):
            for month_data in results.get('yearly_summary', []):
                st.markdown(f"**{month_data['month']}:** {month_data['orders']:,} orders, ${month_data['revenue']:,.2f}")
    
    if st.button("🔄 Reset to Today"):
        st.session_state.simulation_date = datetime.now()
        st.session_state.simulation_mode = None
        st.session_state.simulation_results = {}
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

