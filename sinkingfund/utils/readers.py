"""
Data Readers
============

Format-specific data readers that convert multiple file formats into
standardized dictionary representations with robust pandas integration
and comprehensive data type normalization for financial applications.

Core Abstractions
-----------------

**Format-Agnostic Output**: All reader functions produce identical
list[dict] output structures regardless of input format, enabling
downstream code to process data uniformly without format-specific
logic. This abstraction layer isolates file format complexity from
business logic.

**Pandas Integration**: Leverages pandas for robust data parsing,
type inference, and missing value handling across formats. The readers
then normalize pandas-specific data types (Timestamp, NaT, NA) to
standard Python types for consistent downstream processing.

**Data Type Normalization**: Converts pandas extension types to native
Python equivalents to prevent type-related errors in business logic.
Date columns become datetime.date objects, missing values become None,
and numeric types are preserved as appropriate Python primitives.

Key Features
------------

* **Multi-Format Support**: Unified interface for CSV, Excel, and JSON
  data sources with format-specific optimizations and configurations.
* **Pandas Type Coercion**: Automatic conversion from pandas types
  (Timestamp, NaT, pd.NA) to Python native types (date, None) for
  consistent downstream processing.
* **Missing Value Handling**: Standardized conversion of all missing
  value representations (NaT, pd.NA, NaN) to Python None for reliable
  null checking throughout the application.
* **Date Parsing**: Automatic parsing and normalization of date columns
  to datetime.date objects with proper handling of invalid dates.
* **Path-Like Support**: Accepts both string paths and path-like objects
  for flexible integration with different path handling patterns.
* **Error Recovery**: Graceful handling of parsing errors with coercion
  to valid defaults where possible.

Examples
--------

Reading CSV financial data:

.. code-block:: python

   # Basic CSV reading with automatic type inference
   data = read_csv_to_dict("bills.csv")
   # Returns list of dicts with standardized types
   
   # All date fields are datetime.date objects
   bill = data[0]
   assert isinstance(bill['due_date'], date)
   
   # Missing values are consistently None  
   if bill['end_date'] is None:
       print("No end date specified")

Reading Excel data with sheet selection:

.. code-block:: python

   # Read from default sheet
   data = read_excel_to_dict("quarterly_reports.xlsx")
   
   # Read from specific sheet
   data = read_excel_to_dict("reports.xlsx", sheet_name="Q1_Bills")

Reading JSON data with automatic type conversion:

.. code-block:: python

   # JSON with string dates converted to date objects
   data = read_json_to_dict("bill_config.json") 
   
   # All readers produce identical output structure
   for bill in data:
       print(f"{bill['service']}: {bill['amount_due']}")

"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import datetime
import os
import warnings

import pandas as pd

from typing import Any, List, Optional, Union

from .date_utils import parse_date, normalize_date_fields

########################################################################
## TYPE DEFINITIONS
########################################################################

# Type alias for path-like objects to improve code readability.
PathLike = Union[str, os.PathLike]

########################################################################
## HELPER FUNCTIONS
########################################################################

def _coerce_scalar(value: Any) -> Any:
    """
    Convert pandas scalars to plain-Python scalars for type consistency.

    Transforms pandas extension types to native Python equivalents to
    prevent type-related errors in downstream business logic that expects
    standard Python types rather than pandas-specific objects.

    Parameters
    ----------
    value : Any
        Input value that may be a pandas scalar type.

    Returns
    -------
    Any
        Native Python equivalent of the input value.

    Notes
    -----
    DESIGN CHOICE: Explicit type conversion prevents subtle bugs that
    arise from pandas extension types not behaving identically to their
    Python counterparts in boolean contexts and equality comparisons.

    This function handles the following conversions:
    - pd.Timestamp/datetime -> datetime.date
    - pd.NaT/pd.NA/np.nan -> None
    - String dates -> datetime.date (via parse_date)
    - All other types -> unchanged
    """
    # BUSINESS GOAL: Convert all missing value representations to None
    # for consistent null checking throughout the application.
    if pd.isna(value):
        return None

    # EDGE CASE: Convert datetime-like objects to date for financial
    # applications where time components are typically not relevant.
    if isinstance(value, (pd.Timestamp, datetime.datetime)):
        return value.date()
    
    # BUSINESS GOAL: Convert date strings to date objects using centralized
    # date parsing. This ensures consistent date handling across all file
    # formats and input sources.
    if isinstance(value, str):
        parsed = parse_date(value)
        if parsed is not None:
            return parsed
        # If parse_date returns None, it means the string wasn't a date,
        # so return the original string unchanged.

    # Leave all other scalar types unchanged.
    return value


def _coerce_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert DataFrame with pandas scalars to plain-Python equivalents.

    Applies scalar coercion to every element in the DataFrame, ensuring
    that downstream code receives only standard Python types for
    consistent processing behavior.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame potentially containing pandas extension types.

    Returns
    -------
    pd.DataFrame
        DataFrame with all elements converted to plain Python types.

    Notes
    -----
    PERFORMANCE NOTE: Uses DataFrame.map() for element-wise conversion,
    which is the recommended approach in modern pandas versions.
    """
    return df.map(_coerce_scalar)

