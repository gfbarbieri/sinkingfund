"""
File Utilities Tests
====================

Comprehensive tests for file utilities covering format detection,
path handling, and error cases with various file types and edge
conditions.
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch
import pytest

from sinkingfund.utils.file_utils import detect_file_format, PathLike

########################################################################
## TEST CLASSES
########################################################################

class TestDetectFileFormat:
    """Test file format detection from file paths."""

    def test_csv_format_detection(self) -> None:
        """
        Test CSV format detection from file paths.
        """
        
        # Test: Standard CSV file.
        result = detect_file_format("data/bills.csv")
        assert result == "csv"
        
        # Test: CSV file with path.
        result = detect_file_format("/home/user/documents/expenses.csv")
        assert result == "csv"
        
        # Test: CSV file with relative path.
        result = detect_file_format("./files/budget.csv")
        assert result == "csv"

    def test_excel_format_detection(self) -> None:
        """
        Test Excel format detection from file paths.
        """
        
        # Test: Modern Excel format (.xlsx).
        result = detect_file_format("data/bills.xlsx")
        assert result == "excel"
        
        # Test: Legacy Excel format (.xls).
        result = detect_file_format("data/bills.xls")
        assert result == "excel"
        
        # Test: Excel file with complex path.
        result = detect_file_format("/Documents/Financial/Q1_2024.xlsx")
        assert result == "excel"

    def test_json_format_detection(self) -> None:
        """
        Test JSON format detection from file paths.
        """
        
        # Test: Standard JSON file.
        result = detect_file_format("config/bills.json")
        assert result == "json"
        
        # Test: JSON file with path.
        result = detect_file_format("/etc/app/configuration.json")
        assert result == "json"

    def test_case_insensitive_detection(self) -> None:
        """
        Test case-insensitive file extension detection.
        """
        
        # Test: Uppercase extensions.
        result = detect_file_format("data/BILLS.CSV")
        assert result == "csv"
        
        result = detect_file_format("data/REPORT.XLSX")
        assert result == "excel"
        
        result = detect_file_format("config/SETTINGS.JSON")
        assert result == "json"
        
        # Test: Mixed case extensions.
        result = detect_file_format("data/bills.CsV")
        assert result == "csv"
        
        result = detect_file_format("data/report.XlSx")
        assert result == "excel"

    def test_pathlib_path_support(self) -> None:
        """
        Test support for pathlib.Path objects.
        """
        
        # Test: Path object with CSV.
        path = Path("data/bills.csv")
        result = detect_file_format(path)
        assert result == "csv"
        
        # Test: Path object with Excel.
        path = Path("reports/quarterly.xlsx")
        result = detect_file_format(path)
        assert result == "excel"
        
        # Test: Path object with JSON.
        path = Path("config/settings.json")
        result = detect_file_format(path)
        assert result == "json"

    def test_complex_file_paths(self) -> None:
        """
        Test format detection with complex file paths.
        """
        
        # Test: Multiple dots in filename.
        result = detect_file_format("backup.2024.01.15.csv")
        assert result == "csv"
        
        # Test: Spaces in path.
        result = detect_file_format("My Documents/Budget 2024.xlsx")
        assert result == "excel"
        
        # Test: Special characters in path.
        result = detect_file_format("data/bills-2024_Q1.json")
        assert result == "json"

    def test_unsupported_format_errors(self) -> None:
        """
        Test error handling for unsupported file formats.
        """
        
        # Test: Unsupported extension raises ValueError.
        with pytest.raises(ValueError, match="Unsupported file format"):
            detect_file_format("data/document.pdf")
        
        with pytest.raises(ValueError, match="Unsupported file format"):
            detect_file_format("data/document.txt")
        
        with pytest.raises(ValueError, match="Unsupported file format"):
            detect_file_format("data/document.xml")

    def test_error_message_includes_supported_formats(self) -> None:
        """
        Test that error messages include list of supported formats.
        """
        
        # Test: Error message contains supported extensions.
        with pytest.raises(ValueError) as exc_info:
            detect_file_format("data/unsupported.abc")
        
        error_message = str(exc_info.value)
        assert ".csv" in error_message
        assert ".xlsx" in error_message or ".xls" in error_message
        assert ".json" in error_message

    def test_no_extension_files(self) -> None:
        """
        Test handling of files without extensions.
        """
        
        # Test: File without extension raises ValueError.
        with pytest.raises(ValueError, match="Unsupported file format"):
            detect_file_format("data/bills")
        
        # Test: Directory-like path without extension.
        with pytest.raises(ValueError, match="Unsupported file format"):
            detect_file_format("data/folder")

    def test_dot_files(self) -> None:
        """
        Test handling of dot files and hidden files.
        """
        
        # Test: Hidden file with supported extension.
        result = detect_file_format(".hidden_bills.csv")
        assert result == "csv"
        
        # Test: Hidden file without extension after dot.
        with pytest.raises(ValueError, match="Unsupported file format"):
            detect_file_format(".hidden")

########################################################################
## INTEGRATION TESTS
########################################################################

class TestFileUtilsIntegration:
    """Test integration with format registry."""

    @patch('sinkingfund.utils.file_utils.get_format_from_extension')
    def test_format_registry_integration(self, mock_get_format) -> None:
        """
        Test integration with format registry functions.
        """
        
        # Test: Mock format registry returning a format.
        mock_get_format.return_value = "csv"
        
        result = detect_file_format("test.csv")
        assert result == "csv"
        
        # Test: Verify the registry was called with lowercase extension.
        mock_get_format.assert_called_once_with(".csv")

    @patch('sinkingfund.utils.file_utils.get_format_from_extension')
    @patch('sinkingfund.utils.file_utils.get_supported_extensions')
    def test_error_handling_integration(self, mock_get_extensions, mock_get_format) -> None:
        """
        Test error handling integration with format registry.
        """
        
        # Test: Mock format registry returning None (unsupported).
        mock_get_format.return_value = None
        mock_get_extensions.return_value = [".csv", ".xlsx", ".json"]
        
        with pytest.raises(ValueError) as exc_info:
            detect_file_format("test.xyz")
        
        # Test: Verify both registry functions were called.
        mock_get_format.assert_called_once_with(".xyz")
        mock_get_extensions.assert_called_once()
        
        # Test: Verify error message includes supported extensions.
        error_message = str(exc_info.value)
        assert ".csv" in error_message
        assert ".xlsx" in error_message
        assert ".json" in error_message

########################################################################
## EDGE CASE TESTS
########################################################################

class TestFileUtilsEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_filename(self) -> None:
        """
        Test handling of empty filenames.
        """
        
        # Test: Empty string raises ValueError.
        with pytest.raises(ValueError, match="Unsupported file format"):
            detect_file_format("")

    def test_just_extension(self) -> None:
        """
        Test handling of paths that are just extensions.
        """
        
        # Test: Just an extension (pathlib treats this as a hidden file).
        # Path(".csv").suffix returns "." not ".csv", so this should fail.
        with pytest.raises(ValueError, match="Unsupported file format"):
            detect_file_format(".csv")
        
        # Test: Just an unsupported extension.
        with pytest.raises(ValueError, match="Unsupported file format"):
            detect_file_format(".xyz")

    def test_multiple_extensions(self) -> None:
        """
        Test handling of files with multiple extensions.
        """
        
        # Test: File with multiple extensions uses the last one.
        result = detect_file_format("data.backup.csv")
        assert result == "csv"
        
        result = detect_file_format("report.2024.xlsx")
        assert result == "excel"
        
        # Test: Multiple extensions with unsupported final extension.
        with pytest.raises(ValueError, match="Unsupported file format"):
            detect_file_format("data.csv.backup")

    def test_extension_only_dots(self) -> None:
        """
        Test handling of filenames with only dots.
        """
        
        # Test: Multiple dots without extension.
        with pytest.raises(ValueError, match="Unsupported file format"):
            detect_file_format("...")
        
        # Test: Single dot.
        with pytest.raises(ValueError, match="Unsupported file format"):
            detect_file_format(".")

    def test_path_with_spaces_and_special_chars(self) -> None:
        """
        Test handling of paths with spaces and special characters.
        """
        
        # Test: Spaces in filename.
        result = detect_file_format("My Budget File.csv")
        assert result == "csv"
        
        # Test: Special characters in filename.
        result = detect_file_format("bills_2024-Q1&Q2.xlsx")
        assert result == "excel"
        
        # Test: Unicode characters in filename.
        result = detect_file_format("prévu_budget.json")
        assert result == "json"

########################################################################
## TYPE ANNOTATION TESTS
########################################################################

class TestPathLikeTypeHints:
    """Test PathLike type annotation behavior."""

    def test_string_path_accepted(self) -> None:
        """
        Test that string paths work with PathLike type hint.
        """
        
        # Test: Regular string path.
        path: PathLike = "data/bills.csv"
        result = detect_file_format(path)
        assert result == "csv"

    def test_pathlib_path_accepted(self) -> None:
        """
        Test that pathlib.Path objects work with PathLike type hint.
        """
        
        # Test: pathlib.Path object.
        path: PathLike = Path("data/bills.xlsx")
        result = detect_file_format(path)
        assert result == "excel"

    def test_os_pathlike_interface(self) -> None:
        """
        Test that objects implementing os.PathLike work.
        """
        
        # Test: Create a custom PathLike object.
        class CustomPath:
            def __init__(self, path: str) -> None:
                self._path = path
            
            def __fspath__(self) -> str:
                return self._path
        
        # Test: Custom PathLike object.
        custom_path = CustomPath("data/bills.json")
        result = detect_file_format(custom_path)
        assert result == "json"

########################################################################
## PERFORMANCE TESTS
########################################################################

class TestFileUtilsPerformance:
    """Test performance characteristics."""

    def test_format_detection_efficiency(self) -> None:
        """
        Test that format detection is efficient for various path lengths.
        """
        
        # Test: Short path.
        result = detect_file_format("a.csv")
        assert result == "csv"
        
        # Test: Very long path.
        long_path = "/".join(["very_long_directory_name"] * 10) + "/file.xlsx"
        result = detect_file_format(long_path)
        assert result == "excel"
        
        # Test: Path with many dots.
        dotted_path = "file." + ".".join(["part"] * 20) + ".json"
        result = detect_file_format(dotted_path)
        assert result == "json"
