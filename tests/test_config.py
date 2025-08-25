"""
Unit tests for configuration loading functionality.
"""
import os
import sys
import tempfile
import configparser
from pathlib import Path
from unittest.mock import patch, mock_open
import pytest

# Add the parent directory to sys.path so we can import main
sys.path.insert(0, str(Path(__file__).parent.parent))

import main


class TestConfigurationLoading:
    """Test configuration loading functions."""
    
    @pytest.fixture
    def mock_env_vars(self):
        """Fixture to provide mock environment variables."""
        return {
            'GOOGLE_MAPS_API_KEY': 'AIzaSyDummyTestKeyFor39CharacterString',
            'SEARCH_LATITUDE': '-6.2088',
            'SEARCH_LONGITUDE': '106.8456',
            'SEARCH_RADIUS': '50000',
            'API_RATE_LIMIT': '10'
        }
    
    @pytest.fixture
    def valid_config_content(self):
        """Fixture providing valid config.ini content."""
        return """[Maps]
api_key = AIzaSyDummyTestKeyFor39CharacterString

[search_parameters]
latitude = -6.2088
longitude = 106.8456
radius = 50000"""
    
    @pytest.mark.unit
    def test_load_config_from_environment(self, mock_env_vars):
        """Test loading configuration from environment variables."""
        with patch.dict(os.environ, mock_env_vars):
            with patch('main.Path.exists', return_value=False):
                config = main.load_config()
                
                assert config['api_key'] == mock_env_vars['GOOGLE_MAPS_API_KEY']
                assert config['latitude'] == float(mock_env_vars['SEARCH_LATITUDE'])
                assert config['longitude'] == float(mock_env_vars['SEARCH_LONGITUDE'])
                assert config['radius'] == int(mock_env_vars['SEARCH_RADIUS'])
                assert config['rate_limit'] == int(mock_env_vars['API_RATE_LIMIT'])
    
    @pytest.mark.unit
    def test_load_config_from_file(self, valid_config_content):
        """Test loading configuration from config.ini file."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('main.Path.exists', return_value=True):
                with patch('builtins.open', mock_open(read_data=valid_config_content)):
                    with patch('configparser.ConfigParser.read'):
                        mock_parser = configparser.ConfigParser()
                        mock_parser.read_string(valid_config_content)
                        
                        with patch('configparser.ConfigParser') as mock_config_class:
                            mock_config_class.return_value = mock_parser
                            config = main.load_config()
                            
                            assert config['api_key'] == 'AIzaSyDummyTestKeyFor39CharacterString'
                            assert config['latitude'] == -6.2088  # Default value
                            assert config['longitude'] == 106.8456  # Default value
                            assert config['radius'] == 50000  # Default value
                            assert config['rate_limit'] == 10  # Default value
    
    @pytest.mark.unit
    def test_load_config_invalid_api_key_exits(self):
        """Test that invalid API key causes system exit."""
        with patch.dict(os.environ, {'GOOGLE_MAPS_API_KEY': 'invalid_key'}):
            with patch('main.Path.exists', return_value=False):
                with pytest.raises(SystemExit) as exc_info:
                    main.load_config()
                assert exc_info.value.code == 1
    
    @pytest.mark.unit
    def test_load_config_missing_api_key_exits(self):
        """Test that missing API key causes system exit."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('main.Path.exists', return_value=False):
                with pytest.raises(SystemExit) as exc_info:
                    main.load_config()
                assert exc_info.value.code == 1
    
    @pytest.mark.unit
    def test_load_config_invalid_coordinates_exits(self):
        """Test that invalid coordinates cause system exit."""
        mock_env_vars = {
            'GOOGLE_MAPS_API_KEY': 'AIzaSyDummyTestKeyFor39CharacterString',
            'SEARCH_LATITUDE': '91.0',  # Invalid latitude
            'SEARCH_LONGITUDE': '106.8456'
        }
        with patch.dict(os.environ, mock_env_vars):
            with patch('main.Path.exists', return_value=False):
                with pytest.raises(SystemExit) as exc_info:
                    main.load_config()
                assert exc_info.value.code == 1
    
    @pytest.mark.unit
    def test_load_config_invalid_radius_exits(self):
        """Test that invalid radius causes system exit."""
        mock_env_vars = {
            'GOOGLE_MAPS_API_KEY': 'AIzaSyDummyTestKeyFor39CharacterString',
            'SEARCH_RADIUS': '50001'  # Too large
        }
        with patch.dict(os.environ, mock_env_vars):
            with patch('main.Path.exists', return_value=False):
                with pytest.raises(SystemExit) as exc_info:
                    main.load_config()
                assert exc_info.value.code == 1
    
    @pytest.mark.unit
    def test_load_config_invalid_value_type_exits(self):
        """Test that invalid value types cause system exit."""
        mock_env_vars = {
            'GOOGLE_MAPS_API_KEY': 'AIzaSyDummyTestKeyFor39CharacterString',
            'SEARCH_LATITUDE': 'not_a_number'
        }
        with patch.dict(os.environ, mock_env_vars):
            with patch('main.Path.exists', return_value=False):
                with pytest.raises(SystemExit) as exc_info:
                    main.load_config()
                assert exc_info.value.code == 1
    
    @pytest.mark.unit
    def test_load_config_uses_defaults(self):
        """Test that default values are used when environment variables are not set."""
        with patch.dict(os.environ, {'GOOGLE_MAPS_API_KEY': 'AIzaSyDummyTestKeyFor39CharacterString'}):
            with patch('main.Path.exists', return_value=False):
                config = main.load_config()
                
                # Check default values
                assert config['latitude'] == -6.2088
                assert config['longitude'] == 106.8456
                assert config['radius'] == 50000
                assert config['rate_limit'] == 10


