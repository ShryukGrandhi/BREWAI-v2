"""
Import Uber Eats data using parse.bot.

Usage:
    python scripts/import_with_parsebot.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.ubereats_parsebot_scraper import UberEatsParseBotScraper
from agents.trace_agent import TraceAgent


def main():
    """Main import function."""
    print("="*60)
    print("  UBER EATS IMPORT - PARSE.BOT SCRAPER")
    print("="*60)
    print()
    
    # Your restaurant ID
    restaurant_id = "57965626-1c94-5aa5-868d-c847cb861236"
    
    print(f"[*] Restaurant ID: {restaurant_id}")
    print(f"[*] Using parse.bot for reliable extraction")
    print()
    
    try:
        trace = TraceAgent()
        scraper = UberEatsParseBotScraper(restaurant_id, trace)
        
        print("[*] Starting extraction...")
        print("   Step 1: Dashboard metrics")
        print("   Step 2: Menu items")
        print("   Step 3: Customer reviews")
        print()
        
        result = scraper.run()
        
        if result.get('success'):
            print()
            print("="*60)
            print("  [SUCCESS] Real data imported!")
            print("="*60)
            print()
            
            data = result.get('data', {})
            
            print("[DATA] Extracted:")
            print(f"   Orders: {len(data.get('orders', []))}")
            print(f"   Menu Items: {len(data.get('menu', []))}")
            print(f"   Reviews: {len(data.get('reviews', []))}")
            print()
            
            if data.get('summary'):
                summary = data['summary']
                print("[METRICS] Today:")
                print(f"   Orders: {summary.get('today_orders', 'N/A')}")
                print(f"   Revenue: ${summary.get('today_revenue', 0):,.2f}")
                print(f"   Restaurant: {summary.get('restaurant_name', 'N/A')}")
                print()
            
            print("[SAVE] Files updated:")
            for filepath in result.get('artifacts', []):
                print(f"   [OK] {filepath}")
            print()
            
            print("[NEXT] Steps:")
            print("   1. Refresh Streamlit: http://localhost:8501")
            print("   2. See YOUR actual restaurant data!")
            print("   3. All forecasts use YOUR real patterns!")
            print()
            
        else:
            print()
            print("[ERROR] Import failed:")
            print(f"   {result.get('error')}")
            print()
            print("[TIP] Troubleshooting:")
            print("   1. Check PARSEBOT_API_KEY in .env")
            print("   2. Verify restaurant ID is correct")
            print("   3. Make sure dashboard URL is accessible")
            print()
    
    except Exception as e:
        print()
        print(f"[EXCEPTION] {e}")
        print()
    
    print("="*60)


if __name__ == "__main__":
    main()

