#!/usr/bin/env python3
"""
Analyze existing Jakarta pet market dataset before enhancement
"""
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def analyze_existing_data():
    """Analyze the existing dataset structure and content"""
    
    # Load existing data
    file_path = 'jakarta_pet_market_CLEAN_20250805_102308.csv'
    logging.info(f"Loading existing data from {file_path}")
    
    df = pd.read_csv(file_path)
    
    # Basic stats
    logging.info(f"\nTotal records: {len(df)}")
    
    # Category breakdown
    logging.info("\nCategory breakdown:")
    category_counts = df['category'].value_counts()
    for cat, count in category_counts.items():
        logging.info(f"  {cat}: {count}")
    
    # Sub-category breakdown for competitors
    competitor_df = df[df['category'] == 'Competitor']
    logging.info(f"\nCompetitor sub-categories ({len(competitor_df)} total):")
    comp_subcats = competitor_df['sub_category'].value_counts()
    for subcat, count in comp_subcats.items():
        logging.info(f"  {subcat}: {count}")
    
    # Unique search zones
    zones = df['search_zone'].unique()
    logging.info(f"\nUnique search zones: {len(zones)}")
    for zone in sorted(zones):
        zone_data = df[df['search_zone'] == zone]
        center_lat = zone_data['latitude'].mean()
        center_lng = zone_data['longitude'].mean()
        logging.info(f"  {zone}: center at ({center_lat:.4f}, {center_lng:.4f})")
    
    # Save zone info for later use
    zone_info = pd.DataFrame({
        'zone_name': zones,
        'center_latitude': [df[df['search_zone'] == z]['latitude'].mean() for z in zones],
        'center_longitude': [df[df['search_zone'] == z]['longitude'].mean() for z in zones]
    })
    zone_info.to_csv('existing_zones_info.csv', index=False)
    logging.info("\nZone information saved to existing_zones_info.csv")
    
    # Column structure
    logging.info(f"\nColumns ({len(df.columns)}): {', '.join(df.columns)}")
    
    return df

if __name__ == "__main__":
    analyze_existing_data()