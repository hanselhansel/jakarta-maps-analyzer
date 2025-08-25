#!/usr/bin/env python3
"""
Supplementary search for missing keywords to complete the comprehensive analysis
"""
import os
import time
import json
import logging
from datetime import datetime
from main_comprehensive import (
    load_search_zones, fetch_places_for_zone_and_keyword, 
    get_place_details_enhanced, is_relevant_business, 
    process_place_for_output
)
import googlemaps
import pandas as pd
from collections import defaultdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('supplementary_search.log'),
        logging.StreamHandler()
    ]
)

def load_existing_place_ids(existing_file):
    """Load existing place IDs to avoid duplicates"""
    try:
        df = pd.read_csv(existing_file)
        return set(df['place_id'].values)
    except:
        return set()

def load_supplementary_queries():
    """Load supplementary queries"""
    try:
        df = pd.read_csv('queries_supplementary.csv')
        logging.info(f"Loaded {len(df)} supplementary search queries")
        return df
    except Exception as e:
        logging.error(f"Error loading supplementary queries: {e}")
        return pd.DataFrame()

def load_supplementary_progress():
    """Load progress from checkpoint file"""
    checkpoint_file = 'supplementary_progress.json'
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            return json.load(f)
    return {
        'completed_zones': [],
        'unique_places': {},
        'stats': defaultdict(int),
        'api_calls': 0
    }

def save_supplementary_progress(progress):
    """Save progress to checkpoint file"""
    checkpoint_file = 'supplementary_progress.json'
    progress_copy = progress.copy()
    progress_copy['stats'] = dict(progress_copy['stats'])
    
    with open(checkpoint_file, 'w') as f:
        json.dump(progress_copy, f, indent=2)

def run_supplementary_search():
    """Run supplementary search for missing keywords"""
    # Load API key
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        logging.error("No API key found")
        return
    
    # Initialize client
    gmaps = googlemaps.Client(key=api_key)
    
    # Load existing place IDs
    existing_ids = load_existing_place_ids('jakarta_pet_market_analysis_20250805_095802.csv')
    logging.info(f"Loaded {len(existing_ids)} existing place IDs to avoid duplicates")
    
    # Load zones and queries
    zones = load_search_zones()
    queries_df = load_supplementary_queries()
    
    if queries_df.empty:
        logging.error("No supplementary queries loaded")
        return
    
    # Load progress
    progress = load_supplementary_progress()
    unique_places = progress['unique_places']
    stats = defaultdict(int, progress['stats'])
    api_calls = progress['api_calls']
    
    logging.info(f"Starting supplementary search...")
    logging.info(f"Zones: {len(zones)}, Queries: {len(queries_df)}")
    logging.info(f"Total searches: {len(zones) * len(queries_df)}")
    logging.info(f"Already completed zones: {len(progress['completed_zones'])}")
    
    # Process remaining zones
    for zone in zones:
        if zone['name'] in progress['completed_zones']:
            logging.info(f"Skipping already completed zone: {zone['name']}")
            continue
            
        logging.info(f"\n🗺️  Processing zone: {zone['name']}")
        zone_start_time = time.time()
        zone_api_calls = 0
        
        # Process each query
        for _, query in queries_df.iterrows():
            keyword = query['keyword']
            category = query['category']
            sub_category = query['sub_category']
            
            logging.info(f"  Searching: {keyword}")
            
            # Fetch places
            places, calls = fetch_places_for_zone_and_keyword(
                gmaps, keyword, zone, rate_limit=10
            )
            zone_api_calls += calls
            stats[f'searches_{category}'] += 1
            
            # Process each place
            new_places = 0
            for place in places:
                place_id = place.get('place_id')
                
                # Skip if already in existing dataset or already found
                if place_id and place_id not in existing_ids and place_id not in unique_places:
                    search_types = place.get('search_types', [])
                    
                    # Get details
                    details = get_place_details_enhanced(gmaps, place_id)
                    zone_api_calls += 1
                    
                    if details:
                        name = details.get('name', '')
                        
                        if is_relevant_business(name, search_types):
                            # Process and store
                            place_info = process_place_for_output(
                                details, category, sub_category,
                                {'zone': zone['name'], 'keyword': keyword},
                                search_types
                            )
                            unique_places[place_id] = place_info
                            stats[f'found_{category}'] += 1
                            stats[f'found_{sub_category}'] += 1
                            new_places += 1
                        else:
                            stats['filtered_irrelevant'] += 1
            
            logging.info(f"    Found {new_places} new unique places")
        
        # Update progress
        api_calls += zone_api_calls
        progress['completed_zones'].append(zone['name'])
        progress['unique_places'] = unique_places
        progress['stats'] = dict(stats)
        progress['api_calls'] = api_calls
        
        zone_time = time.time() - zone_start_time
        logging.info(f"  Zone completed in {zone_time:.1f}s with {zone_api_calls} API calls")
        
        # Save progress
        save_supplementary_progress(progress)
        
        # Save intermediate results
        if len(unique_places) > 0:
            df = pd.DataFrame.from_dict(unique_places, orient='index')
            df = df.sort_values(['category', 'sub_category', 'rating'], 
                              ascending=[True, True, False])
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            intermediate_file = f'jakarta_supplementary_{timestamp}_partial.csv'
            df.to_csv(intermediate_file, index=False, encoding='utf-8')
            logging.info(f"  Saved intermediate results to {intermediate_file}")
    
    # Final save
    if len(unique_places) > 0:
        df = pd.DataFrame.from_dict(unique_places, orient='index')
        df = df.sort_values(['category', 'sub_category', 'rating'], 
                          ascending=[True, True, False])
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        final_file = f'jakarta_supplementary_analysis_{timestamp}.csv'
        df.to_csv(final_file, index=False, encoding='utf-8')
        
        # Print summary
        logging.info("\n" + "=" * 60)
        logging.info("📊 SUPPLEMENTARY SEARCH COMPLETE")
        logging.info("=" * 60)
        logging.info(f"New unique places found: {len(unique_places)}")
        logging.info(f"Total API calls made: {api_calls}")
        logging.info(f"Irrelevant results filtered: {stats.get('filtered_irrelevant', 0)}")
        
        # Category breakdown
        category_counts = df['category'].value_counts()
        logging.info("\nNew Results by Category:")
        for cat, count in category_counts.items():
            logging.info(f"  {cat}: {count}")
        
        # Cost estimation
        text_search_cost = api_calls * 0.017
        logging.info(f"\nEstimated API cost: ${text_search_cost:.2f}")
        logging.info(f"\n✅ Supplementary results saved to: {final_file}")
        
        # Clean up checkpoint
        if os.path.exists('supplementary_progress.json'):
            os.remove('supplementary_progress.json')
            logging.info("Cleaned up checkpoint file")
        
        return final_file

if __name__ == "__main__":
    run_supplementary_search()