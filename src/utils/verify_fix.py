#!/usr/bin/env python3
"""
Quick verification script to test that the types field fix is working
"""

import os
import subprocess
import pandas as pd
from datetime import datetime

print("🔍 Verifying Bug Fix - Types Field Test")
print("=" * 50)

# Check for API key
from dotenv import load_dotenv
load_dotenv()

if not os.getenv('GOOGLE_MAPS_API_KEY'):
    print("❌ Error: Please set GOOGLE_MAPS_API_KEY in .env file")
    exit(1)

# Create minimal test data
print("\n1️⃣ Creating test configuration...")

# Single zone - small area
test_zones = pd.DataFrame([{
    'zone_name': 'Fix_Test',
    'latitude': -6.2600,
    'longitude': 106.8130,
    'radius': 3000  # Small radius
}])

# Just 2 queries to test both scenarios
test_queries = pd.DataFrame([
    {'keyword': 'Ranch Market', 'category': 'Affluence_Proxy', 'sub_category': 'Premium_Supermarket'},
    {'keyword': 'klinik hewan', 'category': 'Competitor', 'sub_category': 'Clinic_General'},
])

# Backup existing files
for f in ['search_zones.csv', 'queries_comprehensive.csv']:
    if os.path.exists(f):
        os.rename(f, f"{f}.verify_backup")

# Save test files
test_zones.to_csv('search_zones.csv', index=False)
test_queries.to_csv('queries_comprehensive.csv', index=False)

print("✅ Test configuration created")
print("   - Zone: Small area in Kemang (3km)")
print("   - Queries: 2 (Ranch Market + klinik hewan)")

# Run the fixed scraper
print("\n2️⃣ Running scraper with bug fixes...")
try:
    result = subprocess.run(
        [os.sys.executable, 'main_comprehensive.py'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Scraper failed: {result.stderr}")
        exit(1)
        
except Exception as e:
    print(f"❌ Error running scraper: {e}")
    exit(1)

# Find and analyze output
print("\n3️⃣ Analyzing results...")
import glob
csv_files = glob.glob('jakarta_pet_market_analysis_*.csv')
if not csv_files:
    print("❌ No output file found")
    exit(1)

latest_file = max(csv_files)
df = pd.read_csv(latest_file)

print(f"\n✅ Output file created: {latest_file}")
print(f"   Total records: {len(df)}")

# Check if types column has data
print("\n4️⃣ Verifying 'types' column...")
types_populated = df['types'].notna().sum()
types_empty = df['types'].isna().sum()

print(f"   Types populated: {types_populated} records")
print(f"   Types empty: {types_empty} records")

if types_populated > 0:
    print("\n✅ SUCCESS: Types field is now being populated!")
    
    # Show some examples
    print("\n📋 Sample types data:")
    for idx, row in df[df['types'].notna()].head(5).iterrows():
        print(f"   {row['name'][:50]}...")
        print(f"   → Types: {row['types']}")
        print()
    
    # Check for filtered results
    print("5️⃣ Checking data quality...")
    
    # Look for obvious irrelevant entries
    potential_junk = df[df['name'].str.contains('loading dock|parking|ATM', case=False, na=False)]
    
    if len(potential_junk) == 0:
        print("✅ No obvious irrelevant entries found (loading docks, parking, ATMs)")
    else:
        print(f"⚠️  Found {len(potential_junk)} potentially irrelevant entries")
        print("   These should have been filtered - checking types...")
        for _, row in potential_junk.iterrows():
            print(f"   - {row['name']} | Types: {row['types']}")
    
    # Summary by category
    print("\n📊 Results by category:")
    for cat in df['category'].unique():
        count = len(df[df['category'] == cat])
        print(f"   {cat}: {count}")
        
else:
    print("\n❌ FAIL: Types field is still empty!")
    print("   The bug fix may not have been applied correctly")

# Cleanup
print("\n6️⃣ Cleaning up test files...")
for f in ['search_zones.csv', 'queries_comprehensive.csv']:
    if os.path.exists(f):
        os.remove(f)
    if os.path.exists(f"{f}.verify_backup"):
        os.rename(f"{f}.verify_backup", f)

print("\n" + "=" * 50)
if types_populated > 0:
    print("🎉 Bug fix verified! The scraper is now working correctly.")
    print("   You can now run the full analysis with confidence.")
else:
    print("❌ Bug fix verification failed. Please check the code.")

# Save verification report
with open('bug_fix_verification.txt', 'w') as f:
    f.write(f"Bug Fix Verification Report\n")
    f.write(f"Date: {datetime.now()}\n")
    f.write(f"Output file: {latest_file}\n")
    f.write(f"Total records: {len(df)}\n")
    f.write(f"Types populated: {types_populated}\n")
    f.write(f"Types empty: {types_empty}\n")
    f.write(f"Status: {'PASS' if types_populated > 0 else 'FAIL'}\n")

print(f"\n📄 Verification report saved to: bug_fix_verification.txt")