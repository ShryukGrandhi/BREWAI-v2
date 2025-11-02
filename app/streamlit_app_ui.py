"""
Brew.AI - UI Design from Sketch
Complete dashboard matching the hand-drawn UI concept.
"""
import streamlit as st
import os
import sys
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import json
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import plotly.graph_objects as go
import plotly.express as px

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.scraper_agent import run_scraper_agent
from agents.weather_agent import run_weather_agent
from agents.forecast_agent_lstm import run_forecast_agent_lstm
from agents.staffing_agent import run_staffing_agent
from agents.prep_agent import run_prep_agent
from agents.analyst_agent_captain import run_analyst_agent_captain
from agents.geo_agent import run_geo_agent
from agents.trace_agent import get_trace_agent

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Brew.AI - Restaurant Analytics",
    page_icon="🍺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2127;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #2e3137;
    }
    .metric-card {
        background-color: #1e2127;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #2e3137;
        margin: 10px 0;
    }
    .section-header {
        background: linear-gradient(90deg, #FF6B35 0%, #FF8555 100%);
        padding: 15px;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        font-size: 20px;
        margin: 10px 0;
        text-align: center;
    }
    .status-box {
        background-color: #1a1d24;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #FF6B35;
    }
    .chatbot-container {
        position: fixed;
        right: 20px;
        bottom: 20px;
        width: 350px;
        height: 500px;
        background-color: #1e2127;
        border-radius: 12px;
        border: 2px solid #FF6B35;
        padding: 20px;
        z-index: 1000;
    }
    .keyword-button {
        background-color: #FF6B35;
        color: white;
        padding: 8px 16px;
        border-radius: 6px;
        border: none;
        margin: 5px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
TENANT_ID = os.getenv("TENANT_ID", "burger_queen")
RESTAURANT_NAME = "Burger Queen"

def init_session_state():
    """Initialize session state."""
    if 'current_time' not in st.session_state:
        st.session_state.current_time = datetime.now()
    if 'current_orders' not in st.session_state:
        st.session_state.current_orders = 30
    if 'current_revenue' not in st.session_state:
        st.session_state.current_revenue = 1000
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'forecast_data' not in st.session_state:
        st.session_state.forecast_data = None
    if 'show_chatbot' not in st.session_state:
        st.session_state.show_chatbot = False


def create_pie_chart(labels, values, colors):
    """Create a pie chart using Plotly."""
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        hole=0.3,
        textinfo='label+percent'
    )])
    fig.update_layout(
        showlegend=True,
        height=250,
        margin=dict(t=30, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=10)
    )
    return fig


def create_bar_chart(hours, orders, current_hour=None):
    """Create hourly orders bar chart."""
    colors = ['#FF6B35' if h == current_hour else '#4A5568' for h in hours]
    
    fig = go.Figure(data=[go.Bar(
        x=hours,
        y=orders,
        marker=dict(color=colors),
        text=orders,
        textposition='outside'
    )])
    
    fig.update_layout(
        title="Orders/Hour",
        xaxis_title="Hours",
        yaxis_title="Orders",
        height=300,
        margin=dict(t=40, b=40, l=40, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(tickmode='linear', tick0=11, dtick=1),
        showlegend=False
    )
    
    # Add "You are here" annotation
    if current_hour:
        fig.add_annotation(
            x=current_hour,
            y=orders[hours.index(current_hour)] if current_hour in hours else max(orders),
            text="You are here →",
            showarrow=True,
            arrowhead=2,
            arrowcolor="#4A90E2",
            font=dict(color="#4A90E2", size=12),
            yshift=20
        )
    
    return fig


def create_peak_hours_chart():
    """Create peak hours curve."""
    hours = list(range(8, 17))
    # Bell curve pattern
    orders = [10, 15, 25, 35, 40, 35, 25, 15, 10]
    
    fig = go.Figure(data=[go.Scatter(
        x=hours,
        y=orders,
        mode='lines+markers',
        line=dict(color='#4A90E2', width=3),
        marker=dict(size=8, color='#4A90E2')
    )])
    
    # Highlight peak
    peak_idx = orders.index(max(orders))
    fig.add_trace(go.Scatter(
        x=[hours[peak_idx]],
        y=[orders[peak_idx]],
        mode='markers',
        marker=dict(size=15, color='#FFD700', line=dict(color='black', width=2)),
        showlegend=False
    ))
    
    fig.update_layout(
        title="Peak Hours",
        height=200,
        margin=dict(t=30, b=30, l=30, r=30),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=10),
        xaxis=dict(tickmode='array', tickvals=[8, 12, 16]),
        yaxis=dict(showticklabels=False),
        showlegend=False
    )
    
    return fig


