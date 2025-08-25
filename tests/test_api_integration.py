"""
Unit tests for Google Maps API integration functionality.
"""
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
import googlemaps
from googlemaps.exceptions import ApiError

# Add the parent directory to sys.path so we can import main
sys.path.insert(0, str(Path(__file__).parent.parent))

import main


class TestGoogleMapsClientInitialization:
    """Test Google Maps client initialization."""
    
    @pytest.fixture
    def mock_googlemaps_client(self):
        """Fixture providing a mock Google Maps client."""
        mock_client = Mock(spec=googlemaps.Client)
        mock_client.geocode.return_value = [{"formatted_address": "Test Address"}]
        return mock_client
    
    @pytest.mark.unit
    @patch('googlemaps.Client')
    def test_initialize_maps_client_success(self, mock_client_class, mock_googlemaps_client):
        """Test successful Google Maps client initialization."""
        mock_client_class.return_value = mock_googlemaps_client
        
        api_key = "AIzaSyDummyTestKeyFor39CharacterString"
        client = main.initialize_maps_client(api_key)
        
        mock_client_class.assert_called_once_with(key=api_key)
        mock_googlemaps_client.geocode.assert_called_once_with("test", language="en")
        assert client == mock_googlemaps_client
    
    @pytest.mark.unit
    @patch('googlemaps.Client')
    def test_initialize_maps_client_api_error_exits(self, mock_client_class):
        """Test that API error during initialization causes system exit."""
        mock_client = Mock(spec=googlemaps.Client)
        mock_client.geocode.side_effect = ApiError("Invalid API key")
        mock_client_class.return_value = mock_client
        
        api_key = "invalid_key"
        with pytest.raises(SystemExit) as exc_info:
            main.initialize_maps_client(api_key)
        
        assert exc_info.value.code == 1
    
    @pytest.mark.unit
    @patch('googlemaps.Client')
    def test_initialize_maps_client_general_error_exits(self, mock_client_class):
        """Test that general error during initialization causes system exit."""
        mock_client_class.side_effect = Exception("Connection error")
        
        api_key = "valid_key"
        with pytest.raises(SystemExit) as exc_info:
            main.initialize_maps_client(api_key)
        
        assert exc_info.value.code == 1


