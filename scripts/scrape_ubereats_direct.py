"""
Direct Playwright scraper for Uber Eats - No external APIs needed!

This will open Chrome with your logged-in session and extract data.
"""
import sys
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent))


async def scrape_ubereats():
    """Scrape Uber Eats merchant dashboard."""
    
    print("="*60)
    print("  UBER EATS DIRECT SCRAPER (Playwright)")
    print("="*60)
    print()
    
    restaurant_id = "57965626-1c94-5aa5-868d-c847cb861236"
    dashboard_url = f"https://merchants.ubereats.com/manager/home/{restaurant_id}"
    
    print(f"[*] Restaurant ID: {restaurant_id}")
    print(f"[*] URL: {dashboard_url}")
    print()
    print("[*] Opening Chrome with your logged-in session...")
    print("   This will use your existing Uber Eats login")
    print()
    
    async with async_playwright() as p:
        try:
            # Launch browser with your Chrome profile
            user_data_dir = r"C:\Users\shryu\AppData\Local\Google\Chrome\User Data"
            
            print(f"[CHROME] Using profile: {user_data_dir}")
            
            browser = await p.chromium.launch_persistent_context(
                user_data_dir,
                headless=False,
                channel="chrome",
                args=['--profile-directory=Default']
            )
            
            page = await browser.new_page()
            
            print("[NAVIGATE] Going to Uber Eats dashboard...")
            await page.goto(dashboard_url, wait_until='networkidle', timeout=30000)
            
            print("[WAIT] Waiting for page to load...")
            await asyncio.sleep(5)
            
            # Take screenshot
            await page.screenshot(path='artifacts/ubereats_dashboard.png')
            print("[OK] Screenshot saved: artifacts/ubereats_dashboard.png")
            
            # Extract visible text content
            print("[EXTRACT] Getting page content...")
            
            # Get all text content
            body_text = await page.inner_text('body')
            
            # Save raw HTML
            html_content = await page.content()
            with open('artifacts/ubereats_dashboard.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("[OK] HTML saved: artifacts/ubereats_dashboard.html")
            
            # Try to find specific elements
            print("[SEARCH] Looking for orders data...")
            
            # Look for order cards or tables
            orders_data = []
            try:
                # This is a placeholder - actual selectors depend on Uber Eats structure
                order_elements = await page.query_selector_all('[data-testid*="order"], .order-card, [class*="OrderCard"]')
                print(f"[FOUND] {len(order_elements)} potential order elements")
                
                for elem in order_elements[:10]:  # Get first 10
                    text = await elem.inner_text()
                    orders_data.append(text)
            
            except Exception as e:
                print(f"[WARN] Could not find order elements: {e}")
            
            # Look for metrics
            print("[SEARCH] Looking for metrics...")
            metrics = {}
            
            try:
                # Try common metric selectors
                metric_elements = await page.query_selector_all('[class*="metric"], [class*="stat"], [data-testid*="metric"]')
                print(f"[FOUND] {len(metric_elements)} potential metric elements")
                
                for elem in metric_elements[:5]:
                    text = await elem.inner_text()
                    print(f"   Metric: {text[:50]}")
            
            except Exception as e:
                print(f"[WARN] Could not find metrics: {e}")
            
            print()
            print("[INFO] Page inspection complete!")
            print("   Screenshot: artifacts/ubereats_dashboard.png")
            print("   HTML: artifacts/ubereats_dashboard.html")
            print()
            print("[NEXT] Manual extraction needed:")
            print("   1. Check the screenshot to see your dashboard")
            print("   2. Open the HTML file to inspect elements")
            print("   3. Or manually enter data using the import tool")
            print()
            
            await browser.close()
            
            print("="*60)
            print("  DONE - Check artifacts/ for captured data")
            print("="*60)
            
        except Exception as e:
            print()
            print(f"[ERROR] Scraping failed: {e}")
            print()
            print("[TIP] Make sure you're logged into Uber Eats!")
            print("   1. Open Chrome manually")
            print("   2. Go to merchants.ubereats.com")
            print("   3. Log in")
            print("   4. Run this script again")
            print()


if __name__ == "__main__":
    asyncio.run(scrape_ubereats())

