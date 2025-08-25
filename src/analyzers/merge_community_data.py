#!/usr/bin/env python3
"""
Community Data Merger
Safely merges community locations data with existing pet market dataset
while preserving all existing competitor data and maintaining data integrity.
"""

import pandas as pd
import logging
from datetime import datetime
from pathlib import Path
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def load_and_validate_dataset(file_path, dataset_name):
    """Load and validate a dataset file."""
    if not Path(file_path).exists():
        logging.error(f"{dataset_name} file '{file_path}' not found.")
        return None
    
    try:
        df = pd.read_csv(file_path)
        logging.info(f"Loaded {dataset_name}: {len(df)} records")
        
        # Validate required columns
        required_columns = [
            'place_id', 'name', 'category', 'sub_category', 'latitude', 'longitude',
            'address', 'vicinity', 'rating', 'review_count', 'website', 'phone',
            'price_level', 'types', 'is_operational', 'search_zone', 'search_keyword',
            'is_open_now', 'timestamp', 'popularity_score', 'buffer_radius_m'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logging.error(f"{dataset_name} missing required columns: {missing_columns}")
            return None
        
        # Validate place_id uniqueness
        duplicate_ids = df[df['place_id'].duplicated()]['place_id'].tolist()
        if duplicate_ids:
            logging.warning(f"{dataset_name} has duplicate place_ids: {len(duplicate_ids)} duplicates")
            # Remove duplicates, keeping first occurrence
            df = df.drop_duplicates(subset=['place_id'], keep='first')
            logging.info(f"After deduplication: {len(df)} records")
        
        return df
        
    except Exception as e:
        logging.error(f"Error loading {dataset_name}: {e}")
        return None


def analyze_datasets(existing_df, community_df):
    """Analyze both datasets before merging."""
    print("\n" + "="*60)
    print("📊 DATASET ANALYSIS")
    print("="*60)
    
    print(f"\n📋 EXISTING DATASET SUMMARY:")
    print(f"   - Total records: {len(existing_df)}")
    print(f"   - Categories: {existing_df['category'].value_counts().to_dict()}")
    
    print(f"\n🏘️  COMMUNITY DATASET SUMMARY:")
    print(f"   - Total records: {len(community_df)}")
    print(f"   - Categories: {community_df['category'].value_counts().to_dict()}")
    
    # Check for any overlapping place_ids (should be none due to deduplication)
    existing_ids = set(existing_df['place_id'])
    community_ids = set(community_df['place_id'])
    overlapping_ids = existing_ids.intersection(community_ids)
    
    print(f"\n🔍 OVERLAP ANALYSIS:")
    print(f"   - Existing place_ids: {len(existing_ids)}")
    print(f"   - Community place_ids: {len(community_ids)}")
    print(f"   - Overlapping place_ids: {len(overlapping_ids)}")
    
    if overlapping_ids:
        print(f"   - ⚠️  WARNING: Found {len(overlapping_ids)} overlapping place_ids")
        print(f"   - These will be removed from community data to avoid duplicates")
    else:
        print(f"   - ✅ No overlapping place_ids - safe to merge")
    
    return overlapping_ids


def merge_datasets(existing_df, community_df, overlapping_ids):
    """Merge datasets while handling any overlaps."""
    
    # Remove any overlapping place_ids from community data
    if overlapping_ids:
        logging.warning(f"Removing {len(overlapping_ids)} overlapping records from community data")
        community_df = community_df[~community_df['place_id'].isin(overlapping_ids)]
        logging.info(f"Community data after overlap removal: {len(community_df)} records")
    
    # Combine datasets
    merged_df = pd.concat([existing_df, community_df], ignore_index=True)
    
    # Final validation
    duplicate_check = merged_df[merged_df['place_id'].duplicated()]
    if len(duplicate_check) > 0:
        logging.error(f"ERROR: Merged dataset still has {len(duplicate_check)} duplicates!")
        return None
    
    logging.info(f"Successfully merged datasets: {len(merged_df)} total records")
    return merged_df


def validate_merged_dataset(merged_df, original_existing_count, original_community_count):
    """Validate the merged dataset for integrity."""
    
    print(f"\n✅ MERGE VALIDATION:")
    print(f"   - Original existing records: {original_existing_count}")
    print(f"   - Original community records: {original_community_count}")
    print(f"   - Merged dataset records: {len(merged_df)}")
    
    # Check that we didn't lose any existing data
    competitor_records = len(merged_df[merged_df['category'] == 'Competitor'])
    print(f"   - Competitor records preserved: {competitor_records}")
    
    # Check community categories
    community_categories = ['Community_Infrastructure', 'Middle_Class_Accessibility', 
                          'Family_Services', 'Value_Conscious_Retail']
    community_records = len(merged_df[merged_df['category'].isin(community_categories)])
    print(f"   - Community records added: {community_records}")
    
    # Category breakdown
    print(f"\n📈 FINAL CATEGORY BREAKDOWN:")
    category_counts = merged_df['category'].value_counts()
    for category, count in category_counts.items():
        print(f"   - {category}: {count} records")
    
    return True


def main():
    """Main execution function."""
    print("🔄 Community Data Merger")
    print("="*60)
    print("Safely merging community locations with existing pet market dataset")
    print("="*60)
    
    # Default file paths - can be overridden via command line
    existing_file = 'jakarta_pet_market_CLEAN_20250805_102308.csv'
    community_file = None
    
    # Check for command line arguments
    if len(sys.argv) == 3:
        existing_file = sys.argv[1]
        community_file = sys.argv[2]
    elif len(sys.argv) == 2:
        community_file = sys.argv[1]
    else:
        # Find the most recent community file
        community_files = list(Path('.').glob('jakarta_community_locations_*.csv'))
        if community_files:
            community_file = str(max(community_files, key=lambda x: x.stat().st_mtime))
            print(f"📁 Auto-detected community file: {community_file}")
        else:
            print("❌ No community locations file found!")
            print("Usage: python merge_community_data.py [existing_file] <community_file>")
            return
    
    print(f"📥 Existing dataset: {existing_file}")
    print(f"📥 Community dataset: {community_file}")
    print()
    
    # Load datasets
    existing_df = load_and_validate_dataset(existing_file, "Existing dataset")
    if existing_df is None:
        return
        
    community_df = load_and_validate_dataset(community_file, "Community dataset")
    if community_df is None:
        return
    
    # Store original counts
    original_existing_count = len(existing_df)
    original_community_count = len(community_df)
    
    # Analyze datasets
    overlapping_ids = analyze_datasets(existing_df, community_df)
    
    # Merge datasets
    print(f"\n🔄 Merging datasets...")
    merged_df = merge_datasets(existing_df, community_df, overlapping_ids)
    
    if merged_df is None:
        print("❌ Merge failed!")
        return
    
    # Validate merged dataset
    validate_merged_dataset(merged_df, original_existing_count, original_community_count)
    
    # Save merged dataset
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'jakarta_complete_with_community_{timestamp}.csv'
    
    try:
        merged_df.to_csv(output_file, index=False)
        print(f"\n💾 Merged dataset saved to: {output_file}")
        print(f"📊 Total records: {len(merged_df)}")
        
        # Create a summary report
        summary_file = f'merge_summary_{timestamp}.txt'
        with open(summary_file, 'w') as f:
            f.write("COMMUNITY DATA MERGE SUMMARY\n")
            f.write("="*40 + "\n\n")
            f.write(f"Merge timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Existing dataset: {existing_file} ({original_existing_count} records)\n")
            f.write(f"Community dataset: {community_file} ({original_community_count} records)\n")
            f.write(f"Merged dataset: {output_file} ({len(merged_df)} records)\n\n")
            f.write("Category breakdown:\n")
            for category, count in merged_df['category'].value_counts().items():
                f.write(f"  - {category}: {count} records\n")
            f.write(f"\nOverlapping place_ids removed: {len(overlapping_ids)}\n")
            f.write(f"Merge completed successfully: {len(merged_df) == (original_existing_count + original_community_count - len(overlapping_ids))}\n")
        
        print(f"📋 Summary report saved to: {summary_file}")
        
    except Exception as e:
        logging.error(f"Error saving merged dataset: {e}")
        return
    
    print("\n✅ Community data merge completed successfully!")
    print("💡 The merged dataset now includes both pet market and community location data.")
    print("🎯 Ready for comprehensive market analysis!")


if __name__ == "__main__":
    main()