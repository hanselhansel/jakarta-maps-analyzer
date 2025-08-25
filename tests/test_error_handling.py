"""
Unit tests for error handling scenarios and edge cases.
"""
import sys
import os
import logging
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock
import pytest
import googlemaps
from googlemaps.exceptions import ApiError, TransportError, Timeout
import pandas as pd

# Add the parent directory to sys.path so we can import main
sys.path.insert(0, str(Path(__file__).parent.parent))

import main


class TestLoggingSetup:
    """Test logging configuration and setup."""
    
    @pytest.mark.unit
    def test_setup_logging_creates_handlers(self):
        """Test that logging setup creates proper handlers."""
        with patch('logging.basicConfig') as mock_basic_config:
            main.setup_logging()
            
            mock_basic_config.assert_called_once()
            call_args = mock_basic_config.call_args[1]
            
            assert call_args['level'] == logging.INFO
            assert 'handlers' in call_args
            assert len(call_args['handlers']) == 2  # File and stream handler
    
    @pytest.mark.unit
    def test_setup_logging_format(self):
        """Test that logging format is properly configured."""
        with patch('logging.basicConfig') as mock_basic_config:
            main.setup_logging()
            
            call_args = mock_basic_config.call_args[1]
            expected_format = '%(asctime)s - %(levelname)s - %(message)s'
            assert call_args['format'] == expected_format


class TestAPIErrorHandling:
    """Test API error handling scenarios."""
    
    @pytest.fixture
    def mock_gmaps_client(self):
        """Fixture providing a mock Google Maps client."""
        return Mock(spec=googlemaps.Client)
    
    @pytest.mark.unit
    def test_api_error_during_places_search(self, mock_gmaps_client, caplog):
        """Test handling of API errors during places search."""
        api_errors = [
            ApiError("OVER_QUERY_LIMIT"),
            ApiError("REQUEST_DENIED"),
            ApiError("INVALID_REQUEST"),
            ApiError("ZERO_RESULTS"),
            ApiError("UNKNOWN_ERROR")
        ]
        
        for api_error in api_errors:
            mock_gmaps_client.places.side_effect = api_error
            
            with patch('time.sleep'):
                places, api_calls = main.fetch_places_for_keyword(
                    mock_gmaps_client, "test", (-6.2088, 106.8456), 5000, 10
                )
            
            assert len(places) == 0
            assert api_calls == 0
            assert "API error fetching places for keyword" in caplog.text
    
    @pytest.mark.unit
    def test_transport_error_during_places_search(self, mock_gmaps_client, caplog):
        """Test handling of transport errors during places search."""
        transport_errors = [
            TransportError("Connection timeout"),
            Timeout("Request timeout"),
            Exception("Network error")
        ]
        
        for transport_error in transport_errors:
            mock_gmaps_client.places.side_effect = transport_error
            
            with patch('time.sleep'):
                places, api_calls = main.fetch_places_for_keyword(
                    mock_gmaps_client, "test", (-6.2088, 106.8456), 5000, 10
                )
            
            assert len(places) == 0
            assert api_calls == 0
    
    @pytest.mark.unit
    def test_api_error_during_place_details(self, mock_gmaps_client, caplog):
        """Test handling of API errors during place details fetching."""
        api_errors = [
            ApiError("NOT_FOUND"),
            ApiError("OVER_QUERY_LIMIT"),
            ApiError("REQUEST_DENIED")
        ]
        
        for api_error in api_errors:
            mock_gmaps_client.place.side_effect = api_error
            
            with patch('time.sleep'):
                result = main.get_place_details(mock_gmaps_client, "test_place_id", 10)
            
            assert result == {}
            assert "API error fetching details for place_id" in caplog.text
    
    @pytest.mark.unit
    def test_pagination_error_handling(self, mock_gmaps_client, caplog):
        """Test error handling during pagination."""
        # First call succeeds, second call (pagination) fails
        mock_gmaps_client.places.side_effect = [
            {
                'results': [{'place_id': 'place_1'}],
                'next_page_token': 'token_123'
            },
            ApiError("INVALID_REQUEST")
        ]
        
        with patch('time.sleep'):
            places, api_calls = main.fetch_places_for_keyword(
                mock_gmaps_client, "test", (-6.2088, 106.8456), 5000, 10
            )
        
        # Should have results from first call, but pagination should fail gracefully
        assert len(places) == 1
        assert api_calls == 2
        assert "API error during pagination" in caplog.text
    
    @pytest.mark.unit
    def test_malformed_api_response_handling(self, mock_gmaps_client):
        """Test handling of malformed API responses."""
        malformed_responses = [
            {},  # Empty response
            {'status': 'OK'},  # Missing results
            {'results': None},  # Null results
            {'results': 'not_a_list'},  # Invalid results type
            None  # Null response
        ]
        
        for malformed_response in malformed_responses:
            mock_gmaps_client.places.return_value = malformed_response
            
            with patch('time.sleep'):
                places, api_calls = main.fetch_places_for_keyword(
                    mock_gmaps_client, "test", (-6.2088, 106.8456), 5000, 10
                )
            
            # Should handle gracefully and return empty list
            assert isinstance(places, list)
            assert api_calls == 1


