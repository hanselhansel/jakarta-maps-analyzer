#!/usr/bin/env python3
"""
Merge the main comprehensive dataset with supplementary search results
"""
import pandas as pd
from datetime import datetime
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def merge_datasets():
    """Merge main and supplementary datasets"""
    
    # Load main dataset
    logging.info("Loading main comprehensive dataset...")
    main_df = pd.read_csv('jakarta_pet_market_analysis_20250805_095802.csv')
    logging.info(f"Main dataset: {len(main_df)} locations")
    
    # Load supplementary dataset
    logging.info("Loading supplementary dataset...")
    try:
        # Load the final supplementary file
        supp_file = 'jakarta_supplementary_analysis_20250805_103712.csv'
        if os.path.exists(supp_file):
            supp_df = pd.read_csv(supp_file)
            logging.info(f"Supplementary dataset (final): {len(supp_df)} locations")
        else:
            logging.error("No supplementary files found")
            return
    except Exception as e:
        logging.error(f"Error loading supplementary data: {e}")
        return
    
    # Combine datasets
    logging.info("Merging datasets...")
    combined_df = pd.concat([main_df, supp_df], ignore_index=True)
    
    # Remove duplicates based on place_id
    before_dedup = len(combined_df)
    combined_df = combined_df.drop_duplicates(subset='place_id', keep='first')
    after_dedup = len(combined_df)
    logging.info(f"Combined dataset: {before_dedup} → {after_dedup} locations ({before_dedup - after_dedup} duplicates removed)")
    
    # Sort by category and sub_category
    combined_df = combined_df.sort_values(['category', 'sub_category', 'rating'], 
                                        ascending=[True, True, False])
    
    # Save merged dataset
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'jakarta_pet_market_COMPLETE_{timestamp}.csv'
    combined_df.to_csv(output_file, index=False, encoding='utf-8')
    
    # Print summary
    logging.info("\n" + "="*60)
    logging.info("MERGE COMPLETE")
    logging.info("="*60)
    logging.info(f"Total unique locations: {len(combined_df)}")
    
    # Category breakdown
    logging.info("\nCategory Breakdown:")
    category_counts = combined_df['category'].value_counts()
    for cat, count in category_counts.items():
        logging.info(f"  {cat}: {count}")
    
    # Sub-category breakdown
    logging.info("\nTop Sub-Categories:")
    sub_category_counts = combined_df['sub_category'].value_counts()
    for sub_cat, count in sub_category_counts.head(10).items():
        logging.info(f"  {sub_cat}: {count}")
    
    logging.info(f"\n✅ Complete dataset saved to: {output_file}")
    
    return output_file

if __name__ == "__main__":
    merge_datasets()