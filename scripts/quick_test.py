#!/usr/bin/env python3
"""Quick test to verify Google Maps API setup"""

import os
from dotenv import load_dotenv
import googlemaps

# Load environment variables
load_dotenv()
api_key = os.getenv('GOOGLE_MAPS_API_KEY')

if not api_key:
    print("❌ No API key found! Please set GOOGLE_MAPS_API_KEY in .env file")
    exit(1)

print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")

try:
    # Initialize client
    gmaps = googlemaps.Client(key=api_key)
    
    # Simple test - search for a well-known place in Jakarta
    print("\nTesting Places search for 'Monas Jakarta'...")
    results = gmaps.places('Monas Jakarta')
    
    if results['results']:
        place = results['results'][0]
        print(f"✅ Success! Found: {place['name']}")
        print(f"   Address: {place.get('formatted_address', 'N/A')}")
        print(f"   Place ID: {place['place_id']}")
        print("\n🎉 Your API key is working correctly!")
    else:
        print("❌ No results found (but API is working)")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nPlease ensure:")
    print("1. Places API is enabled in Google Cloud Console")
    print("2. Billing is set up for your project")
    print("3. Your API key has proper restrictions")
    print("\nVisit: https://console.cloud.google.com/")