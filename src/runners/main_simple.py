#!/usr/bin/env python3
"""
Simplified Google Maps Scraper - Testing Basic Functionality
"""

import os
import csv
from dotenv import load_dotenv
import googlemaps
from datetime import datetime

# Load environment variables
load_dotenv()
api_key = os.getenv('GOOGLE_MAPS_API_KEY')

if not api_key:
    print("Error: No API key found in .env file")
    exit(1)

# Initialize Google Maps client
gmaps = googlemaps.Client(key=api_key)

# Test location (Central Jakarta)
location = (-6.2088, 106.8456)
radius = 50000

# Read queries
queries = []
with open('queries.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        queries.append(row)

print(f"Testing with {len(queries)} queries...")
print("=" * 50)

# Store unique places
all_places = {}

# Process each query
for query in queries[:3]:  # Test with first 3 queries only
    keyword = query['keyword']
    category = query['category']
    
    print(f"\nSearching for: {keyword} (Category: {category})")
    
    try:
        # Use places_nearby instead of text search
        response = gmaps.places_nearby(
            location=location,
            radius=radius,
            keyword=keyword
        )
        
        if 'results' in response:
            print(f"  Found {len(response['results'])} places")
            
            for place in response['results']:
                place_id = place.get('place_id')
                if place_id and place_id not in all_places:
                    all_places[place_id] = {
                        'name': place.get('name', ''),
                        'category': category,
                        'address': place.get('vicinity', ''),
                        'place_id': place_id
                    }
        else:
            print(f"  No results found")
            
    except Exception as e:
        print(f"  Error: {e}")

print("\n" + "=" * 50)
print(f"Total unique places found: {len(all_places)}")

# Save results
if all_places:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'jakarta_results_{timestamp}.csv'
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['place_id', 'name', 'category', 'address']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for place in all_places.values():
            writer.writerow(place)
    
    print(f"Results saved to: {output_file}")
else:
    print("No results to save")

print("\nDone!")