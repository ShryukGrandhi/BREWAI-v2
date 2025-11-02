"""
Voice-First Chatbot - Simplified for voice conversation
"""
import streamlit as st
import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Voice Chat", page_icon="🎤", layout="wide")

# Initialize
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'waiting_for_voice' not in st.session_state:
    st.session_state.waiting_for_voice = False

st.title("🎤 Voice Conversation with Brew.AI")
st.caption("Speak naturally - I'll respond with voice!")

# Voice interface
st.markdown("""
<div style="text-align: center; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; margin: 20px 0;">
    <h2 style="color: white; margin: 0;">Click below and start speaking</h2>
    <p style="color: #e0e7ff; margin: 10px 0;">Ask about orders, revenue, staffing, or operations</p>
</div>
""", unsafe_allow_html=True)

# Big voice button
if st.button("🎤 START VOICE CONVERSATION", use_container_width=True, type="primary"):
    st.session_state.waiting_for_voice = True

if st.session_state.waiting_for_voice:
    # Voice input/output component
    st.components.v1.html("""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                background-color: #0e1117;
                color: white;
                font-family: Arial, sans-serif;
                padding: 20px;
                text-align: center;
            }
            .voice-circle {
                width: 200px;
                height: 200px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 50%;
                margin: 20px auto;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 80px;
                cursor: pointer;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7); }
                50% { transform: scale(1.05); box-shadow: 0 0 0 20px rgba(102, 126, 234, 0); }
            }
            .status {
                font-size: 24px;
                margin: 20px;
                color: #4A90E2;
            }
            .transcript {
                background-color: #1e2127;
                padding: 20px;
                border-radius: 12px;
                margin: 20px 0;
                min-height: 60px;
                font-size: 18px;
            }
        </style>
    </head>
    <body>
        <div class="voice-circle" onclick="toggleVoice()" id="voiceBtn">🎤</div>
        <div class="status" id="status">Click to speak</div>
        <div class="transcript" id="transcript">Your question will appear here...</div>
        <div class="transcript" id="response">Captain's response will appear here...</div>
        
        <script>
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        const synthesis = window.speechSynthesis;
        
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        
        let isListening = false;
        
        function toggleVoice() {
            if (!isListening) {
                startListening();
            } else {
                recognition.stop();
            }
        }
        
        function startListening() {
            recognition.start();
            isListening = true;
            document.getElementById('status').textContent = '🎤 Listening...';
            document.getElementById('voiceBtn').style.animation = 'pulse 1s infinite';
        }
        
        recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript = transcript;
                } else {
                    interimTranscript = transcript;
                }
            }
            
            if (interimTranscript) {
                document.getElementById('transcript').textContent = '🎤 ' + interimTranscript;
            }
            
            if (finalTranscript) {
                document.getElementById('transcript').textContent = '✅ You: ' + finalTranscript;
                document.getElementById('status').textContent = '🤔 Thinking...';
                
                // Call Captain API
                getCaptainResponse(finalTranscript);
            }
        };
        
        recognition.onerror = (event) => {
            console.error('Error:', event.error);
            document.getElementById('status').textContent = '❌ Error: ' + event.error;
            isListening = false;
        };
        
        recognition.onend = () => {
            isListening = false;
            document.getElementById('voiceBtn').style.animation = '';
        };
        
        async function getCaptainResponse(userQuestion) {
            try {
                // Call your backend to get Captain response
                // For now, simulate with a delay
                await new Promise(resolve => setTimeout(resolve, 1500));
                
                // Simulated response (in production, this comes from Captain via your backend)
                const response = "Based on the data, your forecast shows peak at 6 PM with 42 orders.";
                
                document.getElementById('response').textContent = '🤖 Captain: ' + response;
                document.getElementById('status').textContent = '🔊 Speaking...';
                
                // Speak the response
                speakText(response);
                
            } catch (error) {
                console.error('Captain error:', error);
                document.getElementById('status').textContent = '❌ Error getting response';
            }
        }
        
        function speakText(text) {
            // Cancel any ongoing speech
            synthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;
            
            // Get voices
            const voices = synthesis.getVoices();
            const preferredVoice = voices.find(voice => 
                voice.name.includes('Google') || 
                voice.name.includes('Microsoft') ||
                (voice.lang.includes('en-US') && voice.name.includes('Female'))
            );
            
            if (preferredVoice) {
                utterance.voice = preferredVoice;
            }
            
            utterance.onend = () => {
                document.getElementById('status').textContent = '✅ Ready - Click to speak again';
            };
            
            synthesis.speak(utterance);
        }
        
        // Auto-start on load
        setTimeout(() => {
            startListening();
        }, 500);
        </script>
    </body>
    </html>
    """, height=600)