def render_top_section():
    """Render top section: Current Status | EOD Predictions | Snapshot."""
    st.markdown('<div class="section-header">🍺 Brew.AI — Burger Queen Today</div>', 
                unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1.2])
    
    # Current Status (As of 9:14 am)
    with col1:
        st.markdown("### As of 9:14 AM")
        
        st.metric("Orders Filled", "30", "↑ 12 vs yesterday")
        st.metric("Revenue", "$1,000", "+$200")
        st.metric("Take Home", "$200", "+$40")
        
        st.markdown("**Order Split:**")
        order_split_fig = create_pie_chart(
            labels=['In Person', 'DoorDash', 'Pickup', 'Uber'],
            values=[45, 30, 20, 5],
            colors=['#FF6B35', '#4A90E2', '#10B981', '#F59E0B']
        )
        st.plotly_chart(order_split_fig, use_container_width=True)
        
        # Hovering info tooltip
        with st.expander("☀️ Weather & Traffic Impact"):
            st.info("Over last year an average **30% increase** over base on sunny days.")
            st.info("On high traffic days, delivery orders increase by **15-25%**.")
    
    # EOD Predictions
    with col2:
        st.markdown("### EOD Predictions")
        
        # Get forecast data if available
        forecast_orders = st.session_state.forecast_data.get('total_daily_orders', 193) if st.session_state.forecast_data else 193
        forecast_revenue = st.session_state.forecast_data.get('total_daily_revenue', 3000) if st.session_state.forecast_data else 3000
        
        st.metric("Orders", f"{int(forecast_orders)}", "Predicted")
        st.metric("Revenue", f"${int(forecast_revenue):,}", "Predicted")
        st.metric("Take Home", f"${int(forecast_revenue * 0.33):,}", "Projected")
        
        st.markdown("**Predicted Order Split:**")
        eod_split_fig = create_pie_chart(
            labels=['Delivery', 'In Person', 'Pickup'],
            values=[50, 35, 15],
            colors=['#4A90E2', '#FF6B35', '#10B981']
        )
        st.plotly_chart(eod_split_fig, use_container_width=True)
    
    # Snapshot of Today
    with col3:
        st.markdown("### Snapshot of Today")
        
        # Generate hourly data
        current_hour = datetime.now().hour
        hours = list(range(11, 20))  # 11 AM to 7 PM
        
        # Realistic order pattern
        base_orders = [5, 15, 25, 20, 8, 10, 18, 28, 22]
        
        hourly_chart = create_bar_chart(hours, base_orders, current_hour)
        st.plotly_chart(hourly_chart, use_container_width=True)


def render_staffing_section():
    """Render staffing cards for each day of the week."""
    st.markdown('<div class="section-header">📅 Weekly Staffing Predictions</div>', 
                unsafe_allow_html=True)
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Show 3 days at a time with scroll
    cols = st.columns(3)
    
    for idx, day in enumerate(days[:3]):
        with cols[idx]:
            st.markdown(f"#### {day}")
            
            # Predictions
            expected_revenue = np.random.randint(2500, 4000)
            expected_orders = int(expected_revenue / 18.5)
            
            st.markdown(f"**Expected Revenue:** ${expected_revenue:,}")
            st.markdown(f"**Expected Orders:** {expected_orders}")
            
            st.markdown("**STAFF:** Automated on Gusto")
            st.checkbox(f"2x Cashier", value=True, key=f"cashier_{day}")
            st.checkbox(f"1x Cooks", value=True, key=f"cook_{day}")
            
            # Peak hours mini chart
            peak_fig = create_peak_hours_chart()
            st.plotly_chart(peak_fig, use_container_width=True)
    
    if st.button("→ View More Days"):
        st.info("Scroll to see additional day forecasts")


