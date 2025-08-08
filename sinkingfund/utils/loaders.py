"""
Data Loaders
============

Functions for converting standardized dictionary data into domain model
objects. These loaders are format-agnostic and work with data from any
supported file format.
"""

########################################################################
## IMPORTS
########################################################################

from typing import List

from ..models.bills import Bill
from .file_utils import detect_file_format
from .format_registry import get_reader_for_format

########################################################################
## FUNCTIONS
########################################################################

def load_bills_from_data(data: List[dict]) -> List[Bill]:
    """
    Convert standardized dictionary data into Bill objects.
    
    This function is format-agnostic - it only cares about the
    dictionary structure, not where the data originated. It handles
    the business logic of converting raw data into properly configured
    Bill instances.
    
    Parameters
    ----------
    data : List[dict]
        List of dictionaries containing bill data with standardized
        column names and types.
        
    Returns
    -------
    List[Bill]
        List of properly configured Bill objects.
    """

    # Initialize the list of bills.
    bills = []

    # Convert the data to Bill objects.
    for record in data:

        # Create a Bill object from the record.
        bill = Bill(
            bill_id=record['bill_id'],
            service=record['service'],
            amount_due=record['amount_due'],
            recurring=record['recurring'],
            due_date=record.get('due_date'),
            start_date=record.get('start_date'),
            end_date=record.get('end_date'),
            frequency=record.get('frequency'),
            interval=record.get('interval'),
            occurrences=record.get('occurrences')
        )

        # Add the bill to the list.
        bills.append(bill)

    return bills

def load_bills_from_file(file_path: str, **kwargs) -> List[Bill]:
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
    List[Bill] 
        List of Bill objects loaded from the file.
    """

    # Detect the file format and choose the appropriate reader.
    file_format = detect_file_format(file_path)
    
    reader = get_reader_for_format(file_format)
    data = reader(file_path, **kwargs)
    
    # Convert the data to Bill objects.
    bills = load_bills_from_data(data)

    return bills