"""
Data Readers
============

Format-specific readers that convert various file formats into
standardized dictionary representations for the sinking fund system.

This module provides readers for different data formats (CSV, Excel,
JSON) that all produce the same standardized output format. This
separation allows the business logic to remain format-agnostic while
supporting multiple input sources.

The readers handle format-specific concerns like data type conversion,
missing value handling, and structural differences between formats.
"""

########################################################################
## IMPORTS
########################################################################

import pandas as pd

from typing import Optional

########################################################################
## FUNCTIONS
########################################################################

def read_csv_to_dict(file_path: str) -> list[dict]:
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
    bills_df = pd.read_csv(
        file_path,
        usecols=[
            'bill_id', 'service', 'amount_due', 'recurring', 'due_date',
            'start_date', 'end_date', 'frequency', 'interval', 'occurrences'
        ],
        parse_dates=['due_date', 'start_date', 'end_date'],
        date_format='%m/%d/%Y',
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
    
    # Convert to list of dictionaries.
    to_dict = bills_df.to_dict('records')
    
    return to_dict

def read_excel_to_dict(
    file_path: str, sheet_name: Optional[str] = None
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

    # Convert to list of dictionaries.
    to_dict = bills_df.to_dict('records')
    
    return to_dict


def read_json_to_dict(file_path: str) -> list[dict]:
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
    
    # Convert to list of dictionaries.
    to_dict = bills_df.to_dict('records')
    
    return to_dict