# ⚠️ IMPORTANT: Add Nivara API Key to .env

## ✅ Fixed:
- ✅ pyvis installed in venv
- ✅ networkx installed in venv
- ✅ Streamlit restarted

## 🔴 Action Required:

### Add this line to your `.env` file:

```
NIVARA_API_KEY=ak_live_mvd53oex7zonxq3463xcaxfmii.blcuge5vfzt36jiug6eoafy3wkj57wxtwwv5t3y
```

### Location:
`C:\Users\shryu\Downloads\Hackathons\BrewAI v2\.env`

### Your .env should look like:
```env
BROWSER_USE_API_KEY=bu_zlGdp05P86sdd6H2lTFHE43rpLbXRHMXKbXGE53hIQU
GOOGLE_PLACES_API_KEY=AIzaSyAvUEtgR9OodyikazbFVrP_wD7sIhNfkDI
GEMINI_API_KEY=AIzaSyCcw2F4nOy-5kkSSEdpfsK4LuDWcepspCY
CHROME_USER_DATA_DIR=C:\Users\shryu\AppData\Local\Google\Chrome\User Data
CHROME_PROFILE_DIR=Default
TENANT_ID=charcoal_eats_us
CAPTAIN_ORG_ID=019a43c1-e932-d3e3-577b-ec35b74dea81
CAPTAIN_API_KEY=cap_dev_1l4tvPw0I4rbnxa4Plsz6Cu0tDH4k8ym
NIVARA_API_KEY=ak_live_mvd53oex7zonxq3463xcaxfmii.blcuge5vfzt36jiug6eoafy3wkj57wxtwwv5t3y
AUTO_CLICK_PLAN=true
AUTO_SUBMIT_SUPPLIER=false
USE_PINECONE=false
```

### Then:
1. Save the file
2. Refresh browser: http://localhost:8501
3. Knowledge Map and Compliance will work!

---

## What Was Fixed:

### 1. ModuleNotFoundError: No module named 'pyvis'
**Solution:** Installed pyvis in the venv
```bash
pip install pyvis networkx
```

### 2. NIVARA_API_KEY not set
**Solution:** You need to manually add it to `.env` (file was blocked from automatic edit)

---

## After Adding the Key:

**Knowledge Map will show:**
- Interactive force-directed graph
- Causality chains
- Nivara security badges on compliance nodes

**Compliance Agent will work:**
- Upload documents securely
- Query with Nivara AI
- Show security confirmations

---

**Add the key to .env and refresh!** 🔒✅

