"""
Unit tests for CSV processing and file handling functionality.
"""
import sys
import os
import tempfile
import csv
from pathlib import Path
from unittest.mock import patch, mock_open
import pytest
import pandas as pd

# Add the parent directory to sys.path so we can import main
sys.path.insert(0, str(Path(__file__).parent.parent))

import main


class TestReadQueries:
    """Test CSV queries reading functionality."""
    
    @pytest.fixture
    def valid_csv_content(self):
        """Fixture providing valid CSV content."""
        return """keyword,category
vet clinic,Competitor
pet grooming,Competitor
animal hospital,Competitor
pet store,Lifestyle_Proxy"""
    
    @pytest.fixture
    def invalid_csv_content(self):
        """Fixture providing invalid CSV content (wrong columns)."""
        return """name,type
vet clinic,Competitor
pet grooming,Competitor"""
    
    @pytest.fixture
    def empty_csv_content(self):
        """Fixture providing CSV with empty rows."""
        return """keyword,category
,
"",""
   ,   """
    
    @pytest.fixture
    def large_csv_content(self):
        """Fixture providing CSV with many rows."""
        lines = ["keyword,category"]
        for i in range(150):  # More than the 100 limit
            lines.append(f"vet clinic {i},Competitor")
        return "\\n".join(lines)
    
    @pytest.fixture
    def csv_with_dangerous_content(self):
        """Fixture providing CSV with potentially dangerous content."""
        return """keyword,category
<script>alert("xss")</script>,Competitor
"normal clinic",Normal
'; DROP TABLE users; --,SQL_Injection
clinic\\with\\backslashes,Test"""
    
    @pytest.mark.unit
    def test_read_queries_success(self, valid_csv_content):
        """Test successful reading of valid CSV file."""
        with patch('main.Path.exists', return_value=True):
            with patch('pandas.read_csv') as mock_read_csv:
                # Create a mock DataFrame
                mock_df = pd.DataFrame({
                    'keyword': ['vet clinic', 'pet grooming', 'animal hospital', 'pet store'],
                    'category': ['Competitor', 'Competitor', 'Competitor', 'Lifestyle_Proxy']
                })
                mock_read_csv.return_value = mock_df.copy()
                
                result = main.read_queries('test_queries.csv')
                
                assert len(result) == 4
                assert list(result.columns) == ['keyword', 'category']
                assert result.iloc[0]['keyword'] == 'vet clinic'
                assert result.iloc[0]['category'] == 'Competitor'
    
    @pytest.mark.unit
    def test_read_queries_file_not_found(self):
        """Test handling of missing CSV file."""
        with patch('main.Path.exists', return_value=False):
            with pytest.raises(SystemExit) as exc_info:
                main.read_queries('nonexistent.csv')
            assert exc_info.value.code == 1
    
    @pytest.mark.unit
    def test_read_queries_invalid_columns(self):
        """Test handling of CSV with invalid column names."""
        with patch('main.Path.exists', return_value=True):
            with patch('pandas.read_csv') as mock_read_csv:
                # Create a mock DataFrame with wrong columns
                mock_df = pd.DataFrame({
                    'name': ['vet clinic', 'pet grooming'],
                    'type': ['Competitor', 'Competitor']
                })
                mock_read_csv.return_value = mock_df
                
                with pytest.raises(SystemExit) as exc_info:
                    main.read_queries('invalid_queries.csv')
                assert exc_info.value.code == 1
    
    @pytest.mark.unit
    def test_read_queries_limits_large_files(self, caplog):
        """Test that large CSV files are limited to prevent excessive API usage."""
        with patch('main.Path.exists', return_value=True):
            with patch('pandas.read_csv') as mock_read_csv:
                # Create a large mock DataFrame
                keywords = [f'vet clinic {i}' for i in range(150)]
                categories = ['Competitor'] * 150
                large_df = pd.DataFrame({
                    'keyword': keywords,
                    'category': categories
                })
                mock_read_csv.return_value = large_df
                
                result = main.read_queries('large_queries.csv')
                
                assert len(result) == 100  # Should be limited
                assert "Too many queries (150). Limiting to 100" in caplog.text
    
    @pytest.mark.unit
    def test_read_queries_sanitizes_input(self):
        """Test that CSV content is sanitized."""
        with patch('main.Path.exists', return_value=True):
            with patch('pandas.read_csv') as mock_read_csv:
                # Create DataFrame with dangerous content
                dangerous_df = pd.DataFrame({
                    'keyword': ['<script>alert("xss")</script>', 'normal clinic', '; DROP TABLE users; --'],
                    'category': ['Competitor', 'Normal', 'SQL_Injection']
                })
                mock_read_csv.return_value = dangerous_df
                
                result = main.read_queries('dangerous_queries.csv')
                
                # Check that dangerous characters are removed
                assert '<script>' not in result.iloc[0]['keyword']
                assert 'alert' in result.iloc[0]['keyword']  # Safe parts preserved
                assert ';' not in result.iloc[2]['keyword']
                assert 'DROP TABLE users' in result.iloc[2]['keyword']  # Safe parts preserved
    
    @pytest.mark.unit
    def test_read_queries_removes_empty_rows(self):
        """Test that empty rows are removed."""
        with patch('main.Path.exists', return_value=True):
            with patch('pandas.read_csv') as mock_read_csv:
                # Create DataFrame with empty rows
                df_with_empty = pd.DataFrame({
                    'keyword': ['vet clinic', '', '   ', 'pet store', ''],
                    'category': ['Competitor', '', 'Empty', 'Lifestyle', '']
                })
                mock_read_csv.return_value = df_with_empty
                
                result = main.read_queries('queries_with_empty.csv')
                
                # Should only have non-empty keywords
                assert len(result) == 2
                assert 'vet clinic' in result['keyword'].values
                assert 'pet store' in result['keyword'].values
    
    @pytest.mark.unit
    def test_read_queries_all_empty_exits(self):
        """Test that CSV with all empty rows causes system exit."""
        with patch('main.Path.exists', return_value=True):
            with patch('pandas.read_csv') as mock_read_csv:
                # Create DataFrame with only empty rows
                empty_df = pd.DataFrame({
                    'keyword': ['', '   ', ''],
                    'category': ['', 'Empty', '']
                })
                mock_read_csv.return_value = empty_df
                
                with pytest.raises(SystemExit) as exc_info:
                    main.read_queries('empty_queries.csv')
                assert exc_info.value.code == 1
    
    @pytest.mark.unit
    def test_read_queries_handles_pandas_errors(self):
        """Test handling of pandas reading errors."""
        with patch('main.Path.exists', return_value=True):
            with patch('pandas.read_csv', side_effect=pd.errors.EmptyDataError("No data")):
                with pytest.raises(SystemExit) as exc_info:
                    main.read_queries('corrupt_queries.csv')
                assert exc_info.value.code == 1
    
    @pytest.mark.unit
    def test_read_queries_handles_unicode_content(self):
        """Test handling of Unicode content in CSV."""
        with patch('main.Path.exists', return_value=True):
            with patch('pandas.read_csv') as mock_read_csv:
                # Create DataFrame with Unicode content
                unicode_df = pd.DataFrame({
                    'keyword': ['café veterinaire', 'клиника для животных', '動物病院'],
                    'category': ['Competitor', 'Competitor', 'Competitor']
                })
                mock_read_csv.return_value = unicode_df
                
                result = main.read_queries('unicode_queries.csv')
                
                assert len(result) == 3
                assert 'café veterinaire' in result['keyword'].values
                assert 'клиника для животных' in result['keyword'].values
                assert '動物病院' in result['keyword'].values
    
    @pytest.mark.unit
    def test_read_queries_with_real_file(self):
        """Test reading from actual CSV files using fixtures."""
        fixture_path = Path(__file__).parent / 'fixtures' / 'test_queries.csv'
        
        result = main.read_queries(str(fixture_path))
        
        assert len(result) > 0
        assert 'keyword' in result.columns
        assert 'category' in result.columns
        assert 'test clinic' in result['keyword'].values
    
    @pytest.mark.unit
    def test_read_queries_invalid_file_exits(self):
        """Test handling of CSV file with invalid columns using fixture."""
        fixture_path = Path(__file__).parent / 'fixtures' / 'test_queries_invalid.csv'
        
        with pytest.raises(SystemExit) as exc_info:
            main.read_queries(str(fixture_path))
        assert exc_info.value.code == 1
    
    @pytest.mark.unit
    def test_read_queries_empty_file_exits(self):
        """Test handling of CSV file with empty content using fixture."""
        fixture_path = Path(__file__).parent / 'fixtures' / 'test_queries_empty.csv'
        
        with pytest.raises(SystemExit) as exc_info:
            main.read_queries(str(fixture_path))
        assert exc_info.value.code == 1