class TestAPIKeyValidation:
    """Test API key validation functionality."""
    
    @pytest.mark.unit
    def test_validate_api_key_valid(self):
        """Test validation of valid API key."""
        valid_key = "AIzaSyDummyTestKeyFor39CharacterString"
        assert main.validate_api_key(valid_key) is True
    
    @pytest.mark.unit
    def test_validate_api_key_empty(self):
        """Test validation of empty API key."""
        assert main.validate_api_key("") is False
        assert main.validate_api_key(None) is False
    
    @pytest.mark.unit
    def test_validate_api_key_placeholder(self):
        """Test validation rejects placeholder values."""
        placeholders = [
            'your_api_key_here',
            'api_key_here',
            'placeholder',
            'YOUR_API_KEY_HERE',
            'API_KEY_HERE',
            'PLACEHOLDER'
        ]
        
        for placeholder in placeholders:
            assert main.validate_api_key(placeholder) is False
    
    @pytest.mark.unit
    def test_validate_api_key_wrong_format_warning(self, caplog):
        """Test that wrong format triggers warning but doesn't fail validation."""
        wrong_format_key = "wrong_format_key"
        result = main.validate_api_key(wrong_format_key)
        
        assert result is True  # Still passes validation
        assert "API key doesn't match expected Google API key format" in caplog.text
    
    @pytest.mark.unit
    def test_validate_api_key_correct_format(self):
        """Test validation of correctly formatted API key."""
        # Test various valid formats
        valid_keys = [
            "AIzaSyDummyTestKeyFor39CharacterString",
            "AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q",
            "AIzaSy123456789012345678901234567890123"
        ]
        
        for key in valid_keys:
            assert main.validate_api_key(key) is True


class TestParameterValidation:
    """Test validation functions for coordinates and radius."""
    
    @pytest.mark.unit
    @pytest.mark.parametrize("lat,lng,expected", [
        (0, 0, True),
        (-90, -180, True),
        (90, 180, True),
        (-6.2088, 106.8456, True),
        (-91, 0, False),
        (91, 0, False),
        (0, -181, False),
        (0, 181, False),
        (-90.1, 0, False),
        (90.1, 0, False),
    ])
    def test_validate_coordinates(self, lat, lng, expected):
        """Test coordinate validation with various values."""
        assert main.validate_coordinates(lat, lng) == expected
    
    @pytest.mark.unit
    @pytest.mark.parametrize("radius,expected", [
        (1, True),
        (1000, True),
        (50000, True),
        (0, False),
        (50001, False),
        (-1, False),
        (25000, True),
    ])
    def test_validate_radius(self, radius, expected):
        """Test radius validation with various values."""
        assert main.validate_radius(radius) == expected