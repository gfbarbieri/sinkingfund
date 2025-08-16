"""
File Utilities
==============

File format detection and validation utilities for the sinking fund data
loading system with support for multiple input formats and robust error
handling.

Core Abstractions
-----------------

**Extension-Based Detection**: The format detection system uses file
extensions as the primary mechanism for determining the appropriate data
reader. This approach provides fast, reliable format identification
without requiring file content inspection or external dependencies.

**Format Registry Integration**: Rather than hardcoding format mappings,
this module delegates to a centralized format registry that maintains
the canonical mapping between file extensions and format names. This
design enables easy extension to new formats without modifying detection
logic.

**Path-Like Support**: Functions accept both string paths and path-like
objects, providing flexibility for different path handling patterns
throughout the application.

Key Features
------------

* **Multi-Format Support**: Detects CSV, Excel, and JSON formats through
  standardized extension mapping.
* **Comprehensive Error Messages**: Provides actionable error messages
  that include lists of supported formats when detection fails.
* **Registry-Driven**: Uses centralized format registry for consistent
  format definitions across the application.
* **Input Validation**: Validates file paths and extensions with clear
  error reporting for unsupported formats.
* **Cross-Platform**: Uses pathlib for robust path handling across
  different operating systems.

Examples
--------

Basic format detection:

.. code-block:: python

   # Detect CSV format.
   format_name = detect_file_format("data/bills.csv")
   # Returns 'csv'
   
   # Detect Excel format.
   format_name = detect_file_format("data/quarterly_reports.xlsx")
   # Returns 'excel'
   
   # Detect JSON format.
   format_name = detect_file_format("config/bill_definitions.json")
   # Returns 'json'.

Error handling for unsupported formats:

.. code-block:: python

   try:
       format_name = detect_file_format("data/bills.xml")
   except ValueError as e:
       print(f"Format detection failed: {e}")
       # Shows supported formats in error message.

"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import os

from pathlib import Path
from typing import Union

from .format_registry import (
    get_format_from_extension, get_supported_extensions
)

########################################################################
## TYPE DEFINITIONS
########################################################################

# Type alias for path-like objects to improve type clarity.
PathLike = Union[str, os.PathLike]

########################################################################
## FUNCTIONS
########################################################################


def detect_file_format(file_path: PathLike) -> str:
    """
    Auto-detect file format from file extension with validation.
    
    Examines the file extension to determine the appropriate data reader
    for loading financial data. Uses the centralized format registry to
    ensure consistent format definitions across the application.
    
    Parameters
    ----------
    file_path : str or path-like
        Path to the file whose format should be detected. Accepts both
        string paths and pathlib.Path objects for flexibility.
        
    Returns
    -------
    str
        The detected file format identifier. Valid values include 'csv',
        'excel', and 'json', corresponding to supported data formats.
        
    Raises
    ------
    ValueError
        If the file extension is not supported by the system. The error
        message includes a list of supported extensions for guidance.
        
    Notes
    -----
    DESIGN CHOICE: Extension-based detection provides fast, reliable
    format identification without requiring file content inspection or
    external libraries for format sniffing.
    
    BUSINESS GOAL: Centralized format detection ensures consistent
    behavior across all data loading paths and simplifies adding support
    for new file formats.
    
    Examples
    --------
    Detect format from various file types:
    
    .. code-block:: python
    
       # CSV detection.
       format_type = detect_file_format("data/bills.csv")
       # Returns 'csv'.
       
       # Excel detection.
       format_type = detect_file_format("data/bills.xlsx") 
       # Returns 'excel'.
       
       # JSON detection.
       format_type = detect_file_format("data/bills.json")
       # Returns 'json'.
       
    Using with pathlib:
    
    .. code-block:: python
    
       from pathlib import Path
       
       file_path = Path("data") / "bills.csv"
       format_type = detect_file_format(file_path)
       # Returns 'csv'

    """

    # EARLY EXIT OPTIMIZATION: Convert path-like objects to Path for
    # consistent handling without requiring string conversion from
    # caller.
    path_obj = Path(file_path)
    
    # BUSINESS GOAL: Case-insensitive extension matching prevents issues
    # with mixed-case filenames across different operating systems.
    suffix = path_obj.suffix.lower()
    
    # Delegate to format registry for consistent mapping logic.
    format_name = get_format_from_extension(suffix)

    # FAILURE MODE: Provide actionable error message with supported
    # formats when detection fails.
    if format_name is None:
        supported = get_supported_extensions()
        raise ValueError(
            f"Unsupported file format: {suffix}. "
            f"Supported extensions: {', '.join(supported)}"
        )

    return format_name