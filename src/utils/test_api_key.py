#!/usr/bin/env python3
"""
Google Maps API Key Test Script
This script safely tests the Google Maps API key functionality without exposing sensitive data.
"""

import os
import sys
import logging
from dotenv import load_dotenv
import googlemaps

def setup_logging():
    """Configure logging for the test script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def validate_api_key_format(api_key: str) -> bool:
    """Validate API key format without exposing the key."""
    if not api_key:
        logging.error("API key is empty or None")
        return False
    
    if len(api_key) < 35:
        logging.error("API key appears to be too short")
        return False
    
    if not api_key.startswith('AIza'):
        logging.error("API key doesn't start with expected prefix 'AIza'")
        return False
    
    logging.info(f"API key format validation passed (length: {len(api_key)})")
    return True

def test_api_key():
    """Test the Google Maps API key functionality."""
    setup_logging()
    
    logging.info("Google Maps API Key Test")
    logging.info("=" * 30)
    
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    if not api_key:
        logging.error("GOOGLE_MAPS_API_KEY environment variable not found")
        logging.error("Please ensure you have a .env file with your API key")
        return False
    
    # Validate API key format first
    if not validate_api_key_format(api_key):
        return False
    
    try:
        # Initialize Google Maps client
        logging.info("Initializing Google Maps client...")
        gmaps = googlemaps.Client(key=api_key)
        
        # Test 1: Simple geocoding request
        logging.info("Testing geocoding functionality...")
        result = gmaps.geocode("Jakarta, Indonesia")
        
        if result:
            location = result[0]['geometry']['location']
            logging.info(f"✓ Geocoding test passed - Jakarta coordinates: {location['lat']:.4f}, {location['lng']:.4f}")
        else:
            logging.warning("Geocoding returned empty results")
            return False
        
        # Test 2: Places search in Jakarta
        logging.info("Testing Places API functionality...")
        places_result = gmaps.places(
            query="restaurant",
            location=(-6.2088, 106.8456),  # Jakarta coordinates
            radius=1000  # 1km radius
        )
        
        if places_result and 'results' in places_result:
            num_places = len(places_result['results'])
            logging.info(f"✓ Places search test passed - Found {num_places} restaurants")
        else:
            logging.warning("Places search returned empty results")
            return False
        
        # Test 3: Check API quotas and billing status (this will show in API console)
        logging.info("API key tests completed successfully!")
        logging.info("✓ Your API key is working correctly")
        logging.info("")
        logging.info("Next steps:")
        logging.info("1. Monitor your API usage in the Google Cloud Console")
        logging.info("2. Set up billing alerts if not already configured")
        logging.info("3. Review your API quotas and limits")
        logging.info("4. Run the main scraper: python main.py")
        
        return True
        
    except googlemaps.exceptions.ApiError as e:
        logging.error(f"Google Maps API Error: {e}")
        logging.error("This could indicate:")
        logging.error("- Invalid API key")
        logging.error("- API key doesn't have required permissions")
        logging.error("- Billing not enabled")
        logging.error("- API quotas exceeded")
        return False
        
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return False

def main():
    """Main function."""
    success = test_api_key()
    
    if success:
        logging.info("\n🎉 API key test completed successfully!")
        sys.exit(0)
    else:
        logging.error("\n❌ API key test failed!")
        logging.error("Please check your API key and configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()