class TestFetchPlacesForKeyword:
    """Test fetching places for keywords."""
    
    @pytest.fixture
    def mock_gmaps_client(self):
        """Fixture providing a mock Google Maps client."""
        return Mock(spec=googlemaps.Client)
    
    @pytest.fixture
    def sample_places_response(self):
        """Fixture providing sample places API response."""
        return {
            'results': [
                {
                    'place_id': 'place_1',
                    'name': 'Test Clinic 1',
                    'formatted_address': '123 Test St, Jakarta',
                    'geometry': {'location': {'lat': -6.2088, 'lng': 106.8456}}
                },
                {
                    'place_id': 'place_2',
                    'name': 'Test Clinic 2',
                    'formatted_address': '456 Test Ave, Jakarta',
                    'geometry': {'location': {'lat': -6.2089, 'lng': 106.8457}}
                }
            ],
            'status': 'OK'
        }
    
    @pytest.fixture
    def sample_places_response_with_pagination(self):
        """Fixture providing sample places API response with pagination."""
        return {
            'results': [
                {
                    'place_id': 'place_1',
                    'name': 'Test Clinic 1',
                    'formatted_address': '123 Test St, Jakarta'
                }
            ],
            'next_page_token': 'next_page_token_123',
            'status': 'OK'
        }
    
    @pytest.mark.unit
    def test_fetch_places_for_keyword_success(self, mock_gmaps_client, sample_places_response):
        """Test successful places fetching."""
        mock_gmaps_client.places.return_value = sample_places_response
        
        keyword = "vet clinic"
        location = (-6.2088, 106.8456)
        radius = 5000
        rate_limit = 10
        
        with patch('time.sleep'):  # Mock sleep to speed up tests
            places, api_calls = main.fetch_places_for_keyword(
                mock_gmaps_client, keyword, location, radius, rate_limit
            )
        
        assert len(places) == 2
        assert api_calls == 1
        assert places[0]['place_id'] == 'place_1'
        assert places[1]['place_id'] == 'place_2'
        
        mock_gmaps_client.places.assert_called_once_with(
            query=keyword,
            location=location,
            radius=radius
        )
    
    @pytest.mark.unit
    def test_fetch_places_for_keyword_with_pagination(self, mock_gmaps_client, sample_places_response_with_pagination):
        """Test places fetching with pagination."""
        # First call returns response with next_page_token
        # Second call returns final page
        second_page_response = {
            'results': [
                {
                    'place_id': 'place_2',
                    'name': 'Test Clinic 2',
                    'formatted_address': '456 Test Ave, Jakarta'
                }
            ],
            'status': 'OK'
        }
        
        mock_gmaps_client.places.side_effect = [
            sample_places_response_with_pagination,
            second_page_response
        ]
        
        keyword = "vet clinic"
        location = (-6.2088, 106.8456)
        radius = 5000
        rate_limit = 10
        
        with patch('time.sleep'):  # Mock sleep to speed up tests
            places, api_calls = main.fetch_places_for_keyword(
                mock_gmaps_client, keyword, location, radius, rate_limit
            )
        
        assert len(places) == 2
        assert api_calls == 2
        assert places[0]['place_id'] == 'place_1'
        assert places[1]['place_id'] == 'place_2'
    
    @pytest.mark.unit
    def test_fetch_places_for_keyword_api_error(self, mock_gmaps_client, caplog):
        """Test handling of API error during places fetching."""
        mock_gmaps_client.places.side_effect = ApiError("OVER_QUERY_LIMIT")
        
        keyword = "vet clinic"
        location = (-6.2088, 106.8456)
        radius = 5000
        rate_limit = 10
        
        with patch('time.sleep'):
            places, api_calls = main.fetch_places_for_keyword(
                mock_gmaps_client, keyword, location, radius, rate_limit
            )
        
        assert len(places) == 0
        assert api_calls == 0
        assert "API error fetching places for keyword" in caplog.text
    
    @pytest.mark.unit
    def test_fetch_places_for_keyword_general_error(self, mock_gmaps_client, caplog):
        """Test handling of general error during places fetching."""
        mock_gmaps_client.places.side_effect = Exception("Connection timeout")
        
        keyword = "vet clinic"
        location = (-6.2088, 106.8456)
        radius = 5000
        rate_limit = 10
        
        with patch('time.sleep'):
            places, api_calls = main.fetch_places_for_keyword(
                mock_gmaps_client, keyword, location, radius, rate_limit
            )
        
        assert len(places) == 0
        assert api_calls == 0
        assert "Unexpected error fetching places for keyword" in caplog.text
    
    @pytest.mark.unit
    def test_fetch_places_for_keyword_pagination_limit(self, mock_gmaps_client):
        """Test that pagination is limited to prevent excessive API usage."""
        paginated_response = {
            'results': [{'place_id': f'place_{i}', 'name': f'Place {i}'}],
            'next_page_token': f'token_{i}',
            'status': 'OK'
        }
        
        # Mock many paginated responses
        mock_gmaps_client.places.return_value = paginated_response
        
        keyword = "vet clinic"
        location = (-6.2088, 106.8456)
        radius = 5000
        rate_limit = 10
        
        with patch('time.sleep'):
            places, api_calls = main.fetch_places_for_keyword(
                mock_gmaps_client, keyword, location, radius, rate_limit
            )
        
        # Should be limited to max 3 pages (1 initial + 2 paginated)
        assert api_calls <= 3
    
    @pytest.mark.unit
    def test_fetch_places_for_keyword_rate_limiting(self, mock_gmaps_client, sample_places_response):
        """Test that rate limiting is applied."""
        mock_gmaps_client.places.return_value = sample_places_response
        
        keyword = "vet clinic"
        location = (-6.2088, 106.8456)
        radius = 5000
        rate_limit = 10
        
        with patch('time.sleep') as mock_sleep:
            main.fetch_places_for_keyword(
                mock_gmaps_client, keyword, location, radius, rate_limit
            )
            
            # Should call sleep with 1/rate_limit
            mock_sleep.assert_called_with(1.0 / rate_limit)


