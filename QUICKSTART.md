# 🚀 Quick Start Guide

## Run the Demo (Simplified)

1. **Double-click** `run_app.bat` 
   - OR run in PowerShell: `.\run_app.bat`

2. Browser will open at `http://localhost:8501`

3. Click **"▶️ Plan Tomorrow"** in the sidebar

4. Watch the agents work through all 8 steps!

## What You'll See

### ✅ Working Without Full Dependencies

The app is designed to run even without all packages installed:

- **BrowserUse**: Falls back to mock implementation that simulates browser actions
- **ChromaDB/LangChain**: Uses simple in-memory storage
- **XGBoost**: Included and working for ML forecasting

### 📊 Demo Flow (2-3 minutes)

1. **Scraper Agent** → Mock-scrapes 45 Google Maps reviews
2. **Weather Agent** → Fetches real weather from Open-Meteo  
3. **Forecast Agent** → Predicts orders with XGBoost
4. **Staffing Agent** → Calculates cook requirements
5. **Prep Agent** → Creates purchase order with rain buffer
6. **Analyst Agent** → Answers "Why add a cook?" with citations
7. **Geo Agent** → Analyzes 10 SF locations with ROI scores
8. **Trace Agent** → Logs everything to trace.json

### 🎯 Key Outputs

- `artifacts/forecast_plot.png` - Tomorrow's order curve
- `artifacts/asana_tasks_screenshot.png` - Mock Asana board
- `artifacts/expansion_map.html` - Interactive SF map
- `artifacts/trace.json` - Full audit trail

## Install Full Dependencies (Optional)

For real browser automation:

```powershell
.\venv\Scripts\Activate.ps1
pip install browser-use chromadb langchain-community
playwright install chromium
```

Then restart the app!

## Environment Setup

The `.env` file is already configured with your API keys:
- ✅ BROWSER_USE_API_KEY
- ✅ GOOGLE_PLACES_API_KEY  
- ✅ GEMINI_API_KEY

Update `CHROME_USER_DATA_DIR` and `CHROME_PROFILE_DIR` for real browser automation.

## Troubleshooting

**Port already in use?**
```powershell
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

**Package errors?**
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

**Can't find venv?**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

**Need help?** Check the full README.md for detailed documentation.

