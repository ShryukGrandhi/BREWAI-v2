"""
Mock BrowserUse client for demo purposes.
This version simulates browser automation without requiring the full browser-use package.
"""
import os
import asyncio
from typing import Dict, Any, List
import random


class BrowserUseClient:
    """Mock wrapper for BrowserUse agent."""
    
    def __init__(self, api_key: str, gemini_api_key: str):
        self.api_key = api_key
        self.gemini_api_key = gemini_api_key
        self.chrome_user_data_dir = os.getenv("CHROME_USER_DATA_DIR")
        self.chrome_profile_dir = os.getenv("CHROME_PROFILE_DIR", "Default")
    
    async def execute_task(self, task: str, max_steps: int = 50) -> Dict[str, Any]:
        """Mock execute a browser automation task."""
        await asyncio.sleep(1)  # Simulate work
        return {
            "success": True,
            "result": f"Mock: Completed task - {task[:100]}...",
            "history": [],
            "extracted_data": None
        }
    
    async def scrape_google_maps_reviews(
        self, 
        place_name: str, 
        place_address: str,
        num_reviews: int = 50
    ) -> Dict[str, Any]:
        """Mock scrape Google Maps reviews."""
        await asyncio.sleep(2)  # Simulate scraping
        
        # Generate mock reviews
        reviews = []
        for i in range(min(num_reviews, 45)):
            reviews.append({
                "name": f"Reviewer {i+1}",
                "rating": random.choice([3, 4, 4, 5, 5]),
                "text": random.choice([
                    "Great wings! Love the buffalo sauce.",
                    "Best chicken wings in NYC. Crispy and flavorful.",
                    "Good food, friendly service. Will come back.",
                    "Amazing garlic parmesan wings. Highly recommend!",
                    "Fast service and delicious wings. Great spot!",
                    "The Korean BBQ wings are incredible. Must try!",
                    "Solid wings, good prices. Perfect for game day.",
                    "Nice atmosphere and tasty wings. Would recommend."
                ]),
                "date": f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
            })
        
        return {
            "success": True,
            "result": f"Mock: Scraped {len(reviews)} reviews from Google Maps",
            "history": [
                {"action": "Opened Google Maps", "url": "https://maps.google.com"},
                {"action": "Searched for restaurant", "result": "Found"},
                {"action": "Clicked Reviews tab", "result": "Success"},
                {"action": f"Scraped {len(reviews)} reviews", "result": "Success"}
            ],
            "extracted_data": reviews
        }
    
    async def scrape_yelp_reviews(
        self, 
        business_name: str, 
        location: str,
        num_reviews: int = 30
    ) -> Dict[str, Any]:
        """Mock scrape Yelp reviews."""
        await asyncio.sleep(1.5)
        
        reviews = []
        for i in range(min(num_reviews, 20)):
            reviews.append({
                "name": f"Yelp User {i+1}",
                "rating": random.choice([4, 4, 5, 5]),
                "text": random.choice([
                    "Excellent wings and great service!",
                    "Best wings in the area. Crispy and delicious.",
                    "Love this place! Always consistent quality.",
                    "The Nashville hot wings are fire! 🔥"
                ]),
                "date": f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
            })
        
        return {
            "success": True,
            "result": f"Mock: Scraped {len(reviews)} reviews from Yelp",
            "history": [],
            "extracted_data": reviews
        }
    
    async def create_asana_tasks(
        self, 
        project_name: str,
        tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Mock create Asana project and tasks."""
        await asyncio.sleep(1.5)
        
        return {
            "success": True,
            "result": f"Mock: Created Asana project '{project_name}' with {len(tasks)} tasks",
            "history": [
                {"action": "Opened Asana", "url": "https://app.asana.com"},
                {"action": "Created project", "result": project_name},
                {"action": "Added sections", "result": "Staffing, Inventory Orders, Notes"},
                {"action": f"Created {len(tasks)} tasks", "result": "Success"}
            ],
            "project_url": "https://app.asana.com/mock-project"
        }
    
    async def fill_supplier_form(
        self,
        supplier_url: str,
        po_data: Dict[str, Any],
        submit: bool = False
    ) -> Dict[str, Any]:
        """Mock fill supplier form."""
        await asyncio.sleep(1)
        
        action = "filled and submitted" if submit else "filled (not submitted)"
        
        return {
            "success": True,
            "result": f"Mock: Supplier form {action}",
            "history": [
                {"action": "Opened supplier portal", "url": supplier_url},
                {"action": "Filled form fields", "result": "Success"},
                {"action": "Submitted" if submit else "Ready to submit", "result": "Success"}
            ]
        }
    
    async def analyze_web_content(self, url: str, analysis_prompt: str) -> Dict[str, Any]:
        """Mock analyze web content."""
        await asyncio.sleep(1)
        
        return {
            "success": True,
            "result": f"Mock: Analyzed content from {url}",
            "history": [],
            "extracted_data": "Mock analysis complete"
        }


def get_browseruse_client() -> BrowserUseClient:
    """Get mock BrowserUse client."""
    api_key = os.getenv("BROWSER_USE_API_KEY", "mock_key")
    gemini_api_key = os.getenv("GEMINI_API_KEY", "mock_key")
    
    return BrowserUseClient(api_key, gemini_api_key)

