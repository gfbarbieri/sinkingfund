"""
Format Registry Tests
=====================

Comprehensive tests for format registry functions covering extension
mapping, reader retrieval, and registry introspection with edge cases
and error handling validation.
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import pytest

from sinkingfund.utils.format_registry import (
    get_format_from_extension,
    get_reader_for_format,
    get_supported_extensions,
    get_format_config,
    SUPPORTED_FORMATS
)
from sinkingfund.utils.readers import (
    read_csv_to_dict, read_excel_to_dict, read_json_to_dict
)

########################################################################
## TEST CLASSES
########################################################################

class TestGetFormatFromExtension:
    """Test format detection from file extensions."""

    def test_csv_extension_detection(self) -> None:
        """
        Test CSV format detection from extension.
        """
        
        # Test: Standard CSV extension.
        result = get_format_from_extension('.csv')
        assert result == 'csv'

    def test_excel_extension_detection(self) -> None:
        """
        Test Excel format detection from extensions.
        """
        
        # Test: Modern Excel format.
        result = get_format_from_extension('.xlsx')
        assert result == 'excel'
        
        # Test: Legacy Excel format.
        result = get_format_from_extension('.xls')
        assert result == 'excel'

    def test_json_extension_detection(self) -> None:
        """
        Test JSON format detection from extension.
        """
        
        # Test: Standard JSON extension.
        result = get_format_from_extension('.json')
        assert result == 'json'

    def test_case_insensitive_detection(self) -> None:
        """
        Test case-insensitive extension matching.
        """
        
        # Test: Uppercase extension.
        result = get_format_from_extension('.CSV')
        assert result == 'csv'
        
        # Test: Mixed case extension.
        result = get_format_from_extension('.XlSx')
        assert result == 'excel'
        
        # Test: Lowercase JSON.
        result = get_format_from_extension('.json')
        assert result == 'json'

    def test_extension_without_dot(self) -> None:
        """
        Test extension detection without leading dot.
        """
        
        # Test: Extension without dot should still work if implementation
        # handles it, but based on the registry it expects dots.
        result = get_format_from_extension('csv')
        assert result is None  # Should return None since registry has '.csv'

    def test_unsupported_extension(self) -> None:
        """
        Test handling of unsupported file extensions.
        """
        
        # Test: Unsupported extension returns None.
        result = get_format_from_extension('.xml')
        assert result is None
        
        # Test: Random extension returns None.
        result = get_format_from_extension('.abc')
        assert result is None
        
        # Test: Empty extension returns None.
        result = get_format_from_extension('')
        assert result is None

class TestGetReaderForFormat:
    """Test reader function retrieval for formats."""

    def test_csv_reader_retrieval(self) -> None:
        """
        Test retrieving CSV reader function.
        """
        
        # Test: Get CSV reader function.
        reader = get_reader_for_format('csv')
        assert reader == read_csv_to_dict
        
        # Test: Verify it's callable.
        assert callable(reader)

    def test_excel_reader_retrieval(self) -> None:
        """
        Test retrieving Excel reader function.
        """
        
        # Test: Get Excel reader function.
        reader = get_reader_for_format('excel')
        assert reader == read_excel_to_dict
        
        # Test: Verify it's callable.
        assert callable(reader)

    def test_json_reader_retrieval(self) -> None:
        """
        Test retrieving JSON reader function.
        """
        
        # Test: Get JSON reader function.
        reader = get_reader_for_format('json')
        assert reader == read_json_to_dict
        
        # Test: Verify it's callable.
        assert callable(reader)

    def test_unsupported_format_error(self) -> None:
        """
        Test error handling for unsupported formats.
        """
        
        # Test: Unsupported format raises KeyError.
        with pytest.raises(KeyError, match="Unknown format: invalid"):
            get_reader_for_format('invalid')
        
        # Test: Error message includes supported formats.
        with pytest.raises(KeyError, match="Supported formats"):
            get_reader_for_format('unsupported')

class TestGetSupportedExtensions:
    """Test supported extensions enumeration."""

    def test_supported_extensions_list(self) -> None:
        """
        Test getting list of all supported extensions.
        """
        
        # Test: Get supported extensions.
        extensions = get_supported_extensions()
        
        # Test: Verify it's a list.
        assert isinstance(extensions, list)
        
        # Test: Verify it contains expected extensions.
        assert '.csv' in extensions
        assert '.xlsx' in extensions
        assert '.xls' in extensions
        assert '.json' in extensions

    def test_extensions_completeness(self) -> None:
        """
        Test that all extensions from registry are included.
        """
        
        # Test: Get extensions from function.
        extensions = get_supported_extensions()
        
        # Test: Get extensions from registry directly.
        expected_extensions = []
        for config in SUPPORTED_FORMATS.values():
            expected_extensions.extend(config['extensions'])
        
        # Test: Verify all expected extensions are present.
        for ext in expected_extensions:
            assert ext in extensions

    def test_extensions_no_duplicates(self) -> None:
        """
        Test that supported extensions list has no duplicates.
        """
        
        # Test: Get supported extensions.
        extensions = get_supported_extensions()
        
        # Test: Verify no duplicates.
        assert len(extensions) == len(set(extensions))

class TestGetFormatConfig:
    """Test format configuration retrieval."""

    def test_csv_config_retrieval(self) -> None:
        """
        Test retrieving CSV format configuration.
        """
        
        # Test: Get CSV configuration.
        config = get_format_config('csv')
        
        # Test: Verify configuration structure.
        assert isinstance(config, dict)
        assert 'extensions' in config
        assert 'reader' in config
        assert 'description' in config
        assert 'mime_types' in config
        
        # Test: Verify CSV-specific values.
        assert '.csv' in config['extensions']
        assert config['reader'] == read_csv_to_dict
        assert 'comma-separated' in config['description'].lower()

    def test_excel_config_retrieval(self) -> None:
        """
        Test retrieving Excel format configuration.
        """
        
        # Test: Get Excel configuration.
        config = get_format_config('excel')
        
        # Test: Verify Excel-specific values.
        assert '.xlsx' in config['extensions']
        assert '.xls' in config['extensions']
        assert config['reader'] == read_excel_to_dict
        assert 'excel' in config['description'].lower()

    def test_json_config_retrieval(self) -> None:
        """
        Test retrieving JSON format configuration.
        """
        
        # Test: Get JSON configuration.
        config = get_format_config('json')
        
        # Test: Verify JSON-specific values.
        assert '.json' in config['extensions']
        assert config['reader'] == read_json_to_dict
        assert 'javascript' in config['description'].lower() or 'json' in config['description'].lower()

    def test_config_isolation(self) -> None:
        """
        Test that returned configuration is a copy, not reference.
        """
        
        # Test: Get configuration.
        config = get_format_config('csv')
        
        # Test: Modify the returned configuration.
        original_description = config['description']
        config['description'] = 'Modified'
        
        # Test: Get configuration again.
        config2 = get_format_config('csv')
        
        # Test: Verify original wasn't modified.
        assert config2['description'] == original_description
        assert config2['description'] != 'Modified'

    def test_unsupported_format_config_error(self) -> None:
        """
        Test error handling for unsupported format configurations.
        """
        
        # Test: Unsupported format raises KeyError.
        with pytest.raises(KeyError, match="Unknown format: invalid"):
            get_format_config('invalid')
        
        # Test: Error message includes supported formats.
        with pytest.raises(KeyError, match="Supported formats"):
            get_format_config('nonexistent')

########################################################################
## INTEGRATION TESTS
########################################################################

class TestFormatRegistryIntegration:
    """Test integration between format registry functions."""

    def test_extension_to_reader_workflow(self) -> None:
        """
        Test complete workflow from extension to reader function.
        """
        
        # Test: CSV workflow.
        format_name = get_format_from_extension('.csv')
        assert format_name == 'csv'
        
        reader = get_reader_for_format(format_name)
        assert reader == read_csv_to_dict
        
        # Test: Excel workflow.
        format_name = get_format_from_extension('.xlsx')
        assert format_name == 'excel'
        
        reader = get_reader_for_format(format_name)
        assert reader == read_excel_to_dict

    def test_all_supported_formats_complete(self) -> None:
        """
        Test that all supported formats have complete configurations.
        """
        
        # Test: Get all extensions.
        extensions = get_supported_extensions()
        
        for ext in extensions:
            # Test: Extension maps to format.
            format_name = get_format_from_extension(ext)
            assert format_name is not None
            
            # Test: Format has reader.
            reader = get_reader_for_format(format_name)
            assert callable(reader)
            
            # Test: Format has complete config.
            config = get_format_config(format_name)
            assert 'extensions' in config
            assert 'reader' in config
            assert 'description' in config
            assert 'mime_types' in config

    def test_registry_consistency(self) -> None:
        """
        Test consistency between registry and accessor functions.
        """
        
        # Test: All formats in SUPPORTED_FORMATS are accessible.
        for format_name in SUPPORTED_FORMATS.keys():
            
            # Test: Config is retrievable.
            config = get_format_config(format_name)
            assert config is not None
            
            # Test: Reader is retrievable.
            reader = get_reader_for_format(format_name)
            assert reader is not None
            
            # Test: Extensions are mappable back to format.
            for ext in config['extensions']:
                detected_format = get_format_from_extension(ext)
                assert detected_format == format_name

########################################################################
## EDGE CASE TESTS
########################################################################

class TestFormatRegistryEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_extension_handling(self) -> None:
        """
        Test handling of empty or malformed extensions.
        """
        
        # Test: Empty string.
        result = get_format_from_extension('')
        assert result is None
        
        # Test: Just a dot.
        result = get_format_from_extension('.')
        assert result is None
        
        # Test: Multiple dots.
        result = get_format_from_extension('..csv')
        assert result is None

    def test_whitespace_extension_handling(self) -> None:
        """
        Test handling of extensions with whitespace.
        """
        
        # Test: Extension with spaces (should not match).
        result = get_format_from_extension('.csv ')
        assert result is None
        
        # Test: Extension with leading space.
        result = get_format_from_extension(' .csv')
        assert result is None

    def test_format_name_case_sensitivity(self) -> None:
        """
        Test case sensitivity in format names for reader retrieval.
        """
        
        # Test: Uppercase format name should fail.
        with pytest.raises(KeyError):
            get_reader_for_format('CSV')
        
        # Test: Mixed case format name should fail.
        with pytest.raises(KeyError):
            get_reader_for_format('Csv')
