#!/usr/bin/env python3
"""
Data Cleaning Script for QGIS Import
Filters and prepares the scraped data for optimal QGIS analysis
"""

import pandas as pd
import sys
import os
from datetime import datetime

def clean_market_data(input_file, output_file=None):
    """Clean and filter market analysis data for QGIS."""
    
    print("🧹 Pet Wellness Market Data Cleaner")
    print("=" * 50)
    
    # Load data
    print(f"\n📁 Loading: {input_file}")
    df = pd.read_csv(input_file)
    original_count = len(df)
    print(f"   Original records: {original_count}")
    
    # 1. Remove duplicates based on place_id
    df = df.drop_duplicates(subset=['place_id'])
    print(f"   After deduplication: {len(df)} (-{original_count - len(df)} duplicates)")
    
    # 2. Filter by operational status
    if 'is_operational' in df.columns:
        operational_before = len(df)
        df = df[df['is_operational'] == True]
        print(f"   After operational filter: {len(df)} (-{operational_before - len(df)} closed)")
    
    # 3. Enhanced category-specific filtering
    print("\n🔍 Applying category-specific filters...")
    
    # For competitors - keep only relevant sub-categories
    competitor_mask = df['category'] == 'Competitor'
    relevant_competitor_types = ['Clinic_Only', 'Clinic+Grooming', 'Grooming_Only', 
                                'Pet_Hotel', 'Emergency_Hospital']
    df.loc[competitor_mask, 'keep'] = df.loc[competitor_mask, 'sub_category'].isin(relevant_competitor_types)
    
    # For affluence proxies - filter by review count (popularity indicator)
    affluence_mask = df['category'] == 'Affluence_Proxy'
    df.loc[affluence_mask, 'keep'] = df.loc[affluence_mask, 'review_count'] >= 10
    
    # For lifestyle proxies - keep all (already filtered by script)
    lifestyle_mask = df['category'] == 'Lifestyle_Proxy'
    df.loc[lifestyle_mask, 'keep'] = True
    
    # Apply the filter
    filtered_df = df[df['keep'] == True].drop(columns=['keep'])
    print(f"   After category filters: {len(filtered_df)} (-{len(df) - len(filtered_df)} low-relevance)")
    
    # 4. Add analysis columns
    print("\n📊 Adding analysis columns...")
    
    # Popularity score (normalized review count * rating)
    max_reviews = filtered_df['review_count'].max()
    if max_reviews > 0:
        filtered_df['popularity_score'] = (
            (filtered_df['review_count'] / max_reviews) * 
            filtered_df['rating'].fillna(3.0)
        ).round(2)
    
    # Competition intensity zones (for competitors)
    if 'Competitor' in filtered_df['category'].values:
        # This will be used in QGIS to create buffer zones
        filtered_df.loc[filtered_df['category'] == 'Competitor', 'buffer_radius_m'] = \
            filtered_df.loc[filtered_df['category'] == 'Competitor', 'sub_category'].map({
                'Clinic+Grooming': 3000,  # Full service = largest impact
                'Emergency_Hospital': 3000,
                'Clinic_Only': 2000,
                'Grooming_Only': 1500,
                'Pet_Hotel': 1500
            })
    
    # 5. Sort for better organization
    filtered_df = filtered_df.sort_values(
        ['category', 'sub_category', 'popularity_score'],
        ascending=[True, True, False]
    )
    
    # 6. Save cleaned data
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'jakarta_pet_market_CLEAN_{timestamp}.csv'
    
    filtered_df.to_csv(output_file, index=False)
    
    # 7. Generate summary report
    print("\n📈 Cleaning Summary:")
    print(f"   Input file: {input_file}")
    print(f"   Output file: {output_file}")
    print(f"   Records: {original_count} → {len(filtered_df)} ({len(filtered_df)/original_count*100:.1f}% retained)")
    
    print("\n📊 Category Breakdown:")
    for cat in filtered_df['category'].unique():
        cat_df = filtered_df[filtered_df['category'] == cat]
        print(f"\n   {cat} ({len(cat_df)} locations):")
        
        # Sub-category breakdown
        for sub_cat, count in cat_df['sub_category'].value_counts().items():
            avg_rating = cat_df[cat_df['sub_category'] == sub_cat]['rating'].mean()
            avg_reviews = cat_df[cat_df['sub_category'] == sub_cat]['review_count'].mean()
            print(f"      {sub_cat}: {count} (avg rating: {avg_rating:.1f}, avg reviews: {avg_reviews:.0f})")
    
    # 8. QGIS import instructions
    print("\n🗺️  QGIS Import Instructions:")
    print(f"1. Open QGIS")
    print(f"2. Layer → Add Layer → Add Delimited Text Layer")
    print(f"3. Select: {output_file}")
    print(f"4. X field: longitude, Y field: latitude")
    print(f"5. CRS: EPSG:4326 (WGS 84)")
    print(f"\n💡 Pro Tips for QGIS Analysis:")
    print("   - Use 'buffer_radius_m' for competitor impact zones")
    print("   - Weight heat maps by 'popularity_score'")
    print("   - Filter by 'sub_category' for detailed analysis")
    print("   - Style by 'category' with different colors")
    
    return output_file


def main():
    """Main entry point for command line usage."""
    if len(sys.argv) < 2:
        # Find the most recent analysis file
        import glob
        files = glob.glob('jakarta_pet_market_analysis_*.csv')
        if not files:
            print("❌ No analysis files found.")
            print("Usage: python clean_data_for_qgis.py <input_file.csv>")
            return
        
        input_file = max(files)  # Most recent
        print(f"No file specified, using most recent: {input_file}")
    else:
        input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return
    
    output_file = clean_market_data(input_file)
    print(f"\n✅ Cleaning complete! Your QGIS-ready file: {output_file}")


if __name__ == "__main__":
    main()