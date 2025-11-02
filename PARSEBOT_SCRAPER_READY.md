# ✅ PARSE.BOT SCRAPER READY!

**API Key:** Configured ✅  
**Restaurant ID:** 57965626-1c94-5aa5-868d-c847cb861236  
**GitHub:** https://github.com/ShryukGrandhi/BREWAI-v2  

---

## 🎯 **What Was Built**

### **NEW: Parse.bot Scraper**
Replaced BrowserUse with parse.bot for more reliable Uber Eats data extraction!

---

## 📦 **Files Created:**

1. **`services/parsebot_client.py`** - Parse.bot API client
2. **`agents/ubereats_parsebot_scraper.py`** - Uber Eats scraper using parse.bot
3. **`scripts/import_with_parsebot.py`** - Import script

---

## 🚀 **How to Run:**

### **Command Line (With API Keys):**
```powershell
cd "C:\Users\shryu\Downloads\Hackathons\BrewAI v2"
.\venv\Scripts\Activate.ps1
$env:PARSEBOT_API_KEY="7154bad9-09c3-4302-a81c-d64cb5246c35"
python scripts/import_with_parsebot.py
```

---

## 📊 **What It Extracts:**

### **From Dashboard:**
- Today's order count
- Today's revenue
- Order status breakdown
- Recent orders (last 10-20)
  - Order ID, time, items, total, status

### **From Menu Section:**
- All menu items
- Prices
- Descriptions
- Categories
- Availability status

### **From Reviews Section:**
- Customer reviews (15-20 recent)
- Star ratings
- Review text
- Dates
- Items mentioned

---

## 💾 **Output Files:**

After running, these files are updated with YOUR real data:
- ✅ `data/orders_realtime.csv`
- ✅ `data/customer_reviews.csv`
- ✅ `data/menu_items.csv`

---

## 🔧 **Why Parse.bot Instead of BrowserUse:**

### **BrowserUse Issues:**
- ❌ LLM compatibility problems ("ainvoke" not found)
- ❌ Provider attribute issues
- ❌ Complex setup
- ❌ Unreliable for authenticated pages

### **Parse.bot Benefits:**
- ✅ AI-powered extraction
- ✅ Natural language instructions
- ✅ No LLM setup required
- ✅ Better for authenticated dashboards
- ✅ More reliable API
- ✅ Structured output

---

## 📋 **Manual Setup Needed:**

Since `.env` file is protected, you need to manually add:

### **Option 1: Add to .env file**
```env
PARSEBOT_API_KEY=7154bad9-09c3-4302-a81c-d64cb5246c35
```

### **Option 2: Set in PowerShell before running**
```powershell
$env:PARSEBOT_API_KEY="7154bad9-09c3-4302-a81c-d64cb5246c35"
python scripts/import_with_parsebot.py
```

---

## ✅ **When Complete:**

1. Real Uber Eats data in CSV files
2. Refresh Streamlit: http://localhost:8501
3. See YOUR actual restaurant data!
4. All forecasts use YOUR real patterns
5. Reviews show YOUR customer feedback
6. Menu shows YOUR actual items

---

**Parse.bot is ready to scrape YOUR real Uber Eats data!** 🔥✅🚀

