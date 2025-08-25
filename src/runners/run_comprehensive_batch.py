#!/usr/bin/env python3
"""
Batch runner for comprehensive analysis that can handle interruptions
"""
import os
import time
import json
import logging
from datetime import datetime
from main_comprehensive import (
    load_search_zones, load_queries_with_categories,
    fetch_places_for_zone_and_keyword, get_place_details_enhanced,
    is_relevant_business, process_place_for_output
)
import googlemaps
import pandas as pd
from collections import defaultdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comprehensive_batch.log'),
        logging.StreamHandler()
    ]
)

def load_progress():
    """Load progress from checkpoint file"""
    checkpoint_file = 'batch_progress.json'
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            return json.load(f)
    return {
        'completed_zones': [],
        'unique_places': {},
        'stats': defaultdict(int),
        'api_calls': 0
    }

def save_progress(progress):
    """Save progress to checkpoint file"""
    checkpoint_file = 'batch_progress.json'
    # Convert defaultdict to regular dict for JSON serialization
    progress_copy = progress.copy()
    progress_copy['stats'] = dict(progress_copy['stats'])
    
    with open(checkpoint_file, 'w') as f:
        json.dump(progress_copy, f, indent=2)

def run_batch_analysis():
    """Run analysis in batches with checkpoint support"""
    # Load API key
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        logging.error("No API key found")
        return
    
    # Initialize client
    gmaps = googlemaps.Client(key=api_key)
    
    # Load zones and queries
    zones = load_search_zones()
    queries_df = load_queries_with_categories()
    
    # Load progress
    progress = load_progress()
    unique_places = progress['unique_places']
    stats = defaultdict(int, progress['stats'])
    api_calls = progress['api_calls']
    
    logging.info(f"Starting/resuming batch processing...")
    logging.info(f"Already completed zones: {len(progress['completed_zones'])}")
    logging.info(f"Existing unique places: {len(unique_places)}")
    
    # Process remaining zones
    for zone in zones:
        if zone['name'] in progress['completed_zones']:
            logging.info(f"Skipping already completed zone: {zone['name']}")
            continue
            
        logging.info(f"\n🗺️  Processing zone: {zone['name']}")
        logging.info(f"   Location: {zone['location']}")
        logging.info(f"   Radius: {zone['radius']}m")
        
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
                
                if place_id and place_id not in unique_places:
                    # Get the types from search response
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
        
        # Update progress after completing zone
        api_calls += zone_api_calls
        progress['completed_zones'].append(zone['name'])
        progress['unique_places'] = unique_places
        progress['stats'] = dict(stats)
        progress['api_calls'] = api_calls
        
        zone_time = time.time() - zone_start_time
        logging.info(f"  Zone completed in {zone_time:.1f}s with {zone_api_calls} API calls")
        
        # Save progress
        save_progress(progress)
        
        # Save intermediate results
        if len(unique_places) > 0:
            df = pd.DataFrame.from_dict(unique_places, orient='index')
            df = df.sort_values(['category', 'sub_category', 'rating'], 
                              ascending=[True, True, False])
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            intermediate_file = f'jakarta_pet_market_analysis_{timestamp}_partial.csv'
            df.to_csv(intermediate_file, index=False, encoding='utf-8')
            logging.info(f"  Saved intermediate results to {intermediate_file}")
    
    # Final save
    if len(unique_places) > 0:
        df = pd.DataFrame.from_dict(unique_places, orient='index')
        df = df.sort_values(['category', 'sub_category', 'rating'], 
                          ascending=[True, True, False])
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        final_file = f'jakarta_pet_market_analysis_{timestamp}.csv'
        df.to_csv(final_file, index=False, encoding='utf-8')
        
        # Print summary
        logging.info("\n" + "=" * 60)
        logging.info("📊 ANALYSIS COMPLETE")
        logging.info("=" * 60)
        logging.info(f"Total unique places found: {len(unique_places)}")
        logging.info(f"Total API calls made: {api_calls}")
        logging.info(f"Irrelevant results filtered: {stats.get('filtered_irrelevant', 0)}")
        
        # Category breakdown
        category_counts = df['category'].value_counts()
        logging.info("\nResults by Category:")
        for cat, count in category_counts.items():
            logging.info(f"  {cat}: {count}")
        
        # Cost estimation
        text_search_cost = api_calls * 0.017
        logging.info(f"\nEstimated API cost: ${text_search_cost:.2f}")
        logging.info(f"\n✅ Final results saved to: {final_file}")
        
        # Clean up checkpoint file
        if os.path.exists('batch_progress.json'):
            os.remove('batch_progress.json')
            logging.info("Cleaned up checkpoint file")

if __name__ == "__main__":
    run_batch_analysis()