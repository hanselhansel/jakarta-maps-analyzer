"""
Unit tests for data processing and extraction functionality.
"""
import sys
from pathlib import Path
import pytest

# Add the parent directory to sys.path so we can import main
sys.path.insert(0, str(Path(__file__).parent.parent))

import main


class TestExtractPlaceInfo:
    """Test place information extraction functionality."""
    
    @pytest.fixture
    def complete_place_details(self):
        """Fixture providing complete place details."""
        return {
            'place_id': 'ChIJN1t_tDeuEmsRUsoyG83frY4',
            'name': 'Jakarta Veterinary Clinic',
            'formatted_address': '123 Jalan Sudirman, Jakarta Pusat, DKI Jakarta 10270, Indonesia',
            'geometry': {
                'location': {
                    'lat': -6.2088,
                    'lng': 106.8456
                }
            },
            'rating': 4.5,
            'user_ratings_total': 128,
            'website': 'https://jakartavetclinic.com',
            'types': ['veterinary_care', 'point_of_interest', 'establishment'],
            'opening_hours': {
                'open_now': True
            }
        }
    
    @pytest.fixture
    def minimal_place_details(self):
        """Fixture providing minimal place details."""
        return {
            'place_id': 'minimal_place_id',
            'name': 'Minimal Clinic'
        }
    
    @pytest.fixture
    def place_details_with_missing_fields(self):
        """Fixture providing place details with some missing fields."""
        return {
            'place_id': 'partial_place_id',
            'name': 'Partial Clinic',
            'formatted_address': '456 Test Street, Jakarta',
            'geometry': {
                'location': {
                    'lat': -6.2089,
                    'lng': 106.8457
                }
            },
            'rating': 4.0
            # Missing: user_ratings_total, website, types, opening_hours
        }
    
    @pytest.mark.unit
    def test_extract_place_info_complete_data(self, complete_place_details):
        """Test extraction with complete place data."""
        category = "Competitor"
        result = main.extract_place_info(complete_place_details, category)
        
        expected = {
            'place_id': 'ChIJN1t_tDeuEmsRUsoyG83frY4',
            'name': 'Jakarta Veterinary Clinic',
            'category': 'Competitor',
            'address': '123 Jalan Sudirman, Jakarta Pusat, DKI Jakarta 10270, Indonesia',
            'latitude': -6.2088,
            'longitude': 106.8456,
            'rating': 4.5,
            'review_count': 128,
            'website': 'https://jakartavetclinic.com',
            'types': 'veterinary_care, point_of_interest, establishment',
            'is_open_now': True
        }
        
        assert result == expected
    
    @pytest.mark.unit
    def test_extract_place_info_minimal_data(self, minimal_place_details):
        """Test extraction with minimal place data."""
        category = "Test"
        result = main.extract_place_info(minimal_place_details, category)
        
        expected = {
            'place_id': 'minimal_place_id',
            'name': 'Minimal Clinic',
            'category': 'Test',
            'address': '',
            'latitude': '',
            'longitude': '',
            'rating': '',
            'review_count': 0,
            'website': '',
            'types': '',
            'is_open_now': ''
        }
        
        assert result == expected
    
    @pytest.mark.unit
    def test_extract_place_info_partial_data(self, place_details_with_missing_fields):
        """Test extraction with partial place data."""
        category = "Partial"
        result = main.extract_place_info(place_details_with_missing_fields, category)
        
        expected = {
            'place_id': 'partial_place_id',
            'name': 'Partial Clinic',
            'category': 'Partial',
            'address': '456 Test Street, Jakarta',
            'latitude': -6.2089,
            'longitude': 106.8457,
            'rating': 4.0,
            'review_count': 0,
            'website': '',
            'types': '',
            'is_open_now': ''
        }
        
        assert result == expected
    
    @pytest.mark.unit
    def test_extract_place_info_sanitizes_inputs(self):
        """Test that extraction sanitizes dangerous inputs."""
        dangerous_place_details = {
            'place_id': 'test_place_id',
            'name': 'Clinic <script>alert("xss")</script>',
            'formatted_address': 'Address with "quotes" and \'single quotes\'',
            'types': ['type<script>', 'type"with"quotes', 'normal_type'],
            'geometry': {
                'location': {
                    'lat': -6.2088,
                    'lng': 106.8456
                }
            }
        }
        
        category = 'Category with "quotes" and <script>'
        result = main.extract_place_info(dangerous_place_details, category)
        
        # Check that dangerous characters are removed
        assert '<script>' not in result['name']
        assert 'alert' in result['name']  # Should keep safe parts
        assert '"' not in result['address']
        assert "'" not in result['address']
        assert '<script>' not in result['category']
        assert '"' not in result['category']
        assert 'script' not in result['types']
        assert 'quotes' in result['types']
    
    @pytest.mark.unit
    def test_extract_place_info_handles_invalid_coordinates(self):
        """Test handling of invalid coordinates."""
        place_details_invalid_coords = {
            'place_id': 'test_place_id',
            'name': 'Test Clinic',
            'geometry': {
                'location': {
                    'lat': 91.0,  # Invalid latitude
                    'lng': 181.0  # Invalid longitude
                }
            }
        }
        
        result = main.extract_place_info(place_details_invalid_coords, "Test")
        
        # Should not include invalid coordinates
        assert result['latitude'] == ''
        assert result['longitude'] == ''
    
    @pytest.mark.unit
    def test_extract_place_info_handles_non_numeric_coordinates(self):
        """Test handling of non-numeric coordinates."""
        place_details_non_numeric = {
            'place_id': 'test_place_id',
            'name': 'Test Clinic',
            'geometry': {
                'location': {
                    'lat': 'not_a_number',
                    'lng': None
                }
            }
        }
        
        result = main.extract_place_info(place_details_non_numeric, "Test")
        
        # Should not include non-numeric coordinates
        assert result['latitude'] == ''
        assert result['longitude'] == ''
    
    @pytest.mark.unit
    def test_extract_place_info_handles_invalid_review_count(self):
        """Test handling of invalid review count values."""
        invalid_review_counts = [
            'not_a_number',
            None,
            -5,
            3.14,
            'mixed123text'
        ]
        
        for invalid_count in invalid_review_counts:
            place_details = {
                'place_id': 'test_place_id',
                'name': 'Test Clinic',
                'user_ratings_total': invalid_count
            }
            
            result = main.extract_place_info(place_details, "Test")
            
            # Should default to 0 for invalid values
            if invalid_count == -5:
                assert result['review_count'] == -5  # Negative numbers are converted
            elif invalid_count == 3.14:
                assert result['review_count'] == 3  # Floats are converted to int
            else:
                assert result['review_count'] == 0  # Invalid values default to 0
    
    @pytest.mark.unit
    def test_extract_place_info_handles_empty_types(self):
        """Test handling of empty or missing types."""
        place_details = {
            'place_id': 'test_place_id',
            'name': 'Test Clinic',
            'types': []
        }
        
        result = main.extract_place_info(place_details, "Test")
        assert result['types'] == ''
        
        # Test with missing types key
        place_details_no_types = {
            'place_id': 'test_place_id',
            'name': 'Test Clinic'
        }
        
        result = main.extract_place_info(place_details_no_types, "Test")
        assert result['types'] == ''
    
    @pytest.mark.unit
    def test_extract_place_info_limits_field_lengths(self):
        """Test that field lengths are properly limited."""
        long_strings = {
            'place_id': 'test_place_id',
            'name': 'A' * 300,  # Should be limited to 200
            'formatted_address': 'B' * 500,  # Should be limited to 300
            'types': ['C' * 100, 'D' * 100],  # Each type should be limited to 50
        }
        
        result = main.extract_place_info(long_strings, 'E' * 100)  # Category limited to 50
        
        assert len(result['name']) == 200
        assert len(result['address']) == 300
        assert len(result['category']) == 50
        
        # Check that types are properly limited and joined
        types_list = result['types'].split(', ')
        for type_str in types_list:
            assert len(type_str) <= 50
    
    @pytest.mark.unit
    def test_extract_place_info_preserves_valid_data(self):
        """Test that valid data is preserved without modification."""
        valid_place_details = {
            'place_id': 'valid_place_id',
            'name': 'Valid Veterinary Clinic',
            'formatted_address': '789 Valid Street, Jakarta Selatan',
            'geometry': {
                'location': {
                    'lat': -6.2500,
                    'lng': 106.8000
                }
            },
            'rating': 4.8,
            'user_ratings_total': 250,
            'website': 'https://validclinic.com',
            'types': ['veterinary_care', 'health', 'point_of_interest'],
            'opening_hours': {
                'open_now': False
            }
        }
        
        category = "Valid Category"
        result = main.extract_place_info(valid_place_details, category)
        
        # All valid data should be preserved
        assert result['place_id'] == 'valid_place_id'
        assert result['name'] == 'Valid Veterinary Clinic'
        assert result['category'] == 'Valid Category'
        assert result['address'] == '789 Valid Street, Jakarta Selatan'
        assert result['latitude'] == -6.2500
        assert result['longitude'] == 106.8000
        assert result['rating'] == 4.8
        assert result['review_count'] == 250
        assert result['website'] == 'https://validclinic.com'
        assert result['types'] == 'veterinary_care, health, point_of_interest'
        assert result['is_open_now'] is False
    
    @pytest.mark.unit
    def test_extract_place_info_handles_missing_geometry(self):
        """Test handling of missing geometry information."""
        place_details_no_geometry = {
            'place_id': 'test_place_id',
            'name': 'Test Clinic'
            # No geometry field
        }
        
        result = main.extract_place_info(place_details_no_geometry, "Test")
        
        assert result['latitude'] == ''
        assert result['longitude'] == ''
    
    @pytest.mark.unit
    def test_extract_place_info_handles_incomplete_geometry(self):
        """Test handling of incomplete geometry information."""
        incomplete_geometries = [
            {'geometry': {}},  # Empty geometry
            {'geometry': {'location': {}}},  # Empty location
            {'geometry': {'location': {'lat': -6.2088}}},  # Missing lng
            {'geometry': {'location': {'lng': 106.8456}}},  # Missing lat
        ]
        
        for place_details in incomplete_geometries:
            place_details.update({
                'place_id': 'test_place_id',
                'name': 'Test Clinic'
            })
            
            result = main.extract_place_info(place_details, "Test")
            
            assert result['latitude'] == ''
            assert result['longitude'] == ''
    
    @pytest.mark.unit
    def test_extract_place_info_handles_missing_opening_hours(self):
        """Test handling of missing opening hours."""
        place_details = {
            'place_id': 'test_place_id',
            'name': 'Test Clinic'
            # No opening_hours field
        }
        
        result = main.extract_place_info(place_details, "Test")
        assert result['is_open_now'] == ''
        
        # Test with empty opening_hours
        place_details_empty_hours = {
            'place_id': 'test_place_id',
            'name': 'Test Clinic',
            'opening_hours': {}
        }
        
        result = main.extract_place_info(place_details_empty_hours, "Test")
        assert result['is_open_now'] == ''