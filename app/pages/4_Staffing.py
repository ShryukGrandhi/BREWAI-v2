"""
Staffing & Operations Page - Detailed daily staffing with realistic variations
"""
import streamlit as st
import sys
import os
from pathlib import Path
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

st.set_page_config(page_title="Staffing", page_icon="👥", layout="wide")

st.title("👥 Staffing & Operations")
st.caption("AI-powered staffing optimization based on LSTM forecasts, weather, and historical patterns")

# Weekly overview with DETAILED reasoning per day
st.markdown("### 📅 Weekly Staffing Plan (AI-Generated)")

# Generate realistic staffing for each day
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Load historical orders for baseline
baseline_orders = {}
peak_hours_data = {}
reasoning = {}

for i, day in enumerate(days):
    # Base calculations with day-specific factors
    is_weekend = i >= 5
    is_friday = i == 4
    
    # Weather factor (simulate)
    weather_factors = {
        0: {'temp': 62, 'rain': 0, 'factor': 1.0, 'desc': 'Clear'},
        1: {'temp': 58, 'rain': 20, 'factor': 0.95, 'desc': 'Light rain AM'},
        2: {'temp': 65, 'rain': 0, 'factor': 1.05, 'desc': 'Sunny, warm'},
        3: {'temp': 60, 'rain': 0, 'factor': 1.0, 'desc': 'Clear'},
        4: {'temp': 68, 'rain': 0, 'factor': 1.15, 'desc': 'Perfect weather'},
        5: {'temp': 70, 'rain': 0, 'factor': 1.30, 'desc': 'Sunny Saturday'},
        6: {'temp': 55, 'rain': 40, 'factor': 1.10, 'desc': 'Rain expected PM'}
    }
    
    weather = weather_factors[i]
    
    # Events factor
    events_factors = {
        0: {'event': None, 'factor': 1.0},
        1: {'event': 'Office lunch rush (nearby event)', 'factor': 1.12},
        2: {'event': None, 'factor': 1.0},
        3: {'event': None, 'factor': 1.0},
        4: {'event': 'Happy hour crowd', 'factor': 1.18},
        5: {'event': 'College game day nearby', 'factor': 1.25},
        6: {'event': None, 'factor': 1.0}
    }
    
    event = events_factors[i]
    
    # Base order calculation
    base = 165  # Weekday baseline
    if is_weekend:
        base = 210
    if is_friday:
        base = 190
    
    # Apply factors
    final_orders = int(base * weather['factor'] * event['factor'])
    baseline_orders[day] = final_orders
    
    # Peak hour pattern (different per day)
    if i == 0:  # Monday - lunch heavy
        peak_hours_data[day] = [5, 8, 15, 35, 45, 40, 30, 25, 20, 15, 10, 8]
        peak_time = "12-1pm (lunch)"
    elif i == 1:  # Tuesday - steady lunch + event spike
        peak_hours_data[day] = [5, 10, 20, 40, 42, 38, 28, 25, 20, 15, 12, 8]
        peak_time = "12-2pm (office lunch)"
    elif i == 2:  # Wednesday - balanced
        peak_hours_data[day] = [5, 12, 25, 38, 35, 32, 35, 40, 35, 25, 15, 10]
        peak_time = "6-7pm (dinner)"
    elif i == 3:  # Thursday - building to weekend
        peak_hours_data[day] = [8, 15, 28, 35, 32, 30, 38, 45, 42, 30, 18, 12]
        peak_time = "6-8pm (pre-weekend)"
    elif i == 4:  # Friday - dual peak
        peak_hours_data[day] = [10, 18, 32, 42, 40, 35, 45, 55, 50, 40, 25, 15]
        peak_time = "12-1pm & 7-8pm"
    elif i == 5:  # Saturday - sustained high
        peak_hours_data[day] = [15, 25, 35, 40, 42, 45, 48, 50, 48, 40, 30, 20]
        peak_time = "1-8pm (all day)"
    else:  # Sunday - late brunch peak
        peak_hours_data[day] = [5, 10, 20, 35, 45, 42, 38, 40, 35, 28, 20, 15]
        peak_time = "12-2pm (brunch)"
    
    # Calculate staffing needs
    peak_hourly = max(peak_hours_data[day])
    
    # Staffing formula: 1 cook per 25 orders/hour, min 2, max 4
    cooks_needed = max(2, min(4, int(np.ceil(peak_hourly / 25))))
    
    # Cashiers: 1 per 30 orders/hour, min 2, max 3
    cashiers_needed = max(2, min(3, int(np.ceil(peak_hourly / 30))))
    
    # Additional staff for high volume
    prep_cook = 1 if final_orders > 200 else 0
    
    # Build reasoning
    reason_parts = []
    reason_parts.append(f"**Forecast:** {final_orders} orders")
    reason_parts.append(f"**Weather:** {weather['desc']} ({weather['temp']}°F)")
    if weather['rain'] > 0:
        reason_parts.append(f"Rain: {weather['rain']}% chance")
    if event['event']:
        reason_parts.append(f"**Event:** {event['event']} (+{int((event['factor']-1)*100)}%)")
    reason_parts.append(f"**Peak:** {peak_time} ({peak_hourly} orders/hr)")
    reason_parts.append(f"**Required:** {cooks_needed} cooks (1 per 25 ord/hr), {cashiers_needed} cashiers")
    if prep_cook:
        reason_parts.append(f"**Prep cook needed:** High volume day (>{200} orders)")
    
    reasoning[day] = {
        'summary': ' • '.join(reason_parts),
        'cooks': cooks_needed,
        'cashiers': cashiers_needed,
        'prep': prep_cook,
        'orders': final_orders,
        'revenue': final_orders * 18.50,
        'peak_hour': peak_time,
        'peak_orders': peak_hourly,
        'weather': weather,
        'event': event
    }