class TestConfigurationErrorHandling:
    """Test configuration error handling scenarios."""
    
    @pytest.mark.unit
    def test_missing_env_file_fallback(self):
        """Test fallback when .env file is missing."""
        with patch('main.load_dotenv'):  # Mock load_dotenv to avoid actual file operations
            with patch.dict(os.environ, {}, clear=True):
                with patch('main.Path.exists', return_value=False):
                    with pytest.raises(SystemExit) as exc_info:
                        main.load_config()
                    assert exc_info.value.code == 1
    
    @pytest.mark.unit
    def test_corrupted_config_file(self):
        """Test handling of corrupted config.ini file."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('main.Path.exists', return_value=True):
                with patch('configparser.ConfigParser.read', side_effect=Exception("Corrupted config")):
                    with pytest.raises(SystemExit) as exc_info:
                        main.load_config()
                    assert exc_info.value.code == 1
    
    @pytest.mark.unit
    def test_invalid_numeric_config_values(self):
        """Test handling of invalid numeric configuration values."""
        invalid_configs = [
            {'SEARCH_LATITUDE': 'not_a_number'},
            {'SEARCH_LONGITUDE': 'invalid'},
            {'SEARCH_RADIUS': 'abc'},
            {'API_RATE_LIMIT': 'xyz'},
        ]
        
        for invalid_config in invalid_configs:
            base_config = {'GOOGLE_MAPS_API_KEY': 'AIzaSyDummyTestKeyFor39CharacterString'}
            base_config.update(invalid_config)
            
            with patch.dict(os.environ, base_config):
                with patch('main.Path.exists', return_value=False):
                    with pytest.raises(SystemExit) as exc_info:
                        main.load_config()
                    assert exc_info.value.code == 1


class TestFileSystemErrorHandling:
    """Test file system error handling scenarios."""
    
    @pytest.mark.unit
    def test_csv_file_permission_denied(self):
        """Test handling of CSV file permission errors."""
        with patch('main.Path.exists', return_value=True):
            with patch('pandas.read_csv', side_effect=PermissionError("Permission denied")):
                with pytest.raises(SystemExit) as exc_info:
                    main.read_queries('protected.csv')
                assert exc_info.value.code == 1
    
    @pytest.mark.unit
    def test_csv_file_not_found_during_read(self):
        """Test handling when CSV file disappears during read."""
        with patch('main.Path.exists', return_value=True):
            with patch('pandas.read_csv', side_effect=FileNotFoundError("File not found")):
                with pytest.raises(SystemExit) as exc_info:
                    main.read_queries('disappeared.csv')
                assert exc_info.value.code == 1
    
    @pytest.mark.unit
    def test_output_file_write_error(self):
        """Test handling of output file write errors."""
        # This would be tested in integration tests with the main function
        # For now we'll test the pandas to_csv error handling concept
        df = pd.DataFrame({'test': [1, 2, 3]})
        
        with patch.object(df, 'to_csv', side_effect=PermissionError("Cannot write file")):
            with pytest.raises(PermissionError):
                df.to_csv('protected_output.csv')
    
    @pytest.mark.unit
    def test_disk_space_error(self):
        """Test handling of disk space errors."""
        df = pd.DataFrame({'test': [1, 2, 3]})
        
        with patch.object(df, 'to_csv', side_effect=OSError("No space left on device")):
            with pytest.raises(OSError):
                df.to_csv('output.csv')


class TestNetworkErrorHandling:
    """Test network-related error handling."""
    
    @pytest.fixture
    def mock_gmaps_client(self):
        """Fixture providing a mock Google Maps client."""
        return Mock(spec=googlemaps.Client)
    
    @pytest.mark.unit
    def test_network_timeout_handling(self, mock_gmaps_client, caplog):
        """Test handling of network timeouts."""
        mock_gmaps_client.places.side_effect = Timeout("Request timeout")
        
        with patch('time.sleep'):
            places, api_calls = main.fetch_places_for_keyword(
                mock_gmaps_client, "test", (-6.2088, 106.8456), 5000, 10
            )
        
        assert len(places) == 0
        assert api_calls == 0
        assert "Unexpected error fetching places for keyword" in caplog.text
    
    @pytest.mark.unit
    def test_connection_error_handling(self, mock_gmaps_client, caplog):
        """Test handling of connection errors."""
        mock_gmaps_client.places.side_effect = ConnectionError("Failed to connect")
        
        with patch('time.sleep'):
            places, api_calls = main.fetch_places_for_keyword(
                mock_gmaps_client, "test", (-6.2088, 106.8456), 5000, 10
            )
        
        assert len(places) == 0
        assert api_calls == 0
        assert "Unexpected error fetching places for keyword" in caplog.text
    
    @pytest.mark.unit
    def test_ssl_error_handling(self, mock_gmaps_client, caplog):
        """Test handling of SSL errors."""
        import ssl
        mock_gmaps_client.places.side_effect = ssl.SSLError("SSL certificate error")
        
        with patch('time.sleep'):
            places, api_calls = main.fetch_places_for_keyword(
                mock_gmaps_client, "test", (-6.2088, 106.8456), 5000, 10
            )
        
        assert len(places) == 0
        assert api_calls == 0
        assert "Unexpected error fetching places for keyword" in caplog.text


class TestDataValidationErrorHandling:
    """Test data validation error handling."""
    
    @pytest.mark.unit
    def test_invalid_place_data_handling(self):
        """Test handling of invalid place data."""
        invalid_place_data = [
            None,
            {},
            {'invalid': 'structure'},
            {'place_id': None},
            {'place_id': ''},
        ]
        
        for invalid_data in invalid_place_data:
            # Should not crash when extracting info from invalid data
            result = main.extract_place_info(invalid_data or {}, "Test")
            
            # Should return a valid structure with default values
            assert isinstance(result, dict)
            assert 'place_id' in result
            assert 'name' in result
            assert 'category' in result
    
    @pytest.mark.unit
    def test_malformed_geometry_handling(self):
        """Test handling of malformed geometry data."""
        malformed_geometries = [
            {'geometry': None},
            {'geometry': {'location': None}},
            {'geometry': {'location': {'lat': None, 'lng': None}}},
            {'geometry': {'location': {'lat': 'invalid', 'lng': 'invalid'}}},
            {'geometry': {'location': {'lat': float('inf'), 'lng': float('nan')}}},
        ]
        
        for place_data in malformed_geometries:
            place_data.update({
                'place_id': 'test_id',
                'name': 'Test Place'
            })
            
            result = main.extract_place_info(place_data, "Test")
            
            # Should handle gracefully and return empty coordinates
            assert result['latitude'] == ''
            assert result['longitude'] == ''
    
    @pytest.mark.unit
    def test_extreme_coordinate_values(self):
        """Test handling of extreme coordinate values."""
        extreme_coordinates = [
            (-91, 106.8456),  # Invalid latitude
            (91, 106.8456),   # Invalid latitude
            (-6.2088, -181),  # Invalid longitude
            (-6.2088, 181),   # Invalid longitude
            (float('inf'), 106.8456),  # Infinity
            (-6.2088, float('nan')),   # NaN
        ]
        
        for lat, lng in extreme_coordinates:
            place_data = {
                'place_id': 'test_id',
                'name': 'Test Place',
                'geometry': {
                    'location': {'lat': lat, 'lng': lng}
                }
            }
            
            result = main.extract_place_info(place_data, "Test")
            
            # Should reject invalid coordinates
            assert result['latitude'] == ''
            assert result['longitude'] == ''


class TestRecoveryMechanisms:
    """Test error recovery mechanisms."""
    
    @pytest.fixture
    def mock_gmaps_client(self):
        """Fixture providing a mock Google Maps client."""
        return Mock(spec=googlemaps.Client)
    
    @pytest.mark.unit
    def test_partial_success_handling(self, mock_gmaps_client):
        """Test handling when some API calls succeed and others fail."""
        # First call succeeds, second fails, third succeeds
        mock_gmaps_client.places.side_effect = [
            {'results': [{'place_id': 'place_1'}]},
            ApiError("OVER_QUERY_LIMIT"),
            {'results': [{'place_id': 'place_3'}]}
        ]
        
        # Simulate multiple keyword searches
        all_places = []
        for keyword in ['keyword1', 'keyword2', 'keyword3']:
            with patch('time.sleep'):
                places, _ = main.fetch_places_for_keyword(
                    mock_gmaps_client, keyword, (-6.2088, 106.8456), 5000, 10
                )
                all_places.extend(places)
        
        # Should have results from successful calls
        assert len(all_places) == 2
        assert all_places[0]['place_id'] == 'place_1'
        assert all_places[1]['place_id'] == 'place_3'
    
    @pytest.mark.unit
    def test_graceful_degradation(self, mock_gmaps_client, caplog):
        """Test graceful degradation when services are unavailable."""
        mock_gmaps_client.places.side_effect = ApiError("SERVICE_UNAVAILABLE")
        
        with patch('time.sleep'):
            places, api_calls = main.fetch_places_for_keyword(
                mock_gmaps_client, "test", (-6.2088, 106.8456), 5000, 10
            )
        
        # Should fail gracefully without crashing
        assert len(places) == 0
        assert api_calls == 0
        assert "API error fetching places for keyword" in caplog.text
    
    @pytest.mark.unit
    def test_rate_limit_recovery(self, mock_gmaps_client):
        """Test that rate limiting prevents cascading failures."""
        # Simulate rapid successive calls
        mock_gmaps_client.places.return_value = {'results': []}
        
        with patch('time.sleep') as mock_sleep:
            for i in range(5):
                main.fetch_places_for_keyword(
                    mock_gmaps_client, f"keyword_{i}", (-6.2088, 106.8456), 5000, 10
                )
        
        # Should have called sleep for rate limiting
        assert mock_sleep.call_count >= 5


class TestErrorLogging:
    """Test error logging functionality."""
    
    @pytest.mark.unit
    def test_api_errors_are_logged(self, caplog):
        """Test that API errors are properly logged."""
        mock_client = Mock(spec=googlemaps.Client)
        mock_client.places.side_effect = ApiError("TEST_ERROR")
        
        with patch('time.sleep'):
            main.fetch_places_for_keyword(
                mock_client, "test", (-6.2088, 106.8456), 5000, 10
            )
        
        assert "API error fetching places for keyword" in caplog.text
        assert "TEST_ERROR" in caplog.text
    
    @pytest.mark.unit
    def test_validation_errors_are_logged(self, caplog):
        """Test that validation errors are properly logged."""
        with patch.dict(os.environ, {'GOOGLE_MAPS_API_KEY': 'invalid_key'}):
            with patch('main.Path.exists', return_value=False):
                with pytest.raises(SystemExit):
                    main.load_config()
        
        assert "Invalid or missing API key" in caplog.text
    
    @pytest.mark.unit
    def test_file_errors_are_logged(self, caplog):
        """Test that file errors are properly logged."""
        with pytest.raises(SystemExit):
            main.read_queries('nonexistent_file.csv')
        
        assert "not found" in caplog.text