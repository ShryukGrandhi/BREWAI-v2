"""
Knowledge Map - Interactive force-directed graph of agent reasoning.
"""
import streamlit as st
import sys
import os
import json
from pathlib import Path
from pyvis.network import Network
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

st.set_page_config(
    page_title="Knowledge Map - Brew.AI",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .node-info-card {
        background: #1e1e1e;
        border: 2px solid #8B5CF6;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .decision-path {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    .legend-item {
        display: inline-block;
        margin: 5px 10px;
        padding: 5px 15px;
        border-radius: 15px;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🧠 Knowledge Map")
st.caption("Agent reasoning and compliance paths — fully explainable")

st.markdown("""
<div class="decision-path">
    <h3 style="margin: 0;">🔄 Live Decision Chain</h3>
    <p style="margin: 5px 0;">Rain 🌧️ → Delivery Surge +45% → Wings Demand Spike → Add Cook → Fryer Cert Check → Assign Mary → ✅ Compliant</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Controls
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.markdown("### 🎛️ Controls")
    
with col2:
    if st.button("🔄 Rebuild Graph", type="primary"):
        st.session_state.rebuild_graph = True
        st.rerun()

with col3:
    if st.button("💾 Export JSON"):
        if os.path.exists("artifacts/knowledge_graph.json"):
            with open("artifacts/knowledge_graph.json", 'r') as f:
                graph_data = f.read()
            st.download_button(
                "Download Graph Data",
                graph_data,
                "knowledge_graph.json",
                "application/json"
            )

# Graph options
with st.expander("⚙️ Graph Options"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        physics_enabled = st.checkbox("Enable Physics", value=True, help="Force-directed layout with physics simulation")
        show_edges = st.checkbox("Show Edge Labels", value=True, help="Display relationship labels on edges")
    
    with col2:
        node_size_scale = st.slider("Node Size", 50, 200, 100, help="Scale node sizes")
        edge_width_scale = st.slider("Edge Width", 1, 5, 2, help="Scale edge widths")
    
    with col3:
        highlight_decisions = st.checkbox("Highlight Decisions", value=True, help="Emphasize decision nodes")
        show_secured = st.checkbox("Show Security Badges", value=True, help="Display Nivara security on compliance nodes")

# Build or load graph
if st.session_state.get('rebuild_graph') or not os.path.exists("artifacts/knowledge_graph.json"):
    with st.spinner("🧠 Building knowledge graph from all agents..."):
        try:
            from agents.knowledge_map_agent import run_knowledge_map_agent
            
            tenant_id = os.getenv("TENANT_ID", "charcoal_eats_us")
            
            # Load agent outputs
            forecast_data = {}
            weather_data = {}
            
            # Try to load from artifacts
            if os.path.exists("artifacts/forecast.csv"):
                import pandas as pd
                try:
                    fc_df = pd.read_csv("artifacts/forecast.csv")
                    if not fc_df.empty:
                        forecast_data = {
                            'success': True,
                            'peak_hour': int(fc_df['hour'].iloc[fc_df['orders'].idxmax()]),
                            'peak_orders': int(fc_df['orders'].max()),
                            'total_daily_orders': int(fc_df['orders'].sum()),
                            'total_daily_revenue': float(fc_df['orders'].sum() * 18.5),
                            'confidence': 0.85
                        }
                except:
                    pass
            
            # Generate graph
            result = run_knowledge_map_agent(
                tenant_id=tenant_id,
                forecast_data=forecast_data if forecast_data else None,
                weather_data={'success': True, 'rain_hours': 3, 'avg_temp': 62} if not weather_data else weather_data
            )
            
            if result.get('success'):
                st.success(f"✅ Graph built: {result['node_count']} nodes, {result['edge_count']} edges")
            else:
                st.error(f"❌ Error: {result.get('error')}")
            
            st.session_state.rebuild_graph = False
        
        except Exception as e:
            st.error(f"❌ Error building graph: {e}")

# Load graph data
if os.path.exists("artifacts/knowledge_graph.json"):
    with open("artifacts/knowledge_graph.json", 'r') as f:
        graph_data = json.load(f)
    
    st.success(f"📊 Loaded graph: {len(graph_data['nodes'])} nodes, {len(graph_data['edges'])} edges")
    
    # Create PyVis network
    net = Network(
        height="600px",
        width="100%",
        bgcolor="#0e1117",
        font_color="white",
        directed=True
    )
    
    # Configure physics
    if physics_enabled:
        net.barnes_hut(
            gravity=-5000,
            central_gravity=0.3,
            spring_length=200,
            spring_strength=0.05,
            damping=0.09
        )
    else:
        net.toggle_physics(False)
    
    # Add nodes
    for node in graph_data['nodes']:
        node_id = node['id']
        node_type = node.get('type', 'unknown')
        color = node.get('color', '#666666')
        size = node.get('size', 20) * (node_size_scale / 100)
        title = node.get('title', node_id)
        
        # Add security badge for compliance nodes
        if node.get('secured_by') == 'Nivara' and show_secured:
            title = f"🔒 SECURED BY NIVARA\n\n{title}\n\nAccess: {node.get('access_level', 'restricted')}"
        
        # Add confidence/impact to title
        if 'confidence' in node:
            title += f"\n\nConfidence: {node['confidence']*100:.0f}%"
        if 'impact_score' in node:
            title += f"\nImpact: {node['impact_score']*100:.0f}%"
        
        # Highlight decisions
        if highlight_decisions and node_type == 'decision':
            color = "#A855F7"
            size *= 1.2
        
        shape = node.get('shape', 'dot')
        
        net.add_node(
            node_id,
            label=node_id,
            color=color,
            size=size,
            title=title,
            shape=shape
        )
    
    # Add edges
    for edge in graph_data['edges']:
        source = edge['source']
        target = edge['target']
        relationship = edge.get('relationship', '')
        width = edge.get('width', 1) * edge_width_scale
        
        label = relationship if show_edges else ""
        
        # Color code edges
        edge_color = "#666666"
        if 'confidence' in edge:
            conf = edge['confidence']
            if conf > 0.8:
                edge_color = "#10B981"  # High confidence = green
            elif conf > 0.6:
                edge_color = "#F59E0B"  # Medium = yellow
            else:
                edge_color = "#EF4444"  # Low = red
        
        net.add_edge(
            source,
            target,
            label=label,
            width=width,
            color=edge_color,
            arrows="to"
        )
    
    # Save and display
    try:
        net.save_graph("temp_graph.html")
        
        with open("temp_graph.html", 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        components.html(html_content, height=650, scrolling=False)
        
        # Clean up
        if os.path.exists("temp_graph.html"):
            os.remove("temp_graph.html")
    
    except Exception as e:
        st.error(f"❌ Error rendering graph: {e}")
    
    # Legend
    st.markdown("---")
    st.markdown("### 🎨 Legend")
    
    st.markdown("""
    <div>
        <span class="legend-item" style="background: #FF6B35; color: white;">⭐ Restaurant</span>
        <span class="legend-item" style="background: #8B5CF6; color: white;">🧠 Decisions</span>
        <span class="legend-item" style="background: #10B981; color: white;">🍴 Menu</span>
        <span class="legend-item" style="background: #FCD34D; color: black;">🌤️ Conditions</span>
        <span class="legend-item" style="background: #60A5FA; color: white;">👥 Staff</span>
        <span class="legend-item" style="background: #F97316; color: white;">🔒 Compliance</span>
        <span class="legend-item" style="background: #EF4444; color: white;">⚠️ Risks</span>
        <span class="legend-item" style="background: #06B6D4; color: white;">📍 Expansion</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Node details
    st.markdown("### 📋 Node Details")
    
    # Show key nodes
    tabs = st.tabs(["🧠 Decisions", "🔒 Compliance", "👥 Staff", "📝 Reviews", "⚠️ Risks"])
    
    with tabs[0]:  # Decisions
        decision_nodes = [n for n in graph_data['nodes'] if n.get('type') == 'decision']
        if decision_nodes:
            for node in decision_nodes:
                with st.expander(f"💡 {node['id']}"):
                    st.markdown(f"**Title:** {node.get('title', 'N/A')}")
                    st.markdown(f"**Confidence:** {node.get('confidence', 0)*100:.0f}%")
                    st.markdown(f"**Cluster:** {node.get('cluster', 'N/A')}")
        else:
            st.info("No decision nodes in current graph")
    
    with tabs[1]:  # Compliance
        compliance_nodes = [n for n in graph_data['nodes'] if n.get('type') == 'compliance']
        if compliance_nodes:
            for node in compliance_nodes:
                with st.expander(f"🔒 {node['id']}"):
                    st.markdown(f"**Title:** {node.get('title', 'N/A')}")
                    st.markdown(f"**Risk Level:** {node.get('risk_level', 'N/A')}")
                    st.markdown(f"**Secured By:** {node.get('secured_by', 'N/A')}")
                    st.markdown(f"**Access Level:** {node.get('access_level', 'N/A')}")
                    
                    if node.get('access_level') == 'manager_only':
                        st.warning("🔒 Manager access required to view full details")
        else:
            st.info("No compliance nodes in current graph")
    
    with tabs[2]:  # Staff
        staff_nodes = [n for n in graph_data['nodes'] if n.get('type') == 'staff']
        if staff_nodes:
            for node in staff_nodes:
                with st.expander(f"👤 {node['id']}"):
                    st.markdown(f"**Role:** {node.get('role', 'N/A')}")
                    st.markdown(f"**Cluster:** {node.get('cluster', 'N/A')}")
        else:
            st.info("No staff nodes in current graph")
    
    with tabs[3]:  # Reviews
        review_nodes = [n for n in graph_data['nodes'] if n.get('type') == 'review']
        if review_nodes:
            for node in review_nodes:
                with st.expander(f"📝 {node['id']}"):
                    st.markdown(f"**Title:** {node.get('title', 'N/A')}")
                    sentiment = node.get('sentiment', 'neutral')
                    emoji = "😊" if sentiment == "positive" else ("😐" if sentiment == "neutral" else "😞")
                    st.markdown(f"**Sentiment:** {emoji} {sentiment.capitalize()}")
        else:
            st.info("No review nodes in current graph")
    
    with tabs[4]:  # Risks
        risk_nodes = [n for n in graph_data['nodes'] if n.get('risk_level')]
        if risk_nodes:
            for node in risk_nodes:
                risk = node.get('risk_level', 'UNKNOWN')
                color = "#EF4444" if risk == "CRITICAL" else ("#F59E0B" if risk == "HIGH" else "#FCD34D")
                with st.expander(f"⚠️ {node['id']}", expanded=(risk=="CRITICAL")):
                    st.markdown(f"**Title:** {node.get('title', 'N/A')}")
                    st.markdown(f"<span style='background: {color}; color: white; padding: 5px 15px; border-radius: 10px;'>**Risk: {risk}**</span>", unsafe_allow_html=True)
        else:
            st.info("No risk nodes in current graph")

else:
    st.warning("⚠️ No graph data available. Click 'Rebuild Graph' to generate.")

# Voice integration
st.markdown("---")
st.markdown("### 🎤 Voice Agent Integration")

col1, col2 = st.columns(2)

with col1:
    if st.button("🎤 Ask About Decision", type="primary"):
        st.info("💡 Try asking: 'Why add a cook tomorrow?' to see the decision chain highlighted!")

with col2:
    if st.button("📖 Explain Compliance Path"):
        st.markdown("""
        **Compliance Decision Path:**
        
        1. 🔒 Fryer Cert Required (NYC Food Code)
        2. ↓
        3. 🧠 Decision: Add Cook Tomorrow
        4. ↓
        5. 👤 Assign: Mary Fryer
        6. ↓
        7. ✅ Compliant
        
        **Reasoning:** Forecast shows 50+ orders/hour. NYC regulations require 1 certified cook per active fryer during peak. Mary is fryer-certified, so she's assigned.
        """)

# Footer
st.markdown("---")
st.caption("""
🧠 **Knowledge Map Features:**
- Drag nodes to rearrange
- Hover for detailed info
- Color-coded by type
- Edge thickness = confidence × impact
- 🔒 Compliance nodes secured by Nivara
- Real-time updates on each planning run
""")

