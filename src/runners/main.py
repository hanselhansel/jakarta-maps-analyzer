#!/usr/bin/env python3
"""
Google Maps Market Analysis Scraper
This script uses the Google Maps Platform API to collect location data for market analysis.
"""

import configparser
import time
import sys
import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import googlemaps
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraper.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def validate_api_key(api_key: str) -> bool:
    """Validate API key format and check for common issues."""
    if not api_key:
        return False
    
    # Check for placeholder values
    if api_key.lower() in ['your_api_key_here', 'api_key_here', 'placeholder']:
        return False
    
    # Basic format validation for Google API keys
    # Google API keys are typically 39 characters and start with 'AIza'
    if not re.match(r'^AIza[0-9A-Za-z-_]{35}$', api_key):
        logging.warning("API key doesn't match expected Google API key format")
        # Don't fail here as format might change, just warn
    
    return True

def sanitize_input(input_str: str, max_length: int = 100) -> str:
    """Sanitize and validate input strings."""
    if not isinstance(input_str, str):
        raise ValueError("Input must be a string")
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\';\\]', '', input_str.strip())
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
        logging.warning(f"Input truncated to {max_length} characters")
    
    return sanitized

def validate_coordinates(lat: float, lng: float) -> bool:
    """Validate latitude and longitude values."""
    return -90 <= lat <= 90 and -180 <= lng <= 180

def validate_radius(radius: int) -> bool:
    """Validate search radius."""
    # Google Places API has a maximum radius of 50,000 meters
    return 1 <= radius <= 50000

def load_config() -> Dict:
    """Load configuration from environment variables or config file."""
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    config = {}
    
    # Try to get API key from environment first (more secure)
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    if not api_key:
        # Fallback to config.ini
        config_parser = configparser.ConfigParser()
        config_path = 'config.ini'
        
        if Path(config_path).exists():
            config_parser.read(config_path)
            if 'Maps' in config_parser and 'api_key' in config_parser['Maps']:
                api_key = config_parser['Maps']['api_key']
    
    if not validate_api_key(api_key):
        logging.error("Invalid or missing API key. Please set GOOGLE_MAPS_API_KEY environment variable or config.ini")
        sys.exit(1)
    
    config['api_key'] = api_key
    
    # Get search parameters from environment or defaults
    try:
        config['latitude'] = float(os.getenv('SEARCH_LATITUDE', -6.2088))
        config['longitude'] = float(os.getenv('SEARCH_LONGITUDE', 106.8456))
        config['radius'] = int(os.getenv('SEARCH_RADIUS', 50000))
        config['rate_limit'] = int(os.getenv('API_RATE_LIMIT', 10))
    except ValueError as e:
        logging.error(f"Invalid configuration values: {e}")
        sys.exit(1)
    
    # Validate parameters
    if not validate_coordinates(config['latitude'], config['longitude']):
        logging.error("Invalid coordinates")
        sys.exit(1)
    
    if not validate_radius(config['radius']):
        logging.error("Invalid radius (must be between 1 and 50000 meters)")
        sys.exit(1)
    
    return config


def initialize_maps_client(api_key: str) -> googlemaps.Client:
    """Initialize the Google Maps client with the provided API key."""
    try:
        client = googlemaps.Client(key=api_key)
        # Test the API key with a simple request
        # client.geocode("test", language="en")  # Commented out - not needed for places_nearby
        return client
    except googlemaps.exceptions.ApiError as e:
        logging.error(f"Google Maps API error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error initializing Google Maps client: {e}")
        sys.exit(1)


