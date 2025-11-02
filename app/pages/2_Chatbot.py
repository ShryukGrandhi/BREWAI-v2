"""
Captain AI Chatbot Page with Voice Integration (Coval STT/TTS)
"""
import streamlit as st
import sys
import os
from pathlib import Path
from datetime import datetime
import json
import base64

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

from services.voice_agent import get_voice_agent

st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="wide")

# Custom CSS for voice controls
st.markdown("""
<style>
    .voice-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 30px;
        border-radius: 50px;
        border: none;
        font-size: 18px;
        font-weight: bold;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    .voice-btn:hover {
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    .listening {
        animation: pulse 1.5s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "Hi, Welcome to Brew.AI! Ask questions about your restaurant data. You can type or use voice!"}
    ]
if 'voice_enabled' not in st.session_state:
    st.session_state.voice_enabled = True
if 'auto_speak' not in st.session_state:
    st.session_state.auto_speak = True
if 'last_spoken' not in st.session_state:
    st.session_state.last_spoken = None

# Get voice agent
voice_agent = get_voice_agent()

st.title("🤖 Brew.AI Voice Assistant")
st.caption("🎤 Powered by Captain RAG + Coval Voice | Speak or Type")

# Voice controls
col1, col2, col3 = st.columns([1, 1, 3])

with col1:
    voice_enabled = st.toggle("🎤 Voice Input", value=st.session_state.voice_enabled)
    st.session_state.voice_enabled = voice_enabled

with col2:
    auto_speak = st.toggle("🔊 Auto-Speak Responses", value=st.session_state.auto_speak)
    st.session_state.auto_speak = auto_speak

# Voice input button (if enabled)
if st.session_state.voice_enabled:
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🎤 Press to Speak", use_container_width=True, type="primary"):
            st.session_state.listening = True
            st.info("🎤 Listening... Speak now!")
            
            # Inject Web Speech API
            st.components.v1.html("""
            <div style="text-align: center; padding: 20px;">
                <button onclick="startVoiceInput()" class="voice-btn listening">
                    🎤 Listening... Speak now!
                </button>
                <p id="transcript" style="color: white; margin-top: 20px;"></p>
            </div>
            
            <script>
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            
            function startVoiceInput() {
                recognition.start();
                console.log('Voice recognition started');
            }
            
            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                document.getElementById('transcript').textContent = 'You said: ' + transcript;
                
                // Auto-submit after 1 second of silence
                if (event.results[0].isFinal) {
                    setTimeout(() => {
                        // Set the value in Streamlit's text input
                        const textInput = window.parent.document.querySelector('input[type="text"]');
                        if (textInput) {
                            textInput.value = transcript;
                            textInput.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    }, 500);
                }
            };
            
            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                document.getElementById('transcript').textContent = 'Error: ' + event.error;
            };
            
            recognition.onend = () => {
                console.log('Voice recognition ended');
            };
            
            // Auto-start
            startVoiceInput();
            </script>
            """, height=150)

st.markdown("---")

# Chat interface
chat_container = st.container()

with chat_container:
    for i, message in enumerate(st.session_state.chat_messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Add "Speak" button for assistant messages
            if message["role"] == "assistant" and st.session_state.voice_enabled:
                if st.button(f"🔊 Speak", key=f"speak_{i}"):
                    # Trigger TTS for this message
                    st.session_state.speak_message = message["content"]
                    st.rerun()

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
                
                # Auto-speak response if enabled
                if st.session_state.auto_speak:
                    st.session_state.speak_message = full_response
                    st.rerun()
                
            except Exception as e:
                error_msg = f"I'm having trouble right now. Error: {str(e)[:200]}"
                st.error(error_msg)
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# Text-to-Speech Output (if triggered)
if 'speak_message' in st.session_state and st.session_state.speak_message:
    message_to_speak = st.session_state.speak_message
    st.session_state.speak_message = None  # Clear
    
    # Use Web Speech API for TTS
    tts_code = voice_agent.text_to_speech_web(message_to_speak)
    st.components.v1.html(f"""
    <div style="text-align: center; padding: 10px; background-color: #1e2127; border-radius: 8px;">
        <p style="color: #10B981; margin: 0;">🔊 Speaking response...</p>
    </div>
    {tts_code}
    """, height=60)

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

