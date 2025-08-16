"""
Utils Package
=============

Comprehensive data loading and processing utilities for the sinking fund
system with modular architecture, format detection, and robust type
normalization for reliable financial data handling.

Core Architecture
-----------------

**Layered Data Pipeline**: The utils package implements a clean layered
architecture that separates format detection, data reading, and domain
model conversion. This design enables independent testing, easy format
extension, and clear separation of concerns across the data loading
pipeline.

**Registry-Driven Dispatch**: Format detection and reader selection use
a centralized registry pattern that maps file extensions to appropriate
reader functions. This eliminates conditional logic and provides a
single point of configuration for adding new data formats.

**Type Normalization Layer**: All readers produce standardized Python
types regardless of input format, converting pandas extension types
(Timestamp, NaT, pd.NA) to native Python equivalents (date, None) for
consistent downstream processing.

Package Structure
-----------------

The utils package consists of several specialized modules:

* **readers**: Format-specific functions (read_csv_to_dict, etc.) that
  parse files and return standardized list[dict] structures.
* **format_registry**: Centralized configuration mapping file extensions
  to reader functions with metadata for each supported format.
* **file_utils**: Path handling and format detection utilities that
  determine appropriate readers based on file extensions.
* **loaders**: Format-agnostic conversion from standardized dictionaries
  to domain model objects (Bill instances).
* **date_utils**: Calendar-aware date arithmetic with proper handling
  of month-end transitions and leap years.

Data Flow
---------

The typical data loading flow follows this pattern:

1. **Format Detection**: file_utils.detect_file_format() examines file
   extension and returns format identifier.
2. **Reader Selection**: format_registry.get_reader_for_format() returns
   appropriate reader function for the detected format.
3. **Data Reading**: Reader function parses file and returns standardized
   list[dict] with normalized Python types.
4. **Domain Conversion**: loaders.load_bills_from_data() converts
   dictionaries to properly configured domain objects.

Examples
--------

High-level file loading:

.. code-block:: python

   from sinkingfund.utils import load_bills_from_file
   
   # Automatic format detection and loading.
   bills = load_bills_from_file("data/bills.csv")
   bills = load_bills_from_file("data/reports.xlsx")
   bills = load_bills_from_file("config/bills.json")

Low-level component usage:

.. code-block:: python

   from sinkingfund.utils import (
       detect_file_format, get_reader_for_format, load_bills_from_data
   )
   
   # Manual pipeline control.
   format_name = detect_file_format("data/bills.csv")
   reader = get_reader_for_format(format_name)
   data = reader("data/bills.csv")
   bills = load_bills_from_data(data)

Date arithmetic utilities:

.. code-block:: python

   from sinkingfund.utils import increment_date
   from datetime import date
   
   # Calendar-aware date calculations.
   next_month = increment_date(date(2025, 1, 31), 'monthly', 1)
   # Returns date(2025, 2, 28) - handles month-end properly.

"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

# Core date utilities.
from .date_utils import increment_date, increment_monthly, Frequency

# File format detection and handling.
from .file_utils import detect_file_format

# Format registry for extensible format support.
from .format_registry import (
    get_format_from_extension,
    get_reader_for_format, 
    get_supported_extensions,
    get_format_config
)

# Domain model loaders.
from .loaders import load_bill_data_from_file

# Data readers for multiple formats.
from .readers import (
    read_csv_to_dict,
    read_excel_to_dict, 
    read_json_to_dict
)

########################################################################
## PUBLIC API
########################################################################

__all__ = [
   
    # Date utilities.
    'increment_date',
    'increment_monthly', 
    'Frequency',
    
    # File utilities.
    'detect_file_format',
    
    # Format registry.
    'get_format_from_extension',
    'get_reader_for_format',
    'get_supported_extensions', 
    'get_format_config',
    
    # Data readers.
    'read_csv_to_dict',
    'read_excel_to_dict',
    'read_json_to_dict',
    
    # Domain loaders.
    'load_bills_from_data',
    'load_bills_from_file'

]