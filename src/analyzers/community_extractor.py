#!/usr/bin/env python3
"""
Community-Centered Locations Extractor for Jakarta
Extracts ONLY community infrastructure and services without touching existing competitor data.
Uses Indonesian language settings and focuses on community-relevant categories.
"""

import os
import csv
import time
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Set, Tuple
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


def load_existing_place_ids(existing_dataset_path='jakarta_pet_market_CLEAN_20250805_102308.csv') -> Set[str]:
    """Load existing place_ids to avoid duplicates."""
    existing_ids = set()
    try:
        df = pd.read_csv(existing_dataset_path)
        existing_ids = set(df['place_id'].dropna().astype(str))
        logging.info(f"Loaded {len(existing_ids)} existing place_ids for deduplication")
    except Exception as e:
        logging.warning(f"Could not load existing dataset for deduplication: {e}")
    
    return existing_ids


def get_community_search_queries():
    """Define community-centered search queries with Indonesian language focus."""
    community_queries = [
        # Community_Infrastructure
        {'keyword': 'posyandu', 'category': 'Community_Infrastructure', 'sub_category': 'Health_Center', 'radius': 1000},
        {'keyword': 'balai RT', 'category': 'Community_Infrastructure', 'sub_category': 'Community_Hall', 'radius': 500},
        {'keyword': 'balai RW', 'category': 'Community_Infrastructure', 'sub_category': 'Community_Hall', 'radius': 800},
        {'keyword': 'pasar tradisional', 'category': 'Community_Infrastructure', 'sub_category': 'Traditional_Market', 'radius': 1500},
        {'keyword': 'warung kopi', 'category': 'Community_Infrastructure', 'sub_category': 'Local_Coffee_Shop', 'radius': 800},
        {'keyword': 'masjid', 'category': 'Community_Infrastructure', 'sub_category': 'Mosque', 'radius': 1000},
        {'keyword': 'gereja', 'category': 'Community_Infrastructure', 'sub_category': 'Church', 'radius': 1000},
        {'keyword': 'vihara', 'category': 'Community_Infrastructure', 'sub_category': 'Buddhist_Temple', 'radius': 1000},
        {'keyword': 'pura', 'category': 'Community_Infrastructure', 'sub_category': 'Hindu_Temple', 'radius': 1000},
        
        # Middle_Class_Accessibility
        {'keyword': 'Indomaret', 'category': 'Middle_Class_Accessibility', 'sub_category': 'Convenience_Store', 'radius': 800},
        {'keyword': 'Alfamart', 'category': 'Middle_Class_Accessibility', 'sub_category': 'Convenience_Store', 'radius': 800},
        {'keyword': 'bank lokal', 'category': 'Middle_Class_Accessibility', 'sub_category': 'Local_Bank', 'radius': 1000},
        {'keyword': 'BRI', 'category': 'Middle_Class_Accessibility', 'sub_category': 'Local_Bank', 'radius': 1000},
        {'keyword': 'BNI', 'category': 'Middle_Class_Accessibility', 'sub_category': 'Local_Bank', 'radius': 1000},
        {'keyword': 'Bank Mandiri', 'category': 'Middle_Class_Accessibility', 'sub_category': 'Local_Bank', 'radius': 1000},
        {'keyword': 'halte bus', 'category': 'Middle_Class_Accessibility', 'sub_category': 'Bus_Stop', 'radius': 500},
        {'keyword': 'halte transjakarta', 'category': 'Middle_Class_Accessibility', 'sub_category': 'Bus_Stop', 'radius': 500},
        {'keyword': 'puskesmas', 'category': 'Middle_Class_Accessibility', 'sub_category': 'Public_Health_Center', 'radius': 1500},
        
        # Family_Services
        {'keyword': 'SD negeri', 'category': 'Family_Services', 'sub_category': 'Public_Elementary_School', 'radius': 1000},
        {'keyword': 'sekolah dasar negeri', 'category': 'Family_Services', 'sub_category': 'Public_Elementary_School', 'radius': 1000},
        {'keyword': 'TK', 'category': 'Family_Services', 'sub_category': 'Kindergarten', 'radius': 800},
        {'keyword': 'taman kanak-kanak', 'category': 'Family_Services', 'sub_category': 'Kindergarten', 'radius': 800},
        {'keyword': 'PAUD', 'category': 'Family_Services', 'sub_category': 'Early_Childhood_Education', 'radius': 800},
        {'keyword': 'taman bermain', 'category': 'Family_Services', 'sub_category': 'Playground', 'radius': 1000},
        {'keyword': 'playground', 'category': 'Family_Services', 'sub_category': 'Playground', 'radius': 1000},
        {'keyword': 'apotek', 'category': 'Family_Services', 'sub_category': 'Pharmacy', 'radius': 800},
        {'keyword': 'kimia farma', 'category': 'Family_Services', 'sub_category': 'Pharmacy', 'radius': 800},
        {'keyword': 'guardian pharmacy', 'category': 'Family_Services', 'sub_category': 'Pharmacy', 'radius': 800},
        
        # Value_Conscious_Retail
        {'keyword': 'rumah makan padang', 'category': 'Value_Conscious_Retail', 'sub_category': 'Padang_Restaurant', 'radius': 1000},
        {'keyword': 'warung makan', 'category': 'Value_Conscious_Retail', 'sub_category': 'Local_Eatery', 'radius': 800},
        {'keyword': 'warteg', 'category': 'Value_Conscious_Retail', 'sub_category': 'Local_Eatery', 'radius': 800},
        {'keyword': 'laundry', 'category': 'Value_Conscious_Retail', 'sub_category': 'Laundry_Service', 'radius': 800},
        {'keyword': 'laundromat', 'category': 'Value_Conscious_Retail', 'sub_category': 'Laundry_Service', 'radius': 800},
        {'keyword': 'toko kelontong', 'category': 'Value_Conscious_Retail', 'sub_category': 'Grocery_Store', 'radius': 800},
        {'keyword': 'mini market', 'category': 'Value_Conscious_Retail', 'sub_category': 'Grocery_Store', 'radius': 800},
    ]
    
    return community_queries