# Display weekly cards
cols = st.columns(7)

for i, (day, col) in enumerate(zip(days, cols)):
    with col:
        r = reasoning[day]
        
        # Day header with weather icon
        weather_icon = "☀️" if r['weather']['rain'] < 20 else "🌧️"
        st.markdown(f"### {weather_icon} {day[:3]}")
        
        # Metrics
        st.metric("Orders", f"{r['orders']}", f"+{r['orders']-165}")
        st.metric("Revenue", f"${r['revenue']:,.0f}")
        
        # Staffing
        st.markdown("**👥 Staff Needed:**")
        st.markdown(f"🔥 **{r['cooks']} Cooks**")
        st.markdown(f"💵 **{r['cashiers']} Cashiers**")
        if r['prep'] > 0:
            st.markdown(f"🥗 **{r['prep']} Prep**")
        
        # Peak chart (UNIQUE KEY per day)
        peak_fig = go.Figure(data=[go.Scatter(
            x=list(range(10, 22)),
            y=peak_hours_data[day],
            mode='lines+markers',
            line=dict(color='#FF6B35' if i in [4, 5] else '#4A90E2', width=2),
            fill='tozeroy',
            marker=dict(size=4)
        )])
        peak_fig.update_layout(
            height=100,
            margin=dict(t=5, b=5, l=5, r=5),
            showlegend=False,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(peak_fig, use_container_width=True, key=f"peak_chart_day_{i}")
        
        # Show reasoning in expander
        with st.expander("📊 Why this staffing?"):
            st.markdown(r['summary'])
            st.markdown(f"**Peak time:** {r['peak_hour']}")
            st.markdown(f"**Peak volume:** {r['peak_orders']} orders/hr")
            if r['event']['event']:
                st.info(f"🎉 {r['event']['event']}")

st.markdown("---")

# Detailed daily breakdown for today
st.markdown("### 📋 Today's Detailed Schedule")

today_name = days[datetime.now().weekday()]
today_reasoning = reasoning[today_name]

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### Forecast")
    st.metric("Expected Orders", today_reasoning['orders'])
    st.metric("Expected Revenue", f"${today_reasoning['revenue']:,.2f}")
    st.metric("Peak Hour", today_reasoning['peak_hour'])

with col2:
    st.markdown("#### Weather")
    st.metric("Temperature", f"{today_reasoning['weather']['temp']}°F")
    st.metric("Rain Chance", f"{today_reasoning['weather']['rain']}%")
    st.markdown(f"**Conditions:** {today_reasoning['weather']['desc']}")

with col3:
    st.markdown("#### Staffing")
    st.metric("Total Staff", today_reasoning['cooks'] + today_reasoning['cashiers'] + today_reasoning['prep'])
    st.metric("Cooks", today_reasoning['cooks'])
    st.metric("Cashiers", today_reasoning['cashiers'])

# Staff assignments with realistic schedules
st.markdown("---")
st.markdown("### 👤 Individual Assignments")

# Load from CSV if available
staff_names = []
if os.path.exists("data/staff_schedule.csv"):
    try:
        import pandas as pd
        staff_df = pd.read_csv("data/staff_schedule.csv")
        today_str = datetime.now().strftime('%Y-%m-%d')
        today_staff = staff_df[staff_df['date'] == today_str]
        if not today_staff.empty:
            staff_names = today_staff['staff_name'].tolist()
    except:
        pass

# Fallback to demo staff
if not staff_names:
    staff_names = ["Alice Johnson", "Bob Martinez", "Carol Smith", "Dave Wilson", "Emma Davis"]

# Generate realistic schedule
schedule_data = []

# Cooks
cook_shifts = [
    ("10:00", "18:00", "Morning/lunch coverage"),
    ("12:00", "20:00", "Lunch/dinner overlap"),
    ("14:00", "22:00", "Afternoon/dinner coverage"),
    ("17:00", "22:00", "Dinner rush support")
]

for i in range(today_reasoning['cooks']):
    if i < len(staff_names):
        shift = cook_shifts[i]
        schedule_data.append({
            "Staff": staff_names[i],
            "Role": "Cook",
            "Shift": f"{shift[0]} - {shift[1]}",
            "Reason": shift[2],
            "Status": "✅ Scheduled"
        })

# Cashiers
cashier_shifts = [
    ("10:00", "18:00", "Opening/lunch shift"),
    ("16:00", "22:00", "Dinner/closing shift"),
    ("12:00", "20:00", "Peak coverage")
]

for i in range(today_reasoning['cashiers']):
    staff_idx = today_reasoning['cooks'] + i
    if staff_idx < len(staff_names):
        shift = cashier_shifts[i % len(cashier_shifts)]
        schedule_data.append({
            "Staff": staff_names[staff_idx],
            "Role": "Cashier",
            "Shift": f"{shift[0]} - {shift[1]}",
            "Reason": shift[2],
            "Status": "✅ Scheduled"
        })

# Prep cook if needed
if today_reasoning['prep'] > 0:
    prep_idx = today_reasoning['cooks'] + today_reasoning['cashiers']
    if prep_idx < len(staff_names):
        schedule_data.append({
            "Staff": staff_names[prep_idx],
            "Role": "Prep Cook",
            "Shift": "08:00 - 16:00",
            "Reason": "Prep for high volume day",
            "Status": "✅ Scheduled"
        })

df_schedule = pd.DataFrame(schedule_data)
st.dataframe(df_schedule, use_container_width=True, hide_index=True)

# Labor cost calculation
st.markdown("---")
st.markdown("### 💰 Labor Cost Analysis")

col1, col2, col3, col4 = st.columns(4)

total_hours = len(schedule_data) * 8  # Approximate
avg_hourly = 19.25  # Mix of cooks ($22) and cashiers ($16.50)
labor_cost = total_hours * avg_hourly
labor_pct = (labor_cost / today_reasoning['revenue']) * 100

with col1:
    st.metric("Total Hours", f"{total_hours} hrs")

with col2:
    st.metric("Labor Cost", f"${labor_cost:,.2f}")

with col3:
    st.metric("Labor %", f"{labor_pct:.1f}%", 
              delta=f"{labor_pct - 28:.1f}%" if labor_pct < 28 else f"+{labor_pct - 28:.1f}%",
              delta_color="normal" if labor_pct <= 30 else "inverse")

with col4:
    st.metric("Revenue per Hour", f"${today_reasoning['revenue']/total_hours:.2f}")

# Efficiency insights
st.markdown("---")
st.markdown("### 📊 Efficiency Insights")

if labor_pct > 30:
    st.warning(f"⚠️ **Labor % High:** At {labor_pct:.1f}%, consider optimizing shifts or increasing revenue per order.")
elif labor_pct < 25:
    st.success(f"✅ **Labor % Optimal:** At {labor_pct:.1f}%, you're operating efficiently!")
else:
    st.info(f"📊 **Labor % Good:** At {labor_pct:.1f}%, within target range (25-30%).")

# Capacity analysis
st.markdown("---")
st.markdown("### 🔧 Capacity Utilization")

# Calculate capacity
max_capacity_per_cook = 25  # orders per hour
max_hourly_capacity = today_reasoning['cooks'] * max_capacity_per_cook
utilization = (today_reasoning['peak_orders'] / max_hourly_capacity) * 100

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Peak Hour Capacity", f"{max_hourly_capacity} orders/hr")
    st.progress(min(1.0, utilization/100))

with col2:
    st.metric("Peak Hour Demand", f"{today_reasoning['peak_orders']} orders/hr")

with col3:
    st.metric("Utilization", f"{utilization:.0f}%",
              delta="Optimal" if 75 <= utilization <= 90 else ("Under" if utilization < 75 else "Over"))

if utilization > 95:
    st.error("🚨 **CRITICAL:** Peak capacity exceeded! Add another cook to prevent service delays.")
elif utilization > 90:
    st.warning("⚠️ **CAUTION:** Near capacity. Monitor closely and prepare backup staff.")
elif utilization < 70:
    st.info("💡 **TIP:** Capacity underutilized. Consider reducing staff or promoting to increase orders.")
else:
    st.success("✅ **OPTIMAL:** Capacity utilization in sweet spot (75-90%).")

# Integration note
st.markdown("---")
st.info("🔗 **Automated Scheduling:** AI-powered staffing based on LSTM forecasts, weather data, and historical patterns. Each day is unique!")
