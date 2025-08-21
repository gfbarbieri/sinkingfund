"""
Loaders Tests
=============

Comprehensive tests for data loading utilities covering format
detection, reader orchestration, and error handling for the high-level
data loading interface.
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

from unittest.mock import patch, Mock
import pytest

from sinkingfund.utils.loaders import load_bill_data_from_file

########################################################################
## TEST CLASSES
########################################################################

class TestLoadBillDataFromFile:
    """Test high-level bill data loading from files."""

    @patch('sinkingfund.utils.loaders.detect_file_format')
    @patch('sinkingfund.utils.loaders.get_reader_for_format')
    def test_csv_file_loading(self, mock_get_reader, mock_detect_format) -> None:
        """
        Test loading bill data from CSV files.
        """
        
        # Test: Mock format detection and reader.
        mock_detect_format.return_value = 'csv'
        mock_reader = Mock()
        mock_reader.return_value = {'bills': [{'bill_id': 'test'}]}
        mock_get_reader.return_value = mock_reader
        
        # Test: Load data from CSV file.
        result = load_bill_data_from_file('data/bills.csv')
        
        # Test: Verify format detection was called.
        mock_detect_format.assert_called_once_with('data/bills.csv')
        
        # Test: Verify reader retrieval was called.
        mock_get_reader.assert_called_once_with('csv')
        
        # Test: Verify reader was called with file path.
        mock_reader.assert_called_once_with('data/bills.csv')
        
        # Test: Verify result is returned.
        assert result == {'bills': [{'bill_id': 'test'}]}

    @patch('sinkingfund.utils.loaders.detect_file_format')
    @patch('sinkingfund.utils.loaders.get_reader_for_format')
    def test_excel_file_loading(self, mock_get_reader, mock_detect_format) -> None:
        """
        Test loading bill data from Excel files.
        """
        
        # Test: Mock format detection and reader.
        mock_detect_format.return_value = 'excel'
        mock_reader = Mock()
        mock_reader.return_value = {'bills': [{'bill_id': 'excel_test'}]}
        mock_get_reader.return_value = mock_reader
        
        # Test: Load data from Excel file.
        result = load_bill_data_from_file('data/bills.xlsx')
        
        # Test: Verify format detection was called.
        mock_detect_format.assert_called_once_with('data/bills.xlsx')
        
        # Test: Verify reader retrieval was called.
        mock_get_reader.assert_called_once_with('excel')
        
        # Test: Verify reader was called with file path.
        mock_reader.assert_called_once_with('data/bills.xlsx')
        
        # Test: Verify result is returned.
        assert result == {'bills': [{'bill_id': 'excel_test'}]}

    @patch('sinkingfund.utils.loaders.detect_file_format')
    @patch('sinkingfund.utils.loaders.get_reader_for_format')
    def test_json_file_loading(self, mock_get_reader, mock_detect_format) -> None:
        """
        Test loading bill data from JSON files.
        """
        
        # Test: Mock format detection and reader.
        mock_detect_format.return_value = 'json'
        mock_reader = Mock()
        mock_reader.return_value = {'bills': [{'bill_id': 'json_test'}]}
        mock_get_reader.return_value = mock_reader
        
        # Test: Load data from JSON file.
        result = load_bill_data_from_file('config/bills.json')
        
        # Test: Verify format detection was called.
        mock_detect_format.assert_called_once_with('config/bills.json')
        
        # Test: Verify reader retrieval was called.
        mock_get_reader.assert_called_once_with('json')
        
        # Test: Verify reader was called with file path.
        mock_reader.assert_called_once_with('config/bills.json')
        
        # Test: Verify result is returned.
        assert result == {'bills': [{'bill_id': 'json_test'}]}

    @patch('sinkingfund.utils.loaders.detect_file_format')
    @patch('sinkingfund.utils.loaders.get_reader_for_format')
    def test_kwargs_passing(self, mock_get_reader, mock_detect_format) -> None:
        """
        Test passing format-specific kwargs to readers.
        """
        
        # Test: Mock format detection and reader.
        mock_detect_format.return_value = 'excel'
        mock_reader = Mock()
        mock_reader.return_value = {'bills': []}
        mock_get_reader.return_value = mock_reader
        
        # Test: Load data with Excel-specific kwargs.
        result = load_bill_data_from_file(
            'data/bills.xlsx', 
            sheet_name='Bills'
        )
        
        # Test: Verify reader was called with kwargs.
        mock_reader.assert_called_once_with('data/bills.xlsx', sheet_name='Bills')

    @patch('sinkingfund.utils.loaders.detect_file_format')
    def test_format_detection_error_propagation(self, mock_detect_format) -> None:
        """
        Test that format detection errors are properly propagated.
        """
        
        # Test: Mock format detection raising ValueError.
        mock_detect_format.side_effect = ValueError("Unsupported format")
        
        # Test: Verify error is propagated.
        with pytest.raises(ValueError, match="Unsupported format"):
            load_bill_data_from_file('data/unsupported.xyz')

    @patch('sinkingfund.utils.loaders.detect_file_format')
    @patch('sinkingfund.utils.loaders.get_reader_for_format')
    def test_reader_retrieval_error_propagation(self, mock_get_reader, mock_detect_format) -> None:
        """
        Test that reader retrieval errors are properly propagated.
        """
        
        # Test: Mock format detection succeeding.
        mock_detect_format.return_value = 'invalid'
        
        # Test: Mock reader retrieval raising KeyError.
        mock_get_reader.side_effect = KeyError("Unknown format")
        
        # Test: Verify error is propagated.
        with pytest.raises(KeyError, match="Unknown format"):
            load_bill_data_from_file('data/bills.invalid')

    @patch('sinkingfund.utils.loaders.detect_file_format')
    @patch('sinkingfund.utils.loaders.get_reader_for_format')
    def test_reader_execution_error_propagation(self, mock_get_reader, mock_detect_format) -> None:
        """
        Test that reader execution errors are properly propagated.
        """
        
        # Test: Mock format detection and reader retrieval.
        mock_detect_format.return_value = 'csv'
        mock_reader = Mock()
        mock_reader.side_effect = FileNotFoundError("File not found")
        mock_get_reader.return_value = mock_reader
        
        # Test: Verify error is propagated.
        with pytest.raises(FileNotFoundError, match="File not found"):
            load_bill_data_from_file('data/nonexistent.csv')

########################################################################
## INTEGRATION TESTS
########################################################################

class TestLoadersIntegration:
    """Test integration with actual utility functions."""

    @patch('sinkingfund.utils.loaders.get_reader_for_format')
    def test_real_format_detection_csv(self, mock_get_reader) -> None:
        """
        Test integration with real format detection for CSV.
        """
        
        # Test: Mock only the reader, use real format detection.
        mock_reader = Mock()
        mock_reader.return_value = {'test': 'data'}
        mock_get_reader.return_value = mock_reader
        
        # Test: Load CSV file (format detection should work).
        result = load_bill_data_from_file('test.csv')
        
        # Test: Verify CSV format was detected and reader called.
        mock_get_reader.assert_called_once_with('csv')
        mock_reader.assert_called_once_with('test.csv')
        assert result == {'test': 'data'}

    @patch('sinkingfund.utils.loaders.get_reader_for_format')
    def test_real_format_detection_excel(self, mock_get_reader) -> None:
        """
        Test integration with real format detection for Excel.
        """
        
        # Test: Mock only the reader, use real format detection.
        mock_reader = Mock()
        mock_reader.return_value = {'test': 'data'}
        mock_get_reader.return_value = mock_reader
        
        # Test: Load Excel file (format detection should work).
        result = load_bill_data_from_file('test.xlsx')
        
        # Test: Verify Excel format was detected and reader called.
        mock_get_reader.assert_called_once_with('excel')
        mock_reader.assert_called_once_with('test.xlsx')
        assert result == {'test': 'data'}

    @patch('sinkingfund.utils.loaders.get_reader_for_format')
    def test_real_format_detection_json(self, mock_get_reader) -> None:
        """
        Test integration with real format detection for JSON.
        """
        
        # Test: Mock only the reader, use real format detection.
        mock_reader = Mock()
        mock_reader.return_value = {'test': 'data'}
        mock_get_reader.return_value = mock_reader
        
        # Test: Load JSON file (format detection should work).
        result = load_bill_data_from_file('test.json')
        
        # Test: Verify JSON format was detected and reader called.
        mock_get_reader.assert_called_once_with('json')
        mock_reader.assert_called_once_with('test.json')
        assert result == {'test': 'data'}

    def test_real_format_detection_unsupported(self) -> None:
        """
        Test integration with real format detection for unsupported formats.
        """
        
        # Test: Use real format detection with unsupported format.
        with pytest.raises(ValueError, match="Unsupported file format"):
            load_bill_data_from_file('test.pdf')

########################################################################
## PATHLIB TESTS
########################################################################

class TestLoadersPathSupport:
    """Test Path-like object support in loaders."""

    @patch('sinkingfund.utils.loaders.detect_file_format')
    @patch('sinkingfund.utils.loaders.get_reader_for_format')
    def test_pathlib_path_support(self, mock_get_reader, mock_detect_format) -> None:
        """
        Test loading with pathlib.Path objects.
        """
        
        from pathlib import Path
        
        # Test: Mock format detection and reader.
        mock_detect_format.return_value = 'csv'
        mock_reader = Mock()
        mock_reader.return_value = {'test': 'data'}
        mock_get_reader.return_value = mock_reader
        
        # Test: Load data using Path object.
        path = Path('data/bills.csv')
        result = load_bill_data_from_file(path)
        
        # Test: Verify path was passed through correctly.
        mock_detect_format.assert_called_once_with(path)
        mock_reader.assert_called_once_with(path)
        assert result == {'test': 'data'}

########################################################################
## EDGE CASE TESTS
########################################################################

class TestLoadersEdgeCases:
    """Test edge cases and boundary conditions."""

    @patch('sinkingfund.utils.loaders.detect_file_format')
    @patch('sinkingfund.utils.loaders.get_reader_for_format')
    def test_empty_file_path(self, mock_get_reader, mock_detect_format) -> None:
        """
        Test handling of empty file paths.
        """
        
        # Test: Mock format detection raising error for empty path.
        mock_detect_format.side_effect = ValueError("Unsupported file format")
        
        # Test: Verify error handling.
        with pytest.raises(ValueError):
            load_bill_data_from_file('')

    def test_none_file_path(self) -> None:
        """
        Test handling of None file paths.
        """
        
        # Test: This should cause a TypeError in pathlib.Path().
        with pytest.raises(TypeError, match="argument should be a str or an os.PathLike"):
            load_bill_data_from_file(None)  # type: ignore

    @patch('sinkingfund.utils.loaders.detect_file_format')
    @patch('sinkingfund.utils.loaders.get_reader_for_format')
    def test_reader_returns_none(self, mock_get_reader, mock_detect_format) -> None:
        """
        Test handling when reader returns None.
        """
        
        # Test: Mock format detection and reader returning None.
        mock_detect_format.return_value = 'csv'
        mock_reader = Mock()
        mock_reader.return_value = None
        mock_get_reader.return_value = mock_reader
        
        # Test: Load data and verify None is returned.
        result = load_bill_data_from_file('test.csv')
        assert result is None

    @patch('sinkingfund.utils.loaders.detect_file_format')
    @patch('sinkingfund.utils.loaders.get_reader_for_format')
    def test_reader_returns_empty_dict(self, mock_get_reader, mock_detect_format) -> None:
        """
        Test handling when reader returns empty data.
        """
        
        # Test: Mock format detection and reader returning empty dict.
        mock_detect_format.return_value = 'csv'
        mock_reader = Mock()
        mock_reader.return_value = {}
        mock_get_reader.return_value = mock_reader
        
        # Test: Load data and verify empty dict is returned.
        result = load_bill_data_from_file('test.csv')
        assert result == {}

########################################################################
## KWARGS TESTS
########################################################################

class TestLoadersKwargsHandling:
    """Test handling of format-specific keyword arguments."""

    @patch('sinkingfund.utils.loaders.detect_file_format')
    @patch('sinkingfund.utils.loaders.get_reader_for_format')
    def test_excel_sheet_name_kwarg(self, mock_get_reader, mock_detect_format) -> None:
        """
        Test passing sheet_name kwarg for Excel files.
        """
        
        # Test: Mock format detection and reader.
        mock_detect_format.return_value = 'excel'
        mock_reader = Mock()
        mock_reader.return_value = {'test': 'data'}
        mock_get_reader.return_value = mock_reader
        
        # Test: Load with sheet_name kwarg.
        result = load_bill_data_from_file(
            'test.xlsx', 
            sheet_name='Sheet2'
        )
        
        # Test: Verify kwarg was passed to reader.
        mock_reader.assert_called_once_with('test.xlsx', sheet_name='Sheet2')

    @patch('sinkingfund.utils.loaders.detect_file_format')
    @patch('sinkingfund.utils.loaders.get_reader_for_format')
    def test_multiple_kwargs(self, mock_get_reader, mock_detect_format) -> None:
        """
        Test passing multiple kwargs to readers.
        """
        
        # Test: Mock format detection and reader.
        mock_detect_format.return_value = 'csv'
        mock_reader = Mock()
        mock_reader.return_value = {'test': 'data'}
        mock_get_reader.return_value = mock_reader
        
        # Test: Load with multiple kwargs.
        result = load_bill_data_from_file(
            'test.csv',
            delimiter=';',
            encoding='utf-8'
        )
        
        # Test: Verify all kwargs were passed to reader.
        mock_reader.assert_called_once_with(
            'test.csv', 
            delimiter=';', 
            encoding='utf-8'
        )