def read_queries(queries_path: str = 'queries.csv') -> pd.DataFrame:
    """Read and validate search queries from the CSV file."""
    if not Path(queries_path).exists():
        logging.error(f"Queries file '{queries_path}' not found.")
        sys.exit(1)
    
    try:
        # Read with size limit to prevent memory issues
        queries_df = pd.read_csv(queries_path)
        
        # Validate required columns
        if 'keyword' not in queries_df.columns or 'category' not in queries_df.columns:
            logging.error("queries.csv must have 'keyword' and 'category' columns")
            sys.exit(1)
        
        # Limit number of queries to prevent excessive API usage
        max_queries = 100
        if len(queries_df) > max_queries:
            logging.warning(f"Too many queries ({len(queries_df)}). Limiting to {max_queries}")
            queries_df = queries_df.head(max_queries)
        
        # Sanitize inputs
        queries_df['keyword'] = queries_df['keyword'].apply(lambda x: sanitize_input(str(x), 100))
        queries_df['category'] = queries_df['category'].apply(lambda x: sanitize_input(str(x), 50))
        
        # Remove empty queries
        queries_df = queries_df[queries_df['keyword'].str.strip() != '']
        
        if len(queries_df) == 0:
            logging.error("No valid queries found after sanitization")
            sys.exit(1)
        
        return queries_df
        
    except Exception as e:
        logging.error(f"Error reading queries file: {e}")
        sys.exit(1)


def fetch_places_for_keyword(gmaps: googlemaps.Client, keyword: str, location: Tuple[float, float], radius: int, rate_limit: int = 10) -> Tuple[List[Dict], int]:
    """Fetch all places for a given keyword, handling pagination with rate limiting."""
    places = []
    api_calls = 0
    max_pages = 3  # Limit pagination to prevent excessive API usage
    
    try:
        # Rate limiting
        time.sleep(1.0 / rate_limit)
        
        # Initial search using places_nearby
        response = gmaps.places_nearby(
            location=location,
            radius=radius,
            keyword=keyword
        )
        api_calls += 1
        
        if 'results' in response:
            places.extend(response['results'])
        
        # Handle pagination with limits
        page_count = 1
        while 'next_page_token' in response and page_count < max_pages:
            # API requires a short delay before using next_page_token
            time.sleep(max(2, 1.0 / rate_limit))
            
            try:
                response = gmaps.places_nearby(
                    page_token=response['next_page_token']
                )
                api_calls += 1
                page_count += 1
                
                if 'results' in response:
                    places.extend(response['results'])
                    
            except googlemaps.exceptions.ApiError as e:
                logging.warning(f"API error during pagination for '{keyword}': {e}")
                break
    
    except googlemaps.exceptions.ApiError as e:
        logging.warning(f"API error fetching places for keyword '{keyword}': {e}")
    except Exception as e:
        logging.warning(f"Unexpected error fetching places for keyword '{keyword}': {e}")
    
    return places, api_calls


def get_place_details(gmaps: googlemaps.Client, place_id: str, rate_limit: int = 10) -> Dict:
    """Get detailed information for a specific place with rate limiting."""
    if not place_id or not isinstance(place_id, str):
        logging.warning("Invalid place_id provided")
        return {}
    
    try:
        # Rate limiting
        time.sleep(1.0 / rate_limit)
        
        # Specify fields to control costs
        fields = [
            'place_id', 'name', 'formatted_address', 'geometry',
            'rating', 'user_ratings_total', 'website', 'type', 'opening_hours'
        ]
        
        response = gmaps.place(
            place_id=place_id,
            fields=fields
        )
        
        return response.get('result', {})
    
    except googlemaps.exceptions.ApiError as e:
        logging.warning(f"API error fetching details for place_id '{place_id}': {e}")
        return {}
    except Exception as e:
        logging.warning(f"Unexpected error fetching details for place_id '{place_id}': {e}")
        return {}


