"""
Expansion Insights Page
"""
import streamlit as st
import sys
import os
from pathlib import Path
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

st.set_page_config(page_title="Expansion", page_icon="🗺️", layout="wide")

st.title("🗺️ Expansion Insights")

# Target city selector
col1, col2 = st.columns([2, 1])

with col1:
    target_city = st.selectbox(
        "Expansion Target:",
        ["San Francisco, CA", "Los Angeles, CA", "Seattle, WA", "Austin, TX"]
    )

with col2:
    if st.button("🔍 Analyze Locations", type="primary", use_container_width=True):
        with st.spinner("Analyzing locations..."):
            from agents.geo_agent import run_geo_agent
            result = run_geo_agent(target_city)
            st.session_state.expansion_result = result

# Show results if available
if 'expansion_result' in st.session_state and st.session_state.expansion_result.get('success'):
    result = st.session_state.expansion_result
    locations = result.get('locations', [])
    
    st.markdown("---")
    st.markdown(f"### 📍 Top Locations in {target_city}")
    
    # Top 3 locations
    for i, loc in enumerate(locations[:3], 1):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
            <div style="background-color: #1e2127; padding: 20px; margin: 10px 0; border-radius: 8px; border-left: 4px solid {'#10B981' if i == 1 else '#FF6B35'};">
                <h3 style="color: {'#10B981' if i == 1 else '#FF6B35'}; margin: 0;">
                    #{i} {loc['name']}
                </h3>
                <p style="color: white; font-size: 18px; margin: 10px 0;">
                    ROI Score: <b>{loc['roi_score']:.2f}</b>
                </p>
                <p style="color: #9CA3AF; margin: 5px 0;">
                    Traffic Score: {loc['traffic_score']:.2f} | 
                    Competition: {loc['competition_score']:.2f} | 
                    Income: {loc['income_score']:.2f}
                </p>
                <p style="color: #9CA3AF; font-size: 12px;">
                    {loc['competitors_count']} competitors nearby • 
                    {loc['businesses_count']} businesses
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button(f"📍 View on Maps", key=f"maps_{i}"):
                st.info(f"Opening: {loc.get('gmaps_url')}")
    
    # Show map if available
    if os.path.exists("artifacts/expansion_map.html"):
        st.markdown("---")
        st.markdown("### 🗺️ Interactive Map")
        
        with open("artifacts/expansion_map.html", 'r', encoding='utf-8') as f:
            map_html = f.read()
        st.components.v1.html(map_html, height=600)

else:
    st.info("👆 Click 'Analyze Locations' to run expansion analysis")
    
    # Show placeholder
    st.markdown("### 📊 Expansion Criteria")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Traffic Score (40%)**
        - Nearby businesses
        - Transit access
        - Foot traffic density
        """)
    
    with col2:
        st.markdown("""
        **Competition (30%)**
        - Similar restaurants
        - Market saturation
        - Differentiation opportunity
        """)
    
    with col3:
        st.markdown("""
        **Demographics (30%)**
        - Income levels
        - Population density
        - Target customer density
        """)

