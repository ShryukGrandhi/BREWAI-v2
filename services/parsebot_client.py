"""
Parse.bot Client - Web scraping with AI-powered extraction.
"""
import os
import requests
import json
from typing import Dict, Any, Optional
import time


class ParseBotClient:
    """Client for parse.bot web scraping API."""
    
    BASE_URL = "https://api.parse.bot/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        print(f"[OK] Parse.bot client initialized")
    
    def scrape_page(
        self,
        url: str,
        extraction_schema: Dict[str, Any],
        wait_for: Optional[str] = None,
        timeout: int = 30000
    ) -> Dict[str, Any]:
        """
        Scrape a page using parse.bot.
        
        Args:
            url: URL to scrape
            extraction_schema: Schema defining what data to extract
            wait_for: CSS selector to wait for before extracting
            timeout: Timeout in milliseconds
            
        Returns:
            Dict with extracted data
        """
        try:
            payload = {
                "url": url,
                "extraction": extraction_schema,
                "timeout": timeout
            }
            
            if wait_for:
                payload["waitFor"] = wait_for
            
            print(f"[PARSEBOT] Scraping: {url}")
            
            response = requests.post(
                f"{self.BASE_URL}/scrape",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"[OK] Data extracted successfully")
                return {
                    "success": True,
                    "data": data.get("data", {}),
                    "raw": data
                }
            else:
                print(f"[ERROR] Parse.bot error: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        
        except Exception as e:
            print(f"[ERROR] Parse.bot request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def scrape_with_ai(
        self,
        url: str,
        instructions: str,
        output_schema: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Scrape using AI-powered extraction with natural language instructions.
        
        Args:
            url: URL to scrape
            instructions: Natural language description of what to extract
            output_schema: Optional JSON schema for output
            
        Returns:
            Dict with extracted data
        """
        try:
            payload = {
                "url": url,
                "instructions": instructions
            }
            
            if output_schema:
                payload["schema"] = output_schema
            
            print(f"[PARSEBOT-AI] Scraping with AI: {url}")
            print(f"[PARSEBOT-AI] Instructions: {instructions[:100]}...")
            
            response = requests.post(
                f"{self.BASE_URL}/ai-extract",
                headers=self.headers,
                json=payload,
                timeout=90
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"[OK] AI extraction complete")
                return {
                    "success": True,
                    "data": data.get("data", {}),
                    "raw": data
                }
            else:
                print(f"[ERROR] Parse.bot AI error: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        
        except Exception as e:
            print(f"[ERROR] Parse.bot AI request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


def get_parsebot_client() -> ParseBotClient:
    """Get configured parse.bot client."""
    api_key = os.getenv("PARSEBOT_API_KEY")
    
    if not api_key:
        raise ValueError("PARSEBOT_API_KEY not set in environment")
    
    return ParseBotClient(api_key)

