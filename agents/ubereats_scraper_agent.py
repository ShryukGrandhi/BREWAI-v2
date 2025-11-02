"""
UberEats Scraper Agent - Extract real restaurant data from Uber Eats merchant dashboard.
"""
import os
import asyncio
from typing import Dict, Any, List
from datetime import datetime
import pandas as pd
from pathlib import Path


class UberEatsScraperAgent:
    """Agent to scrape real data from Uber Eats merchant dashboard."""
    
    def __init__(self, restaurant_id: str, trace_agent=None):
        self.restaurant_id = restaurant_id
        self.trace = trace_agent
        
        print(f"[INIT] UberEatsScraperAgent for restaurant: {restaurant_id}")
    
    async def run(self) -> Dict[str, Any]:
        """
        Scrape Uber Eats merchant dashboard for real data.
        
        Returns:
            Dict with orders, menu, reviews, revenue data
        """
        results = {
            "success": False,
            "artifacts": []
        }
        
        try:
            if self.trace:
                self.trace.log(
                    agent="UberEatsScraperAgent",
                    action="Initializing Uber Eats scraper",
                    metadata={"restaurant_id": self.restaurant_id}
                )
            
            # Initialize BrowserUse
            from services.browseruse_client import BrowserUseClient
            
            api_key = os.getenv("BROWSER_USE_API_KEY")
            gemini_key = os.getenv("GEMINI_API_KEY")
            
            if not api_key or not gemini_key:
                raise Exception("BrowserUse API keys not configured")
            
            browser = BrowserUseClient(api_key, gemini_key)
            
            # Task 1: Navigate to dashboard and extract orders
            if self.trace:
                self.trace.log(
                    agent="UberEatsScraperAgent",
                    action="Navigating to Uber Eats dashboard",
                    url=f"https://merchants.ubereats.com/manager/home/{self.restaurant_id}"
                )
            
            dashboard_task = f"""
STEP 1: Navigate to https://merchants.ubereats.com/manager/home/{self.restaurant_id}

STEP 2: Wait 5 seconds for page to fully load

STEP 3: Look for and extract these visible elements:
- Total orders today (usually in a metric card or header)
- Total revenue today (dollar amount)  
- Order status counts (completed, active, cancelled)

STEP 4: Scroll down to find recent orders table/list

STEP 5: For each visible order, extract:
- Order number/ID
- Time placed
- Items ordered
- Total amount
- Status

STEP 6: Click on "Orders" or "Order History" if available to see more details

STEP 7: Extract at least 20-30 recent orders with full details

STEP 8: Take a screenshot and save the extracted data
"""
            
            print("[BROWSER] Navigating to Uber Eats dashboard...")
            print(f"[URL] https://merchants.ubereats.com/manager/home/{self.restaurant_id}")
            
            dashboard_result = await browser.execute_task(dashboard_task, max_steps=25)
            
            if self.trace:
                self.trace.log(
                    agent="UberEatsScraperAgent",
                    action="Dashboard data extracted",
                    result=f"Extracted: {len(dashboard_result.get('history', []))} steps"
                )
            
            # Task 2: Navigate to orders page for detailed history
            orders_task = f"""
STEP 1: Look for "Orders" or "Order History" link in the navigation menu

STEP 2: Click it to go to the orders page

STEP 3: Wait for orders table to load

STEP 4: For each row in the orders table, extract:
- Order ID (usually starts with #)
- Date and timestamp
- Customer name (if visible)
- Items (full list with quantities)
- Subtotal
- Delivery fee
- Total amount
- Order status (completed/cancelled/refunded)
- Delivery method (delivery/pickup)

STEP 5: If there's a "Load More" or pagination, click to see more orders

STEP 6: Extract at least 30 orders total

STEP 7: Export or copy the data in structured format
"""
            
            print("[BROWSER] Navigating to Orders section...")
            
            orders_result = await browser.execute_task(orders_task, max_steps=30)
            
            if self.trace:
                self.trace.log(
                    agent="UberEatsScraperAgent",
                    action="Order history extracted",
                    result="Detailed orders retrieved"
                )
            
            # Task 3: Extract menu data
            menu_task = f"""
STEP 1: Find and click "Menu" or "Items" in the navigation

STEP 2: Wait for menu items to load

STEP 3: For each menu item visible, extract:
- Item name
- Price
- Description
- Category (burger, sides, drinks, etc.)
- Status (available/unavailable)
- Image URL if available

STEP 4: If menu is paginated or categorized, navigate through all sections:
- Burgers
- Sides
- Drinks  
- Combos
- Etc.

STEP 5: Extract complete menu with all items

STEP 6: Note which items are your best sellers (if that data is visible)
"""
            
            print("[BROWSER] Navigating to Menu section...")
            
            menu_result = await browser.execute_task(menu_task, max_steps=25)
            
            if self.trace:
                self.trace.log(
                    agent="UberEatsScraperAgent",
                    action="Menu data extracted",
                    result="Menu items retrieved"
                )
            
            # Task 4: Extract reviews/ratings
            reviews_task = f"""
STEP 1: Find and click "Reviews", "Ratings", or "Feedback" in navigation

STEP 2: Wait for reviews to load

STEP 3: For each review, extract:
- Star rating (1-5 stars)
- Review text/comment
- Date posted
- Items ordered (if mentioned)
- Your response (if any)
- Thumbs up/down if available

STEP 4: Scroll to load more reviews

STEP 5: Extract at least 15-20 recent reviews

STEP 6: Note overall rating average if displayed
"""
            
            print("[BROWSER] Navigating to Reviews section...")
            
            reviews_result = await browser.execute_task(reviews_task, max_steps=25)
            
            if self.trace:
                self.trace.log(
                    agent="UberEatsScraperAgent",
                    action="Reviews extracted",
                    result="Customer reviews retrieved"
                )
            
            # Process and structure the data
            structured_data = self._process_scraped_data(
                dashboard_result,
                orders_result,
                menu_result,
                reviews_result
            )
            
            # Save to CSV files
            self._save_to_csv(structured_data)
            
            results["success"] = True
            results["data"] = structured_data
            results["artifacts"].extend([
                "data/orders_realtime.csv",
                "data/customer_reviews.csv",
                "data/menu_items.csv"
            ])
            
            if self.trace:
                self.trace.log(
                    agent="UberEatsScraperAgent",
                    action="Data extraction complete",
                    result=f"Saved {len(structured_data.get('orders', []))} orders, {len(structured_data.get('reviews', []))} reviews",
                    artifacts=results["artifacts"]
                )
            
            return results
            
        except Exception as e:
            error_msg = str(e)
            
            if self.trace:
                self.trace.log(
                    agent="UberEatsScraperAgent",
                    action="Error during scraping",
                    result=f"Error: {error_msg[:200]}"
                )
            
            print(f"[ERROR] UberEatsScraperAgent: {error_msg}")
            
            results["success"] = False
            results["error"] = error_msg
            
            return results
    
    def _process_scraped_data(
        self,
        dashboard_result: Dict,
        orders_result: Dict,
        menu_result: Dict,
        reviews_result: Dict
    ) -> Dict[str, Any]:
        """Process raw scraped data into structured format."""
        
        # This is a placeholder - actual processing would parse BrowserUse results
        # For now, we'll extract from the action history
        
        structured = {
            "orders": [],
            "menu": [],
            "reviews": [],
            "summary": {}
        }
        
        # Parse dashboard summary
        dashboard_history = dashboard_result.get('history', [])
        for action in dashboard_history:
            if 'extracted' in action.get('result', {}).get('extracted_content', '').lower():
                # Would parse actual data here
                pass
        
        # Parse orders
        orders_history = orders_result.get('history', [])
        # Would extract order data from browser interactions
        
        # Parse menu
        menu_history = menu_result.get('history', [])
        # Would extract menu data
        
        # Parse reviews
        reviews_history = reviews_result.get('history', [])
        # Would extract review data
        
        return structured
    
    def _save_to_csv(self, data: Dict[str, Any]):
        """Save structured data to CSV files."""
        
        # Save orders
        if data.get('orders'):
            orders_df = pd.DataFrame(data['orders'])
            orders_df.to_csv('data/orders_realtime.csv', index=False)
            print(f"[OK] Saved {len(orders_df)} orders to data/orders_realtime.csv")
        
        # Save menu
        if data.get('menu'):
            menu_df = pd.DataFrame(data['menu'])
            menu_df.to_csv('data/menu_items.csv', index=False)
            print(f"[OK] Saved {len(menu_df)} menu items to data/menu_items.csv")
        
        # Save reviews
        if data.get('reviews'):
            reviews_df = pd.DataFrame(data['reviews'])
            reviews_df.to_csv('data/customer_reviews.csv', index=False)
            print(f"[OK] Saved {len(reviews_df)} reviews to data/customer_reviews.csv")


async def run_ubereats_scraper(restaurant_id: str) -> Dict[str, Any]:
    """Convenience function to run Uber Eats scraper."""
    from agents.trace_agent import TraceAgent
    
    trace = TraceAgent()
    agent = UberEatsScraperAgent(restaurant_id, trace)
    
    return await agent.run()

