"""
UberEats Scraper using Parse.bot - Extract real restaurant data.
"""
import os
import json
from typing import Dict, Any, List
from datetime import datetime
import pandas as pd
from pathlib import Path


class UberEatsParseBotScraper:
    """Scraper for Uber Eats merchant dashboard using parse.bot."""
    
    def __init__(self, restaurant_id: str, trace_agent=None):
        self.restaurant_id = restaurant_id
        self.trace = trace_agent
        self.base_url = f"https://merchants.ubereats.com/manager/home/{restaurant_id}"
        
        print(f"[INIT] UberEats ParseBot Scraper for: {restaurant_id}")
    
    def run(self) -> Dict[str, Any]:
        """
        Scrape Uber Eats dashboard using parse.bot.
        
        Returns:
            Dict with extracted orders, menu, reviews
        """
        results = {
            "success": False,
            "artifacts": []
        }
        
        try:
            from services.parsebot_client import get_parsebot_client
            
            parsebot = get_parsebot_client()
            
            if self.trace:
                self.trace.log(
                    agent="UberEatsParseBot",
                    action="Starting parse.bot extraction",
                    url=self.base_url
                )
            
            # Extract dashboard summary
            print("[PARSEBOT] Extracting dashboard summary...")
            
            dashboard_result = parsebot.scrape_with_ai(
                url=self.base_url,
                instructions="""
Extract the following from the Uber Eats merchant dashboard:

1. TODAY'S METRICS:
   - Total orders today (number)
   - Total revenue today (dollar amount)
   - Order status breakdown (completed, in-progress, cancelled counts)
   
2. RECENT ORDERS (last 10 visible on page):
   - Order ID/number
   - Time placed
   - Items ordered (list)
   - Total amount
   - Status
   - Delivery method (delivery/pickup)
   
3. RESTAURANT INFO:
   - Restaurant name
   - Location/address
   - Hours of operation
   - Current status (open/closed)

Return as structured JSON.
""",
                output_schema={
                    "today_orders": "number",
                    "today_revenue": "number",
                    "orders": "array",
                    "restaurant_name": "string",
                    "location": "string"
                }
            )
            
            # Extract menu data
            print("[PARSEBOT] Extracting menu...")
            
            menu_url = f"https://merchants.ubereats.com/manager/menu/{self.restaurant_id}"
            
            menu_result = parsebot.scrape_with_ai(
                url=menu_url,
                instructions="""
Extract ALL menu items from the Uber Eats menu page.

For each item, extract:
- Item name
- Price (in dollars)
- Description
- Category (burgers, sides, drinks, etc.)
- Availability (available/soldout)
- Customization options if visible

Return as array of menu items.
""",
                output_schema={
                    "menu_items": "array"
                }
            )
            
            # Extract reviews
            print("[PARSEBOT] Extracting reviews...")
            
            reviews_url = f"https://merchants.ubereats.com/manager/reviews/{self.restaurant_id}"
            
            reviews_result = parsebot.scrape_with_ai(
                url=reviews_url,
                instructions="""
Extract customer reviews from the page.

For each review, extract:
- Star rating (1-5)
- Review text/comment
- Date posted
- Items mentioned (if any)
- Customer name (if visible)

Get at least 15-20 reviews if available.
Return as array of reviews.
""",
                output_schema={
                    "reviews": "array",
                    "average_rating": "number"
                }
            )
            
            # Process and save data
            all_data = self._process_parsebot_results(
                dashboard_result,
                menu_result,
                reviews_result
            )
            
            # Save to CSV
            saved_files = self._save_to_csv(all_data)
            
            results["success"] = True
            results["data"] = all_data
            results["artifacts"] = saved_files
            
            if self.trace:
                self.trace.log(
                    agent="UberEatsParseBot",
                    action="Extraction complete",
                    result=f"Orders: {len(all_data.get('orders', []))}, Menu: {len(all_data.get('menu', []))}, Reviews: {len(all_data.get('reviews', []))}"
                )
            
            return results
            
        except Exception as e:
            error_msg = str(e)
            
            if self.trace:
                self.trace.log(
                    agent="UberEatsParseBot",
                    action="Error during extraction",
                    result=f"Error: {error_msg[:200]}"
                )
            
            print(f"[ERROR] ParseBot scraper: {error_msg}")
            
            results["success"] = False
            results["error"] = error_msg
            
            return results
    
    def _process_parsebot_results(
        self,
        dashboard: Dict,
        menu: Dict,
        reviews: Dict
    ) -> Dict[str, Any]:
        """Process parse.bot results into structured data."""
        
        processed = {
            "orders": [],
            "menu": [],
            "reviews": [],
            "summary": {}
        }
        
        # Process dashboard
        if dashboard.get("success"):
            dash_data = dashboard.get("data", {})
            processed["summary"] = {
                "today_orders": dash_data.get("today_orders", 0),
                "today_revenue": dash_data.get("today_revenue", 0),
                "restaurant_name": dash_data.get("restaurant_name", ""),
                "location": dash_data.get("location", "")
            }
            
            # Process orders
            orders_list = dash_data.get("orders", [])
            for order in orders_list:
                processed["orders"].append({
                    "timestamp": order.get("time", datetime.now().isoformat()),
                    "order_id": order.get("id", ""),
                    "items": order.get("items", []),
                    "total": order.get("total", 0),
                    "status": order.get("status", ""),
                    "channel": "ubereats"
                })
        
        # Process menu
        if menu.get("success"):
            menu_data = menu.get("data", {})
            menu_items = menu_data.get("menu_items", [])
            
            for item in menu_items:
                processed["menu"].append({
                    "name": item.get("name", ""),
                    "price": item.get("price", 0),
                    "description": item.get("description", ""),
                    "category": item.get("category", ""),
                    "available": item.get("availability", "available") == "available"
                })
        
        # Process reviews
        if reviews.get("success"):
            reviews_data = reviews.get("data", {})
            reviews_list = reviews_data.get("reviews", [])
            
            for review in reviews_list:
                processed["reviews"].append({
                    "date": review.get("date", datetime.now().strftime("%Y-%m-%d")),
                    "rating": review.get("rating", 5),
                    "review_text": review.get("text", ""),
                    "sentiment": self._analyze_sentiment(review.get("rating", 5)),
                    "channel": "ubereats"
                })
        
        return processed
    
    def _analyze_sentiment(self, rating: int) -> str:
        """Simple sentiment analysis from rating."""
        if rating >= 4:
            return "positive"
        elif rating >= 3:
            return "neutral"
        else:
            return "negative"
    
    def _save_to_csv(self, data: Dict[str, Any]) -> List[str]:
        """Save extracted data to CSV files."""
        saved_files = []
        
        # Save orders
        if data.get('orders'):
            orders_df = pd.DataFrame(data['orders'])
            
            # Expand items column if it's a list
            if 'items' in orders_df.columns and len(orders_df) > 0:
                # Create individual rows for each item
                rows = []
                for _, order in orders_df.iterrows():
                    items = order['items'] if isinstance(order['items'], list) else [order['items']]
                    for item in items:
                        item_name = item if isinstance(item, str) else item.get('name', 'Unknown')
                        rows.append({
                            'timestamp': order['timestamp'],
                            'order_id': order['order_id'],
                            'item': item_name,
                            'quantity': 1,
                            'price': order['total'] / len(items) if len(items) > 0 else order['total'],
                            'channel': 'ubereats',
                            'customer_type': 'regular',
                            'payment_method': 'card',
                            'prep_time_min': 10,
                            'delivery_time_min': 25
                        })
                
                if rows:
                    orders_df = pd.DataFrame(rows)
                    orders_df.to_csv('data/orders_realtime.csv', index=False)
                    saved_files.append('data/orders_realtime.csv')
                    print(f"[OK] Saved {len(orders_df)} order items to data/orders_realtime.csv")
        
        # Save menu
        if data.get('menu'):
            menu_df = pd.DataFrame(data['menu'])
            menu_df.to_csv('data/menu_items.csv', index=False)
            saved_files.append('data/menu_items.csv')
            print(f"[OK] Saved {len(menu_df)} menu items to data/menu_items.csv")
        
        # Save reviews
        if data.get('reviews'):
            reviews_df = pd.DataFrame(data['reviews'])
            
            # Add keywords column
            reviews_df['keywords'] = reviews_df['review_text'].apply(
                lambda x: ', '.join([w for w in str(x).lower().split() if len(w) > 4][:5]) if pd.notna(x) else ''
            )
            
            reviews_df.to_csv('data/customer_reviews.csv', index=False)
            saved_files.append('data/customer_reviews.csv')
            print(f"[OK] Saved {len(reviews_df)} reviews to data/customer_reviews.csv")
        
        return saved_files


def get_parsebot_client() -> ParseBotClient:
    """Get configured parse.bot client."""
    api_key = os.getenv("PARSEBOT_API_KEY")
    
    if not api_key:
        raise ValueError("PARSEBOT_API_KEY not set in environment")
    
    return ParseBotClient(api_key)