def _parse_date_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Parse specified columns to pandas datetime with error recovery.

    Converts string or numeric date representations to pandas datetime
    objects, with unparseable values gracefully converted to NaT for
    consistent missing value handling.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing date columns to parse.
    columns : list[str]
        List of column names to parse as dates.

    Returns
    -------
    pd.DataFrame
        DataFrame with specified columns converted to datetime.

    Notes
    -----
    DESIGN CHOICE: Uses errors='coerce' to convert unparseable dates to
    NaT rather than raising exceptions, enabling graceful handling of
    mixed data quality in real-world financial datasets.
    """

    df_copy = df.copy()

    for col in columns:

        # BUSINESS GOAL: Convert the column to a datetime object.
        if col in df_copy.columns:
            # DESIGN CHOICE: Suppress expected warning when pandas can't
            # infer date format, as this function handles various formats
            # and invalid dates gracefully via errors='coerce'.
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    'ignore',
                    message='Could not infer format',
                    category=UserWarning
                )
                df_copy[col] = pd.to_datetime(df_copy[col], errors='coerce')
    
    return df_copy

def _normalize_int_columns(
    df: pd.DataFrame, columns: List[str]
) -> pd.DataFrame:
    """
    Ensure integer-like columns are Python int or None, never float/NA.

    Converts pandas nullable integer columns to standard Python int
    values or None, preventing downstream errors from pandas extension
    types like pd.NA in boolean contexts.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with potentially nullable integer columns.
    columns : List[str]
        List of column names to normalize as integers.

    Returns
    -------
    pd.DataFrame
        DataFrame with integer columns normalized to int or None.

    Notes
    -----
    BUSINESS GOAL: Financial applications require reliable integer
    handling for quantities like occurrence counts and intervals without
    the ambiguity of pandas nullable integer types.
    """

    df_copy = df.copy()
    
    for col in columns:
    
        # BUSINESS GOAL: Convert the column to an integer.
        if col in df_copy.columns:
            # Use list comprehension to convert each value explicitly.
            # This ensures proper handling of None and int conversion,
            # avoiding pandas dtype coercion issues with apply().
            normalized_values = [
                None if pd.isna(x) else int(float(x))
                for x in df_copy[col]
            ]
            # Create Series with explicit object dtype to preserve Python
            # int and None types rather than pandas numeric types.
            df_copy[col] = pd.Series(normalized_values, dtype='object')
    
    return df_copy

########################################################################
## READER FUNCTIONS
########################################################################

def read_csv_to_dict(file_path: PathLike) -> list[dict]:
    """
    Read CSV file and return standardized dictionary representation.
    
    This function handles the CSV-specific logic including pandas data
    type specification, missing value conversion, and column validation.
    The output format is standardized regardless of the input CSV
    structure variations.
    
    Parameters
    ----------
    file_path : str
        Path to the CSV file to read.
        
    Returns
    -------
    list[dict]
        List of dictionaries representing the data rows. Each dictionary
        contains the standardized column names and properly typed
        values.
        
    Examples
    --------
    Read a bills CSV file:
    
    .. code-block:: python
    
       # {'bill_id': 'rent', 'service': 'Monthly Rent', ...}
       data = read_csv_to_dict("data/bills.csv")
       print(data[0])

    """

    # Load the bills from the CSV file.
    # DESIGN CHOICE: Let pandas try to infer date formats first, then
    # use explicit parsing for any remaining string dates. This provides
    # flexibility for various date formats while maintaining performance.
    bills_df = pd.read_csv(
        file_path,
        usecols=[
            'bill_id', 'service', 'amount_due', 'recurring', 'due_date',
            'start_date', 'end_date', 'frequency', 'interval', 'occurrences'
        ],
        parse_dates=['due_date', 'start_date', 'end_date'],
        dtype={
            'bill_id': 'str', 
            'service': 'str', 
            'amount_due': 'float',
            'recurring': 'bool', 
            'interval': 'Int64', 
            'frequency': 'str',
            'occurrences': 'Int64'
        }
    )
    
    # BUSINESS GOAL: Ensure all date columns are properly parsed. If pandas
    # couldn't parse some dates (e.g., non-standard formats), try explicit
    # parsing as a fallback.
    bills_df = _parse_date_columns(
        bills_df,
        ['due_date', 'start_date', 'end_date']
    )
    
    # Coerce the dataframe to convert Timestamps to date objects and
    # handle missing values.
    bills_df = _coerce_dataframe(bills_df)

    # BUSINESS GOAL: Normalize integer columns to ensure interval and
    # occurrences are Python int or None, never floats or pandas types.
    # This prevents type-related errors from float values like 1.0 in CSV
    # files.
    bills_df = _normalize_int_columns(
        bills_df, ['interval', 'occurrences']
    )

    # Convert to list of dictionaries.
    to_dict = bills_df.to_dict('records')
    
    # BUSINESS GOAL: Apply final normalization pass to ensure all date
    # fields are datetime.date objects. This provides a safety net for
    # any date strings that weren't converted by pandas or coercion.
    normalized_records = [
        normalize_date_fields(record, ['due_date', 'start_date', 'end_date'])
        for record in to_dict
    ]
    
    return normalized_records

def read_excel_to_dict(
    file_path: PathLike, sheet_name: Optional[str] = None
) -> list[dict]:
    """
    Read Excel file and return standardized dictionary representation.
    
    This function handles Excel-specific logic including sheet
    selection, data type conversion, and missing value handling. The
    output format matches the CSV reader for consistency.
    
    Parameters
    ----------
    file_path : str
        Path to the Excel file to read.
    sheet_name : str, optional
        Name of the sheet to read. If None, reads the first sheet.
        
    Returns
    -------
    list[dict]
        List of dictionaries representing the data rows with
        standardized column names and properly typed values.
        
    Examples
    --------
    Read from default sheet:
    
    .. code-block:: python
    
       data = read_excel_to_dict("data/bills.xlsx")
       
    Read from specific sheet:
    
    .. code-block:: python
    
       data = read_excel_to_dict("data/bills.xlsx", sheet_name="Bills")

    """

    # Read Excel file with similar logic to CSV
    bills_df = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        usecols=[
            'bill_id', 'service', 'amount_due', 'recurring', 'due_date',
            'start_date', 'end_date', 'frequency', 'interval',
            'occurrences'
        ],
        dtype={
            'bill_id': 'str',
            'service': 'str', 
            'amount_due': 'float',
            'recurring': 'bool',
            'interval': 'Int64',
            'frequency': 'str',
            'occurrences': 'Int64'
        }
    )

    # BUSINESS GOAL: Parse date columns first to convert string dates to
    # Timestamps, then coerce to date objects. This ensures consistent
    # date handling regardless of how Excel stores the dates.
    bills_df = _parse_date_columns(
        bills_df,
        ['due_date', 'start_date', 'end_date']
    )

    # Coerce the dataframe to convert Timestamps to date objects and
    # handle missing values.
    bills_df = _coerce_dataframe(bills_df)

    # BUSINESS GOAL: Normalize integer columns to ensure interval and
    # occurrences are Python int or None, never floats or pandas types.
    # This prevents type-related errors from float values like 1.0 in Excel
    # files.
    bills_df = _normalize_int_columns(
        bills_df, ['interval', 'occurrences']
    )

    # Convert to list of dictionaries.
    to_dict = bills_df.to_dict('records')
    
    # BUSINESS GOAL: Apply final normalization pass to ensure all date
    # fields are datetime.date objects. This provides a safety net for
    # any date strings that weren't converted by pandas or coercion.
    normalized_records = [
        normalize_date_fields(record, ['due_date', 'start_date', 'end_date'])
        for record in to_dict
    ]
    
    return normalized_records

def read_json_to_dict(file_path: PathLike) -> list[dict]:
    """
    Read JSON file and return standardized dictionary representation.
    
    This function uses pandas to read JSON data, ensuring consistent
    data type handling and structure with the CSV and Excel readers.
    It applies the same standardization pipeline for missing values
    and data types.
    
    Parameters
    ----------
    file_path : str
        Path to the JSON file to read.
        
    Returns
    -------
    list[dict]
        List of dictionaries representing the data with standardized
        structure and types.
        
    Examples
    --------
    Read JSON file:
    
    .. code-block:: python
    
       data = read_json_to_dict("data/bills.json")
    """

    # Load the JSON file.
    bills_df = pd.read_json(
        file_path,
        dtype={
            'bill_id': 'str',
            'service': 'str', 
            'amount_due': 'float',
            'recurring': 'bool',
            'interval': 'Int64',
            'frequency': 'str',
            'occurrences': 'Int64'
        }
    )

    # BUSINESS GOAL: Parse date columns first to convert string dates to
    # Timestamps, then coerce to date objects. This ensures consistent
    # date handling regardless of how pandas interprets the JSON data.
    bills_df = _parse_date_columns(
        bills_df, 
        ['due_date', 'start_date', 'end_date']
    )

    # Coerce the dataframe to convert Timestamps to date objects and
    # handle missing values.
    bills_df = _coerce_dataframe(bills_df)

    # BUSINESS GOAL: Normalize integer columns to ensure interval and
    # occurrences are Python int or None, never floats or pandas types.
    # This prevents type-related errors from float values like 1.0 in JSON
    # files.
    bills_df = _normalize_int_columns(
        bills_df, ['interval', 'occurrences']
    )

    # Convert to list of dictionaries.
    to_dict = bills_df.to_dict('records')
    
    # BUSINESS GOAL: Apply final normalization pass to ensure all date
    # fields are datetime.date objects. This provides a safety net for
    # any date strings that weren't converted by pandas or coercion.
    normalized_records = [
        normalize_date_fields(record, ['due_date', 'start_date', 'end_date'])
        for record in to_dict
    ]
    
    return normalized_records