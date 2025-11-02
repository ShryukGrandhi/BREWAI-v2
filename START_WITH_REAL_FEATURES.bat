@echo off
echo.
echo ========================================
echo  🚀 Brew.AI - REAL Features Edition
echo ========================================
echo.
echo ✅ Real Browser Automation (BrowserUse)
echo ✅ Vector Embeddings (ChromaDB)
echo ✅ Semantic RAG (LangChain + Gemini)
echo.
echo ⚠️  IMPORTANT: Close ALL Chrome windows first!
echo.
echo Press any key to start...
pause >nul

cd /d "%~dp0"
call venv\Scripts\activate.bat

echo.
echo Starting Streamlit with REAL features...
echo Browser will open at http://localhost:8501
echo.

streamlit run app/streamlit_app.py

pause

