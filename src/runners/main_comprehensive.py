#!/usr/bin/env python3
"""
Comprehensive Google Maps Market Analysis Scraper for Pet Wellness Hub
Uses grid-based search strategy to maximize coverage
"""

import os
import csv
import time
import logging
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict

from dotenv import load_dotenv
import googlemaps
import pandas as pd
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()


def load_search_zones(zones_file='search_zones.csv'):
    """Load search zones from CSV file."""
    zones = []
    try:
        df = pd.read_csv(zones_file)
        for _, row in df.iterrows():
            zones.append({
                'name': row['zone_name'],
                'location': (float(row['latitude']), float(row['longitude'])),
                'radius': int(row['radius'])
            })
        logging.info(f"Loaded {len(zones)} search zones")
        return zones
    except Exception as e:
        logging.error(f"Error loading search zones: {e}")
        # Fall back to single central zone
        return [{
            'name': 'Jakarta_Central',
            'location': (-6.2088, 106.8456),
            'radius': 50000
        }]


def load_queries_with_categories(queries_file='queries_comprehensive_optimized.csv'):
    """Load queries with category and sub-category information."""
    try:
        df = pd.read_csv(queries_file)
        logging.info(f"Loaded {len(df)} search queries with categories")
        return df
    except Exception as e:
        logging.error(f"Error loading queries: {e}")
        return pd.DataFrame()


def fetch_places_for_zone_and_keyword(gmaps, keyword, zone, rate_limit=10):
    """Fetch places for a specific zone and keyword combination."""
    places = []
    api_calls = 0
    max_pages = 3  # Limit to prevent excessive API usage
    
    try:
        # Rate limiting
        time.sleep(1.0 / rate_limit)
        
        # Initial search
        response = gmaps.places_nearby(
            location=zone['location'],
            radius=zone['radius'],
            keyword=keyword
        )
        api_calls += 1
        
        if 'results' in response:
            # Add zone information and capture types from search response
            for place in response['results']:
                place['search_zone'] = zone['name']
                place['search_keyword'] = keyword
                # Capture types from the search response (this is the key fix)
                place['search_types'] = place.get('types', [])
            places.extend(response['results'])
        
        # Handle pagination
        page_count = 1
        while 'next_page_token' in response and page_count < max_pages:
            time.sleep(2)  # Required delay for next_page_token
            
            try:
                response = gmaps.places_nearby(
                    page_token=response['next_page_token']
                )
                api_calls += 1
                page_count += 1
                
                if 'results' in response:
                    for place in response['results']:
                        place['search_zone'] = zone['name']
                        place['search_keyword'] = keyword
                        # Capture types from the search response (this is the key fix)
                        place['search_types'] = place.get('types', [])
                    places.extend(response['results'])
                    
            except Exception as e:
                logging.warning(f"Pagination error for '{keyword}' in {zone['name']}: {e}")
                break
    
    except Exception as e:
        logging.error(f"Error fetching places for '{keyword}' in {zone['name']}: {e}")
    
    return places, api_calls


def get_place_details_enhanced(gmaps, place_id, rate_limit=10):
    """Get detailed information for a place with enhanced fields."""
    try:
        time.sleep(1.0 / rate_limit)
        
        # Request specific fields (removed 'type' since it's often None in details API)
        fields = [
            'place_id', 'name', 'formatted_address', 'geometry',
            'rating', 'user_ratings_total', 'website',
            'opening_hours', 'formatted_phone_number', 'price_level',
            'business_status', 'vicinity'
        ]
        
        response = gmaps.place(
            place_id=place_id,
            fields=fields
        )
        
        return response.get('result', {})
    
    except Exception as e:
        logging.warning(f"Error fetching details for place_id '{place_id}': {e}")
        return {}


