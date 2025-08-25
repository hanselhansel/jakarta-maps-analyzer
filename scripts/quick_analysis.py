#!/usr/bin/env python3
"""
Quick targeted analysis script for specific areas or categories
Perfect for testing before running comprehensive analysis
"""

import os
import sys
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

def create_targeted_files(area=None, category=None):
    """Create targeted search files based on user selection."""
    
    # Define available options
    areas = {
        '1': ('South Jakarta - Kemang', -6.2600, 106.8130, 8000),
        '2': ('South Jakarta - Pondok Indah', -6.2840, 106.7810, 8000),
        '3': ('Central Jakarta', -6.2088, 106.8456, 10000),
        '4': ('PIK/North Jakarta', -6.1090, 106.7380, 8000),
        '5': ('BSD City', -6.3019, 106.6527, 10000),
        '6': ('Gading Serpong', -6.2351, 106.6289, 8000),
        '7': ('Custom Location', None, None, None)
    }
    
    categories = {
        '1': 'Competitors Only',
        '2': 'Affluence Indicators Only',
        '3': 'Pet Lifestyle Only',
        '4': 'Comprehensive (All)'
    }
    
    # Interactive selection if not provided
    if not area:
        print("\n📍 Select target area:")
        for key, value in areas.items():
            print(f"{key}. {value[0] if isinstance(value, tuple) else value}")
        area = input("\nEnter number (1-7): ").strip()
    
    if not category:
        print("\n📊 Select analysis type:")
        for key, value in categories.items():
            print(f"{key}. {value}")
        category = input("\nEnter number (1-4): ").strip()
    
    # Create targeted zones file
    if area in areas:
        if area == '7':
            # Custom location
            lat = float(input("Enter latitude: "))
            lon = float(input("Enter longitude: "))
            radius = int(input("Enter search radius in meters (e.g., 5000): "))
            zone_name = input("Enter zone name: ")
        else:
            zone_name, lat, lon, radius = areas[area]
        
        # Write zones file
        zones_df = pd.DataFrame([{
            'zone_name': zone_name.replace(' ', '_'),
            'latitude': lat,
            'longitude': lon,
            'radius': radius
        }])
        zones_df.to_csv('search_zones_targeted.csv', index=False)
        print(f"✅ Created search zone: {zone_name}")
    
    # Create targeted queries file
    if category in categories:
        full_queries = pd.read_csv('queries_comprehensive.csv')
        
        if category == '1':  # Competitors only
            filtered = full_queries[full_queries['category'] == 'Competitor']
        elif category == '2':  # Affluence only
            filtered = full_queries[full_queries['category'] == 'Affluence_Proxy']
        elif category == '3':  # Pet Lifestyle only
            filtered = full_queries[full_queries['category'] == 'Lifestyle_Proxy']
        else:  # All
            filtered = full_queries
        
        filtered.to_csv('queries_targeted.csv', index=False)
        print(f"✅ Created query set: {categories[category]} ({len(filtered)} queries)")
    
    return 'search_zones_targeted.csv', 'queries_targeted.csv'


def main():
    """Run targeted analysis."""
    print("🎯 Pet Wellness Hub - Quick Targeted Analysis")
    print("=" * 50)
    
    # Check API key
    if not os.getenv('GOOGLE_MAPS_API_KEY'):
        print("❌ Error: Please set your API key in .env file first!")
        return
    
    # Create targeted files
    zones_file, queries_file = create_targeted_files()
    
    # Estimate cost
    zones_df = pd.read_csv(zones_file)
    queries_df = pd.read_csv(queries_file)
    estimated_searches = len(zones_df) * len(queries_df)
    estimated_cost = estimated_searches * 0.017  # Rough estimate
    
    print(f"\n💰 Estimated cost: ${estimated_cost:.2f}")
    print(f"⏱️  Estimated time: {estimated_searches * 2 / 60:.0f} minutes")
    
    proceed = input("\n🚀 Run analysis? (y/n): ").strip().lower()
    
    if proceed == 'y':
        # Run the comprehensive script with targeted files
        print("\n🔄 Starting analysis...")
        import subprocess
        
        # Temporarily rename files
        os.rename(zones_file, 'search_zones.csv.tmp')
        os.rename(queries_file, 'queries_comprehensive.csv.tmp')
        
        if os.path.exists('search_zones.csv'):
            os.rename('search_zones.csv', 'search_zones.csv.bak')
        if os.path.exists('queries_comprehensive.csv'):
            os.rename('queries_comprehensive.csv', 'queries_comprehensive.csv.bak')
        
        os.rename('search_zones.csv.tmp', 'search_zones.csv')
        os.rename('queries_comprehensive.csv.tmp', 'queries_comprehensive.csv')
        
        # Run analysis
        subprocess.run([sys.executable, 'main_comprehensive.py'])
        
        # Restore original files
        os.rename('search_zones.csv', zones_file)
        os.rename('queries_comprehensive.csv', queries_file)
        
        if os.path.exists('search_zones.csv.bak'):
            os.rename('search_zones.csv.bak', 'search_zones.csv')
        if os.path.exists('queries_comprehensive.csv.bak'):
            os.rename('queries_comprehensive.csv.bak', 'queries_comprehensive.csv')
        
        print("\n✅ Analysis complete! Check the output CSV file.")
    else:
        print("\n❌ Analysis cancelled.")


if __name__ == "__main__":
    main()