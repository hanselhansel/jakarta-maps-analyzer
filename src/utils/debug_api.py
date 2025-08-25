#!/usr/bin/env python3
"""
Debug script to understand Google Places API response structure
"""

import os
from dotenv import load_dotenv
import googlemaps
import json

load_dotenv()
api_key = os.getenv('GOOGLE_MAPS_API_KEY')

if not api_key:
    print("Error: No API key found")
    exit(1)

# Initialize client
gmaps = googlemaps.Client(key=api_key)

print("🔍 Google Places API Debug Test")
print("=" * 50)

# First, do a simple search
print("\n1. Searching for Ranch Market in Kemang...")
search_response = gmaps.places_nearby(
    location=(-6.2600, 106.8130),
    radius=3000,
    keyword="Ranch Market"
)

if 'results' in search_response and search_response['results']:
    first_place = search_response['results'][0]
    place_id = first_place['place_id']
    
    print(f"\n✅ Found: {first_place.get('name', 'Unknown')}")
    print(f"   Place ID: {place_id}")
    
    # Check what fields are in the basic response
    print(f"\n2. Fields in basic search response:")
    for key in first_place.keys():
        print(f"   - {key}: {type(first_place[key])}")
    
    # Now get detailed information
    print(f"\n3. Getting place details...")
    
    # Try with just basic fields first
    basic_fields = ['place_id', 'name', 'formatted_address']
    basic_details = gmaps.place(place_id=place_id, fields=basic_fields)
    
    print(f"\n   Basic details retrieved successfully")
    
    # Try adding 'type' field
    print(f"\n4. Testing 'type' field...")
    try:
        with_type = gmaps.place(place_id=place_id, fields=['place_id', 'name', 'type'])
        if 'result' in with_type:
            type_value = with_type['result'].get('type')
            print(f"   ✅ 'type' field works! Value: {type_value}")
            print(f"   Type of value: {type(type_value)}")
    except Exception as e:
        print(f"   ❌ Error with 'type' field: {e}")
    
    # Try adding 'types' field (should fail)
    print(f"\n5. Testing 'types' field (should fail)...")
    try:
        with_types = gmaps.place(place_id=place_id, fields=['place_id', 'name', 'types'])
        print(f"   🤔 Unexpected: 'types' field worked?")
    except Exception as e:
        print(f"   ✅ Expected error with 'types' field: {e}")
    
    # Get all available data
    print(f"\n6. Getting all available fields...")
    all_fields = [
        'place_id', 'name', 'formatted_address', 'geometry',
        'rating', 'user_ratings_total', 'website', 'type',
        'opening_hours', 'formatted_phone_number', 'price_level',
        'business_status', 'vicinity'
    ]
    
    try:
        full_details = gmaps.place(place_id=place_id, fields=all_fields)
        if 'result' in full_details:
            result = full_details['result']
            print(f"\n   Full details retrieved!")
            print(f"\n   Key findings:")
            print(f"   - Name: {result.get('name')}")
            print(f"   - Type field value: {result.get('type')}")
            print(f"   - Type field type: {type(result.get('type'))}")
            
            # Save full response for inspection
            with open('api_debug_response.json', 'w') as f:
                json.dump(full_details, f, indent=2)
            print(f"\n   Full response saved to: api_debug_response.json")
            
    except Exception as e:
        print(f"   ❌ Error getting full details: {e}")

else:
    print("❌ No results found")

print("\n" + "=" * 50)
print("Debug complete!")