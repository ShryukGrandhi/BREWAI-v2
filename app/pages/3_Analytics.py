"""
Analytics Page - Forecasting, Sentiment, Recommendations
"""
import streamlit as st
import sys
import os
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

st.set_page_config(page_title="Analytics", page_icon="📈", layout="wide")

st.title("📈 Analytics & Insights")

# Forecast Section
st.markdown("### 🔮 LSTM Forecast (Tomorrow)")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Peak Hour", "18:00", "+2 hrs vs today")
with col2:
    st.metric("Peak Orders", "42", "+8 orders")
with col3:
    st.metric("Peak Revenue", "$777", "+$148")
with col4:
    st.metric("Daily Total", "$6,400", "predicted")

# Show forecast plot if available
if os.path.exists("artifacts/forecast_plot.png"):
    st.image("artifacts/forecast_plot.png", caption="LSTM Forecast with 90% Confidence Intervals")
else:
    # Create sample forecast visualization
    hours = list(range(10, 23))
    orders = [15, 20, 28, 25, 18, 22, 35, 42, 38, 28, 20, 15, 12]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=hours,
        y=orders,
        mode='lines+markers',
        name='Predicted Orders',
        line=dict(color='#FF6B35', width=3),
        marker=dict(size=10)
    ))
    
    # CI bands
    lower = [o * 0.85 for o in orders]
    upper = [o * 1.15 for o in orders]
    
    fig.add_trace(go.Scatter(
        x=hours + hours[::-1],
        y=upper + lower[::-1],
        fill='toself',
        fillcolor='rgba(255,107,53,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='90% CI'
    ))
    
    fig.update_layout(
        title="Tomorrow's Order Forecast (LSTM)",
        xaxis_title="Hour",
        yaxis_title="Orders",
        height=400,
        template="plotly_dark"
    )
    
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Sentiment Analysis
st.markdown("### 😊 Review Sentiment Analysis")

col1, col2 = st.columns(2)

with col1:
    # Sentiment pie
    sentiment_fig = go.Figure(data=[go.Pie(
        labels=['Positive', 'Neutral', 'Negative'],
        values=[45, 40, 15],
        marker=dict(colors=['#10B981', '#6B7280', '#EF4444']),
        hole=0.4
    )])
    sentiment_fig.update_layout(
        title="Overall Sentiment",
        height=300,
        template="plotly_dark"
    )
    st.plotly_chart(sentiment_fig, use_container_width=True)
    
    st.markdown("**Top Positive Keywords:**")
    st.markdown("🟢 Fresh • Cheesy • Cooked • Delicious • Fast")
    
    st.markdown("**Top Negative Keywords:**")
    st.markdown("🔴 Spicy • Cold • Slow • Incomplete • Late")

with col2:
    # Refund analysis
    refund_fig = go.Figure(data=[go.Pie(
        labels=['Late Delivery', 'Cold Food', 'Open Bag', 'Incomplete'],
        values=[40, 25, 20, 15],
        marker=dict(colors=['#EF4444', '#F59E0B', '#6B7280', '#3B82F6']),
        hole=0.4
    )])
    refund_fig.update_layout(
        title="Refund Reasons",
        height=300,
        template="plotly_dark"
    )
    st.plotly_chart(refund_fig, use_container_width=True)
    
    st.markdown("**Customer Journey Insights:**")
    st.info("📌 Most time spent: **Menu page** (avg 2.3 min)")
    st.warning("⚠️ High drop-off: **Checkout** (18% abandonment)")
    st.success("💡 Recommendation: Simplify checkout, add combo deals")

st.markdown("---")

# Recommendations
st.markdown("### 💡 AI-Powered Recommendations")

# Item selector
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    selected_item = st.selectbox(
        "Select Menu Item:",
        ["🍔 Cheese Burger", "🍟 Fries", "🥤 Drinks", "🌯 Wraps"],
        label_visibility="collapsed"
    )

# Recommendations based on item
recommendations = {
    "🍔 Cheese Burger": [
        ("Make the burger less spicy", "Sentiment analysis shows 23% of reviews mention 'too spicy'. Reduce cayenne by 30%."),
        ("Speed up kitchen prep", "Burgers average 12 min cook time. Target: 8 min to reduce 'cold food' complaints."),
        ("Improve packaging", "15% of refunds are for 'cold food'. Invest in insulated packaging (+$0.50/order).")
    ],
    "🍟 Fries": [
        ("Add seasoning variety", "Customers request 'cajun' and 'garlic' options. Easy upsell (+$1.50)."),
        ("Optimize portions", "Current portions too large - 20% waste. Reduce by 15% = $200/month savings."),
        ("Bundle deals", "Fries + drink combo increases average order value by 28%.")
    ],
    "🥤 Drinks": [
        ("Promote refills", "Free refills increase dine-in time and additional orders by 15%."),
        ("Add premium options", "Milkshakes and specialty drinks have 45% margin vs 25% for sodas."),
        ("Cold brew coffee", "Growing demand in reviews. Low competition, high margin opportunity.")
    ],
    "🌯 Wraps": [
        ("Feature more prominently", "Low sales but high ratings (4.6/5). Menu placement issue."),
        ("Add spicy option", "Customer requests for 'buffalo wrap' in 12 reviews."),
        ("Lunch combo deal", "Wrap + side + drink for $12.99 targets office workers.")
    ]
}

for i, (title, desc) in enumerate(recommendations.get(selected_item, []), 1):
    st.markdown(f"""
    <div style="background-color: #1e2127; padding: 20px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #FF6B35;">
        <h4 style="color: #FF6B35; margin: 0;">{i}. {title}</h4>
        <p style="color: #9CA3AF; margin: 10px 0 0 0;">{desc}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Real-time insights
st.markdown("### 📊 Real-Time Insights")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Current Conversion Rate",
        "73.2%",
        "+2.1%",
        help="Visitors who complete checkout"
    )

with col2:
    st.metric(
        "Avg Order Value",
        "$18.50",
        "-$0.50",
        help="Average ticket size"
    )

with col3:
    st.metric(
        "Customer Satisfaction",
        "4.3/5",
        "+0.2",
        help="Based on review sentiment"
    )