def is_relevant_business(name, business_types):
    """Filter out irrelevant business types that are not useful for pet wellness market analysis."""
    name_lower = name.lower()
    types_lower = [t.lower() for t in business_types] if business_types else []
    
    # Irrelevant business types to filter out
    irrelevant_types = [
        'loading_dock',
        'parking',
        'gas_station',
        'atm',
        'bus_station',
        'subway_station',
        'train_station',
        'airport',
        'lodging',
        'storage',
        'warehouse',
        'construction',
        'industrial',
        'utility',
        'government',
        'embassy',
        'cemetery',
        'funeral_home',
        'place_of_worship'
    ]
    
    # Irrelevant name patterns
    irrelevant_name_patterns = [
        'loading dock',
        'parking lot',
        'parking area',
        'gas station',
        'petrol station',
        'atm',
        'bank atm',
        'construction site',
        'warehouse',
        'storage facility'
    ]
    
    # Check if any irrelevant types match
    for irrelevant_type in irrelevant_types:
        if irrelevant_type in types_lower:
            return False
    
    # Check if any irrelevant name patterns match
    for pattern in irrelevant_name_patterns:
        if pattern in name_lower:
            return False
    
    return True


def classify_business(name, business_types, category, sub_category):
    """Enhanced classification based on name and types."""
    name_lower = name.lower()
    types_lower = [t.lower() for t in business_types] if business_types else []
    
    # Refine competitor sub-categories
    if category == 'Competitor':
        if sub_category == 'Clinic_General':
            # Check if it's actually a full-service clinic
            if any(word in name_lower for word in ['grooming', 'salon']):
                return 'Clinic+Grooming'
            elif '24' in name or '24/7' in name:
                return 'Emergency_Hospital'
            else:
                return 'Clinic_Only'
        elif sub_category == 'Emergency_Hospital':
            if '24' not in name and '24/7' not in name:
                return 'Clinic_Only'
    
    # Additional classification based on types
    if 'pet_store' in types_lower:
        if category == 'Customer' and 'pet' in name_lower:
            return 'Pet_Store'
    elif 'veterinary_care' in types_lower:
        if category == 'Competitor':
            return 'Clinic_Only'
    
    return sub_category


def process_place_for_output(place_details, category, sub_category, search_info, search_types=None):
    """Process place details into QGIS-ready format."""
    name = place_details.get('name', '')
    
    # Use search_types from the initial search response, fallback to details if needed
    business_types = search_types if search_types else place_details.get('type', [])
    
    refined_sub_category = classify_business(
        name,
        business_types,
        category,
        sub_category
    )
    
    # Extract business status
    business_status = place_details.get('business_status', 'OPERATIONAL')
    is_operational = business_status == 'OPERATIONAL'
    
    # Extract price level (for affluence indicators)
    price_level = place_details.get('price_level', '')
    if price_level:
        price_level = '$' * price_level  # Convert to $, $$, $$$, $$$$
    
    return {
        'place_id': place_details.get('place_id', ''),
        'name': name,
        'category': category,
        'sub_category': refined_sub_category,
        'latitude': place_details.get('geometry', {}).get('location', {}).get('lat', ''),
        'longitude': place_details.get('geometry', {}).get('location', {}).get('lng', ''),
        'address': place_details.get('formatted_address', ''),
        'vicinity': place_details.get('vicinity', ''),
        'rating': place_details.get('rating', ''),
        'review_count': place_details.get('user_ratings_total', 0),
        'website': place_details.get('website', ''),
        'phone': place_details.get('formatted_phone_number', ''),
        'price_level': price_level,
        'types': ', '.join(business_types),
        'is_operational': is_operational,
        'search_zone': search_info['zone'],
        'search_keyword': search_info['keyword'],
        'is_open_now': place_details.get('opening_hours', {}).get('open_now', ''),
        'timestamp': datetime.now().isoformat()
    }


