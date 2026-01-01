"""
Date Utilities
==============

Robust date arithmetic functions for financial calculations with proper
handling of calendar complexities, month-end edge cases, and leap years.
Also provides centralized date parsing and conversion utilities for
consistent date handling across all data input sources.

Core Abstractions
-----------------

**Calendar-Aware Arithmetic**: The primary function `increment_date`
handles various frequency patterns (daily, weekly, monthly, quarterly,
annual) with configurable intervals. Unlike naive date arithmetic, these
functions properly handle month-end transitions and leap year edge cases
that commonly occur in financial billing cycles.

**Month-End Normalization**: When incrementing dates by months or years,
the system intelligently handles cases where the target month has fewer
days than the source date. For example, January 31st plus one month
becomes February 28th (or 29th in leap years), not March 3rd.

**Frequency Multipliers**: The interval system allows for flexible
billing patterns like bi-weekly (interval=2, frequency='weekly') or
quarterly (interval=1, frequency='quarterly') without requiring separate
functions for each pattern.

**Date Parsing and Conversion**: The `parse_date` function provides a
centralized way to convert date strings, Timestamps, and other date-like
objects into `datetime.date` objects. This ensures consistent date
handling across file readers (CSV, Excel, JSON) and programmatic input.

Key Features
------------

* **Multiple Frequency Support**: Handles daily, weekly, monthly,
  quarterly, and annual increments with configurable intervals.
* **Leap Year Handling**: Properly manages February 29th transitions
  in annual recurrences, falling back to February 28th when necessary.
* **Month-End Safety**: Automatically adjusts to the last valid day
  when target months have fewer days than the source date.
* **Batch Processing**: Single function can increment by multiple
  intervals for efficient sequence generation.
* **Predictable Behavior**: Deterministic results for edge cases
  ensure consistent financial calculations.
* **Flexible Date Input**: Supports multiple date string formats for
  user convenience and data source compatibility.

Examples
--------

Basic date incrementing:

.. code-block:: python

   from datetime import date
   
   # Monthly increment.
   next_month = increment_date(
       reference_date=date(2025, 1, 31),
       frequency='monthly',
       interval=1
   )
   # Returns date(2025, 2, 28) - adjusts for shorter month.
   
   # Bi-weekly increment  
   bi_weekly = increment_date(
       reference_date=date(2025, 1, 15),
       frequency='weekly', 
       interval=2
   )
   # Returns date(2025, 1, 29).

Handling leap years and edge cases:

.. code-block:: python

   # Leap year February 29th to next year.
   next_year = increment_date(
       reference_date=date(2024, 2, 29),
       frequency='annual',
       interval=1
   )
   # Returns date(2025, 2, 28) - no Feb 29 in 2025.
   
   # Multiple intervals at once
   quarterly = increment_date(
       reference_date=date(2025, 1, 31),
       frequency='monthly',
       interval=3,
       num_intervals=2 # Skip ahead 6 months total.
   )
   # Returns date(2025, 7, 31).

"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import calendar
import datetime

from enum import Enum
from typing import Any, Optional, Union

########################################################################
## FREQUENCY ENUM
########################################################################

class Frequency(Enum):
    """
    Supported billing frequency patterns for date calculations.
    
    This enum provides a controlled vocabulary for frequency values,
    preventing typos and enabling type-safe frequency handling
    throughout the system.
    """
    
    DAILY = "daily"
    WEEKLY = "weekly" 
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"

########################################################################
## DATE UTILITIES
########################################################################

def increment_date(
    reference_date: datetime.date,
    frequency: Union[str, Frequency],
    interval: int,
    num_intervals: int=1
) -> datetime.date:
    """
    Increment a date by specified intervals using calendar-aware
    arithmetic.
    
    This function handles various billing frequencies with proper
    calendar arithmetic, including month-end normalization and leap
    year handling. Unlike naive date arithmetic, it ensures predictable
    behavior for financial calculations.
    
    Parameters
    ----------
    reference_date : datetime.date
        The starting date for the increment calculation.
    frequency : str or Frequency
        The unit of time for increments. Supported values: 'daily',
        'weekly', 'monthly', 'quarterly', 'annual'. Can be string or
        Frequency enum value.
    interval : int
        The multiplier for the frequency unit. For example, interval=2
        with frequency='weekly' creates bi-weekly increments. Must be
        positive.
    num_intervals : int, default=1
        How many complete intervals to advance. Allows jumping multiple
        periods in a single calculation for efficiency.
        
    Returns
    -------
    datetime.date
        The incremented date, adjusted for calendar constraints.
        
    Raises
    ------
    ValueError
        If frequency is not supported, or if interval is not positive.
        
    Notes
    -----
    DESIGN CHOICE: Month-end dates are normalized to the last valid day
    of the target month rather than overflowing to the next month. This
    ensures billing cycles remain predictable and don't drift over time.
    
    EDGE CASE: February 29th in leap years becomes February 28th when
    incremented annually to non-leap years, maintaining the "last day of
    February" semantic meaning.
    
    Examples
    --------
    Basic frequency increments:
    
    .. code-block:: python
    
       from datetime import date
       
       # Simple monthly increment
       result = increment_date(date(2025, 1, 15), 'monthly', 1)
       # Returns date(2025, 2, 15)
       
       # Bi-weekly increment
       result = increment_date(date(2025, 1, 1), 'weekly', 2)
       # Returns date(2025, 1, 15)
       
    Handling month-end edge cases:
    
    .. code-block:: python
    
       # January 31st to February (shorter month)
       result = increment_date(date(2025, 1, 31), 'monthly', 1)
       # Returns date(2025, 2, 28) - not March 3rd
       
       # Multiple intervals
       result = increment_date(date(2025, 1, 31), 'monthly', 1, 3)
       # Returns date(2025, 4, 30) - three months later
    """

    # BUSINESS GOAL: Input validation prevents downstream errors and
    # ensures predictable behavior for financial calculations.
    if interval < 1:
        raise ValueError("interval must be positive.")
        
    if num_intervals < 1:
        raise ValueError("num_intervals must be positive.")
    
    # Convert enum to string for consistent processing.
    if isinstance(frequency, Frequency):
        frequency = frequency.value
    
    # PERFORMANCE: Calculate total intervals once to minimize repeated
    # arithmetic in complex frequency calculations.
    effective_interval = interval * num_intervals

    # DESIGN CHOICE: Use string comparison with .lower() to maintain
    # backward compatibility while supporting enum values.
    frequency_lower = frequency.lower()

    if frequency_lower == 'daily':
        return reference_date + datetime.timedelta(days=effective_interval)

    elif frequency_lower == 'weekly':
        # BUSINESS GOAL: Weekly recurrence maintains the same day of week
        # across intervals, ensuring predictable billing cycles.
        return reference_date + datetime.timedelta(
            days=7 * effective_interval
        )

    elif frequency_lower == 'monthly':
        return increment_monthly(reference_date, num_months=effective_interval)

    elif frequency_lower == 'quarterly':
        # DESIGN CHOICE: Quarterly is implemented as 3-month increments
        # rather than 90-day periods to maintain month-day alignment.
        return increment_monthly(
            reference_date, num_months=3 * effective_interval
        )

    elif frequency_lower == 'annual':
        # EDGE CASE: Handle leap year February 29th transitions by
        # falling back to February 28th when the target year is not
        # a leap year.
        try:
            return reference_date.replace(
                year=reference_date.year + effective_interval
            )
        except ValueError:
            # INVARIANT: February 29th only fails when target year is
            # not a leap year, so February 28th is always valid.
            return reference_date.replace(
                year=reference_date.year + effective_interval, day=28
            )
    else:
        raise ValueError(f"Unsupported frequency: {frequency}")

def increment_monthly(date: datetime.date, num_months: int=1) -> datetime.date:
    """
    Increment a date by a specified number of months with day
    normalization.
    
    This function handles month arithmetic while preserving the day of
    month when possible. When the target month has fewer days than the
    source date, it automatically adjusts to the last valid day of the
    target month.
    
    Parameters
    ----------
    date : datetime.date
        The starting date to increment.
    num_months : int, default=1
        Number of months to advance. Can be negative for backwards
        movement.
        
    Returns
    -------
    datetime.date
        The incremented date, normalized for month length differences.
        
    Notes
    -----
    DESIGN CHOICE: Month-end normalization ensures dates don't overflow
    into the next month when the target month is shorter. For example,
    January 31st plus one month becomes February 28th (or 29th), not
    March 3rd.
    
    PERFORMANCE: Uses calendar.monthrange() for accurate month length
    calculation, handling leap years automatically.
    
    Examples
    --------
    Normal month increments:
    
    .. code-block:: python
    
       from datetime import date
       
       # Standard increment
       result = increment_monthly(date(2025, 1, 15), 1)
       # Returns date(2025, 2, 15)
       
    Month-end normalization:
    
    .. code-block:: python
    
       # January 31st to February (shorter month)
       result = increment_monthly(date(2025, 1, 31), 1)
       # Returns date(2025, 2, 28)
       
       # Multiple months
       result = increment_monthly(date(2025, 1, 31), 4)
       # Returns date(2025, 5, 31)
    """

    # BUSINESS GOAL: Convert to 0-based month arithmetic for easier
    # year-boundary calculations and modular arithmetic.
    month = date.month - 1 + num_months
    year = date.year + month // 12
    month = month % 12 + 1
    
    # EDGE CASE: Normalize day to the last valid day of the target month
    # when the source day doesn't exist in the target month.
    day = min(date.day, calendar.monthrange(year, month)[1])

    return datetime.date(year, month, day)

def get_date_range(start_date: datetime.date, end_date: datetime.date) -> list[datetime.date]:
    """
    Get a list of dates between two dates.

    Parameters
    ----------
    start_date : datetime.date
        The starting date.
    end_date : datetime.date
        The ending date.
        
    Returns
    -------
    list[datetime.date]
        A list of dates between the start and end dates.
        
    Examples
    --------
    Get a list of dates between two dates:
    
    .. code-block:: python
    
       from datetime import date
       
       # Get a list of dates between two dates.
       # Returns [
       #     date(2025, 1, 1), date(2025, 1, 2), ..., date(2025, 1, 31)
       # ]
       dates = get_date_range(date(2025, 1, 1), date(2025, 1, 31))

    """

    # BUSINESS GOAL: Get a list of dates between the start and end
    # dates.
    num_days = (end_date - start_date).days + 1

    dates = [start_date + datetime.timedelta(days=i) for i in range(num_days)]

    return dates

########################################################################
## DATE PARSING AND CONVERSION
########################################################################

# Supported date string formats for parsing. Formats are tried in order
# until a successful parse is found.
SUPPORTED_DATE_FORMATS = [
    '%m/%d/%Y',      # 01/15/2025 (US format)
    '%Y-%m-%d',      # 2025-01-15 (ISO format)
    '%m-%d-%Y',      # 01-15-2025 (US with dashes)
    '%d/%m/%Y',      # 15/01/2025 (European format)
    '%d-%m-%Y',      # 15-01-2025 (European with dashes)
    '%Y/%m/%d',      # 2025/01/15 (ISO with slashes)
]

def parse_date(value: Any) -> Optional[datetime.date]:
    """
    Convert various date representations to a datetime.date object.
    
    This function provides a centralized entry point for date conversion
    throughout the system. It handles strings, date objects, datetime
    objects, pandas Timestamps, and None values, ensuring consistent date
    handling across all data input sources.
    
    Parameters
    ----------
    value : Any
        The value to convert to a date. Can be:
        
        - **str**: Date string in one of the supported formats (see
          SUPPORTED_DATE_FORMATS)
        - **datetime.date**: Already a date object, returned as-is
        - **datetime.datetime**: Datetime object, converted to date
        - **pd.Timestamp**: Pandas Timestamp, converted to date
        - **None**: Returns None
    
    Returns
    -------
    datetime.date or None
        The converted date object, or None if value is None or cannot be
        parsed.
    
    Notes
    -----
    DESIGN CHOICE: This function serves as the single source of truth for
    date conversion, ensuring consistent behavior across file readers,
    BillManager, and other components that need to handle dates from
    various sources.
    
    BUSINESS GOAL: Support multiple date string formats to accommodate
    different user preferences and data source conventions (US vs
    European formats, ISO standard, etc.).
    
    The function tries all supported formats in order until one succeeds.
    If no format matches, returns None rather than raising an exception,
    allowing graceful handling of invalid or missing dates.
    
    Examples
    --------
    Parse date strings in various formats:
    
    .. code-block:: python
    
       from sinkingfund.utils import parse_date
       
       # US format
       date1 = parse_date("01/15/2025")
       # Returns date(2025, 1, 15)
       
       # ISO format
       date2 = parse_date("2025-01-15")
       # Returns date(2025, 1, 15)
       
       # European format
       date3 = parse_date("15/01/2025")
       # Returns date(2025, 1, 15)
    
    Handle already-converted dates:
    
    .. code-block:: python
    
       from datetime import date, datetime
       
       # Already a date object
       date4 = parse_date(date(2025, 1, 15))
       # Returns date(2025, 1, 15) unchanged
       
       # Datetime object
       date5 = parse_date(datetime(2025, 1, 15, 10, 30))
       # Returns date(2025, 1, 15)
    
    Handle None and invalid values:
    
    .. code-block:: python
    
       # None returns None
       date6 = parse_date(None)
       # Returns None
       
       # Invalid string returns None
       date7 = parse_date("not a date")
       # Returns None
    """
    
    # BUSINESS GOAL: Handle None values gracefully without raising
    # exceptions.
    if value is None:
        return None
    
    # EDGE CASE: Convert datetime objects to date by extracting the
    # date component. Must check datetime before date because datetime
    # is a subclass of date.
    if isinstance(value, datetime.datetime):
        return value.date()
    
    # EDGE CASE: If already a date object, return as-is for efficiency
    # and to avoid unnecessary conversions.
    if isinstance(value, datetime.date):
        return value
    
    # EDGE CASE: Handle pandas Timestamps if pandas is available.
    # Check for Timestamp type without importing pandas to avoid
    # dependency issues.
    try:
        import pandas as pd
        if isinstance(value, pd.Timestamp):
            return value.date()
    except ImportError:
        # Pandas not available, continue with string parsing.
        pass
    
    # BUSINESS GOAL: Convert date strings to date objects using
    # supported formats. Try each format until one succeeds.
    if isinstance(value, str):
        value = value.strip()
        
        # Try each supported format in order.
        for date_format in SUPPORTED_DATE_FORMATS:
            try:
                parsed_date = datetime.datetime.strptime(value, date_format)
                return parsed_date.date()
            except ValueError:
                # This format didn't match, try next one.
                continue
        
        # DESIGN CHOICE: Return None for unparseable strings rather than
        # raising an exception. This allows graceful handling of invalid
        # dates in data files.
        return None
    
    # DESIGN CHOICE: Return None for unrecognized types rather than
    # raising an exception. This provides flexibility for future types
    # and graceful degradation.
    return None

def normalize_date_fields(
    record: dict[str, Any], date_fields: list[str]
) -> dict[str, Any]:
    """
    Convert date fields in a dictionary record to datetime.date objects.
    
    This function normalizes date fields in dictionary records, ensuring
    all specified date fields are converted to datetime.date objects
    regardless of their input format (strings, Timestamps, etc.).
    
    Parameters
    ----------
    record : dict[str, Any]
        Dictionary record containing fields that may need date conversion.
    date_fields : list[str]
        List of field names in the record that should be converted to
        date objects.
    
    Returns
    -------
    dict[str, Any]
        Dictionary with date fields converted to datetime.date objects.
        Original dictionary is not modified; a new dictionary is returned.
    
    Notes
    -----
    DESIGN CHOICE: This function creates a new dictionary rather than
    modifying the input, ensuring immutability and preventing side effects.
    
    BUSINESS GOAL: Provide a convenient way to normalize date fields in
    records from file readers or user input, ensuring consistent date
    handling before passing data to domain models.
    
    The function uses `parse_date` internally, so it supports all the
    same input formats and gracefully handles None values and invalid
    dates.
    
    Examples
    --------
    Normalize date fields in a bill record:
    
    .. code-block:: python
    
       from sinkingfund.utils import normalize_date_fields
       
       record = {
           'bill_id': 'rent',
           'service': 'Monthly Rent',
           'amount_due': 1200.00,
           'recurring': False,
           'due_date': '01/15/2025',  # String date
           'start_date': None
       }
       
       normalized = normalize_date_fields(
           record, ['due_date', 'start_date', 'end_date']
       )
       
       # normalized['due_date'] is now date(2025, 1, 15)
       # normalized['start_date'] is None
    
    Handle records with missing date fields:
    
    .. code-block:: python
    
       record = {
           'bill_id': 'electric',
           'service': 'Electric Bill',
           'amount_due': 150.00,
           'recurring': True,
           'start_date': '2025-01-01'  # ISO format
       }
       
       normalized = normalize_date_fields(
           record, ['due_date', 'start_date']
       )
       
       # normalized['start_date'] is date(2025, 1, 1)
       # normalized['due_date'] is None (field didn't exist)
    """
    
    # DESIGN CHOICE: Create new dictionary to ensure immutability.
    normalized = record.copy()
    
    # BUSINESS GOAL: Convert each specified date field using the
    # centralized parse_date function.
    for field in date_fields:
        if field in normalized:
            normalized[field] = parse_date(normalized[field])
    
    return normalized