class TestCSVSanitization:
    """Test CSV content sanitization."""
    
    @pytest.mark.unit
    def test_csv_keyword_length_limit(self):
        """Test that keywords are limited to 100 characters."""
        with patch('main.Path.exists', return_value=True):
            with patch('pandas.read_csv') as mock_read_csv:
                long_keyword = 'a' * 150
                df = pd.DataFrame({
                    'keyword': [long_keyword],
                    'category': ['Test']
                })
                mock_read_csv.return_value = df
                
                result = main.read_queries('test.csv')
                
                assert len(result.iloc[0]['keyword']) == 100
    
    @pytest.mark.unit
    def test_csv_category_length_limit(self):
        """Test that categories are limited to 50 characters."""
        with patch('main.Path.exists', return_value=True):
            with patch('pandas.read_csv') as mock_read_csv:
                long_category = 'b' * 80
                df = pd.DataFrame({
                    'keyword': ['test'],
                    'category': [long_category]
                })
                mock_read_csv.return_value = df
                
                result = main.read_queries('test.csv')
                
                assert len(result.iloc[0]['category']) == 50
    
    @pytest.mark.unit
    def test_csv_handles_non_string_values(self):
        """Test handling of non-string values in CSV."""
        with patch('main.Path.exists', return_value=True):
            with patch('pandas.read_csv') as mock_read_csv:
                df = pd.DataFrame({
                    'keyword': [123, None, 'string_keyword'],
                    'category': [456.78, 'valid_category', None]
                })
                mock_read_csv.return_value = df
                
                result = main.read_queries('test.csv')
                
                # Should convert to strings and sanitize
                assert result.iloc[0]['keyword'] == '123'
                assert result.iloc[1]['keyword'] == 'None'
                assert result.iloc[2]['keyword'] == 'string_keyword'
                
                assert result.iloc[0]['category'] == '456.78'
                assert result.iloc[1]['category'] == 'valid_category'
                assert result.iloc[2]['category'] == 'None'


