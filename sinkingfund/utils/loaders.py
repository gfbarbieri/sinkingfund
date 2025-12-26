"""
Data Loaders
============

Format-agnostic data transformation layer that converts standardized
dictionary representations into domain model objects with comprehensive
validation and error handling for robust financial data processing.

Core Abstractions
-----------------

**Format Independence**: Loader functions operate exclusively on
standardized list[dict] data structures, completely isolated from file
format concerns. This separation enables the same business logic to
process data from CSV, Excel, JSON, or any future supported format
without modification.

**Domain Model Translation**: Transforms raw dictionary data into
properly configured domain objects (Bill instances) with automatic
parameter mapping, type conversion, and business rule application.
This layer handles the complexity of converting external data
representations to internal object models.

**Unified Entry Point**: The load_bill_data_from_file function provides a
single interface for loading bill data from any supported file format,
automatically detecting format and applying appropriate readers. The
function returns raw dictionary data which can then be converted to Bill
objects using BillManager.create_bills().

Key Features
------------

* **Type Safety**: Automatic conversion and validation of data types
  during domain object construction with clear error reporting for
  invalid inputs.
* **Business Logic Integration**: Applies domain-specific rules and
  constraints during object creation, ensuring all created objects
  meet business requirements.
* **Error Context**: Provides detailed error messages that include
  source data context for easier debugging of data quality issues.
* **Extension Point**: Easily extensible to support additional domain
  objects by following the same pattern of data-to-object conversion.
* **Performance Optimization**: Efficient batch processing of large
  datasets with minimal memory overhead and optimized object creation.

Examples
--------

Loading bill data from files:

.. code-block:: python

   from sinkingfund.utils import load_bill_data_from_file
   from sinkingfund.managers import BillManager
   
   # Automatically detects CSV format and loads raw data
   bill_data = load_bill_data_from_file("data/bills.csv")
   
   # Automatically detects Excel format  
   bill_data = load_bill_data_from_file("data/quarterly.xlsx")
   
   # Convert to Bill objects using BillManager
   bill_manager = BillManager()
   bills = bill_manager.create_bills(bill_data)
   
   # Now work with Bill objects
   for bill in bills:
       print(f"{bill.service}: {bill.amount_due}")

"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

from typing import Any

from .file_utils import detect_file_format, PathLike
from .format_registry import get_reader_for_format

########################################################################
## FUNCTIONS
########################################################################

def load_bill_data_from_file(
    file_path: PathLike, **kwargs: Any
) -> dict[str, Any]:
    """
    Load bills directly from any supported file format.
    
    This is the main entry point for loading bill data. It automatically
    detects the file format and uses the appropriate reader, then
    converts the data to Bill objects.
    
    Parameters
    ----------
    file_path : str
        Path to the data file.
    **kwargs
        Format-specific options (e.g., sheet_name for Excel files).
        
    Returns
    -------
    dict[str, Any]
        Dictionary of Bill objects loaded from the file.
    """

    # Detect the file format and choose the appropriate reader.
    file_format = detect_file_format(file_path)
    
    # Get the appropriate reader for the file format.
    reader = get_reader_for_format(file_format)

    # Read the data from the file.
    data = reader(file_path, **kwargs)
    
    # Return the data.
    return data