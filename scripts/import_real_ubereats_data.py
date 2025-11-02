"""
Import real Uber Eats data from merchant dashboard.

Usage:
    python scripts/import_real_ubereats_data.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.ubereats_scraper_agent import run_ubereats_scraper


async def main():
    """Main import function."""
    print("="*60)
    print("  UBER EATS DATA IMPORT - REAL RESTAURANT DATA")
    print("="*60)
    print()
    
    # Your restaurant ID from the URL
    restaurant_id = "57965626-1c94-5aa5-868d-c847cb861236"
    
    print(f"[*] Restaurant ID: {restaurant_id}")
    print()
    print("[*] Starting data extraction...")
    print("   This will:")
    print("   1. Navigate to your Uber Eats dashboard")
    print("   2. Extract orders, revenue, menu items")
    print("   3. Extract customer reviews and ratings")
    print("   4. Replace demo data with your real data")
    print()
    print("[*] This may take 2-3 minutes...")
    print()
    
    try:
        # Run the scraper
        result = await run_ubereats_scraper(restaurant_id)
        
        if result.get('success'):
            print()
            print("="*60)
            print("  [SUCCESS] Real data imported")
            print("="*60)
            print()
            
            data = result.get('data', {})
            
            print("[DATA] Summary:")
            print(f"   Orders: {len(data.get('orders', []))}")
            print(f"   Menu Items: {len(data.get('menu', []))}")
            print(f"   Reviews: {len(data.get('reviews', []))}")
            print()
            
            print("[SAVE] Files Updated:")
            for artifact in result.get('artifacts', []):
                print(f"   [OK] {artifact}")
            print()
            
            print("[NEXT] Steps:")
            print("   1. Refresh your Streamlit app: http://localhost:8501")
            print("   2. You'll now see YOUR actual restaurant data!")
            print("   3. All forecasts and analytics use real numbers")
            print()
            
        else:
            print()
            print("[ERROR] Import failed:")
            print(f"   {result.get('error')}")
            print()
            print("[TIP] Troubleshooting:")
            print("   1. Make sure you're logged into Uber Eats in Chrome")
            print("   2. Check that BROWSER_USE_API_KEY is set in .env")
            print("   3. Verify the restaurant ID is correct")
            print()
    
    except Exception as e:
        print()
        print(f"[EXCEPTION] {e}")
        print()
    
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())