def render_analytics_section():
    """Render bottom analytics section."""
    st.markdown('<div class="section-header">📊 Analytics & Recommendations</div>', 
                unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    # Review Sentiment
    with col1:
        st.markdown("### Review Sentiment")
        
        sentiment_fig = create_pie_chart(
            labels=['Neutral', 'Positive', 'Negative'],
            values=[50, 35, 15],
            colors=['#6B7280', '#10B981', '#EF4444']
        )
        st.plotly_chart(sentiment_fig, use_container_width=True)
        
        st.markdown("**Top Positive Keywords:**")
        st.markdown("""
        <div style="text-align: center;">
            <span class="keyword-button">Fresh</span>
            <span class="keyword-button">Cheesy</span>
            <span class="keyword-button">Cooked</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**Top Negative Keywords:**")
        st.markdown("""
        <div style="text-align: center;">
            <span class="keyword-button" style="background-color: #EF4444;">Spicy</span>
            <span class="keyword-button" style="background-color: #EF4444;">Cold</span>
            <span class="keyword-button" style="background-color: #EF4444;">Slow</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Analytics / Recommendations
    with col2:
        st.markdown("### Analytics / Recommendations")
        
        # Item selector
        col_left, col_mid, col_right = st.columns([0.2, 1, 0.2])
        with col_left:
            if st.button("◀"):
                pass
        with col_mid:
            st.markdown('<div style="text-align: center; background-color: #2e3137; padding: 10px; border-radius: 6px; font-weight: bold;">🍔 Cheese Burger</div>', unsafe_allow_html=True)
        with col_right:
            if st.button("▶"):
                pass
        
        st.markdown("**Recommendations:**")
        
        st.markdown("""
        <div class="status-box">
            <b>1. Make the burger less spicy</b><br>
            <span style="color: #9CA3AF; font-size: 13px;">
            Sentiment analysis shows that reviews want lower spice levels.
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="status-box">
            <b>2. Speed up the kitchen</b><br>
            <span style="color: #9CA3AF; font-size: 13px;">
            Sentiment analysis shows that food frequently arrives cold. Refunds are most 
            frequent for late deliveries and cold food.
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="status-box">
            <b>3. Optimize delivery packaging</b><br>
            <span style="color: #9CA3AF; font-size: 13px;">
            Temperature retention during delivery is critical. Consider insulated packaging.
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    # Refund Analysis & Customer Journey
    with col3:
        st.markdown("### Refund Analysis")
        
        refund_fig = create_pie_chart(
            labels=['Late Delivery', 'Open Bag', 'Incomplete', 'Cold Food'],
            values=[40, 20, 15, 25],
            colors=['#EF4444', '#F59E0B', '#6B7280', '#3B82F6']
        )
        st.plotly_chart(refund_fig, use_container_width=True)
        
        st.markdown("### Customer Journey")
        
        st.markdown("""
        <div class="metric-card">
            <b>Most time spent:</b> Menu<br>
            <b>Dropping off:</b> Checkout<br>
            <br>
            <b>💡 Recommendation:</b> Lower prices for combo meals to improve conversion
        </div>
        """, unsafe_allow_html=True)


def render_chatbot_sidebar():
    """Render chatbot in sidebar."""
    if st.session_state.show_chatbot:
        with st.sidebar:
            st.markdown("### 🤖 Brew.AI Assistant")
            st.markdown("Ask questions about your data")
            
            # Chat history
            chat_container = st.container()
            with chat_container:
                for msg in st.session_state.chat_messages:
                    if msg['role'] == 'user':
                        st.markdown(f"**You:** {msg['content']}")
                    else:
                        st.markdown(f"**Brew.AI:** {msg['content']}")
            
            # Input
            user_input = st.text_input("Ask a question...", key="chat_input")
            
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button("Send", use_container_width=True):
                    if user_input:
                        # Add user message
                        st.session_state.chat_messages.append({
                            'role': 'user',
                            'content': user_input
                        })
                        
                        # Get Captain response
                        response = get_captain_response(user_input)
                        
                        st.session_state.chat_messages.append({
                            'role': 'assistant',
                            'content': response
                        })
                        
                        st.rerun()
            
            with col2:
                st.button("🎤", help="Voice input")


def get_captain_response(question: str) -> str:
    """Get response from Captain for chatbot."""
    try:
        from services.captain_client import get_captain_client
        
        captain = get_captain_client()
        
        # Build context from current state
        context = f"""
Current Status:
- Orders: {st.session_state.current_orders}
- Revenue: ${st.session_state.current_revenue}
- Time: {st.session_state.current_time.strftime('%I:%M %p')}

Forecast Data:
{json.dumps(st.session_state.forecast_data, indent=2) if st.session_state.forecast_data else 'Not available'}
"""
        
        response = captain.client.chat.completions.create(
            model="captain-voyager-latest",
            messages=[
                {"role": "system", "content": "You are Brew.AI, a helpful restaurant analytics assistant. Answer questions about the restaurant data concisely."},
                {"role": "user", "content": question}
            ],
            extra_body={
                "captain": {
                    "context": context
                }
            }
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"I'm having trouble accessing the data right now. Error: {str(e)[:100]}"


async def load_forecast_data():
    """Load forecast data in background."""
    if not st.session_state.forecast_data:
        with st.spinner("Loading forecast..."):
            result = run_forecast_agent_lstm()
            if result.get('success'):
                st.session_state.forecast_data = result


def main():
    """Main application."""
    init_session_state()
    
    # Header
    st.markdown(f"""
    <div style="text-align: center; padding: 20px;">
        <h1 style="color: #FF6B35; margin: 0;">🍺 Brew.AI</h1>
        <p style="color: #9CA3AF; margin: 5px 0;">Real-time restaurant analytics & predictions</p>
        <p style="color: #6B7280; font-size: 14px;">{st.session_state.current_time.strftime('%A, %B %d, %Y • %I:%M %p')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chatbot toggle button
    col1, col2, col3 = st.columns([5, 1, 1])
    with col3:
        if st.button("💬 Chat" if not st.session_state.show_chatbot else "✕ Close"):
            st.session_state.show_chatbot = not st.session_state.show_chatbot
            st.rerun()
    
    st.markdown("---")
    
    # Top Section
    render_top_section()
    
    st.markdown("---")
    
    # Staffing Section
    render_staffing_section()
    
    st.markdown("---")
    
    # Analytics Section
    render_analytics_section()
    
    # Chatbot
    if st.session_state.show_chatbot:
        render_chatbot_sidebar()
    
    # Load forecast data in background
    if not st.session_state.forecast_data:
        asyncio.run(load_forecast_data())
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 12px; padding: 20px;">
        Powered by Brew.AI | Captain RAG + LSTM Forecasting + BrowserUse
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

