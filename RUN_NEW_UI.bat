@echo off
echo.
echo ========================================
echo  🍺 Brew.AI - Dashboard UI
echo ========================================
echo.
echo Features:
echo  - Real-time dashboard matching sketch
echo  - Current status + EOD predictions  
echo  - Hourly charts with "You are here"
echo  - Weekly staffing cards
echo  - Sentiment analysis
echo  - AI recommendations
echo  - Captain chatbot
echo.
echo Opening at http://localhost:8501
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat
streamlit run app/streamlit_app_ui.py

pause

