#!/usr/bin/env python3
"""
Analyze coverage and cost for comprehensive Jakarta search
"""

import pandas as pd
import math

# Load search zones
zones_10 = pd.read_csv('search_zones_original.csv')
zones_28 = pd.read_csv('search_zones_comprehensive.csv')

# Load queries - count all the comprehensive queries
queries = pd.DataFrame({
    'keyword': [''] * 40  # We have 40 queries in the comprehensive list
})

print("🗺️  Jakarta Pet Wellness Market Analysis - Coverage Comparison")
print("=" * 70)

# Calculate coverage area
def calculate_coverage_area(zones_df):
    total_area = 0
    for _, zone in zones_df.iterrows():
        # Area = π * r²
        area = math.pi * (zone['radius'] / 1000) ** 2  # Convert to km²
        total_area += area
    return total_area

# Jakarta metropolitan area is approximately 662 km²
jakarta_area = 662

area_10 = calculate_coverage_area(zones_10)
area_28 = calculate_coverage_area(zones_28)

print(f"\n📊 Coverage Analysis:")
print(f"   Jakarta Metropolitan Area: {jakarta_area} km²")
print(f"\n   Original Plan (10 zones):")
print(f"   - Total coverage: {area_10:.0f} km²")
print(f"   - Coverage percentage: {area_10/jakarta_area*100:.1f}%")
print(f"   - Number of zones: {len(zones_10)}")

print(f"\n   Comprehensive Plan (28 zones):")
print(f"   - Total coverage: {area_28:.0f} km²")
print(f"   - Coverage percentage: {area_28/jakarta_area*100:.1f}%")
print(f"   - Number of zones: {len(zones_28)}")

# Cost calculation
searches_10 = len(zones_10) * len(queries)
searches_28 = len(zones_28) * len(queries)

# Estimate ~60 results per search (max), ~50% will need details
est_detail_calls_10 = searches_10 * 30
est_detail_calls_28 = searches_28 * 30

# Places Nearby: $0.032/call, Place Details: $0.017/call
cost_10 = (searches_10 * 0.032) + (est_detail_calls_10 * 0.017)
cost_28 = (searches_28 * 0.032) + (est_detail_calls_28 * 0.017)

print(f"\n💰 Cost Analysis:")
print(f"\n   Original Plan (10 zones × {len(queries)} queries):")
print(f"   - Total searches: {searches_10}")
print(f"   - Estimated API calls: {searches_10 + est_detail_calls_10:,}")
print(f"   - Estimated cost: ${cost_10:.2f}")
print(f"   - Time estimate: {searches_10 * 3 / 60:.0f} minutes")

print(f"\n   Comprehensive Plan (28 zones × {len(queries)} queries):")
print(f"   - Total searches: {searches_28}")
print(f"   - Estimated API calls: {searches_28 + est_detail_calls_28:,}")
print(f"   - Estimated cost: ${cost_28:.2f}")
print(f"   - Time estimate: {searches_28 * 3 / 60:.0f} minutes")

print(f"\n📈 Comparison:")
print(f"   - Coverage increase: +{area_28/area_10*100-100:.0f}%")
print(f"   - Cost increase: +${cost_28-cost_10:.2f} (+{(cost_28/cost_10-1)*100:.0f}%)")
print(f"   - Additional time: +{(searches_28-searches_10)*3/60:.0f} minutes")

# Zone breakdown by area
print(f"\n📍 Zone Distribution (Comprehensive Plan):")
area_counts = zones_28['zone_name'].str.split('_').str[0].value_counts()
for area, count in area_counts.items():
    print(f"   {area}: {count} zones")

# Calculate expected results
print(f"\n🎯 Expected Results:")
print(f"   Original Plan:")
print(f"   - Estimated unique locations: 800-1,200")
print(f"   - After filtering: 600-900")

print(f"\n   Comprehensive Plan:")
print(f"   - Estimated unique locations: 2,200-3,300")
print(f"   - After filtering: 1,700-2,500")

print(f"\n💡 Recommendation:")
print(f"   The comprehensive plan provides {area_28/jakarta_area*100:.0f}% coverage of Jakarta")
print(f"   for approximately ${cost_28:.0f}, which is excellent value for")
print(f"   complete market intelligence across the entire metropolitan area.")

# Save visualization data
visualization_data = pd.DataFrame({
    'zone_name': zones_28['zone_name'],
    'latitude': zones_28['latitude'],
    'longitude': zones_28['longitude'],
    'radius_m': zones_28['radius'],
    'area_km2': zones_28['radius'].apply(lambda r: math.pi * (r/1000)**2).round(1)
})
visualization_data.to_csv('zones_visualization.csv', index=False)
print(f"\n📊 Zone visualization data saved to: zones_visualization.csv")