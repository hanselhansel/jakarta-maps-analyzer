#!/usr/bin/env python3
"""
Automated demo runner - no user input required
"""

import os
import sys
import subprocess
import pandas as pd
from datetime import datetime

print("🐾 Pet Wellness Market Analysis - Automated Demo")
print("=" * 60)

# Check API key
if not os.getenv('GOOGLE_MAPS_API_KEY'):
    from dotenv import load_dotenv
    load_dotenv()

# Create demo files
print("\n📋 Setting up demo analysis...")
print("   Area: Kemang (5km radius)")
print("   Searches: 4 key categories")

# Demo zone - Kemang only
demo_zones = pd.DataFrame([{
    'zone_name': 'Kemang_Demo',
    'latitude': -6.2600,
    'longitude': 106.8130,
    'radius': 5000
}])

# Demo queries - one from each category
demo_queries = pd.DataFrame([
    {'keyword': 'klinik hewan', 'category': 'Competitor', 'sub_category': 'Clinic_General'},
    {'keyword': 'pet grooming', 'category': 'Competitor', 'sub_category': 'Grooming_Only'},
    {'keyword': 'Ranch Market', 'category': 'Affluence_Proxy', 'sub_category': 'Premium_Supermarket'},
    {'keyword': 'pet cafe', 'category': 'Lifestyle_Proxy', 'sub_category': 'Pet_Cafe'},
])

# Backup existing files
for file in ['search_zones.csv', 'queries_comprehensive.csv']:
    if os.path.exists(file):
        os.rename(file, f"{file}.original")

# Save demo files
demo_zones.to_csv('search_zones.csv', index=False)
demo_queries.to_csv('queries_comprehensive.csv', index=False)

print("\n🚀 Starting demo analysis...")
print("   This will take about 2-3 minutes")
print("   Estimated cost: ~$0.50")
print("\n" + "-" * 60)

# Run the analysis
try:
    result = subprocess.run(
        [sys.executable, 'main_comprehensive.py'],
        capture_output=False,
        text=True
    )
    
    if result.returncode == 0:
        print("\n✅ Demo completed successfully!")
        
        # Find output file
        import glob
        csv_files = glob.glob('jakarta_pet_market_analysis_*.csv')
        if csv_files:
            latest_file = max(csv_files)
            
            # Read and show summary
            df = pd.read_csv(latest_file)
            print(f"\n📊 Results Summary:")
            print(f"   File: {latest_file}")
            print(f"   Total locations: {len(df)}")
            
            if not df.empty:
                print("\n📍 Sample Results:")
                # Show a few examples from each category
                for category in df['category'].unique():
                    cat_df = df[df['category'] == category]
                    print(f"\n   {category} ({len(cat_df)} found):")
                    for _, row in cat_df.head(2).iterrows():
                        print(f"   - {row['name']}")
                        if row.get('rating'):
                            print(f"     Rating: {row['rating']} ({row.get('review_count', 0)} reviews)")
            
            print(f"\n💡 Next Steps:")
            print(f"   1. Open QGIS")
            print(f"   2. Add Delimited Text Layer → {latest_file}")
            print(f"   3. X field: longitude, Y field: latitude")
            print(f"   4. Create heat maps by category!")
            
except Exception as e:
    print(f"\n❌ Error: {e}")

finally:
    # Restore original files
    for file in ['search_zones.csv', 'queries_comprehensive.csv']:
        if os.path.exists(f"{file}.original"):
            if os.path.exists(file):
                os.remove(file)
            os.rename(f"{file}.original", file)

print("\n🎯 Demo complete! Ready for full analysis when you are.")