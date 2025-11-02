# 🍺 Brew.AI - Multi-Agent Restaurant Operations Platform

A fully automated restaurant operations system powered by **BrowserUse**, **Gemini AI**, and **8 specialized agents** that work together to optimize staffing, inventory, and expansion planning.

## 🎯 What It Does

Brew.AI orchestrates 8 intelligent agents that perform **visible browser automation** using your signed-in Chrome profile:

1. **ScraperAgent** 🔍 - Scrapes Google Maps & Yelp reviews with BrowserUse
2. **WeatherAgent** 🌤️ - Fetches tomorrow's weather forecast
3. **ForecastAgent** 📈 - Predicts order volume using XGBoost with weather features
4. **StaffingAgent** 👥 - Creates Asana tasks for staff scheduling
5. **PrepAgent** 📦 - Generates purchase orders and fills supplier forms
6. **AnalystAgent** 🤖 - Provides RAG-based insights with citations
7. **GeoAgent** 🗺️ - Analyzes expansion opportunities with ROI scoring
8. **TraceAgent** 📋 - Logs every action with full transparency

**All agents emit step-by-step traces and perform visible actions in Chrome!**

## 🚀 Quick Start

### Prerequisites

- Windows 10/11
- Python 3.9+
- Google Chrome installed
- Active Chrome profile (signed in to Google/Asana/etc.)

### Step 1: Clone & Setup

```powershell
cd "C:\Users\shryu\Downloads\Hackathons\BrewAI v2"

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for BrowserUse)
playwright install chromium
```

### Step 2: Configure Environment

1. **Find your Chrome profile path:**
   - Open Chrome and go to `chrome://version/`
   - Look for "Profile Path"
   - Example: `C:\Users\shryu\AppData\Local\Google\Chrome\User Data\Default`
   - Split into:
     - `CHROME_USER_DATA_DIR`: Everything before the last folder
     - `CHROME_PROFILE_DIR`: The last folder name (e.g., "Default")

2. **Edit `.env` file** (already created with your API keys):
   ```env
   BROWSER_USE_API_KEY=bu_zlGdp05P86sdd6H2lTFHE43rpLbXRHMXKbXGE53hIQU
   GOOGLE_PLACES_API_KEY=AIzaSyAvUEtgR9OodyikazbFVrP_wD7sIhNfkDI
   GEMINI_API_KEY=AIzaSyCcw2F4nOy-5kkSSEdpfsK4LuDWcepspCY
   
   # Update these with your Chrome profile:
   CHROME_USER_DATA_DIR=C:\Users\shryu\AppData\Local\Google\Chrome\User Data
   CHROME_PROFILE_DIR=Default
   ```

### Step 3: Run the Demo

```powershell
# Make sure virtual environment is active
.\venv\Scripts\Activate.ps1

# Run Streamlit
streamlit run app/streamlit_app.py
```

The app will open at `http://localhost:8501`

### Step 4: Execute Workflow

1. Click **"▶️ Plan Tomorrow"** in the sidebar
2. Watch as each agent performs visible actions in Chrome
3. View results in the tabbed panels:
   - 📈 Forecast: Order volume predictions
   - 👥 Staffing: Asana task board
   - 📦 Prep: Supplier purchase orders
   - 🤖 Analyst: RAG Q&A with citations
   - 🗺️ Expansion: Interactive map with ROI scores
   - 📋 Trace: Full action log

## 📂 Project Structure

```
BrewAI v2/
├── app/
│   └── streamlit_app.py          # Main Streamlit UI
├── agents/
│   ├── scraper_agent.py          # Google Maps/Yelp scraper
│   ├── weather_agent.py          # Weather forecast
│   ├── forecast_agent.py         # ML order prediction
│   ├── staffing_agent.py         # Asana task creation
│   ├── prep_agent.py             # Purchase orders
│   ├── analyst_agent.py          # RAG Q&A
│   ├── geo_agent.py              # Expansion analysis
│   └── trace_agent.py            # Action logging
├── services/
│   ├── browseruse_client.py      # BrowserUse wrapper
│   ├── weather.py                # Weather API client
│   └── rag_store.py              # Vector store (Chroma/Pinecone)
├── data/
│   ├── orders.csv                # Historical orders (generated if missing)
│   └── tenant_demo/              # Knowledge base
│       ├── menu.md
│       ├── prep.md
│       ├── ops.md
│       └── weather_rules.md
├── artifacts/                    # Generated artifacts
│   ├── scraped_gmaps.html
│   ├── reviews.json
│   ├── weather_features.csv
│   ├── forecast_plot.png
│   ├── asana_tasks_screenshot.png
│   ├── supplier_po_filled.png
│   ├── expansion_map.html
│   ├── analyst_answer.json
│   └── trace.json
├── requirements.txt
├── .env                          # Environment variables
└── README.md
```

