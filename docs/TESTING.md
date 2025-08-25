# Testing Documentation for Jakarta Maps Analyzer

This document provides comprehensive information about the test suite for the Jakarta Maps Analyzer project.

## Overview

The test suite is designed to ensure the reliability, security, and performance of the Google Maps market analysis scraper. It includes comprehensive unit tests covering all major functionality, with a focus on security features, error handling, and edge cases.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── fixtures/                   # Test data and configuration files
│   ├── test_queries.csv       # Valid test queries
│   ├── test_queries_invalid.csv # Invalid column structure
│   ├── test_queries_empty.csv # Empty queries
│   └── test_config.ini        # Test configuration
├── test_config.py             # Configuration loading tests
├── test_validation.py         # Input validation and sanitization tests
├── test_api_integration.py    # Google Maps API integration tests
├── test_data_processing.py    # Data extraction and processing tests
├── test_csv_processing.py     # CSV file handling tests
└── test_error_handling.py     # Error scenarios and edge cases
```

## Test Categories

### Unit Tests
- **Configuration Loading**: Tests for environment variable and config file loading
- **Input Validation**: Tests for API key validation, coordinate validation, radius validation
- **Input Sanitization**: Tests for XSS prevention, SQL injection prevention, command injection prevention
- **API Integration**: Tests for Google Maps API calls with proper mocking
- **Data Processing**: Tests for place information extraction and transformation
- **CSV Processing**: Tests for reading and validating query files
- **Error Handling**: Tests for various error scenarios and recovery mechanisms

### Security Tests
- Input sanitization to prevent XSS attacks
- SQL injection pattern detection and removal
- Command injection prevention
- API key validation and security checks
- Length limits to prevent DoS attacks
- File handling security

### Error Handling Tests
- API error scenarios (rate limits, invalid requests, network failures)
- File system errors (permissions, missing files, corruption)
- Network connectivity issues
- Malformed data handling
- Configuration errors

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install -r requirements-test.txt
```

### Basic Test Execution

#### Run All Tests
```bash
# Using pytest directly
pytest

# Using the test runner script
python run_tests.py
```

#### Run Specific Test Categories
```bash
# Unit tests only
python run_tests.py unit

# Security-focused tests
python run_tests.py security

# Quick tests (excluding slow tests)
python run_tests.py quick
```

#### Run Tests with Coverage
```bash
# Coverage report in terminal and HTML
python run_tests.py coverage

# View HTML coverage report
open htmlcov/index.html
```

### Advanced Test Options

#### Run Tests with Markers
```bash
# Run only unit tests
pytest -m unit

# Run all except slow tests
pytest -m "not slow"

# Run security-related tests
pytest -k "security or sanitiz or validat"
```

#### Verbose Output
```bash
pytest -v
```

#### Stop on First Failure
```bash
pytest -x
```

#### Run Specific Test Files
```bash
pytest tests/test_config.py
pytest tests/test_validation.py::TestInputSanitization
```

## Test Configuration

### pytest.ini
The project includes a `pytest.ini` configuration file that sets:
- Test discovery patterns
- Coverage settings (minimum 85% coverage required)
- Output formatting
- Warning filters
- Test markers

### Test Markers
- `unit`: Unit tests
- `integration`: Integration tests
- `slow`: Slow-running tests
- `api`: Tests requiring API access

## Mock Objects and Fixtures

### API Mocking
Tests use comprehensive mocking for Google Maps API calls to:
- Avoid making real API requests during testing
- Test error scenarios consistently
- Ensure tests run quickly and reliably
- Prevent API quota usage during testing

### Test Fixtures
- `mock_gmaps_client`: Mock Google Maps client
- `valid_csv_content`: Sample valid CSV data
- `complete_place_details`: Complete place information
- `mock_env_vars`: Mock environment variables

## Coverage Requirements

The test suite maintains a minimum coverage requirement of 85% and includes:
- Line coverage for all critical paths
- Branch coverage for conditional logic
- Error path coverage for exception handling
- Edge case coverage for boundary conditions

### Coverage Report
```bash
# Generate coverage report
python run_tests.py coverage

# View detailed HTML report
open htmlcov/index.html
```

## Security Testing

### Input Sanitization Tests
- XSS attack prevention
- SQL injection prevention
- Command injection prevention
- Path traversal prevention
- Unicode handling

### API Security Tests
- API key validation
- Rate limiting verification
- Error message sanitization
- Secure configuration handling

### Example Security Test Cases
```python
def test_sanitize_xss_patterns(self):
    """Test that XSS patterns are sanitized."""
    xss_patterns = [
        '<script>alert("XSS")</script>',
        '<img src="x" onerror="alert(1)">',
        'javascript:alert("XSS")'
    ]
    
    for pattern in xss_patterns:
        result = main.sanitize_input(pattern)
        assert '<' not in result
        assert '>' not in result
```

## Error Testing

### API Error Scenarios
- Network timeouts
- Rate limit exceeded
- Invalid API keys
- Malformed responses
- Service unavailability

### File System Errors
- Permission denied
- File not found
- Disk space full
- Corrupted files

### Data Validation Errors
- Invalid coordinates
- Malformed CSV files
- Missing required fields
- Type conversion errors

## Best Practices

### Test Writing Guidelines
1. **Descriptive Names**: Use clear, descriptive test names
2. **Arrange-Act-Assert**: Follow the AAA pattern
3. **Single Responsibility**: Each test should test one specific behavior
4. **Independent Tests**: Tests should not depend on each other
5. **Mock External Dependencies**: Always mock API calls and file operations
6. **Test Edge Cases**: Include boundary conditions and error scenarios

### Test Maintenance
1. **Regular Updates**: Keep tests updated with code changes
2. **Performance Monitoring**: Monitor test execution time
3. **Coverage Monitoring**: Maintain high test coverage
4. **Documentation**: Keep test documentation current

## Continuous Integration

The test suite is designed to integrate with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    python -m pip install -r requirements-test.txt
    python run_tests.py coverage
    
- name: Upload Coverage
  uses: codecov/codecov-action@v1
  with:
    file: ./coverage.xml
```

## Test Data Management

### Fixtures Directory
- Contains sample data for testing
- Includes both valid and invalid test cases
- Provides configuration files for different scenarios

### Test Data Security
- No real API keys in test data
- Sanitized sample data
- No sensitive information in version control

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure the main module can be imported
python -c "import main"
```

#### Missing Dependencies
```bash
# Install all test dependencies
pip install -r requirements-test.txt
```

#### Coverage Issues
```bash
# Run with detailed coverage output
pytest --cov=main --cov-report=term-missing
```

### Debug Mode
```bash
# Run tests with Python debugger
pytest --pdb

# Run with verbose output and no capture
pytest -v -s
```

## Performance Testing

While the current test suite focuses on unit tests, performance considerations include:
- API rate limiting verification
- Memory usage monitoring
- File processing efficiency
- Error recovery performance

## Future Enhancements

Potential test suite improvements:
- Integration tests with real API (optional)
- Load testing for batch processing
- Property-based testing with Hypothesis
- Mutation testing for test quality verification
- Performance benchmarking

## Contributing to Tests

When adding new features:
1. Write tests before implementing features (TDD)
2. Ensure all tests pass
3. Maintain or improve coverage percentage
4. Add appropriate test markers
5. Update documentation as needed

## Support

For questions about the test suite:
1. Check this documentation
2. Review existing test examples
3. Run tests with verbose output for debugging
4. Check pytest documentation for advanced features