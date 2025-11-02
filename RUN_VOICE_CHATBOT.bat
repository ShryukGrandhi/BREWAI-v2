@echo off
echo.
echo ========================================
echo  🎤 Brew.AI - Voice Chatbot
echo ========================================
echo.
echo Features:
echo  - Speech-to-Text (STT) - Speak your questions
echo  - Text-to-Speech (TTS) - Hear responses
echo  - Captain RAG - Intelligent answers
echo  - Voice conversation loop
echo.
echo Instructions:
echo  1. Navigate to Chatbot page
echo  2. Enable "Voice Input" toggle
echo  3. Enable "Auto-Speak Responses"
echo  4. Click "Press to Speak"
echo  5. Ask your question
echo  6. Hear Captain's response!
echo.
echo Opening at http://localhost:8501
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat
streamlit run app/Home.py

pause