def load_search_zones(zones_file='existing_zones_info.csv'):
    """Load search zones from CSV file."""
    zones = []
    try:
        df = pd.read_csv(zones_file)
        for _, row in df.iterrows():
            zones.append({
                'name': row['zone_name'],
                'location': (float(row['center_latitude']), float(row['center_longitude']))
            })
        logging.info(f"Loaded {len(zones)} search zones from {zones_file}")
        return zones
    except Exception as e:
        logging.error(f"Error loading search zones: {e}")
        # Fall back to major Jakarta zones
        return [
            {'name': 'Central_Jakarta_Core', 'location': (-6.191873873569024, 106.82447631026935)},
            {'name': 'South_Jakarta_Kemang', 'location': (-6.282365882317072, 106.80258046097559)},
            {'name': 'East_Jakarta_Cakung', 'location': (-6.204436410714286, 106.9663346419643)},
            {'name': 'West_Jakarta_Grogol', 'location': (-6.1597764166666655, 106.77269464666665)},
            {'name': 'North_Jakarta_PIK', 'location': (-6.110968844329898, 106.73049013195875)}
        ]


def fetch_places_for_zone_and_keyword(gmaps, keyword, zone, radius, existing_ids, rate_limit=8):
    """Fetch places for a specific zone and keyword combination using Indonesian language."""
    places = []
    api_calls = 0
    max_pages = 3  # Limit to prevent excessive API usage
    
    try:
        # Rate limiting - more conservative for community search
        time.sleep(1.2 / rate_limit)
        
        # Use Indonesian language setting for better local results
        response = gmaps.places_nearby(
            location=zone['location'],
            radius=radius,
            keyword=keyword,
            language='id'  # Indonesian language setting
        )
        api_calls += 1
        
        if 'results' in response:
            # Filter out existing places immediately
            for place in response['results']:
                place_id = place.get('place_id')
                if place_id and place_id not in existing_ids:
                    place['search_zone'] = zone['name']
                    place['search_keyword'] = keyword
                    place['search_types'] = place.get('types', [])
                    places.append(place)
        
        # Handle pagination
        page_count = 1
        while 'next_page_token' in response and page_count < max_pages:
            time.sleep(2.5)  # Required delay for next_page_token
            
            try:
                response = gmaps.places_nearby(
                    page_token=response['next_page_token'],
                    language='id'
                )
                api_calls += 1
                page_count += 1
                
                if 'results' in response:
                    for place in response['results']:
                        place_id = place.get('place_id')
                        if place_id and place_id not in existing_ids:
                            place['search_zone'] = zone['name']
                            place['search_keyword'] = keyword
                            place['search_types'] = place.get('types', [])
                            places.append(place)
                        
            except Exception as e:
                logging.warning(f"Pagination error for '{keyword}' in {zone['name']}: {e}")
                break
    
    except Exception as e:
        logging.error(f"Error fetching places for '{keyword}' in {zone['name']}: {e}")
    
    return places, api_calls


