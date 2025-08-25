#!/usr/bin/env python3
"""
API Fix Verification Script
This script tests specific API endpoints to verify that the required APIs are enabled.
"""

import os
import sys
import logging
from dotenv import load_dotenv
import googlemaps
import time

def setup_logging():
    """Configure logging for the verification script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def test_places_api(gmaps):
    """Test Places API functionality specifically."""
    print("\n🔍 Testing Places API...")
    
    try:
        # Test 1: places_nearby (used by community_extractor.py)
        print("   Testing places_nearby...")
        nearby_result = gmaps.places_nearby(
            location=(-6.2088, 106.8456),  # Jakarta center
            radius=1000,
            keyword="restaurant"
        )
        
        if 'results' in nearby_result and nearby_result['results']:
            print(f"   ✅ places_nearby works - Found {len(nearby_result['results'])} places")
        else:
            print("   ⚠️  places_nearby returned no results")
            return False
            
        # Test 2: place details (used for detailed information)
        if nearby_result['results']:
            place_id = nearby_result['results'][0]['place_id']
            print("   Testing place details...")
            
            detail_result = gmaps.place(
                place_id=place_id,
                fields=['place_id', 'name', 'formatted_address', 'rating']
            )
            
            if 'result' in detail_result:
                place_name = detail_result['result'].get('name', 'Unknown')
                print(f"   ✅ place details works - Got details for: {place_name}")
            else:
                print("   ⚠️  place details returned no result")
                return False
        
        return True
        
    except googlemaps.exceptions.ApiError as e:
        print(f"   ❌ Places API Error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_geocoding_api(gmaps):
    """Test Geocoding API functionality."""
    print("\n🌍 Testing Geocoding API...")
    
    try:
        result = gmaps.geocode("Jakarta, Indonesia")
        
        if result:
            location = result[0]['geometry']['location']
            print(f"   ✅ Geocoding works - Jakarta: {location['lat']:.4f}, {location['lng']:.4f}")
            return True
        else:
            print("   ⚠️  Geocoding returned no results")
            return False
            
    except googlemaps.exceptions.ApiError as e:
        print(f"   ❌ Geocoding API Error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_community_extractor_simulation(gmaps):
    """Simulate the exact calls made by community_extractor.py."""
    print("\n🏘️  Testing Community Extractor Simulation...")
    
    try:
        # Test with Indonesian language setting (like community_extractor.py)
        print("   Testing Indonesian language places search...")
        result = gmaps.places_nearby(
            location=(-6.2088, 106.8456),
            radius=1000,
            keyword="masjid",  # Indonesian for mosque
            language='id'
        )
        
        if 'results' in result and result['results']:
            print(f"   ✅ Indonesian places search works - Found {len(result['results'])} mosques")
            
            # Test place details with Indonesian language
            place_id = result['results'][0]['place_id']
            detail_result = gmaps.place(
                place_id=place_id,
                fields=['place_id', 'name', 'formatted_address'],
                language='id'
            )
            
            if 'result' in detail_result:
                place_name = detail_result['result'].get('name', 'Unknown')
                print(f"   ✅ Indonesian place details works - Got: {place_name}")
                return True
            else:
                print("   ⚠️  Indonesian place details failed")
                return False
        else:
            print("   ⚠️  Indonesian places search returned no results")
            return False
            
    except googlemaps.exceptions.ApiError as e:
        print(f"   ❌ Community Extractor Simulation Error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def main():
    """Main verification function."""
    setup_logging()
    
    print("🔧 Google Maps API Fix Verification")
    print("=" * 50)
    print("This script verifies that the required APIs are now enabled.")
    print()
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    if not api_key:
        print("❌ Error: GOOGLE_MAPS_API_KEY not found in environment")
        return False
    
    print(f"📋 API Key loaded (length: {len(api_key)})")
    
    try:
        # Initialize Google Maps client
        gmaps = googlemaps.Client(key=api_key)
        print("✅ Google Maps client initialized")
        
        # Run all tests
        tests_passed = 0
        total_tests = 3
        
        if test_geocoding_api(gmaps):
            tests_passed += 1
            
        if test_places_api(gmaps):
            tests_passed += 1
            
        if test_community_extractor_simulation(gmaps):
            tests_passed += 1
        
        print()
        print("=" * 50)
        print("📊 VERIFICATION RESULTS")
        print("=" * 50)
        print(f"Tests passed: {tests_passed}/{total_tests}")
        
        if tests_passed == total_tests:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Your API is ready for community extraction")
            print()
            print("Next steps:")
            print("1. Run: python3 community_extractor.py")
            print("2. Monitor progress and API usage")
            return True
        else:
            print("⚠️  Some tests failed")
            print("Please ensure the following APIs are enabled:")
            print("- Places API")
            print("- Geocoding API")
            return False
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)