def main():
    """Main execution function."""
    print("🐾 Comprehensive Pet Wellness Market Analysis Scraper")
    print("=" * 60)
    
    # Load configuration
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key or api_key == 'YOUR_API_KEY_HERE':
        print("❌ Error: Please set your Google Maps API key in .env file")
        return
    
    # Initialize Google Maps client
    gmaps = googlemaps.Client(key=api_key)
    
    # Load search zones and queries
    zones = load_search_zones()
    queries_df = load_queries_with_categories()
    
    if queries_df.empty:
        print("❌ Error: No queries loaded")
        return
    
    print(f"📍 Search zones: {len(zones)}")
    print(f"🔍 Search queries: {len(queries_df)}")
    print(f"💡 Total searches: {len(zones) * len(queries_df)}")
    print()
    
    # Master dictionary to store unique places
    unique_places = {}
    
    # Statistics
    stats = defaultdict(int)
    api_calls = 0
    
    # Process each zone
    for zone in zones:
        print(f"\n🗺️  Processing zone: {zone['name']}")
        print(f"   Location: {zone['location']}")
        print(f"   Radius: {zone['radius']}m")
        
        # Process each query in this zone
        zone_progress = tqdm(queries_df.iterrows(), 
                           total=len(queries_df),
                           desc=f"  {zone['name']}")
        
        for _, query in zone_progress:
            keyword = query['keyword']
            category = query['category']
            sub_category = query['sub_category']
            
            # Update progress bar
            zone_progress.set_postfix({'keyword': keyword[:20]})
            
            # Fetch places
            places, calls = fetch_places_for_zone_and_keyword(
                gmaps, keyword, zone, rate_limit=10
            )
            api_calls += calls
            stats[f'searches_{category}'] += 1
            
            # Process each place
            for place in places:
                place_id = place.get('place_id')
                
                if place_id and place_id not in unique_places:
                    # Get the types from the search response
                    search_types = place.get('search_types', [])
                    
                    # Get detailed information
                    details = get_place_details_enhanced(gmaps, place_id)
                    api_calls += 1
                    
                    if details:
                        # Check if this is a relevant business using search types
                        name = details.get('name', '')
                        
                        if is_relevant_business(name, search_types):
                            # Process and store, passing the search types
                            place_info = process_place_for_output(
                                details, category, sub_category,
                                {'zone': zone['name'], 'keyword': keyword},
                                search_types
                            )
                            unique_places[place_id] = place_info
                            stats[f'found_{category}'] += 1
                            stats[f'found_{sub_category}'] += 1
                        else:
                            stats['filtered_irrelevant'] += 1
    
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(unique_places, orient='index')
    
    # Sort by category and sub_category for better organization
    if not df.empty:
        df = df.sort_values(['category', 'sub_category', 'rating'], 
                          ascending=[True, True, False])
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'jakarta_pet_market_analysis_{timestamp}.csv'
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 60)
    
    print(f"\n🎯 Total unique places found: {len(unique_places)}")
    print(f"📞 Total API calls made: {api_calls}")
    print(f"🚫 Irrelevant results filtered: {stats.get('filtered_irrelevant', 0)}")
    
    # Category breakdown
    if not df.empty:
        print("\n📈 Results by Category:")
        category_counts = df['category'].value_counts()
        for cat, count in category_counts.items():
            print(f"   {cat}: {count}")
        
        print("\n🏢 Results by Sub-Category:")
        sub_category_counts = df['sub_category'].value_counts()
        for sub_cat, count in sub_category_counts.head(10).items():
            print(f"   {sub_cat}: {count}")
    
    # Cost estimation
    text_search_cost = api_calls * 0.017  # Places Nearby pricing
    print(f"\n💰 Estimated API cost: ${text_search_cost:.2f}")
    
    print(f"\n✅ Results saved to: {output_file}")
    print("\n🗺️  Ready for QGIS import!")
    print("   - Use 'Delimited Text Layer' import")
    print("   - X field: longitude")
    print("   - Y field: latitude")
    print("   - CRS: EPSG:4326 (WGS 84)")


if __name__ == "__main__":
    main()