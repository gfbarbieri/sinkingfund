"""
Format Registry
===============

Centralized configuration registry for file formats and data readers with
extensible architecture for supporting multiple input sources in the
sinking fund system.

Core Abstractions
-----------------

**Single Source of Truth**: The SUPPORTED_FORMATS registry serves as the
canonical definition of all file formats, their extensions, associated
reader functions, and metadata. This centralization prevents duplication
and ensures consistent behavior across the application.

**Reader Function Registry**: Each format configuration includes a
reference to its corresponding reader function, enabling dynamic dispatch
based on detected file formats. This pattern decouples format detection
from reader implementation details.

**Extension Mapping**: Multiple file extensions can map to the same
logical format (e.g., both .xlsx and .xls map to 'excel'), providing
flexibility while maintaining consistent internal format representation.

Key Features
------------

* **Format Extensibility**: New file formats can be added by extending
  the registry configuration without modifying existing code paths.
* **Reader Function Dispatch**: Automatic mapping from format names to
  their corresponding reader functions for clean separation of concerns.
* **Multi-Extension Support**: Single formats can support multiple file
  extensions for comprehensive format coverage.
* **Metadata Storage**: Format descriptions and configuration can be
  stored alongside technical details for documentation and UI purposes.
* **Fast Lookups**: Optimized accessor functions provide efficient
  format detection and reader retrieval for performance-critical paths.

Examples
--------

Format detection and reader retrieval:

.. code-block:: python

   # Get format from extension
   format_name = get_format_from_extension('.csv')
   # Returns 'csv'
   
   # Get reader function for format
   reader_func = get_reader_for_format('csv')
   # Returns read_csv_to_dict function
   
   # Use reader function
   data = reader_func('data/bills.csv')

Registry introspection:

.. code-block:: python

   # Get all supported extensions
   extensions = get_supported_extensions()
   # Returns ['.csv', '.xlsx', '.xls', '.json']
   
   # Check format capabilities
   config = get_format_config('excel')
   print(config['description'])
   # Prints 'Microsoft Excel spreadsheet'

"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

from typing import Callable, Optional

from .readers import read_csv_to_dict, read_excel_to_dict, read_json_to_dict

########################################################################
## TYPE DEFINITIONS
########################################################################

# Type alias for reader function signature
ReaderFunction = Callable[[str], list[dict]]

########################################################################
## REGISTRY CONFIGURATION
########################################################################

# BUSINESS GOAL: Single source of truth for all format configuration
# prevents duplication and ensures consistent behavior across the
# application when adding new formats or modifying existing ones.
SUPPORTED_FORMATS: dict[str, dict] = {
    'csv': {
        'extensions': ['.csv'],
        'reader': read_csv_to_dict,
        'description': 'Comma-separated values',
        'mime_types': ['text/csv', 'application/csv']
    },
    'excel': {
        'extensions': ['.xlsx', '.xls'],
        'reader': read_excel_to_dict,
        'description': 'Microsoft Excel spreadsheet',
        'mime_types': [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel'
        ]
    },
    'json': {
        'extensions': ['.json'],
        'reader': read_json_to_dict,
        'description': 'JavaScript Object Notation',
        'mime_types': ['application/json', 'text/json']
    }
}

########################################################################
## FUNCTIONS
########################################################################

def get_format_from_extension(extension: str) -> Optional[str]:
    """
    Resolve file extension to format name using registry lookup.
    
    Performs case-insensitive lookup of file extensions against the
    format registry to determine the appropriate format identifier for
    data loading operations.
    
    Parameters
    ----------
    extension : str
        File extension to look up, with or without leading dot.
        Case-insensitive matching is performed automatically.
        
    Returns
    -------
    str or None
        Format name if extension is supported, None otherwise.
        
    Examples
    --------
    .. code-block:: python
    
       # Standard extensions
       format_name = get_format_from_extension('.csv')
       # Returns 'csv'
       
       # Case-insensitive matching
       format_name = get_format_from_extension('.CSV')
       # Returns 'csv'
       
       # Multiple extensions for same format
       format_name = get_format_from_extension('.xlsx')
       # Returns 'excel'
    """

    # BUSINESS GOAL: Case-insensitive matching prevents issues with
    # mixed-case filenames across different operating systems.
    extension_lower = extension.lower()

    # PERFORMANCE NOTE: Early return on first match avoids unnecessary
    # iteration through remaining formats.
    for format_name, config in SUPPORTED_FORMATS.items():
        if extension_lower in config['extensions']:
            return format_name

    return None

def get_reader_for_format(format_name: str) -> ReaderFunction:
    """
    Retrieve reader function for specified format.
    
    Returns the appropriate data reader function for the given format
    name, enabling dynamic dispatch based on file format detection.
    
    Parameters
    ----------
    format_name : str
        Format identifier from the registry (e.g., 'csv', 'excel', 'json').
        
    Returns
    -------
    ReaderFunction
        Function that can read files of the specified format and return
        standardized list of dictionaries.
        
    Raises
    ------
    KeyError
        If format_name is not found in the registry.
        
    Examples
    --------
    .. code-block:: python
    
       # Get CSV reader
       reader = get_reader_for_format('csv')
       data = reader('bills.csv')
       
       # Dynamic dispatch based on detection
       format_name = get_format_from_extension('.xlsx')
       reader = get_reader_for_format(format_name)
       data = reader('quarterly_report.xlsx')
    """
    try:
        return SUPPORTED_FORMATS[format_name]['reader']
    except KeyError:
        supported = list(SUPPORTED_FORMATS.keys())
        raise KeyError(
            f"Unknown format: {format_name}. "
            f"Supported formats: {', '.join(supported)}"
        ) from None

def get_supported_extensions() -> list[str]:
    """
    Enumerate all supported file extensions across all formats.
    
    Returns a comprehensive list of file extensions that can be processed
    by the data loading system, useful for validation and user guidance.
    
    Returns
    -------
    List[str]
        All supported file extensions including the leading dot.
        
    Examples
    --------
    .. code-block:: python
    
       extensions = get_supported_extensions()
       # Returns ['.csv', '.xlsx', '.xls', '.json']
       
       # Use for validation
       if file_extension not in get_supported_extensions():
           raise ValueError(f"Unsupported extension: {file_extension}")
    """
    
    # PERFORMANCE: List comprehension with extend is more efficient
    # than repeated append operations for building the final list.
    extensions = []
    for config in SUPPORTED_FORMATS.values():
        extensions.extend(config['extensions'])
    
    return extensions

def get_format_config(format_name: str) -> dict:
    """
    Retrieve complete configuration for specified format.
    
    Returns the full configuration dictionary for a format, including
    extensions, reader function, description, and other metadata.
    
    Parameters
    ----------
    format_name : str
        Format identifier from the registry.
        
    Returns
    -------
    Dict
        Complete format configuration dictionary.
        
    Raises
    ------
    KeyError
        If format_name is not found in the registry.
        
    Examples
    --------
    .. code-block:: python
    
       config = get_format_config('excel')
       print(config['description'])
       # Prints 'Microsoft Excel spreadsheet'
       
       print(config['extensions'])
       # Prints ['.xlsx', '.xls']
    """

    # BUSINESS GOAL: Return a copy of the format configuration to
    # prevent modification of the original registry.
    try:
        return SUPPORTED_FORMATS[format_name].copy()
    except KeyError:
        supported = list(SUPPORTED_FORMATS.keys())
        raise KeyError(
            f"Unknown format: {format_name}. "
            f"Supported formats: {', '.join(supported)}"
        ) from None