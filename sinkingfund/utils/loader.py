"""
Data Loading Utilities
======================

This module provides utilities for loading financial data from external
sources into the sinking fund system, ensuring proper type conversion
and validation.

Loading financial data from external sources is a critical part of any
budgeting system. These utilities bridge the gap between raw data files
(like CSV spreadsheets) and the structured object models used by the
sinking fund system.

Key capabilities:

#. Bill Loading: Convert tabular bill data into fully-formed Bill
objects.

   * Handles both one-time and recurring bills.
   * Processes dates with proper formatting.
   * Converts data types appropriately (dates, numbers, strings).
   * Manages optional fields with proper defaults.

# . Envelope Creation: Transform bill data directly into budget
envelopes.

   * Creates envelope containers for each bill.
   * Associates contribution intervals with each envelope.
   * Supports both uniform and variable contribution schedules.

These loaders handle the complexities of data import, including:

* Type safety: Ensuring numeric values remain numeric, even with
missing values.
* Date parsing: Converting string dates to proper date objects.
* Null handling: Managing optional fields that may be empty.
* Validation: Basic checks to ensure required fields are present.

By centralizing data loading logic, these utilities promote consistency
and reduce the risk of data formatting errors throughout the
application. They provide a clean interface between external data
sources and the internal object model, making it easy to incorporate
financial data from various sources while maintaining data integrity.

"""

########################################################################
## IMPORTS
########################################################################

import pandas as pd

from ..models.envelope import Envelope
from ..models.bills import Bill

########################################################################
## LOADERS
########################################################################

def load_bills_from_csv(path: str) -> list[Bill]:
    """
    Load the bills from a CSV file.

    Parameters
    ----------
    path: str
        The path to the CSV file.

    Returns
    -------
    list[Bill]
        The bills.
    """

    # Load the bills from the CSV file.
    bills_df = pd.read_csv(
        path,
        usecols=[
            'bill_id', 'service', 'amount_due', 'recurring', 'due_date',
            'start_date', 'end_date', 'frequency', 'interval'
        ],
        parse_dates=['due_date', 'start_date', 'end_date'],
        date_format='%m/%d/%Y',
        dtype={'interval': 'Int64', 'frequency': 'string'}
    )

    # Convert the date columns to datetime.date objects. Handle optional
    # date columns which might be NaN.
    for col in ['due_date', 'start_date', 'end_date']:
        bills_df[col] = bills_df[col].apply(
            lambda x: x.date() if pd.notna(x) else None
        )

    # Create the bills.
    bills = []

    for _, row in bills_df.iterrows():

        # Create the bill.
        bill = Bill(
            bill_id=row['bill_id'],
            service=row['service'],
            amount_due=row['amount_due'],
            recurring=row['recurring'],
            due_date=row['due_date'],
            start_date=row['start_date'],
            end_date=row['end_date'],
            frequency=row['frequency'] if pd.notna(row['frequency']) else None,
            interval=row['interval'] if pd.notna(row['interval']) else None,
        )

        bills.append(bill)

    return bills

def load_envelopes_from_csv(
        path: str, contrib_intervals: list[int] | int
    ) -> list[Envelope]:
    """
    Load the envelopes from a CSV file.

    Parameters
    ----------
    path: str
        The path to the CSV file.
    contrib_intervals: list[int] | int
        The contribution intervals for the envelopes. If a single
        integer, all envelopes are expected to have the same
        contribution interval.

    Returns
    -------
    list[Envelope]
        The envelopes.
    """

    # Load the bills from the CSV file.
    bills = load_bills_from_csv(path)

    # Envelopes are 

    # If the contribution intervals are a single integer, the all bills
    # are expected to have the same contribution interval. Convert it
    # to a list equal in length to the number of bills.
    if isinstance(contrib_intervals, int):
        contrib_intervals = [contrib_intervals] * len(bills)

    # Create the envelopes.
    envelopes = [
        Envelope(
            bill=bill,
            interval=interval
        )
        for bill, interval in zip(bills, contrib_intervals)
    ]

    return envelopes