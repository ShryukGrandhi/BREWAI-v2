@echo off
cd /d "%~dp0"

echo.
echo ========================================
echo   IMPORT REAL UBER EATS DATA
echo ========================================
echo.
echo This will replace all demo data with
echo your actual Uber Eats restaurant data!
echo.
echo Press any key to start...
pause >nul

call venv\Scripts\activate.ps1
python scripts/import_real_ubereats_data.py

echo.
echo ========================================
echo   IMPORT COMPLETE!
echo ========================================
echo.
echo Refresh Streamlit to see your real data:
echo http://localhost:8501
echo.
pause

