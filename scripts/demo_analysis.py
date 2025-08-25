#!/usr/bin/env python3
"""
Demo script showing how the comprehensive analysis works
Tests with a small subset to verify functionality
"""

import os
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

# Create a small test zone (Kemang area only)
test_zones = pd.DataFrame([{
    'zone_name': 'Kemang_Test',
    'latitude': -6.2600,
    'longitude': 106.8130,
    'radius': 5000
}])
test_zones.to_csv('test_zones.csv', index=False)

# Create limited test queries (just a few key searches)
test_queries = pd.DataFrame([
    {'keyword': 'klinik hewan', 'category': 'Competitor', 'sub_category': 'Clinic_General'},
    {'keyword': 'pet grooming', 'category': 'Competitor', 'sub_category': 'Grooming_Only'},
    {'keyword': 'Ranch Market', 'category': 'Affluence_Proxy', 'sub_category': 'Premium_Supermarket'},
    {'keyword': 'pet cafe', 'category': 'Lifestyle_Proxy', 'sub_category': 'Pet_Cafe'},
])
test_queries.to_csv('test_queries.csv', index=False)

print("📊 Demo Analysis Configuration")
print("=" * 40)
print("Zone: Kemang area (5km radius)")
print("Queries: 4 strategic searches")
print("\nThis demo will:")
print("1. Find pet clinics in Kemang")
print("2. Identify Ranch Market locations")
print("3. Locate pet cafes")
print("4. Estimate market opportunity")
print("\nEstimated cost: ~$0.50")
print("Estimated time: ~2 minutes")

# Show the searches that will be performed
print("\n🔍 Searches to be performed:")
for _, query in test_queries.iterrows():
    print(f"- {query['keyword']} ({query['sub_category']})")

print("\n✅ Demo files created!")
print("\nTo run the demo:")
print("1. Temporarily rename test files:")
print("   mv test_zones.csv search_zones.csv")
print("   mv test_queries.csv queries_comprehensive.csv")
print("2. Run: python3 main_comprehensive.py")
print("3. Check the output CSV for results!")
print("\nThe output will show you exactly what data you'll get for QGIS analysis.")