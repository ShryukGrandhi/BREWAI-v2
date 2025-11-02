@echo off
echo ========================================
echo  🍺 Brew.AI - Starting Application
echo ========================================
echo.

cd /d "%~dp0"

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start Streamlit
echo Starting Streamlit on http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run app/streamlit_app.py

pause

