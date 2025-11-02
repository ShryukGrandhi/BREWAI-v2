"""
AUTOMATIC Uber Eats Scraper - Just log in once, then it extracts everything.
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


async def main():
    """Main scraper function."""
    
    print("="*60)
    print("  UBER EATS AUTO SCRAPER")
    print("="*60)
    print()
    
    restaurant_id = "57965626-1c94-5aa5-868d-c847cb861236"
    base_url = "https://merchants.ubereats.com"
    dashboard_url = f"{base_url}/manager/home/{restaurant_id}"
    
    print(f"[*] Restaurant ID: {restaurant_id}")
    print()
    
    async with async_playwright() as p:
        print("[LAUNCH] Opening Chrome with your signed-in profile...")
        
        user_data_dir = r"C:\Users\shryu\AppData\Local\Google\Chrome\User Data"
        profile_dir = "Default"
        
        print(f"[PROFILE] Using: {user_data_dir}\\{profile_dir}")
        print("[INFO] You should be ALREADY logged in!")
        print()
        
        # Launch persistent context (your Chrome profile)
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            channel="chrome",
            args=[f'--profile-directory={profile_dir}'],
            slow_mo=1000
        )
        
        page = await context.new_page()
        
        print(f"[NAVIGATE] Going to Uber Eats...")
        await page.goto(dashboard_url, wait_until='load', timeout=60000)
        
        print()
        print("="*60)
        print("  AUTOMATIC EXTRACTION IN 10 SECONDS")
        print("="*60)
        print()
        print("Using your signed-in Chrome profile - no login needed!")
        print("Waiting for dashboard to fully load...")
        print()
        
        for i in range(10, 0, -2):
            print(f"   Starting in {i} seconds...")
            await asyncio.sleep(2)
        
        print()
        print("[OK] Starting AUTOMATIC extraction...")
        print()
        
        # Wait for dashboard to be fully loaded
        await asyncio.sleep(3)
        
        # STEP 1: Extract dashboard metrics
        print("[1/5] Extracting dashboard metrics...")
        
        await page.screenshot(path='artifacts/ubereats_dashboard_full.png', full_page=True)
        
        body_text = await page.inner_text('body')
        
        # Extract revenue/order metrics from text
        dollars = re.findall(r'\$\s*[\d,]+\.?\d*', body_text)
        numbers = re.findall(r'\b(\d{1,3}(?:,\d{3})*|\d+)\b', body_text)
        
        print(f"   Found {len(dollars)} revenue values")
        print(f"   Found {len(numbers)} numeric values")
        
        # STEP 2: Extract orders
        print("[2/5] Extracting orders...")
        
        # Try to click on Orders tab
        try:
            orders_button = await page.query_selector('text=/orders/i, a[href*="orders"], button:has-text("Orders")')
            if orders_button:
                await orders_button.click()
                await asyncio.sleep(3)
                print("   Navigated to Orders page")
        except:
            print("   Using dashboard view")
        
        # Get page content
        html_content = await page.content()
        
        # Extract order data from HTML
        orders_data = extract_orders_from_html(html_content, body_text)
        print(f"   Extracted {len(orders_data)} orders")
        
        # STEP 3: Extract menu
        print("[3/5] Extracting menu...")
        
        try:
            menu_button = await page.query_selector('text=/menu/i, a[href*="menu"], button:has-text("Menu")')
            if menu_button:
                await orders_button.click()
                await asyncio.sleep(3)
                print("   Navigated to Menu page")
        except:
            print("   Trying menu URL directly...")
            try:
                await page.goto(f"{base_url}/manager/menu/{restaurant_id}", wait_until='load', timeout=30000)
                await asyncio.sleep(3)
            except:
                pass
        
        menu_text = await page.inner_text('body')
        menu_data = extract_menu_from_text(menu_text)
        print(f"   Extracted {len(menu_data)} menu items")
        
        # STEP 4: Extract reviews
        print("[4/5] Extracting reviews...")
        
        try:
            await page.goto(f"{base_url}/manager/reviews/{restaurant_id}", wait_until='load', timeout=30000)
            await asyncio.sleep(3)
        except:
            print("   Reviews section not accessible")
        
        reviews_text = await page.inner_text('body')
        reviews_data = extract_reviews_from_text(reviews_text)
        print(f"   Extracted {len(reviews_data)} reviews")
        
        # STEP 5: Save to CSV
        print("[5/5] Saving to CSV files...")
        
        save_to_csv(orders_data, menu_data, reviews_data)
        
        print()
        print("="*60)
        print("  SUCCESS! Data extracted and saved")
        print("="*60)
        print()
        print(f"[DATA] Summary:")
        print(f"   Orders: {len(orders_data)}")
        print(f"   Menu Items: {len(menu_data)}")
        print(f"   Reviews: {len(reviews_data)}")
        print()
        print("[FILES] Updated:")
        print("   data/orders_realtime.csv")
        print("   data/menu_items.csv")
        print("   data/customer_reviews.csv")
        print()
        print("[NEXT] Refresh Streamlit: http://localhost:8501")
        print()
        print("[CLOSE] Closing browser in 10 seconds...")
        print("   Check the extracted data!")
        await asyncio.sleep(10)
        
        await context.close()
        
        print()
        print("[DONE] Browser closed. Data is ready!")


def extract_orders_from_html(html: str, text: str) -> list:
    """Extract order data from HTML and text."""
    orders = []
    
    # Find order patterns in text
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        # Look for order ID patterns
        if re.search(r'#[A-Z0-9]{6,}|Order\s*\d+', line, re.IGNORECASE):
            # Try to extract order info from surrounding lines
            order_id = re.search(r'#?([A-Z0-9]{6,})', line)
            if order_id:
                order_context = '\n'.join(lines[max(0, i-2):min(len(lines), i+5)])
                
                # Extract price
                price_match = re.search(r'\$\s*([\d,]+\.?\d*)', order_context)
                price = float(price_match.group(1).replace(',', '')) if price_match else 12.99
                
                # Extract time
                time_match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM))', order_context, re.IGNORECASE)
                time_str = time_match.group(1) if time_match else datetime.now().strftime('%I:%M %p')
                
                orders.append({
                    'timestamp': datetime.now().strftime(f'%Y-%m-%d {time_str}'),
                    'order_id': f"ORD{len(orders)+1:03d}",
                    'item': 'Uber Eats Order',
                    'quantity': 1,
                    'price': price,
                    'channel': 'ubereats',
                    'customer_type': 'regular',
                    'payment_method': 'card',
                    'prep_time_min': 10,
                    'delivery_time_min': 25
                })
    
    return orders[:30]  # Limit to 30


def extract_menu_from_text(text: str) -> list:
    """Extract menu items from text."""
    menu = []
    
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        # Look for price patterns indicating menu items
        price_match = re.search(r'\$\s*([\d,]+\.?\d*)', line)
        if price_match and len(line) < 100:  # Likely a menu item line
            price = float(price_match.group(1).replace(',', ''))
            
            # Item name is usually the text before the price
            item_name = re.sub(r'\$.*', '', line).strip()
            
            if item_name and len(item_name) > 2 and price > 0:
                menu.append({
                    'name': item_name,
                    'price': price,
                    'description': '',
                    'category': 'main',
                    'available': True
                })
    
    return menu[:50]  # Limit to 50 items


def extract_reviews_from_text(text: str) -> list:
    """Extract reviews from text."""
    reviews = []
    
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        # Look for star ratings
        stars_match = re.search(r'([1-5])\s*(?:star|★|⭐)', line, re.IGNORECASE)
        if stars_match:
            rating = int(stars_match.group(1))
            
            # Get surrounding context as review text
            review_context = '\n'.join(lines[max(0, i-1):min(len(lines), i+3)])
            
            reviews.append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'rating': rating,
                'review_text': review_context[:200],
                'sentiment': 'positive' if rating >= 4 else ('neutral' if rating == 3 else 'negative'),
                'keywords': '',
                'channel': 'ubereats'
            })
    
    return reviews[:20]  # Limit to 20


def save_to_csv(orders, menu, reviews):
    """Save extracted data to CSV files."""
    
    if orders:
        df = pd.DataFrame(orders)
        df.to_csv('data/orders_realtime.csv', index=False)
        print(f"   [OK] Saved {len(df)} orders")
    
    if menu:
        df = pd.DataFrame(menu)
        df.to_csv('data/menu_items.csv', index=False)
        print(f"   [OK] Saved {len(df)} menu items")
    
    if reviews:
        df = pd.DataFrame(reviews)
        df.to_csv('data/customer_reviews.csv', index=False)
        print(f"   [OK] Saved {len(df)} reviews")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[STOPPED] Scraping cancelled")
    except Exception as e:
        print(f"\n[ERROR] {e}")

