#!/usr/bin/env python3
"""
Test script for Community Extractor
Validates setup and runs a limited test extraction to verify functionality.
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
import googlemaps
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()


def test_api_key():
    """Test if the Google Maps API key is properly configured."""
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    if not api_key or api_key == 'YOUR_API_KEY_HERE':
        print("❌ Error: Google Maps API key not configured")
        print("Please set GOOGLE_MAPS_API_KEY in your .env file")
        return None
    
    try:
        gmaps = googlemaps.Client(key=api_key)
        # Test with a simple geocoding request
        result = gmaps.geocode("Jakarta, Indonesia")
        if result:
            print("✅ Google Maps API key is valid and working")
            return gmaps
        else:
            print("❌ API key validation failed - no results returned")
            return None
    except Exception as e:
        print(f"❌ API key validation failed: {e}")
        return None


def test_file_dependencies():
    """Test if required files exist."""
    files_to_check = [
        'existing_zones_info.csv',
        'jakarta_pet_market_CLEAN_20250805_102308.csv'
    ]
    
    missing_files = []
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ Found: {file_path}")
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    return True


def test_existing_data_loading():
    """Test loading existing datasets."""
    try:
        # Test loading existing zones
        zones_df = pd.read_csv('existing_zones_info.csv')
        print(f"✅ Loaded {len(zones_df)} search zones")
        
        # Test loading existing dataset for deduplication
        existing_df = pd.read_csv('jakarta_pet_market_CLEAN_20250805_102308.csv')
        existing_ids = set(existing_df['place_id'].dropna().astype(str))
        print(f"✅ Loaded {len(existing_ids)} existing place_ids for deduplication")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading existing data: {e}")
        return False


def run_limited_test_extraction(gmaps):
    """Run a very limited test extraction to verify the extraction logic works."""
    print("\n🧪 Running limited test extraction...")
    
    # Test with just one zone and one query
    test_zone = {
        'name': 'Central_Jakarta_Core',
        'location': (-6.191873873569024, 106.82447631026935)
    }
    
    test_query = {
        'keyword': 'Indomaret',
        'category': 'Middle_Class_Accessibility',
        'sub_category': 'Convenience_Store',
        'radius': 800
    }
    
    try:
        # Simulate the search
        response = gmaps.places_nearby(
            location=test_zone['location'],
            radius=test_query['radius'],
            keyword=test_query['keyword'],
            language='id'
        )
        
        if 'results' in response and len(response['results']) > 0:
            test_results = len(response['results'])
            print(f"✅ Test search returned {test_results} results")
            
            # Test place details for first result
            first_place = response['results'][0]
            place_id = first_place.get('place_id')
            
            if place_id:
                details = gmaps.place(
                    place_id=place_id,
                    fields=['place_id', 'name', 'formatted_address', 'geometry'],
                    language='id'
                )
                
                if 'result' in details:
                    test_place_name = details['result'].get('name', 'Unknown')
                    print(f"✅ Place details retrieval successful: {test_place_name}")
                    return True
                else:
                    print("❌ Place details retrieval failed")
                    return False
            else:
                print("❌ No place_id in search results")
                return False
        else:
            print("⚠️  Test search returned no results (this may be normal)")
            return True  # Still consider this a pass as the API is working
            
    except Exception as e:
        print(f"❌ Test extraction failed: {e}")
        return False


def main():
    """Run all tests to validate community extractor setup."""
    print("🧪 Community Extractor Setup Validation")
    print("="*50)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: API Key
    print("\n1️⃣  Testing Google Maps API key...")
    gmaps = test_api_key()
    if gmaps:
        tests_passed += 1
    
    # Test 2: File Dependencies
    print("\n2️⃣  Checking required files...")
    if test_file_dependencies():
        tests_passed += 1
    
    # Test 3: Data Loading
    print("\n3️⃣  Testing data loading...")
    if test_existing_data_loading():
        tests_passed += 1
    
    # Test 4: Limited Extraction
    if gmaps:
        print("\n4️⃣  Testing extraction functionality...")
        if run_limited_test_extraction(gmaps):
            tests_passed += 1
    else:
        print("\n4️⃣  Skipping extraction test (API key not working)")
    
    # Results
    print("\n" + "="*50)
    print("📊 TEST RESULTS")
    print("="*50)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("✅ All tests passed! Community extractor is ready to run.")
        print("\n🚀 To run the full extraction:")
        print("   python community_extractor.py")
        print("\n📋 To merge results with existing data:")
        print("   python merge_community_data.py <community_file>")
    else:
        print("❌ Some tests failed. Please fix the issues above before running the extractor.")
        
    return tests_passed == total_tests


if __name__ == "__main__":
    main()