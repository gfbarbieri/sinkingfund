"""
Date Utilities
==============

Robust date arithmetic functions for financial calculations with proper
handling of calendar complexities, month-end edge cases, and leap years.

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
from typing import Union

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