def get_place_details_enhanced(gmaps, place_id, rate_limit=8):
    """Get detailed information for a place with enhanced fields using Indonesian language."""
    try:
        time.sleep(1.2 / rate_limit)
        
        # Request specific fields with Indonesian language
        fields = [
            'place_id', 'name', 'formatted_address', 'geometry',
            'rating', 'user_ratings_total', 'website',
            'opening_hours', 'formatted_phone_number', 'price_level',
            'business_status', 'vicinity'
        ]
        
        response = gmaps.place(
            place_id=place_id,
            fields=fields,
            language='id'  # Indonesian language setting
        )
        
        return response.get('result', {})
    
    except Exception as e:
        logging.warning(f"Error fetching details for place_id '{place_id}': {e}")
        return {}


def is_relevant_community_place(name, business_types, category):
    """Filter to ensure we only get relevant community places."""
    name_lower = name.lower()
    types_lower = [t.lower() for t in business_types] if business_types else []
    
    # Exclude clearly irrelevant places
    irrelevant_types = [
        'parking', 'gas_station', 'atm', 'storage', 'warehouse',
        'construction', 'industrial', 'loading_dock', 'airport',
        'subway_station', 'train_station', 'embassy'
    ]
    
    irrelevant_names = [
        'parking', 'tempat parkir', 'loading dock', 'gudang',
        'konstruksi', 'industri', 'pabrik'
    ]
    
    # Check if any irrelevant types match
    for irrelevant_type in irrelevant_types:
        if irrelevant_type in types_lower:
            return False
    
    # Check if any irrelevant name patterns match
    for pattern in irrelevant_names:
        if pattern in name_lower:
            return False
    
    # Additional category-specific filtering
    if category == 'Community_Infrastructure':
        # For religious places, ensure they are actual places of worship
        if any(word in name_lower for word in ['masjid', 'gereja', 'vihara', 'pura', 'musholla']):
            return True
        # For traditional markets
        if any(word in name_lower for word in ['pasar', 'market']):
            return 'shopping_mall' not in types_lower  # Exclude modern malls
            
    elif category == 'Middle_Class_Accessibility':
        # For convenience stores, check for known chains
        if any(word in name_lower for word in ['indomaret', 'alfamart', 'circle k']):
            return True
        # For banks
        if any(word in name_lower for word in ['bank', 'bri', 'bni', 'mandiri', 'bca']):
            return True
            
    elif category == 'Family_Services':
        # For schools
        if any(word in name_lower for word in ['sd', 'sekolah', 'tk', 'paud']):
            return True
        # For pharmacies
        if any(word in name_lower for word in ['apotek', 'pharmacy', 'kimia farma', 'guardian']):
            return True
            
    elif category == 'Value_Conscious_Retail':
        # For local eateries
        if any(word in name_lower for word in ['warung', 'warteg', 'rumah makan', 'padang']):
            return True
        # For laundry
        if any(word in name_lower for word in ['laundry', 'laundromat', 'cuci']):
            return True
    
    return True