class TestFileHandling:
    """Test file handling edge cases."""
    
    @pytest.mark.unit
    def test_read_queries_with_different_encodings(self):
        """Test handling of different file encodings."""
        # This test would require creating actual files with different encodings
        # For now, we'll test the basic functionality
        with patch('main.Path.exists', return_value=True):
            with patch('pandas.read_csv') as mock_read_csv:
                # Simulate encoding issues being handled by pandas
                mock_read_csv.return_value = pd.DataFrame({
                    'keyword': ['test'],
                    'category': ['test']
                })
                
                result = main.read_queries('test.csv')
                assert len(result) == 1
    
    @pytest.mark.unit
    def test_read_queries_permission_error(self):
        """Test handling of file permission errors."""
        with patch('main.Path.exists', return_value=True):
            with patch('pandas.read_csv', side_effect=PermissionError("Permission denied")):
                with pytest.raises(SystemExit) as exc_info:
                    main.read_queries('protected.csv')
                assert exc_info.value.code == 1
    
    @pytest.mark.unit
    def test_read_queries_file_too_large(self):
        """Test handling of very large CSV files."""
        with patch('main.Path.exists', return_value=True):
            with patch('pandas.read_csv', side_effect=MemoryError("File too large")):
                with pytest.raises(SystemExit) as exc_info:
                    main.read_queries('huge.csv')
                assert exc_info.value.code == 1
    
    @pytest.mark.unit
    def test_read_queries_corrupted_csv(self):
        """Test handling of corrupted CSV files."""
        with patch('main.Path.exists', return_value=True):
            with patch('pandas.read_csv', side_effect=pd.errors.ParserError("Corrupted file")):
                with pytest.raises(SystemExit) as exc_info:
                    main.read_queries('corrupted.csv')
                assert exc_info.value.code == 1
    
    @pytest.mark.unit
    def test_read_queries_default_filename(self):
        """Test reading with default filename."""
        with patch('main.Path.exists', return_value=True):
            with patch('pandas.read_csv') as mock_read_csv:
                mock_read_csv.return_value = pd.DataFrame({
                    'keyword': ['test'],
                    'category': ['test']
                })
                
                # Call without filename argument
                result = main.read_queries()
                
                # Should use default 'queries.csv'
                mock_read_csv.assert_called_once_with('queries.csv')
                assert len(result) == 1