def extract_place_info(place_details: Dict, category: str) -> Dict:
    """Extract and sanitize relevant information from place details."""
    # Sanitize category input
    safe_category = sanitize_input(category, 50)
    
    info = {
        'place_id': place_details.get('place_id', ''),
        'name': sanitize_input(str(place_details.get('name', '')), 200),
        'category': safe_category,
        'address': sanitize_input(str(place_details.get('formatted_address', '')), 300),
        'latitude': '',
        'longitude': '',
        'rating': place_details.get('rating', ''),
        'review_count': place_details.get('user_ratings_total', 0),
        'website': place_details.get('website', ''),
        'types': sanitize_input(str(place_details.get('type', '')), 50),
        'is_open_now': ''
    }
    
    # Extract and validate coordinates
    if 'geometry' in place_details and 'location' in place_details['geometry']:
        lat = place_details['geometry']['location'].get('lat', '')
        lng = place_details['geometry']['location'].get('lng', '')
        
        # Validate coordinates before storing
        if isinstance(lat, (int, float)) and isinstance(lng, (int, float)):
            if validate_coordinates(lat, lng):
                info['latitude'] = lat
                info['longitude'] = lng
    
    # Extract opening hours
    if 'opening_hours' in place_details:
        info['is_open_now'] = place_details['opening_hours'].get('open_now', '')
    
    # Ensure review_count is numeric
    try:
        info['review_count'] = int(info['review_count']) if info['review_count'] else 0
    except (ValueError, TypeError):
        info['review_count'] = 0
    
    return info


def main():
    """Main execution function."""
    # Setup logging first
    setup_logging()
    
    logging.info("Google Maps Market Analysis Scraper")
    logging.info("=" * 40)
    
    # Load configuration
    config = load_config()
    api_key = config['api_key']
    
    # Get search parameters
    location = (config['latitude'], config['longitude'])
    radius = config['radius']
    rate_limit = config['rate_limit']
    
    logging.info(f"Search location: {location}")
    logging.info(f"Search radius: {radius} meters")
    logging.info(f"Rate limit: {rate_limit} requests/second")
    logging.info("")
    
    # Initialize Google Maps client
    gmaps = initialize_maps_client(api_key)
    
    # Read queries
    queries_df = read_queries()
    logging.info(f"Loaded {len(queries_df)} search queries")
    logging.info("")
    
    # Dictionary to store unique places by place_id
    unique_places = {}
    
    # Counters for API calls
    text_search_calls = 0
    place_details_calls = 0
    
    # Process each query
    logging.info("Fetching places...")
    for _, row in tqdm(queries_df.iterrows(), total=len(queries_df), desc="Processing queries"):
        keyword = row['keyword']
        category = row['category']
        
        # Fetch places for this keyword
        places, api_calls = fetch_places_for_keyword(gmaps, keyword, location, radius, rate_limit)
        text_search_calls += api_calls
        
        # Process each place
        for place in places:
            place_id = place.get('place_id')
            
            # Skip if we've already processed this place
            if place_id and place_id not in unique_places:
                # Get detailed information
                place_details = get_place_details(gmaps, place_id, rate_limit)
                place_details_calls += 1
                
                if place_details:
                    # Extract and store information
                    place_info = extract_place_info(place_details, category)
                    unique_places[place_id] = place_info
    
    logging.info("")
    logging.info("=" * 40)
    logging.info("Summary:")
    logging.info(f"Total unique places found: {len(unique_places)}")
    logging.info(f"Total API calls made: {text_search_calls + place_details_calls}")
    logging.info(f"  - Text Search calls: {text_search_calls}")
    logging.info(f"  - Place Details calls: {place_details_calls}")
    
    # Cost estimation (prices as of 2024, may change)
    text_search_cost = text_search_calls * 0.032
    place_details_cost = place_details_calls * 0.017
    total_cost = text_search_cost + place_details_cost
    
    logging.info("")
    logging.info("Estimated cost (based on standard pricing):")
    logging.info(f"  - Text Search @ $0.032/call: ${text_search_cost:.2f}")
    logging.info(f"  - Place Details @ $0.017/call: ${place_details_cost:.2f}")
    logging.info(f"  - Total estimated cost: ${total_cost:.2f}")
    logging.info("")
    
    # Convert to DataFrame and save with timestamp
    if unique_places:
        df = pd.DataFrame.from_dict(unique_places, orient='index')
        
        # Generate secure filename with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = f'jakarta_market_analysis_{timestamp}.csv'
        
        # Save with error handling
        try:
            df.to_csv(output_file, index=False)
            logging.info(f"Results saved to: {output_file}")
        except Exception as e:
            logging.error(f"Error saving results: {e}")
            sys.exit(1)
    else:
        logging.warning("No places found to save.")
    
    logging.info("")
    logging.info("Done!")


if __name__ == "__main__":
    main()