class TestGetPlaceDetails:
    """Test getting place details."""
    
    @pytest.fixture
    def mock_gmaps_client(self):
        """Fixture providing a mock Google Maps client."""
        return Mock(spec=googlemaps.Client)
    
    @pytest.fixture
    def sample_place_details(self):
        """Fixture providing sample place details response."""
        return {
            'result': {
                'place_id': 'place_123',
                'name': 'Test Veterinary Clinic',
                'formatted_address': '123 Test Street, Jakarta',
                'geometry': {
                    'location': {'lat': -6.2088, 'lng': 106.8456}
                },
                'rating': 4.5,
                'user_ratings_total': 125,
                'website': 'https://testveteriniary.com',
                'types': ['veterinary_care', 'point_of_interest'],
                'opening_hours': {'open_now': True}
            }
        }
    
    @pytest.mark.unit
    def test_get_place_details_success(self, mock_gmaps_client, sample_place_details):
        """Test successful place details fetching."""
        mock_gmaps_client.place.return_value = sample_place_details
        
        place_id = "place_123"
        rate_limit = 10
        
        with patch('time.sleep'):
            result = main.get_place_details(mock_gmaps_client, place_id, rate_limit)
        
        assert result == sample_place_details['result']
        
        # Verify the correct fields were requested
        expected_fields = [
            'place_id', 'name', 'formatted_address', 'geometry',
            'rating', 'user_ratings_total', 'website', 'types', 'opening_hours'
        ]
        mock_gmaps_client.place.assert_called_once_with(
            place_id=place_id,
            fields=expected_fields
        )
    
    @pytest.mark.unit
    def test_get_place_details_invalid_place_id(self, mock_gmaps_client, caplog):
        """Test handling of invalid place_id."""
        invalid_place_ids = [None, "", 123, [], {}]
        
        for invalid_id in invalid_place_ids:
            result = main.get_place_details(mock_gmaps_client, invalid_id, 10)
            assert result == {}
        
        assert "Invalid place_id provided" in caplog.text
    
    @pytest.mark.unit
    def test_get_place_details_api_error(self, mock_gmaps_client, caplog):
        """Test handling of API error during place details fetching."""
        mock_gmaps_client.place.side_effect = ApiError("NOT_FOUND")
        
        place_id = "invalid_place_id"
        rate_limit = 10
        
        with patch('time.sleep'):
            result = main.get_place_details(mock_gmaps_client, place_id, rate_limit)
        
        assert result == {}
        assert "API error fetching details for place_id" in caplog.text
    
    @pytest.mark.unit
    def test_get_place_details_general_error(self, mock_gmaps_client, caplog):
        """Test handling of general error during place details fetching."""
        mock_gmaps_client.place.side_effect = Exception("Connection error")
        
        place_id = "place_123"
        rate_limit = 10
        
        with patch('time.sleep'):
            result = main.get_place_details(mock_gmaps_client, place_id, rate_limit)
        
        assert result == {}
        assert "Unexpected error fetching details for place_id" in caplog.text
    
    @pytest.mark.unit
    def test_get_place_details_rate_limiting(self, mock_gmaps_client, sample_place_details):
        """Test that rate limiting is applied."""
        mock_gmaps_client.place.return_value = sample_place_details
        
        place_id = "place_123"
        rate_limit = 5
        
        with patch('time.sleep') as mock_sleep:
            main.get_place_details(mock_gmaps_client, place_id, rate_limit)
            
            # Should call sleep with 1/rate_limit
            mock_sleep.assert_called_with(1.0 / rate_limit)
    
    @pytest.mark.unit
    def test_get_place_details_empty_result(self, mock_gmaps_client):
        """Test handling of empty result from API."""
        mock_gmaps_client.place.return_value = {}
        
        place_id = "place_123"
        rate_limit = 10
        
        with patch('time.sleep'):
            result = main.get_place_details(mock_gmaps_client, place_id, rate_limit)
        
        assert result == {}
    
    @pytest.mark.unit
    def test_get_place_details_missing_result_key(self, mock_gmaps_client):
        """Test handling of missing 'result' key in API response."""
        mock_gmaps_client.place.return_value = {'status': 'OK'}
        
        place_id = "place_123"
        rate_limit = 10
        
        with patch('time.sleep'):
            result = main.get_place_details(mock_gmaps_client, place_id, rate_limit)
        
        assert result == {}


class TestAPIRateLimiting:
    """Test API rate limiting functionality."""
    
    @pytest.mark.unit
    def test_rate_limiting_timing(self):
        """Test that rate limiting introduces appropriate delays."""
        rate_limits = [1, 5, 10, 20]
        
        for rate_limit in rate_limits:
            expected_delay = 1.0 / rate_limit
            
            with patch('time.sleep') as mock_sleep:
                # Mock a simple API call that uses rate limiting
                mock_gmaps = Mock()
                mock_gmaps.places.return_value = {'results': []}
                
                main.fetch_places_for_keyword(
                    mock_gmaps, "test", (-6.2088, 106.8456), 5000, rate_limit
                )
                
                # Verify sleep was called with correct delay
                mock_sleep.assert_called_with(expected_delay)
    
    @pytest.mark.unit
    def test_pagination_rate_limiting(self):
        """Test that pagination uses appropriate rate limiting."""
        mock_gmaps = Mock()
        mock_gmaps.places.side_effect = [
            {
                'results': [{'place_id': 'place_1'}],
                'next_page_token': 'token_123'
            },
            {
                'results': [{'place_id': 'place_2'}]
            }
        ]
        
        rate_limit = 10
        expected_delay = max(2, 1.0 / rate_limit)
        
        with patch('time.sleep') as mock_sleep:
            main.fetch_places_for_keyword(
                mock_gmaps, "test", (-6.2088, 106.8456), 5000, rate_limit
            )
            
            # Should have multiple sleep calls: initial + pagination delay
            sleep_calls = mock_sleep.call_args_list
            assert len(sleep_calls) >= 2
            
            # Second call should use max(2, 1/rate_limit) for pagination
            assert sleep_calls[1][0][0] == expected_delay