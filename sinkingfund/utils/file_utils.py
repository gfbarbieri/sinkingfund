"""
File Utilities
==============

Utilities for detecting and handling different file formats in the
sinking fund system.

This module provides basic file format detection capabilities to support
the flexible data loading architecture. The detection is based on file
extensions and supports the core formats used by the sinking fund
system.
"""

########################################################################
## IMPORTS
########################################################################

from pathlib import Path

from .format_registry import (
    get_format_from_extension, get_supported_extensions
)

########################################################################
## FUNCTIONS
########################################################################

def detect_file_format(file_path: str) -> str:
    """
    Auto-detect file format from file extension.
    
    This function examines the file extension to determine the
    appropriate data reader to use. It supports the core file formats
    commonly used for financial data storage.
    
    Parameters
    ----------
    file_path : str
        Path to the file whose format should be detected.
        
    Returns
    -------
    str
        The detected file format. Valid values are 'csv', 'excel',
        'json'.
        
    Raises
    ------
    ValueError
        If the file extension is not supported by the system.
        
    Examples
    --------
    Detect format from various file types:
    
    .. code-block:: python
    
       format_type = detect_file_format("data/bills.csv")
       print(format_type) # 'csv'
       
       format_type = detect_file_format("data/bills.xlsx") 
       print(format_type) # 'excel'
       
       format_type = detect_file_format("data/bills.json")
       print(format_type) # 'json'

    """

    # Get the file extension.
    suffix = Path(file_path).suffix.lower()
    
    # Map the file extension to the format.
    format_name = get_format_from_extension(suffix)

    # If the file extension is not in the map, raise an error.
    if format_name is None:
        supported = get_supported_extensions()
        raise ValueError(
            f"Unsupported file format: {suffix}. Supported formats: "
            f"{supported}"
        )

    # Return the format name.
    return format_name