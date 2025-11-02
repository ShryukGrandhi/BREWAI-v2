"""
Staffing & Operations Page
"""
import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

st.set_page_config(page_title="Staffing", page_icon="👥", layout="wide")

st.title("👥 Staffing & Operations")

# Weekly overview
st.markdown("### 📅 Weekly Staffing Plan")

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
cols = st.columns(7)

for i, (day, col) in enumerate(zip(days, cols)):
    with col:
        # Generate predictions
        base_orders = 180
        if i >= 4:  # Weekend
            base_orders = int(base_orders * 1.3)
        
        expected_orders = base_orders + np.random.randint(-20, 20)
        expected_revenue = expected_orders * 18.50
        
        # Determine staffing
        cooks = 2 if expected_orders < 200 else 3
        cashiers = 2
        
        st.markdown(f"#### {day[:3]}")
        st.markdown(f"**Orders:** {expected_orders}")
        st.markdown(f"**Rev:** ${expected_revenue:,.0f}")
        st.markdown("**STAFF:**")
        st.checkbox(f"{cashiers}x Cash", value=True, key=f"cash_{i}")
        st.checkbox(f"{cooks}x Cook", value=True, key=f"cook_{i}")
        
        # Mini peak chart
        peak_hours = [10, 15, 25, 35, 40, 35, 25, 15, 10]
        peak_fig = go.Figure(data=[go.Scatter(
            x=list(range(8, 17)),
            y=peak_hours,
            mode='lines',
            line=dict(color='#4A90E2', width=2),
            fill='tozeroy'
        )])
        peak_fig.update_layout(
            height=120,
            margin=dict(t=5, b=5, l=5, r=5),
            showlegend=False,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(peak_fig, use_container_width=True)

st.markdown("---")

# Today's schedule
st.markdown("### 📋 Today's Schedule")

schedule_data = [
    {"Staff": "Alice", "Role": "Cook", "Shift": "10:00 - 18:00", "Status": "✅ On duty"},
    {"Staff": "Bob", "Role": "Cook", "Shift": "12:00 - 20:00", "Status": "✅ On duty"},
    {"Staff": "Carol", "Role": "Cashier", "Shift": "10:00 - 18:00", "Status": "✅ On duty"},
    {"Staff": "Dave", "Role": "Cashier", "Shift": "16:00 - 22:00", "Status": "⏰ Upcoming"},
]

df_schedule = pd.DataFrame(schedule_data)
st.dataframe(df_schedule, use_container_width=True, hide_index=True)

st.markdown("---")

# Capacity metrics
st.markdown("### 📊 Capacity Utilization")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Current Capacity", "75%", "+10%")
    st.progress(0.75)

with col2:
    st.metric("Peak Capacity (6 PM)", "95%", "+20%")
    st.progress(0.95)

with col3:
    st.metric("Labor Cost %", "28%", "-2%")
    st.progress(0.28)

# Gusto integration note
st.info("🔗 **Automated Scheduling:** Connected to Gusto for automatic shift assignments and payroll")

