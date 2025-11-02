"""
Captain AI Chatbot Page
"""
import streamlit as st
import sys
import os
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="wide")

# Initialize chat history
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "Hi, Welcome to Brew.AI! Ask questions about your restaurant data."}
    ]

st.title("🤖 Brew.AI Assistant")
st.caption("Powered by Captain RAG - Ask anything about your operations")

# Chat interface
chat_container = st.container()

with chat_container:
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about orders, revenue, staffing, or anything..."):
    # Add user message
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get Captain response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                from services.captain_client import get_captain_client
                
                captain = get_captain_client()
                
                # Build context from current state
                context_data = f"""
Current Status:
- Date: {st.session_state.get('simulation_date', datetime.now()).strftime('%Y-%m-%d')}
- Orders Today: {st.session_state.get('current_orders', 30)}
- Revenue: ${st.session_state.get('current_revenue', 1000)}

Restaurant: Burger Queen
Location: New York City

Available Data:
- Historical orders
- Weather forecasts
- LSTM predictions
- Sentiment analysis
- Staffing schedules
"""
                
                # Load knowledge base if available
                kb_context = ""
                kb_files = [
                    "data/tenant_demo/menu.md",
                    "data/tenant_demo/ops.md",
                    "data/tenant_demo/prep.md",
                    "data/tenant_demo/weather_rules.md"
                ]
                
                for filepath in kb_files:
                    if os.path.exists(filepath):
                        with open(filepath, 'r', encoding='utf-8') as f:
                            kb_context += f"\n\n=== {os.path.basename(filepath)} ===\n{f.read()}"
                
                full_context = context_data + kb_context
                
                response = captain.client.chat.completions.create(
                    model="captain-voyager-latest",
                    messages=[
                        {"role": "system", "content": "You are Brew.AI, an intelligent restaurant operations assistant. Answer questions concisely using the provided context. Be helpful and specific."},
                        {"role": "user", "content": prompt}
                    ],
                    extra_body={
                        "captain": {
                            "context": full_context
                        }
                    },
                    stream=True
                )
                
                # Stream response
                response_placeholder = st.empty()
                full_response = ""
                
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        response_placeholder.markdown(full_response + "▌")
                
                response_placeholder.markdown(full_response)
                
                # Save to history
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": full_response
                })
                
            except Exception as e:
                error_msg = f"I'm having trouble right now. Error: {str(e)[:200]}"
                st.error(error_msg)
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# Suggested questions
st.markdown("---")
st.markdown("### 💡 Suggested Questions:")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 What's today's forecast?"):
        st.session_state.chat_messages.append({"role": "user", "content": "What's today's forecast?"})
        st.rerun()

with col2:
    if st.button("👥 Do we need more staff?"):
        st.session_state.chat_messages.append({"role": "user", "content": "Do we need more staff?"})
        st.rerun()

with col3:
    if st.button("💰 How can we increase revenue?"):
        st.session_state.chat_messages.append({"role": "user", "content": "How can we increase revenue?"})
        st.rerun()

# Clear chat button
if st.button("🗑️ Clear Chat History"):
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "Hi, Welcome to Brew.AI! Ask questions about your restaurant data."}
    ]
    st.rerun()

