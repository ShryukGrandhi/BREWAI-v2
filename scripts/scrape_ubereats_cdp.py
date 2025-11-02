"""
Uber Eats Scraper using Chrome DevTools Protocol.
Connects to your RUNNING Chrome instance to extract data.
"""
import sys
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime
import json
import re

sys.path.insert(0, str(Path(__file__).parent.parent))


async def find_chrome_cdp_url():
    """Find the CDP URL of running Chrome instance."""
    import requests
    
    # Chrome DevTools Protocol typically runs on port 9222
    possible_ports = [9222, 9223, 9224]
    
    for port in possible_ports:
        try:
            response = requests.get(f'http://localhost:{port}/json/version', timeout=2)
            if response.status_code == 200:
                data = response.json()
                ws_url = data.get('webSocketDebuggerUrl')
                if ws_url:
                    print(f"[OK] Found Chrome CDP on port {port}")
                    return ws_url
        except:
            continue
    
    return None


async def scrape_with_cdp():
    """Scrape using CDP connection to running Chrome."""
    
    print("="*60)
    print("  UBER EATS CDP SCRAPER")
    print("="*60)
    print()
    
    restaurant_id = "57965626-1c94-5aa5-868d-c847cb861236"
    dashboard_url = f"https://merchants.ubereats.com/manager/home/{restaurant_id}"
    
    print("[*] Attempting to connect to running Chrome...")
    print("[*] Make sure Chrome is open with Uber Eats logged in!")
    print()
    
    # Find CDP URL
    cdp_url = await find_chrome_cdp_url()
    
    if not cdp_url:
        print("[WARN] Could not connect to Chrome via CDP")
        print()
        print("[INFO] To enable CDP, restart Chrome with:")
        print('   chrome.exe --remote-debugging-port=9222')
        print()
        print("[ALT] Opening new browser instance...")
        await scrape_with_new_browser(dashboard_url)
        return
    
    # Connect to Chrome
    async with async_playwright() as p:
        try:
            print(f"[OK] Connecting to Chrome: {cdp_url}")
            
            browser = await p.chromium.connect_over_cdp(cdp_url)
            contexts = browser.contexts
            
            if not contexts:
                print("[ERROR] No browser contexts found")
                return
            
            context = contexts[0]
            
            # Create new tab or use existing
            page = await context.new_page()
            
            print(f"[NAVIGATE] Going to: {dashboard_url}")
            await page.goto(dashboard_url, wait_until='load', timeout=30000)
            
            print("[WAIT] Loading dashboard...")
            await asyncio.sleep(5)
            
            # Extract data
            await extract_dashboard_data(page)
            
            await page.close()
            
        except Exception as e:
            print(f"[ERROR] CDP scraping failed: {e}")
            print()
            print("[FALLBACK] Trying with new browser...")
            await scrape_with_new_browser(dashboard_url)


async def scrape_with_new_browser(url):
    """Scrape with a fresh browser instance (will need manual login)."""
    
    print()
    print("[INFO] Opening fresh browser - you may need to log in")
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print(f"[NAVIGATE] Going to: {url}")
        await page.goto(url, wait_until='load', timeout=30000)
        
        print()
        print("[MANUAL] Please log in to Uber Eats if needed...")
        print("   Waiting 30 seconds for you to log in...")
        print()
        
        await asyncio.sleep(30)
        
        # Extract data
        await extract_dashboard_data(page)
        
        print()
        input("Press Enter to close browser...")
        
        await browser.close()


async def extract_dashboard_data(page):
    """Extract data from dashboard page."""
    
    print("[EXTRACT] Analyzing page...")
    
    # Take screenshot
    await page.screenshot(path='artifacts/ubereats_dashboard.png', full_page=True)
    print("[OK] Screenshot: artifacts/ubereats_dashboard.png")
    
    # Get page HTML
    html = await page.content()
    with open('artifacts/ubereats_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("[OK] HTML: artifacts/ubereats_dashboard.html")
    
    # Get all visible text
    body_text = await page.inner_text('body')
    
    # Try to find orders in the text
    print()
    print("[PARSE] Looking for data patterns...")
    
    # Find dollar amounts
    dollars = re.findall(r'\$[\d,]+\.?\d*', body_text)
    if dollars:
        print(f"[FOUND] {len(dollars)} dollar amounts: {dollars[:5]}")
    
    # Find order IDs (common patterns)
    order_ids = re.findall(r'#?\b[A-Z0-9]{6,12}\b', body_text)
    if order_ids:
        print(f"[FOUND] {len(set(order_ids))} potential order IDs: {list(set(order_ids))[:5]}")
    
    # Find times
    times = re.findall(r'\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)', body_text)
    if times:
        print(f"[FOUND] {len(times)} timestamps: {times[:5]}")
    
    # Save extracted data
    extracted_data = {
        "raw_text": body_text,
        "dollars": dollars,
        "order_ids": list(set(order_ids)),
        "times": times,
        "extracted_at": datetime.now().isoformat()
    }
    
    with open('artifacts/ubereats_extracted_data.json', 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=2, ensure_ascii=False)
    
    print("[OK] Extracted data: artifacts/ubereats_extracted_data.json")
    
    # Try to find specific UI elements
    print()
    print("[SEARCH] Looking for specific elements...")
    
    try:
        # Common Uber Eats selectors (these may need adjustment)
        selectors_to_try = [
            'h1, h2, h3',  # Headers
            '[class*="order"]',  # Order elements
            '[class*="metric"]',  # Metrics
            '[data-testid]',  # Test IDs
            'table',  # Tables
        ]
        
        for selector in selectors_to_try:
            elements = await page.query_selector_all(selector)
            if elements:
                print(f"[FOUND] {len(elements)} elements matching: {selector}")
                
                # Get text from first few
                for elem in elements[:3]:
                    try:
                        text = await elem.inner_text()
                        if text and len(text) < 100:
                            print(f"   -> {text[:80]}")
                    except:
                        pass
    
    except Exception as e:
        print(f"[WARN] Element search error: {e}")
    
    print()
    print("="*60)
    print("  EXTRACTION COMPLETE")
    print("="*60)
    print()
    print("[FILES] Check these files for captured data:")
    print("   - artifacts/ubereats_dashboard.png")
    print("   - artifacts/ubereats_dashboard.html")
    print("   - artifacts/ubereats_extracted_data.json")
    print()
    print("[NEXT] Use the captured data to:")
    print("   1. Review screenshot to see what's visible")
    print("   2. Check HTML for element structure")
    print("   3. Use extracted JSON for patterns")
    print("   4. Or manually enter key data into CSV files")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(scrape_with_cdp())
    except KeyboardInterrupt:
        print()
        print("[STOPPED] Scraping cancelled by user")
    except Exception as e:
        print()
        print(f"[ERROR] {e}")

