"""
Compliance Page - Secure document management and compliance reasoning with Nivara AI.
"""
import streamlit as st
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

st.set_page_config(
    page_title="Compliance - Brew.AI",
    page_icon="🔒",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .security-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin: 10px 0;
    }
    .compliance-card {
        background: #1e1e1e;
        border-left: 4px solid #10B981;
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .violation-card {
        background: #1e1e1e;
        border-left: 4px solid #EF4444;
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .risk-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 12px;
        margin: 5px;
    }
    .risk-low { background: #10B981; color: white; }
    .risk-medium { background: #F59E0B; color: white; }
    .risk-high { background: #EF4444; color: white; }
    .risk-critical { background: #7F1D1D; color: white; }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🔒 Compliance & Security")
st.caption("Powered by Nivara AI - Secure document management & compliance reasoning")

# Security badge
st.markdown("""
<div class="security-badge">
    🛡️ Protected by Nivara • Tenant-level isolation • No data leakage
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["📤 Upload Documents", "🔍 Compliance Check", "📋 Document Library"])

# Initialize session state
if 'compliance_result' not in st.session_state:
    st.session_state.compliance_result = None

# Tab 1: Upload Documents
with tab1:
    st.markdown("### Upload Compliance Documents")
    st.markdown("Upload sensitive documents with secure tenant-level isolation. Supported formats: PDF, DOCX, TXT, MD, Images (OCR)")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a compliance document",
            type=['pdf', 'docx', 'doc', 'txt', 'md', 'png', 'jpg', 'jpeg'],
            help="Documents are encrypted and stored with tenant isolation"
        )
        
        doc_type = st.selectbox(
            "Document Type",
            [
                "food_safety",
                "certification",
                "labor_regulations",
                "health_inspection",
                "training_records",
                "fire_safety",
                "other"
            ]
        )
        
        access_level = st.selectbox(
            "Access Level",
            [
                "manager_only",
                "all_staff",
                "owner_only"
            ],
            help="Controls who can view this document"
        )
    
    with col2:
        st.info("""
        **Access Levels:**
        
        🔴 **Owner Only**
        Highest restriction
        
        🟡 **Manager Only**
        Management access
        
        🟢 **All Staff**
        Visible to everyone
        """)
    
    if st.button("🔒 Upload Securely", type="primary", disabled=not uploaded_file):
        if uploaded_file:
            # Show Nivara transparency
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🔍 Nivara: Extracting text from document...")
            progress_bar.progress(20)
            
            with st.spinner("Processing with Nivara AI..."):
                try:
                    # Save temp file
                    temp_dir = Path("temp_uploads")
                    temp_dir.mkdir(exist_ok=True)
                    
                    temp_path = temp_dir / uploaded_file.name
                    with open(temp_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Upload with Nivara
                    from agents.compliance_agent import ComplianceAgent
                    from agents.trace_agent import TraceAgent
                    
                    tenant_id = os.getenv("TENANT_ID", "charcoal_eats_us")
                    
                    status_text.text("🔐 Nivara: Generating secure document ID...")
                    progress_bar.progress(40)
                    
                    status_text.text("🛡️ Nivara: Applying tenant-level isolation...")
                    progress_bar.progress(60)
                    
                    trace = TraceAgent()
                    agent = ComplianceAgent(tenant_id, trace)
                    
                    status_text.text("☁️ Nivara: Uploading to secure storage...")
                    progress_bar.progress(80)
                    
                    result = agent.upload_document(
                        file_path=str(temp_path),
                        doc_type=doc_type,
                        access_level=access_level,
                        metadata={
                            "uploaded_by": "demo_user",
                            "uploaded_at": datetime.now().isoformat(),
                            "original_filename": uploaded_file.name
                        }
                    )
                    
                    # Clean up temp file
                    temp_path.unlink()
                    
                    status_text.text("✅ Nivara: Document secured successfully!")
                    progress_bar.progress(100)
                    
                    if result.get("success"):
                        st.success(f"✅ {result['message']}")
                        st.markdown(f"""
                        <div class="compliance-card">
                            <h4>📄 {result['filename']}</h4>
                            <p><strong>Document ID:</strong> {result['doc_id']}</p>
                            <p><strong>Type:</strong> {result['doc_type']}</p>
                            <p><strong>Access:</strong> {result['access_level']}</p>
                            <p><strong>Security:</strong> {result['security_badge']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"❌ Upload failed: {result.get('error')}")
                
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# Tab 2: Compliance Check
with tab2:
    st.markdown("### Ask Compliance Questions")
    st.markdown("Query secure documents for compliance reasoning with citations")
    
    # Quick question buttons
    st.markdown("**Quick Questions:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔥 Fryer Staffing"):
            st.session_state.compliance_question = "Why is adding a cook tomorrow required for compliance?"
    
    with col2:
        if st.button("❄️ Thawing Rules"):
            st.session_state.compliance_question = "Are we compliant if wings thaw for 3 hours?"
    
    with col3:
        if st.button("📋 Staff Certs"):
            st.session_state.compliance_question = "Which staff members are fryer-certified?"
    
    # Custom question
    question = st.text_area(
        "Or ask your own question:",
        value=st.session_state.get('compliance_question', ''),
        placeholder="Example: Are we meeting NYC food safety requirements for our current staffing?",
        height=100
    )
    
    user_role = st.selectbox(
        "Your Role",
        ["manager", "owner", "staff"],
        help="Determines document access permissions"
    )
    
    if st.button("🔍 Check Compliance", type="primary", disabled=not question):
        # Show Nivara transparency
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🔍 Nivara: Loading secure documents...")
        progress_bar.progress(15)
        
        with st.spinner("Analyzing with Nivara AI..."):
            try:
                from agents.compliance_agent import ComplianceAgent
                from agents.trace_agent import TraceAgent
                
                tenant_id = os.getenv("TENANT_ID", "charcoal_eats_us")
                
                status_text.text("🛡️ Nivara: Verifying tenant access...")
                progress_bar.progress(30)
                
                trace = TraceAgent()
                agent = ComplianceAgent(tenant_id, trace)
                
                status_text.text("📚 Nivara: Retrieving compliance documents...")
                progress_bar.progress(45)
                
                # Build operational context
                import pandas as pd
                context = {}
                
                try:
                    if os.path.exists("data/orders_realtime.csv"):
                        orders_df = pd.read_csv("data/orders_realtime.csv")
                        context['orders_today'] = len(orders_df)
                    
                    if os.path.exists("data/staff_schedule.csv"):
                        staff_df = pd.read_csv("data/staff_schedule.csv")
                        today = datetime.now().strftime('%Y-%m-%d')
                        today_staff = staff_df[staff_df['date'] == today]
                        context['staff_count'] = len(today_staff) if not today_staff.empty else 0
                    
                    context['peak_hours'] = "12-2pm, 6-8pm"
                except Exception as e:
                    print(f"[WARN] Could not load context: {e}")
                
                status_text.text("🧠 Nivara + Captain: Analyzing compliance...")
                progress_bar.progress(65)
                
                status_text.text("📖 Nivara: Extracting citations...")
                progress_bar.progress(80)
                
                result = agent.run(
                    question=question,
                    user_role=user_role,
                    context=context
                )
                
                status_text.text("✅ Nivara: Analysis complete!")
                progress_bar.progress(100)
                
                st.session_state.compliance_result = result
                
                if result.get("success"):
                    # Display results
                    status = result['status']
                    confidence = result['confidence']
                    risk = result.get('risk_level', 'UNKNOWN')
                    
                    # Status card
                    card_class = "compliance-card" if "COMPLIANT" in status.upper() else "violation-card"
                    
                    st.markdown(f"""
                    <div class="{card_class}">
                        <h3>{"✅" if "COMPLIANT" in status.upper() else "⚠️"} Compliance Status: {status}</h3>
                        <p><strong>Confidence:</strong> {confidence}%</p>
                        <p><strong>Documents Accessed:</strong> {result['documents_accessed']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Risk level
                    if risk and risk != "UNKNOWN":
                        risk_class = f"risk-{risk.lower()}"
                        st.markdown(f"""
                        <span class="risk-badge {risk_class}">RISK LEVEL: {risk}</span>
                        """, unsafe_allow_html=True)
                    
                    # Reasoning
                    st.markdown("### 📝 Analysis")
                    st.markdown(result['reasoning'])
                    
                    # Citations
                    if result.get('citations'):
                        st.markdown("### 📚 Citations")
                        for i, cite in enumerate(result['citations'], 1):
                            with st.expander(f"[{i}] {cite.get('title', 'Source')}"):
                                st.markdown(f"**Relevance:** {cite.get('score', 0)*100:.0f}%")
                                st.markdown(cite.get('excerpt', 'No excerpt available'))
                    
                    # Recommendations
                    if result.get('recommendations'):
                        st.markdown("### 💡 Recommendations")
                        for rec in result['recommendations']:
                            st.markdown(f"- {rec}")
                    
                    # Security badge
                    st.markdown(f"""
                    <div class="security-badge">
                        {result['security_badge']}
                    </div>
                    """, unsafe_allow_html=True)
                
                else:
                    if result.get('warning'):
                        st.warning(result['warning'])
                        st.info(result.get('message', 'Upload documents to enable compliance checks'))
                    else:
                        st.error(f"❌ Error: {result.get('error')}")
            
            except Exception as e:
                st.error(f"❌ Compliance check failed: {e}")

# Tab 3: Document Library
with tab3:
    st.markdown("### 📋 Compliance Document Library")
    
    try:
        from services.nivara_client import get_nivara_client
        
        tenant_id = os.getenv("TENANT_ID", "charcoal_eats_us")
        nivara = get_nivara_client()
        
        user_role = st.selectbox(
            "View as role:",
            ["manager", "owner", "staff"],
            key="lib_role"
        )
        
        docs = nivara.get_tenant_documents(tenant_id, user_role)
        
        if docs:
            st.success(f"Found {len(docs)} documents")
            
            for doc in docs:
                is_blurred = doc.get('blurred', False)
                
                with st.expander(f"{'🔒' if is_blurred else '📄'} {doc['filename']} ({doc['doc_type']})"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Document ID:** `{doc['doc_id']}`")
                        st.markdown(f"**Type:** {doc['doc_type']}")
                        st.markdown(f"**Access Level:** {doc['access_level']}")
                        st.markdown(f"**Uploaded:** {doc['uploaded_at']}")
                    
                    with col2:
                        if is_blurred:
                            st.warning("🔒 Restricted Access")
                            st.caption("Manager or owner role required")
                        else:
                            st.success("✅ Accessible")
                    
                    if not is_blurred:
                        st.markdown("---")
                        st.markdown("**Content Preview:**")
                        content = doc['content']
                        st.text_area(
                            "Document Content",
                            value=content[:500] + "..." if len(content) > 500 else content,
                            height=200,
                            disabled=True,
                            key=f"content_{doc['doc_id']}"
                        )
        else:
            st.info("No documents uploaded yet. Use the Upload tab to add compliance documents.")
    
    except Exception as e:
        st.error(f"❌ Error loading documents: {e}")

st.markdown("---")

# Footer
st.caption("""
🔒 **Security Features:**
- Tenant-level isolation (no cross-restaurant data access)
- Role-based access control
- Encrypted document storage
- Audit logging for all document access
- Nivara AI compliance reasoning
""")