def calculate_popularity_score(rating, review_count):
    """Calculate a simple popularity score based on rating and review count."""
    if not rating or not review_count:
        return 0.0
    
    try:
        rating = float(rating)
        review_count = int(review_count)
        
        # Simple popularity formula: normalize rating (0-1) * log-scaled review count
        normalized_rating = (rating - 1) / 4  # Convert 1-5 scale to 0-1
        log_reviews = min(1.0, review_count / 1000)  # Cap at 1000 reviews = 1.0
        
        return round(normalized_rating * log_reviews, 2)
    except:
        return 0.0


def process_community_place_for_output(place_details, category, sub_category, search_info, search_types=None, radius=None):
    """Process place details into the exact 21-column format matching existing dataset."""
    name = place_details.get('name', '')
    
    # Use search_types from the initial search response
    business_types = search_types if search_types else []
    
    # Extract business status
    business_status = place_details.get('business_status', 'OPERATIONAL')
    is_operational = business_status == 'OPERATIONAL'
    
    # Extract price level
    price_level = place_details.get('price_level', '')
    if price_level:
        price_level = '$' * price_level  # Convert to $, $$, $$$, $$$$
    
    # Get coordinates
    lat = place_details.get('geometry', {}).get('location', {}).get('lat', '')
    lng = place_details.get('geometry', {}).get('location', {}).get('lng', '')
    
    # Get rating and review count for popularity score
    rating = place_details.get('rating', '')
    review_count = place_details.get('user_ratings_total', 0)
    popularity_score = calculate_popularity_score(rating, review_count)
    
    return {
        'place_id': place_details.get('place_id', ''),
        'name': name,
        'category': category,
        'sub_category': sub_category,
        'latitude': lat,
        'longitude': lng,
        'address': place_details.get('formatted_address', ''),
        'vicinity': place_details.get('vicinity', ''),
        'rating': rating,
        'review_count': review_count,
        'website': place_details.get('website', ''),
        'phone': place_details.get('formatted_phone_number', ''),
        'price_level': price_level,
        'types': ', '.join(business_types) if business_types else '',
        'is_operational': is_operational,
        'search_zone': search_info['zone'],
        'search_keyword': search_info['keyword'],
        'is_open_now': place_details.get('opening_hours', {}).get('open_now', ''),
        'timestamp': datetime.now().isoformat(),
        'popularity_score': popularity_score,
        'buffer_radius_m': radius or ''
    }


