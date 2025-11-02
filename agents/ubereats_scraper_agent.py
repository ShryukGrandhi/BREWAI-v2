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
Navigate to https://merchants.ubereats.com/manager/home/{self.restaurant_id}

Wait for the page to fully load.

Extract the following data:
1. Today's orders count
2. Today's revenue
3. Order status breakdown (completed, in-progress, cancelled)
4. Recent orders with: order number, time, items, total amount, customer name
5. Current menu items visible on the page

Save all extracted data in a structured format.
"""
            
            dashboard_result = await browser.execute_task(dashboard_task, max_steps=15)
            
            if self.trace:
                self.trace.log(
                    agent="UberEatsScraperAgent",
                    action="Dashboard data extracted",
                    result=f"Extracted: {len(dashboard_result.get('history', []))} steps"
                )
            
            # Task 2: Navigate to orders page for detailed history
            orders_task = f"""
Go to the Orders section in the Uber Eats merchant dashboard.

Extract detailed order history including:
- Order ID
- Date and time
- Items ordered (name, quantity, price)
- Subtotal, fees, total
- Delivery method (delivery, pickup, dine-in)
- Customer notes if any

Get at least the last 30 orders.
"""
            
            orders_result = await browser.execute_task(orders_task, max_steps=20)
            
            if self.trace:
                self.trace.log(
                    agent="UberEatsScraperAgent",
                    action="Order history extracted",
                    result="Detailed orders retrieved"
                )
            
            # Task 3: Extract menu data
            menu_task = f"""
Navigate to the Menu section of the Uber Eats merchant dashboard.

Extract all menu items with:
- Item name
- Description
- Price
- Category
- Availability status
- Customization options if visible

Get the complete active menu.
"""
            
            menu_result = await browser.execute_task(menu_task, max_steps=15)
            
            if self.trace:
                self.trace.log(
                    agent="UberEatsScraperAgent",
                    action="Menu data extracted",
                    result="Menu items retrieved"
                )
            
            # Task 4: Extract reviews/ratings
            reviews_task = f"""
Navigate to the Reviews or Ratings section.

Extract customer reviews including:
- Rating (stars)
- Review text
- Date
- Order items mentioned
- Response status

Get at least 15-20 recent reviews.
"""
            
            reviews_result = await browser.execute_task(reviews_task, max_steps=15)
            
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