## 🔧 Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BROWSER_USE_API_KEY` | BrowserUse API key | `bu_xxx...` |
| `GOOGLE_PLACES_API_KEY` | Google Places API key | `AIza...` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |
| `CHROME_USER_DATA_DIR` | Chrome profile directory | `C:\Users\...\Chrome\User Data` |
| `CHROME_PROFILE_DIR` | Chrome profile name | `Default` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TENANT_ID` | Tenant identifier | `charcoal_eats_us` |
| `AUTO_CLICK_PLAN` | Auto-click "Plan" button | `true` |
| `AUTO_SUBMIT_SUPPLIER` | Auto-submit supplier forms | `false` |
| `USE_PINECONE` | Use Pinecone vs Chroma | `false` |
| `YELP_API_KEY` | Yelp API for reviews | (optional) |
| `METORIAL_PROJECT_ID` | Metorial monitoring | (optional) |

## 🎬 Demo Scenario

**Tenant:** Charcoal Eats US (NYC wing restaurant)  
**Goal:** Plan operations for tomorrow based on weather and demand

### Workflow Steps:

1. **Scrape 40-60 reviews** from Google Maps (visible in Chrome)
2. **Fetch weather forecast** for NYC (Open-Meteo API)
3. **Predict order volume** for tomorrow 10 AM - 10 PM using XGBoost
4. **Calculate staffing needs**: 1 cook per 25 orders/hour
5. **Create Asana tasks** for shifts (visible in your Asana account)
6. **Generate PO** for chicken wings with rain buffer
7. **Fill supplier form** (demo portal, not submitted unless flag set)
8. **Answer**: "Why add a cook tomorrow?" with 4 citations from knowledge base
9. **Analyze San Francisco** expansion with 10 locations and ROI scores
10. **Save trace.json** with all actions and timestamps

### Expected Outputs:

- ✅ 50+ reviews scraped and saved
- ✅ Tomorrow's weather features (precip, temp, rain hours)
- ✅ Hourly forecast with peak hour identified
- ✅ Asana project with staffing tasks
- ✅ Purchase order for wings (with rain buffer if needed)
- ✅ RAG answer with clickable citations
- ✅ Interactive map of SF locations
- ✅ Complete trace log downloadable as JSON

## 🛠️ Troubleshooting

### BrowserUse Issues

**Problem:** "Chrome profile not found"  
**Solution:** Verify `CHROME_USER_DATA_DIR` path exists and profile folder is correct

**Problem:** "Browser won't open"  
**Solution:** Close all Chrome instances and try again. BrowserUse needs exclusive access.

### API Issues

**Problem:** "Google Places API error"  
**Solution:** Enable Places API in Google Cloud Console and verify API key

**Problem:** "Gemini rate limit"  
**Solution:** Wait a few minutes or upgrade to paid tier

### Dependencies

**Problem:** "Module not found"  
**Solution:** 
```powershell
pip install -r requirements.txt
playwright install
```

**Problem:** "XGBoost import error"  
**Solution:** Falls back to rolling average baseline automatically

## 📊 Architecture

```
┌─────────────────────────────────────────────────┐
│          Streamlit UI (Dark Theme)              │
│     Progress Stepper + Multi-Tab Panels         │
└─────────────────────┬───────────────────────────┘
                      │
         ┌────────────┴────────────┐
         │   Orchestration Layer    │
         └────────────┬────────────┘
                      │
      ┌───────────────┼───────────────┐
      │               │               │
┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
│ BrowserUse │  │  Gemini   │  │  Weather  │
│  Client   │  │    LLM    │  │    API    │
└───────────┘  └───────────┘  └───────────┘
      │               │               │
┌─────▼───────────────▼───────────────▼─────┐
│         8 Specialized Agents               │
│  Scraper │ Weather │ Forecast │ Staffing  │
│    Prep │ Analyst │   Geo   │   Trace     │
└────────────────────┬───────────────────────┘
                     │
      ┌──────────────┼──────────────┐
      │              │              │
┌─────▼─────┐  ┌────▼────┐  ┌─────▼─────┐
│  Chroma   │  │  Asana  │  │  Google   │
│   RAG     │  │  Tasks  │  │   Maps    │
└───────────┘  └─────────┘  └───────────┘
```

## 🌟 Key Features

### 1. Visible Browser Automation
- Uses your **signed-in Chrome profile**
- All actions visible in real Chrome windows
- Interacts with Asana, Google Maps, supplier portals

### 2. Weather-Aware Forecasting
- Integrates Open-Meteo forecast with historical orders
- Applies **15% rain buffer** to inventory
- XGBoost model with time + weather features

### 3. Multi-Tenant RAG
- Namespace isolation per tenant (`brew_charcoal_eats_us`)
- Ingests menus, prep guides, ops manuals, reviews
- Citations include source documents with URLs
- Clickable citations open source tabs via BrowserUse

### 4. ROI-Based Expansion
- Analyzes 10 SF locations with Google Places
- Scores: traffic (40%) + income (30%) + competition (30%)
- Interactive Folium map with clickable pins
- Each pin opens Google Maps location

### 5. Full Transparency
- Every agent action logged to `trace.json`
- Timestamps, results, artifacts tracked
- Optional Metorial integration for monitoring
- Downloadable trace for audit trails

## 🎓 Technologies Used

- **BrowserUse** - AI-powered browser automation
- **Gemini 1.5 Pro** - LLM for reasoning and analysis
- **Streamlit** - Interactive web UI
- **XGBoost** - Order volume forecasting
- **Chroma/Pinecone** - Vector database for RAG
- **LangChain** - RAG framework
- **Google Places API** - Location data
- **Open-Meteo** - Weather forecasts
- **Folium** - Interactive maps
- **Playwright** - Browser automation foundation

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

This is a hackathon demo project. Feel free to fork and extend!

## 🔗 Resources

- [BrowserUse Docs](https://docs.browser-use.com)
- [Gemini API](https://ai.google.dev)
- [Streamlit Docs](https://docs.streamlit.io)

---

**Built with ❤️ for Brew.AI Hackathon v2**

