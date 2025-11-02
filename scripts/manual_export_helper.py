"""
Manual Export Helper - Generate template for manually exporting Uber Eats data.

If BrowserUse automation doesn't work, use this to manually export your data.
"""

print("="*60)
print("  MANUAL EXPORT HELPER")
print("="*60)
print()
print("If the automated scraper doesn't work, follow these steps:")
print()
print("STEP 1: Export Orders from Uber Eats")
print("---------------------------------------")
print("1. Go to: https://merchants.ubereats.com/manager/home/57965626-1c94-5aa5-868d-c847cb861236")
print("2. Click 'Orders' or 'Order History'")
print("3. Look for 'Export' or 'Download' button")
print("4. Export as CSV or Excel")
print("5. Save to: data/ubereats_orders_export.csv")
print()

print("STEP 2: Export Menu")
print("--------------------")
print("1. Click 'Menu' or 'Items'")
print("2. Look for 'Export Menu' or manually copy")
print("3. Save to: data/ubereats_menu_export.csv")
print()

print("STEP 3: Convert to Brew.AI Format")
print("-----------------------------------")
print("Run this script to convert:")
print("   python scripts/convert_ubereats_export.py")
print()

print("STEP 4: Or Manually Create CSV")
print("--------------------------------")
print("Create data/orders_realtime.csv with columns:")
print("   timestamp,order_id,item,quantity,price,channel,customer_type,payment_method")
print()
print("Create data/customer_reviews.csv with columns:")
print("   date,rating,review_text,sentiment,keywords,channel")
print()

print("="*60)
print()
print("TIP: If Uber Eats doesn't have export, you can:")
print("1. Manually enter last 10-20 orders")
print("2. Copy/paste from dashboard")
print("3. Use browser console to extract data")
print()
print("See: IMPORT_REAL_DATA_INSTRUCTIONS.md for more help")
print()

