#!/usr/bin/env python3
"""
Simple Community Extractor - Based on Working Pet Market Scraper
Uses EXACTLY the same APIs and structure as the successful main_comprehensive.py
Only changes the search keywords to community-focused terms.
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
    """Load search zones from CSV file - EXACT COPY from working script."""
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


def get_community_queries_dataframe():
    """Get community queries in DataFrame format matching working script structure."""
    community_queries = [
        # Community Infrastructure
        {'keyword': 'posyandu', 'category': 'Community_Infrastructure', 'sub_category': 'Health_Center'},
        {'keyword': 'balai RT', 'category': 'Community_Infrastructure', 'sub_category': 'Community_Hall'},
        {'keyword': 'balai RW', 'category': 'Community_Infrastructure', 'sub_category': 'Community_Hall'},
        {'keyword': 'pasar tradisional', 'category': 'Community_Infrastructure', 'sub_category': 'Traditional_Market'},
        {'keyword': 'warung kopi', 'category': 'Community_Infrastructure', 'sub_category': 'Local_Coffee_Shop'},
        {'keyword': 'masjid', 'category': 'Community_Infrastructure', 'sub_category': 'Mosque'},
        {'keyword': 'gereja', 'category': 'Community_Infrastructure', 'sub_category': 'Church'},
        
        # Middle Class Accessibility
        {'keyword': 'Indomaret', 'category': 'Middle_Class_Accessibility', 'sub_category': 'Convenience_Store'},
        {'keyword': 'Alfamart', 'category': 'Middle_Class_Accessibility', 'sub_category': 'Convenience_Store'},
        {'keyword': 'bank BRI', 'category': 'Middle_Class_Accessibility', 'sub_category': 'Local_Bank'},
        {'keyword': 'bank BNI', 'category': 'Middle_Class_Accessibility', 'sub_category': 'Local_Bank'},
        {'keyword': 'halte transjakarta', 'category': 'Middle_Class_Accessibility', 'sub_category': 'Bus_Stop'},
        {'keyword': 'puskesmas', 'category': 'Middle_Class_Accessibility', 'sub_category': 'Public_Health_Center'},
        
        # Family Services  
        {'keyword': 'SD negeri', 'category': 'Family_Services', 'sub_category': 'Public_Elementary_School'},
        {'keyword': 'TK', 'category': 'Family_Services', 'sub_category': 'Kindergarten'},
        {'keyword': 'PAUD', 'category': 'Family_Services', 'sub_category': 'Early_Childhood_Education'},
        {'keyword': 'apotek', 'category': 'Family_Services', 'sub_category': 'Pharmacy'},
        {'keyword': 'playground', 'category': 'Family_Services', 'sub_category': 'Playground'},
        
        # Value Conscious Retail
        {'keyword': 'rumah makan padang', 'category': 'Value_Conscious_Retail', 'sub_category': 'Padang_Restaurant'},
        {'keyword': 'warung makan', 'category': 'Value_Conscious_Retail', 'sub_category': 'Local_Eatery'},
        {'keyword': 'warteg', 'category': 'Value_Conscious_Retail', 'sub_category': 'Local_Eatery'},
        {'keyword': 'laundry', 'category': 'Value_Conscious_Retail', 'sub_category': 'Laundry_Service'},
        {'keyword': 'mini market', 'category': 'Value_Conscious_Retail', 'sub_category': 'Grocery_Store'},
    ]
    
    return pd.DataFrame(community_queries)


def fetch_places_for_zone_and_keyword(gmaps, keyword, zone, rate_limit=10):
    """Fetch places for a specific zone and keyword - EXACT COPY from working script."""
    places = []
    api_calls = 0
    max_pages = 3  # Limit to prevent excessive API usage
    
    try:
        # Rate limiting
        time.sleep(1.0 / rate_limit)
        
        # Initial search - SAME API CALL AS WORKING SCRIPT
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
        
        # Handle pagination - SAME AS WORKING SCRIPT
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
    """Get detailed information for a place - EXACT COPY from working script."""
    try:
        time.sleep(1.0 / rate_limit)
        
        # Request specific fields - SAME AS WORKING SCRIPT
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
    """Filter out irrelevant businesses - EXACT COPY from working script."""
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
    """Enhanced classification - EXACT COPY from working script."""
    name_lower = name.lower()
    types_lower = [t.lower() for t in business_types] if business_types else []
    
    # Keep original classification logic but for community categories
    return sub_category


def calculate_popularity_score(rating, review_count):
    """Calculate popularity score."""
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


def process_place_for_output(place_details, category, sub_category, search_info, search_types=None):
    """Process place details - EXACT COPY from working script with popularity score added."""
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
    
    # Calculate popularity score
    rating = place_details.get('rating', '')
    review_count = place_details.get('user_ratings_total', 0)
    popularity_score = calculate_popularity_score(rating, review_count)
    
    return {
        'place_id': place_details.get('place_id', ''),
        'name': name,
        'category': category,
        'sub_category': refined_sub_category,
        'latitude': place_details.get('geometry', {}).get('location', {}).get('lat', ''),
        'longitude': place_details.get('geometry', {}).get('location', {}).get('lng', ''),
        'address': place_details.get('formatted_address', ''),
        'vicinity': place_details.get('vicinity', ''),
        'rating': rating,
        'review_count': review_count,
        'website': place_details.get('website', ''),
        'phone': place_details.get('formatted_phone_number', ''),
        'price_level': price_level,
        'types': ', '.join(business_types),
        'is_operational': is_operational,
        'search_zone': search_info['zone'],
        'search_keyword': search_info['keyword'],
        'is_open_now': place_details.get('opening_hours', {}).get('open_now', ''),
        'timestamp': datetime.now().isoformat(),
        'popularity_score': popularity_score,
        'buffer_radius_m': ''
    }


def main():
    """Main execution function - EXACT STRUCTURE as working script."""
    print("🏘️  Simple Community Extractor (Based on Working Pet Market Script)")
    print("=" * 70)
    
    # Load configuration - SAME AS WORKING SCRIPT
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key or api_key == 'YOUR_API_KEY_HERE':
        print("❌ Error: Please set your Google Maps API key in .env file")
        return
    
    # Initialize Google Maps client - SAME AS WORKING SCRIPT
    gmaps = googlemaps.Client(key=api_key)
    
    # Load search zones and queries - SAME STRUCTURE AS WORKING SCRIPT
    zones = load_search_zones()
    queries_df = get_community_queries_dataframe()
    
    if queries_df.empty:
        print("❌ Error: No queries loaded")
        return
    
    print(f"📍 Search zones: {len(zones)}")
    print(f"🔍 Search queries: {len(queries_df)}")
    print(f"💡 Total searches: {len(zones) * len(queries_df)}")
    print()
    
    # Master dictionary to store unique places - SAME AS WORKING SCRIPT
    unique_places = {}
    
    # Statistics - SAME AS WORKING SCRIPT
    stats = defaultdict(int)
    api_calls = 0
    
    # Process each zone - EXACT SAME LOOP STRUCTURE AS WORKING SCRIPT
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
            
            # Fetch places - SAME FUNCTION CALL AS WORKING SCRIPT
            places, calls = fetch_places_for_zone_and_keyword(
                gmaps, keyword, zone, rate_limit=10
            )
            api_calls += calls
            stats[f'searches_{category}'] += 1
            
            # Process each place - SAME LOOP AS WORKING SCRIPT
            for place in places:
                place_id = place.get('place_id')
                
                if place_id and place_id not in unique_places:
                    # Get the types from the search response
                    search_types = place.get('search_types', [])
                    
                    # Get detailed information - SAME API CALL AS WORKING SCRIPT
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
    
    # Convert to DataFrame - SAME AS WORKING SCRIPT
    df = pd.DataFrame.from_dict(unique_places, orient='index')
    
    # Sort by category and sub_category - SAME AS WORKING SCRIPT
    if not df.empty:
        df = df.sort_values(['category', 'sub_category', 'rating'], 
                          ascending=[True, True, False])
    
    # Save results - SAME AS WORKING SCRIPT
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'jakarta_community_simple_{timestamp}.csv'
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    # Print summary - SAME AS WORKING SCRIPT
    print("\n" + "=" * 60)
    print("📊 COMMUNITY EXTRACTION SUMMARY")
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
    
    # Cost estimation - SAME AS WORKING SCRIPT
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