def main():
    """Main execution function for community extraction."""
    print("🏘️  Community-Centered Locations Extractor for Jakarta")
    print("=" * 60)
    print("Extracting ONLY community infrastructure and services")
    print("Using Indonesian language settings for better local results")
    print("=" * 60)
    
    # Load configuration
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key or api_key == 'YOUR_API_KEY_HERE':
        print("❌ Error: Please set your Google Maps API key in .env file")
        return
    
    # Initialize Google Maps client
    gmaps = googlemaps.Client(key=api_key)
    
    # Load existing place_ids for deduplication
    existing_ids = load_existing_place_ids()
    
    # Load search zones and community queries
    zones = load_search_zones()
    community_queries = get_community_search_queries()
    
    print(f"📍 Search zones: {len(zones)}")
    print(f"🔍 Community search queries: {len(community_queries)}")
    print(f"📋 Existing places to avoid: {len(existing_ids)}")
    print()
    
    # Dictionary to store unique places by place_id
    unique_places = {}
    
    # Counters for API calls and statistics
    nearby_search_calls = 0
    place_details_calls = 0
    total_found = 0
    duplicates_avoided = 0
    
    # Process each zone-query combination
    print("🔍 Searching for community places...")
    
    for zone in tqdm(zones, desc="Processing zones"):
        zone_places = 0
        
        for query in community_queries:
            keyword = query['keyword']
            category = query['category']
            sub_category = query['sub_category']
            radius = query['radius']
            
            # Fetch places for this zone-keyword combination
            places, api_calls = fetch_places_for_zone_and_keyword(
                gmaps, keyword, zone, radius, existing_ids, rate_limit=8
            )
            nearby_search_calls += api_calls
            
            # Process each place
            for place in places:
                place_id = place.get('place_id')
                
                # Skip if already processed or in existing dataset
                if place_id and place_id not in unique_places and place_id not in existing_ids:
                    # Check if it's a relevant community place
                    if is_relevant_community_place(
                        place.get('name', ''),
                        place.get('search_types', []),
                        category
                    ):
                        # Get detailed information
                        place_details = get_place_details_enhanced(gmaps, place_id, rate_limit=8)
                        place_details_calls += 1
                        
                        if place_details:
                            # Process and store place information
                            search_info = {
                                'zone': zone['name'],
                                'keyword': keyword
                            }
                            
                            place_info = process_community_place_for_output(
                                place_details, category, sub_category, search_info,
                                place.get('search_types', []), radius
                            )
                            
                            unique_places[place_id] = place_info
                            zone_places += 1
                            total_found += 1
                elif place_id in existing_ids:
                    duplicates_avoided += 1
        
        logging.info(f"Zone {zone['name']}: Found {zone_places} new community places")
    
    print()
    print("=" * 60)
    print("📊 EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"✅ Total new community places found: {total_found}")
    print(f"🔄 Duplicates avoided: {duplicates_avoided}")
    print(f"📡 Total API calls made: {nearby_search_calls + place_details_calls}")
    print(f"   - Nearby Search calls: {nearby_search_calls}")
    print(f"   - Place Details calls: {place_details_calls}")
    
    # Cost estimation (Google Maps pricing as of 2024)
    nearby_cost = nearby_search_calls * 0.032  # $0.032 per call
    details_cost = place_details_calls * 0.017  # $0.017 per call
    total_cost = nearby_cost + details_cost
    
    print()
    print("💰 ESTIMATED COST:")
    print(f"   - Nearby Search @ $0.032/call: ${nearby_cost:.2f}")
    print(f"   - Place Details @ $0.017/call: ${details_cost:.2f}")
    print(f"   - Total estimated cost: ${total_cost:.2f}")
    print()
    
    # Save results with timestamp
    if unique_places:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'jakarta_community_locations_{timestamp}.csv'
        
        # Convert to DataFrame with exact column order matching existing dataset
        columns = [
            'place_id', 'name', 'category', 'sub_category', 'latitude', 'longitude',
            'address', 'vicinity', 'rating', 'review_count', 'website', 'phone',
            'price_level', 'types', 'is_operational', 'search_zone', 'search_keyword',
            'is_open_now', 'timestamp', 'popularity_score', 'buffer_radius_m'
        ]
        
        df = pd.DataFrame.from_dict(unique_places, orient='index')
        df = df.reindex(columns=columns)  # Ensure exact column order
        
        try:
            df.to_csv(output_file, index=False)
            print(f"💾 Results saved to: {output_file}")
            print(f"📊 Dataset contains {len(df)} community locations")
            
            # Show category breakdown
            print()
            print("📈 CATEGORY BREAKDOWN:")
            category_counts = df['category'].value_counts()
            for category, count in category_counts.items():
                print(f"   - {category}: {count} locations")
            
            print()
            print("🎯 SUB-CATEGORY BREAKDOWN:")
            sub_category_counts = df['sub_category'].value_counts()
            for sub_category, count in sub_category_counts.items():
                print(f"   - {sub_category}: {count} locations")
                
        except Exception as e:
            logging.error(f"Error saving results: {e}")
            return
    else:
        print("⚠️  No new community places found to save.")
    
    print()
    print("✅ Community extraction completed!")
    print("💡 This dataset can be merged with existing pet market data for comprehensive analysis.")


if __name__ == "__main__":
    main()