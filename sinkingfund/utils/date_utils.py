"""
Date Utilities
==============

This module contains utility functions for working with dates.

"""

########################################################################
## IMPORTS
########################################################################

import calendar
import datetime

########################################################################
## DATE UTILITIES
########################################################################

def increment_date(
    reference_date: datetime.date, frequency: str, interval: int,
    num_intervals: int=1
) -> datetime.date:
    """
    Increment the date by the interval in the given frequency.
    
    Parameters
    ----------
    reference_date: datetime.date
        The reference date.
    frequency: str
        The frequency of the bill. For example, 'monthly',
        'quarterly', 'annual', etc.
    interval: int
        The interval of the bill. For example, if the bill is
        bi-weekly, the interval is 2 and the frequency is weekly.
        If the bill is monthly, the interval is 1 and the frequency
        is monthly.
        
    Returns
    -------
    datetime.date
        The next due date.
    """

    # How to handle the different frequencies:  
    # 
    # Daily recurrences: Days are defined as 1 day. For daily
    # recurrences, the next due date is the start date plus the
    # interval.
    # 
    # Weekly recurrences: Weeks are defined as 7 days. For
    # weekly recurrences, the next due date is the same day of the
    # week as the start date times the interval. For example, if the
    # start date is Monday and the interval is 1, then the next due
    # date is the next Monday; if the interval is 2, then the next
    # due date is the second Monday.
    #
    # Monthly recurrences: Months do not have a fixed number of
    # days, so a simple 30-day adjustment is not accurate. For
    # monthly recurrences, the next due date is the same day of the
    # month as the start date plus the interval. If the same day
    # cannot be accommodated, then the next due date is the last day
    # of the month. For example, if the start date is February 29
    # and the interval is 12, then the next due date is February 28.
    #
    # Quarterly recurrences: Quarters are defined as 3 months.
    # Months do not have a fixed number of days, so a simple 90-day
    # adjustment is not accurate. For quarterly recurrences, the
    # next due date is the same day of the month as the start date,
    # if it can be accommodated, only three months later times the
    # interval.
    #
    # Annual recurrences: Years are defined as 12 months such that
    # the next occurance lands on the same day of the year as the
    # start date. The *only* exception is if the start date is
    # February 29. In that case, the next due date is February 28.

    # Calculate the effective increment (or interval) based on the
    # interval and the number of occurrences you want to jump to.
    effective_interval = interval * num_intervals

    if frequency.lower() == 'daily':

        next_due_date = (
            reference_date + datetime.timedelta(days=effective_interval)
        )

        return next_due_date

    elif frequency.lower() == 'weekly':

        # The next due date is the start date plus the interval
        # times 7 days.
        next_due_date = (
            reference_date + (
                datetime.timedelta(days=7 * effective_interval)
            )
        )

        return next_due_date

    elif frequency.lower() == 'monthly':

        next_due_date = increment_monthly(
            reference_date, num_months=effective_interval
        )

        return next_due_date

    elif frequency.lower() == 'quarterly':

        next_due_date = increment_monthly(
            reference_date, num_months=3 * effective_interval
        )
        
        return next_due_date

    elif frequency.lower() == 'annual':

        # Simply replace the date by incrementing the date by the
        # interval. This accomplishes the goal of landing on the
        # same day of the year as the start date. Otherwise, control
        # for leap years.
        try:
            return reference_date.replace(
                year=reference_date.year + effective_interval
            )
        except ValueError:
            return reference_date.replace(
                year=reference_date.year + effective_interval, day=28
            )
    else:
        raise ValueError(f"Unknown frequency: {frequency}")
    
def increment_monthly(date: datetime.date, num_months: int=1) -> datetime.date:
    """
    Increment the date by the interval in months.

    Parameters
    ----------
    date: datetime.date
        The date to increment.
    num_months: int
        The number of months to increment by.

    Returns
    -------
    datetime.date
        The incremented date.
    """

    # The month is the month of the start date plus the
    # interval minus one. The minus one is because the month is
    # 0-indexed (January is 0, February is 1, etc.).
    # 
    # The integer division by 12 gives the number of years
    # incremented. For example, if the month = 14, which is the
    # March of the next year in 0-based indexing, then 14/12 = 1
    # year increment.
    month = date.month - 1 + num_months
    year = date.year + month // 12
    month = month % 12 + 1
    
    # Handle month length differences (e.g., Jan 31 -> Feb 28)
    day = min(date.day, calendar.monthrange(year, month)[1])

    next_month = datetime.date(year, month, day)

    return next_month