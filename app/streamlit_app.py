"""
Brew.AI - Multi-Agent Restaurant Operations Platform
Main Streamlit Application
"""
import streamlit as st
import os
import sys
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import json
from dotenv import load_dotenv

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

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Brew.AI - Restaurant Ops Platform",
    page_icon="🍺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF6B35;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 12px;
    }
    .stButton>button:hover {
        background-color: #FF8555;
    }
    .metric-card {
        background-color: #1e2127;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #2e3137;
        margin: 10px 0;
    }
    .success-banner {
        background-color: #10b981;
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .warning-banner {
        background-color: #f59e0b;
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .trace-entry {
        background-color: #1a1d24;
        padding: 10px;
        margin: 5px 0;
        border-left: 3px solid #FF6B35;
        border-radius: 4px;
        font-family: monospace;
        font-size: 12px;
    }
    h1, h2, h3 {
        color: #FF6B35;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
TENANT_ID = os.getenv("TENANT_ID", "charcoal_eats_us")
RESTAURANT_NAME = "Charcoal Eats US"
RESTAURANT_ADDRESS = "Entrance, 370 Lexington Avenue, E 41st St Store 104, New York, NY 10017"
EXPANSION_CITY = "San Francisco, CA"
STAFF = ["Bobby Maguire", "Mary Mcunnigham", "Lia Hunt", "Tory Kest"]

# Feature flags
AUTO_CLICK_PLAN = os.getenv("AUTO_CLICK_PLAN", "true").lower() == "true"

# Verify environment
def check_environment():
    """Check required environment variables."""
    required = {
        "BROWSER_USE_API_KEY": os.getenv("BROWSER_USE_API_KEY"),
        "GOOGLE_PLACES_API_KEY": os.getenv("GOOGLE_PLACES_API_KEY"),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    }
    
    missing = [k for k, v in required.items() if not v]
    
    if missing:
        st.error(f"❌ Missing required environment variables: {', '.join(missing)}")
        st.info("Please set these in your .env file or environment.")
        st.stop()
    
    # Chrome profile warning (optional)
    if not os.getenv("CHROME_USER_DATA_DIR"):
        st.warning("⚠️ CHROME_USER_DATA_DIR not set. BrowserUse will launch a new browser profile.")
    
    return True


def init_session_state():
    """Initialize session state variables."""
    if 'workflow_started' not in st.session_state:
        st.session_state.workflow_started = False
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    if 'results' not in st.session_state:
        st.session_state.results = {}
    if 'error' not in st.session_state:
        st.session_state.error = None


def render_progress_stepper(current_step: int):
    """Render progress stepper."""
    steps = [
        "🔍 Scrape",
        "🌤️ Weather",
        "📈 Forecast",
        "👥 Staffing",
        "📦 Prep",
        "🤖 Analyst",
        "🗺️ Expansion",
        "✅ Done"
    ]
    
    cols = st.columns(len(steps))
    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            if i < current_step:
                st.success(step)
            elif i == current_step:
                st.info(f"**{step}**")
            else:
                st.text(step)


async def run_workflow():
    """Execute the full multi-agent workflow."""
    trace = get_trace_agent()
    results = {}
    
    try:
        # Clear previous traces
        trace.clear()
        
        # Step 1: Scraper Agent
        st.session_state.current_step = 0
        with st.spinner("🔍 Scraping reviews from Google Maps..."):
            scraper_result = await asyncio.to_thread(
                run_scraper_agent,
                RESTAURANT_NAME,
                RESTAURANT_ADDRESS
            )
            results['scraper'] = scraper_result
        
        # Step 2: Weather Agent
        st.session_state.current_step = 1
        with st.spinner("🌤️ Fetching weather forecast..."):
            weather_result = run_weather_agent(
                RESTAURANT_NAME,
                RESTAURANT_ADDRESS
            )
            results['weather'] = weather_result
        
        # Step 3: Forecast Agent (LSTM)
        st.session_state.current_step = 2
        with st.spinner("📈 Predicting order volume & revenue (LSTM)..."):
            forecast_result = run_forecast_agent_lstm()
            results['forecast'] = forecast_result
        
        # Step 4: Staffing Agent
        st.session_state.current_step = 3
        if results['forecast'].get('success'):
            with st.spinner("👥 Creating Asana staffing tasks..."):
                staffing_result = await asyncio.to_thread(
                    run_staffing_agent,
                    STAFF,
                    RESTAURANT_NAME,
                    results['forecast']['peak_hour'],
                    results['forecast']['peak_orders']
                )
                results['staffing'] = staffing_result
        
        # Step 5: Prep Agent
        st.session_state.current_step = 4
        if results['forecast'].get('success') and results['weather'].get('success'):
            with st.spinner("📦 Creating purchase order..."):
                prep_result = await asyncio.to_thread(
                    run_prep_agent,
                    RESTAURANT_NAME,
                    results['forecast']['peak_orders'],
                    results['weather'].get('summary', {})
                )
                results['prep'] = prep_result
        
        # Step 6: Analyst Agent (Captain RAG)
        st.session_state.current_step = 5
        with st.spinner("🤖 Running Captain RAG analysis..."):
            # Build context from previous results
            context = {}
            if results.get('forecast', {}).get('success'):
                context['forecast_data'] = {
                    'peak_hour': results['forecast']['peak_hour'],
                    'peak_orders': results['forecast']['peak_orders']
                }
            if results.get('weather', {}).get('success'):
                context['weather_data'] = results['weather'].get('summary', {})
            
            analyst_result = run_analyst_agent_captain(
                TENANT_ID,
                "Why are we adding a cook tomorrow?",
                context=context
            )
            results['analyst'] = analyst_result
        
        # Step 7: Geo Agent
        st.session_state.current_step = 6
        with st.spinner("🗺️ Analyzing expansion opportunities..."):
            geo_result = await asyncio.to_thread(
                run_geo_agent,
                EXPANSION_CITY
            )
            results['geo'] = geo_result
        
        # Step 8: Done
        st.session_state.current_step = 7
        
        return results
        
    except Exception as e:
        st.session_state.error = str(e)
        return results


def render_forecast_panel(forecast_result: dict):
    """Render LSTM forecast visualization panel."""
    st.subheader("📈 Tomorrow's Forecast (LSTM Model)")
    
    if not forecast_result.get('success'):
        st.error(f"Forecast failed: {forecast_result.get('error', 'Unknown error')}")
        return
    
    # Metrics row 1: Orders
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Peak Hour",
            f"{forecast_result['peak_hour']}:00",
            "Tomorrow"
        )
    
    with col2:
        st.metric(
            "Peak Orders",
            f"{forecast_result['peak_orders']:.0f}",
            "+15% vs avg"
        )
    
    with col3:
        st.metric(
            "Daily Orders",
            f"{forecast_result.get('total_daily_orders', 0):.0f}",
            "10 AM - 10 PM"
        )
    
    with col4:
        st.metric(
            "Model",
            forecast_result.get('model_type', 'LSTM'),
            "90% CI"
        )
    
    # Metrics row 2: Revenue
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Peak Revenue",
            f"${forecast_result.get('peak_revenue', 0):,.2f}",
            f"@ {forecast_result['peak_hour']}:00"
        )
    
    with col2:
        st.metric(
            "Total Daily Revenue",
            f"${forecast_result.get('total_daily_revenue', 0):,.2f}",
            "Predicted"
        )
    
    with col3:
        st.metric(
            "Avg Order Value",
            "$18.50",
            "Historical"
        )
    
    # Show plot
    if os.path.exists("artifacts/forecast_plot.png"):
        st.image("artifacts/forecast_plot.png", use_container_width=True)
    
    # Callout
    st.markdown(f"""
    <div class="warning-banner">
        ⚠️ <b>Action Required:</b> Peak at {forecast_result['peak_hour']}:00 
        with {forecast_result['peak_orders']:.0f} orders 
        (${forecast_result.get('peak_revenue', 0):.2f} revenue). Additional cook needed.
    </div>
    """, unsafe_allow_html=True)


def render_staffing_panel(staffing_result: dict):
    """Render staffing panel."""
    st.subheader("👥 Staffing Plan")
    
    if not staffing_result.get('success'):
        st.error(f"Staffing failed: {staffing_result.get('error', 'Unknown error')}")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**Tomorrow's Shifts:**")
        for shift in staffing_result.get('shifts', []):
            st.markdown(f"""
            <div class="metric-card">
                <b>{shift['staff']}</b> - {shift['role']}<br>
                🕐 {shift['start_time']} - {shift['end_time']} ({shift['shift_hours']} hours)
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.metric("Required Cooks", staffing_result.get('required_cooks', 0))
        
        if st.button("🔗 Open Asana (Live)"):
            st.info("Opening Asana in browser...")
            # In production, this would trigger BrowserUse to open Asana
    
    # Show screenshot
    if os.path.exists("artifacts/asana_tasks_screenshot.png"):
        st.image("artifacts/asana_tasks_screenshot.png", caption="Asana Tasks", use_container_width=True)


def render_prep_panel(prep_result: dict):
    """Render prep/inventory panel."""
    st.subheader("📦 Inventory & Prep")
    
    if not prep_result.get('success'):
        st.error(f"Prep failed: {prep_result.get('error', 'Unknown error')}")
        return
    
    po_data = prep_result.get('po_data', {})
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**Purchase Order:**")
        st.markdown(f"""
        <div class="metric-card">
            <b>Item:</b> {po_data.get('item', 'N/A')}<br>
            <b>Quantity:</b> {po_data.get('quantity', 0)} {po_data.get('unit', 'lbs')}<br>
            <b>Delivery:</b> {po_data.get('delivery_date', 'N/A')}<br>
            <b>Notes:</b> {po_data.get('notes', 'N/A')}
        </div>
        """, unsafe_allow_html=True)
        
        if prep_result.get('buffer_applied'):
            st.markdown("""
            <div class="warning-banner">
                ☔ Rain buffer applied (+15% inventory)
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.metric("Wings (lbs)", prep_result.get('wings_lbs', 0))
        
        if st.button("🔗 Open Supplier (Live)"):
            st.info("Opening supplier portal in browser...")
    
    # Show filled form screenshot
    if os.path.exists("artifacts/supplier_po_filled.png"):
        st.image("artifacts/supplier_po_filled.png", caption="Supplier PO Form", use_container_width=True)


def render_analyst_panel(analyst_result: dict):
    """Render Captain RAG analyst panel."""
    st.subheader("🤖 AI Analyst Insights (Powered by Captain)")
    
    # Don't show error if we have results
    if not analyst_result.get('success') and not analyst_result.get('answer'):
        st.warning(f"⚠️ Note: {analyst_result.get('error', 'Analysis incomplete')}")
        # Continue to show whatever results we have
    
    # Show Captain badge
    st.markdown("""
    <div style="background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%); 
                padding: 10px; border-radius: 8px; margin-bottom: 15px; text-align: center;">
        <span style="color: white; font-weight: bold;">⚡ Powered by Captain RAG</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**Question:** *Why are we adding a cook tomorrow?*")
    
    st.markdown(f"""
    <div class="metric-card">
        {analyst_result.get('answer', 'No answer available')}
    </div>
    """, unsafe_allow_html=True)
    
    # Show conversation ID if available
    if analyst_result.get('conversation_id'):
        st.caption(f"💬 Conversation ID: {analyst_result['conversation_id']}")
    
    st.markdown("**Citations:**")
    
    citations = analyst_result.get('citations', [])
    if citations:
        for i, citation in enumerate(citations, 1):
            with st.expander(f"📄 [{i}] {citation['source']} (Score: {citation.get('score', 0):.2f})"):
                st.markdown(f"*{citation['excerpt']}*")
                
                if citation.get('url'):
                    if st.button(f"Open Source [{i}]", key=f"citation_{i}"):
                        st.info(f"Opening: {citation['url']}")
                        # In production, BrowserUse opens this URL
    else:
        st.info("No citations available")
    
    # Show Captain collection info
    if os.path.exists("artifacts/rag_index_summary.json"):
        with st.expander("📊 Captain RAG Details"):
            with open("artifacts/rag_index_summary.json", 'r') as f:
                summary = json.load(f)
            st.json(summary)


def render_expansion_panel(geo_result: dict):
    """Render expansion map panel."""
    st.subheader(f"🗺️ Expansion Analysis - {EXPANSION_CITY}")
    
    if not geo_result.get('success'):
        st.error(f"Geo analysis failed: {geo_result.get('error', 'Unknown error')}")
        return
    
    locations = geo_result.get('locations', [])
    
    if locations:
        top_location = locations[0]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Top Location", top_location['name'])
        with col2:
            st.metric("ROI Score", f"{top_location['roi_score']:.2f}")
        with col3:
            st.metric("Competitors", top_location['competitors_count'])
        
        # Show map
        if os.path.exists("artifacts/expansion_map.html"):
            with open("artifacts/expansion_map.html", 'r', encoding='utf-8') as f:
                map_html = f.read()
            st.components.v1.html(map_html, height=600)
        
        # Location list
        st.markdown("**All Candidate Locations:**")
        for loc in locations[:5]:
            st.markdown(f"""
            <div class="metric-card">
                <b>{loc['name']}</b> - ROI: {loc['roi_score']:.2f}<br>
                Traffic: {loc['traffic_score']:.2f} | Competition: {loc['competition_score']:.2f} | Income: {loc['income_score']:.2f}<br>
                <a href="{loc['gmaps_url']}" target="_blank">View on Google Maps</a>
            </div>
            """, unsafe_allow_html=True)


def render_trace_panel():
    """Render trace log panel."""
    st.subheader("📋 Agent Trace Log")
    
    trace = get_trace_agent()
    traces = trace.get_traces(limit=50)
    
    if not traces:
        st.info("No traces yet. Run the workflow to see agent actions.")
        return
    
    # Download button
    if os.path.exists("artifacts/trace.json"):
        with open("artifacts/trace.json", 'r') as f:
            trace_json = f.read()
        st.download_button(
            "⬇️ Download trace.json",
            trace_json,
            file_name=f"brew_ai_trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    # Show recent traces
    for t in reversed(traces[-20:]):  # Last 20 traces
        st.markdown(f"""
        <div class="trace-entry">
            <b>{t['timestamp'][:19]}</b> | <b>{t['agent']}</b><br>
            {t['action']}<br>
            {f"✅ {t['result']}" if t.get('result') else ''}
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main application."""
    check_environment()
    init_session_state()
    
    # Header
    st.title(f"🍺 Brew.AI — {RESTAURANT_NAME}")
    st.caption(f"📍 {RESTAURANT_ADDRESS}")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/FF6B35/FFFFFF?text=Brew.AI", use_container_width=True)
        st.markdown(f"**Tenant:** {TENANT_ID}")
        st.markdown(f"**Planning for:** {(datetime.now() + timedelta(days=1)).strftime('%A, %B %d')}")
        st.markdown("---")
        
        # Control buttons
        if not st.session_state.workflow_started:
            if st.button("▶️ Plan Tomorrow", type="primary"):
                st.session_state.workflow_started = True
                st.rerun()
        else:
            st.success("✅ Workflow Running")
            if st.button("🔄 Reset"):
                st.session_state.workflow_started = False
                st.session_state.current_step = 0
                st.session_state.results = {}
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 🎯 Agents")
        agents = ["Scraper", "Weather", "Forecast", "Staffing", "Prep", "Analyst", "Geo", "Trace"]
        for agent in agents:
            st.markdown(f"• {agent}")
    
    # Progress stepper
    render_progress_stepper(st.session_state.current_step)
    st.markdown("---")
    
    # Run workflow if started
    if st.session_state.workflow_started and not st.session_state.results:
        with st.status("🚀 Running multi-agent workflow...", expanded=True) as status:
            st.write("Initializing agents...")
            results = asyncio.run(run_workflow())
            st.session_state.results = results
            status.update(label="✅ Workflow complete!", state="complete")
            st.rerun()
    
    # Display results
    if st.session_state.results:
        results = st.session_state.results
        
        # Tabs for different panels
        tabs = st.tabs([
            "📈 Forecast",
            "👥 Staffing",
            "📦 Prep",
            "🤖 Analyst",
            "🗺️ Expansion",
            "📋 Trace"
        ])
        
        with tabs[0]:
            if 'forecast' in results:
                render_forecast_panel(results['forecast'])
        
        with tabs[1]:
            if 'staffing' in results:
                render_staffing_panel(results['staffing'])
        
        with tabs[2]:
            if 'prep' in results:
                render_prep_panel(results['prep'])
        
        with tabs[3]:
            if 'analyst' in results:
                render_analyst_panel(results['analyst'])
        
        with tabs[4]:
            if 'geo' in results:
                render_expansion_panel(results['geo'])
        
        with tabs[5]:
            render_trace_panel()
    
    elif st.session_state.error:
        st.error(f"❌ Workflow error: {st.session_state.error}")
    
    else:
        # Welcome screen
        st.info("👋 Click **'Plan Tomorrow'** in the sidebar to start the multi-agent workflow.")
        
        st.markdown("""
        ### What This Demo Does:
        
        1. **🔍 Scrape Reviews** - Extracts Google Maps reviews using BrowserUse
        2. **🌤️ Weather Forecast** - Gets tomorrow's weather from Open-Meteo
        3. **📈 Forecast Orders** - Predicts order volume with XGBoost
        4. **👥 Staff Planning** - Creates Asana tasks for shifts
        5. **📦 Inventory Prep** - Calculates purchase orders and fills supplier forms
        6. **🤖 RAG Analysis** - Answers questions with citations from knowledge base
        7. **🗺️ Expansion Map** - Analyzes San Francisco locations with ROI scoring
        8. **📋 Full Tracing** - Logs every agent action with timestamps
        
        All actions are performed in your **signed-in Chrome profile** with visible browser automation!
        """)
    
    # Footer
    st.markdown("---")
    st.caption(f"Powered by Brew.AI | BrowserUse + Gemini | {datetime.now().strftime('%Y-%m-%d %H:%M')}")


if __name__ == "__main__":
    main()

