"""
Bill Models
===========

This module defines the core models for representing financial
obligations in a sinking fund system, capturing both one-time and
recurring expenses.

The bill models serve as the foundation of the sinking fund,
representing the financial obligations that require planning and
saving. This module offers two key abstractions:

#. Bill: Represents the full definition of a financial obligation,
including:

   * Core information (ID, service name, amount).
   * Recurrence pattern (if applicable).
   * Time boundaries (start date, end date).
   
Bills can be one-time expenses (like an annual insurance payment) or
recurring obligations (like a monthly subscription). For recurring
bills, the system supports various frequencies (daily, weekly, monthly,
quarterly, annual) with customizable intervals.

#. BillInstance: Represents a specific occurrence of a bill with a
concrete due date and amount. A recurring bill generates multiple bill
instances over time.

The Bill class provides sophisticated date calculation methods to
determine:

* When the next payment is due.
* The sequence of all future payments.
* The final payment before a specified end date.

These calculations handle calendar complexities like varying month
lengths and leap years. For example, a monthly bill due on the 31st will
correctly adjust to the last day of shorter months.

By modeling bills with this level of detail, the sinking fund system
can:

* Project future cash flow needs with precision.
* Calculate required savings rates to meet obligations.
* Track progress toward fully funded financial goals.
* Visualize the timing of upcoming expenses.
* Group and prioritize expenses for allocation strategies.

The bill models work in concert with the Envelope and CashFlow models
to provide a complete picture of your sinking fund strategy and
execution.

"""

########################################################################
## IMPORTS
########################################################################

import calendar
import datetime

from dataclasses import dataclass
from typing import Optional

########################################################################
## BILLS
########################################################################

@dataclass
class BillInstance:
    """
    An instance of a bill is a single due date and an amount due.

    Attributes
    ----------
    bill_id: str
        The id of the bill.
    service: str
        The name of the service that the bill is for.
    amount: float
        The amount of the bill.
    due_date: datetime.date
        The date of the due date.
    """

    bill_id: str
    service: str
    amount_due: float
    due_date: datetime.date

class Bill:
    """
    A bill is a financial obligation that has a due date and an amount
    due.

    Attributes
    ----------
    bill_id: str
        The id of the bill.
    service: str
        The name of the service that the bill is for.
    amount_due: float
        The amount of the bill.
    start_date: datetime.date
        The date of the first due date.
    end_date: datetime.date
        The end date of the bill.
    frequency: str
        The frequency of the bill. For example, 'monthly', 'quarterly',
        'annual', etc. This is None for non-recurring bills.
    interval: int
        The interval of the bill. For example, if the bill is bi-weekly,
        the interval is 2 and the frequency is weekly. If the bill is
        monthly, the interval is 1 and the frequency is monthly. This is
        None for non-recurring bills.
    """

    def __init__(
        self, bill_id: str, service: str, amount_due: float, recurring: bool,
        due_date: Optional[datetime.date]=None,
        start_date: Optional[datetime.date]=None,
        end_date: Optional[datetime.date]=None, frequency: Optional[str]=None,
        interval: Optional[int]=None, occurrences: Optional[int]=None
    ):
        self.bill_id = bill_id
        self.service = service
        self.amount_due = amount_due
        self.recurring = recurring
        self.start_date = start_date
        self.end_date = end_date
        self.frequency = frequency
        self.interval = interval
        self.occurrences = occurrences

        # If not a recurring bill, then the start and end dates are the
        # the due dates and the occurrences is 1.
        if recurring == False:
            self.start_date = due_date
            self.end_date = due_date
            self.occurrences = 1
    
        # If a bill is marked as recurring but the end date is None and
        # the occurrences is 1, then the bill is not recurring. So
        # instantiate the bill as non-recurring.
        elif (
            recurring == True and end_date is None
            and occurrences is not None and occurrences == 1
        ):
            self.recurring = False
            self.end_date = start_date
            self.frequency = None
            self.interval = None

        # If a recurring bill and the number of occurrences is not None
        # and greater than 1, then we will build the end date. The
        # pattern is always occurrences - 1 because the start_date is
        # already the first occurrence, so you only need to increment by
        # the remaining (occurrences - 1) intervals to reach the final
        # occurrence.
        elif recurring == True and occurrences is not None and occurrences > 1:
            self.end_date = self._increment_date(
                reference_date=start_date,
                frequency=frequency,
                interval=interval,
                num_intervals=(occurrences - 1)
            )

        # If a recurring bill, the end date is set, but the occurrences
        # is None, then we need to calculate the number of occurrences
        # based on the start date, end date, and frequency.
        elif (
            recurring == True and end_date is not None
            and occurrences is None
        ):
            self.occurrences = self._calculate_occurrences_in_range(
                start_date=start_date,
                end_date=end_date,
                frequency=frequency,
                interval=interval
            )

    def next_instance(
        self, reference_date: datetime.date
    ) -> BillInstance | None:
        """
        Get the next upcoming instance of a recurring bill relative to a
        reference date.
        
        This method finds the first bill instance that is due on or
        after the reference date, handling the complexities of recurring
        bill schedules including start dates, end dates, and frequency
        calculations.
        
        Parameters
        ----------
        reference_date : datetime.date
            The reference date from which to search for the next bill
            instance. This can be any date, not necessarily a due date.
            
        Returns
        -------
        BillInstance | None
            The next bill instance due on or after the reference date,
            or None if no future instances exist (e.g., reference date
            is past the bill's end date).
            
        Notes
        -----
        The method handles three main scenarios:
        
        1. **Past end date**: Returns None if reference date exceeds the
        bill's end date (if set).
        2. **Before/at start**: Returns the first instance (start_date)
        if reference date is on or before the bill's start date.
        3. **Within active period**: Iterates through the recurring
        schedule to find the first due date on or after the reference
        date.
        
        For scenario 3, the method efficiently steps through due dates
        without generating the entire schedule, stopping at the first
        valid instance.
        """

        # 1. Reference date is beyond the bill's active period.
        # If an end date is set and we're past it, no future instances
        # exist.
        if self.end_date is not None and reference_date > self.end_date:
            return None
        
        # 2. Reference date is at or before the bill's first due date.
        # The next instance is simply the first occurrence (start_date).
        elif reference_date <= self.start_date:
            return BillInstance(
                bill_id=self.bill_id,
                service=self.service,
                due_date=self.start_date,
                amount_due=self.amount_due
            )
        
        # 3. Reference date falls within the bill's active period.
        # Need to find the first due date that occurs on or after
        # reference_date.
        else:

            # Start iterating from the bill's first due date.
            current_date = self.start_date
            
            # Step through the recurring schedule until we find a due
            # date that is on or after our reference date. This gives
            # us the "upcoming" instance relative to the reference
            # date.
            while current_date < reference_date:
                current_date = self._next_due_date(current_date)

            # Verify the found due date doesn't exceed the bill's end
            # date. If it does, no valid future instances exist within
            # the bill's lifetime.
            if self.end_date is not None and current_date > self.end_date:
                return None
            
            # Return the first valid due date on or after the reference
            # date.
            return BillInstance(
                bill_id=self.bill_id,
                service=self.service,
                due_date=current_date,
                amount_due=self.amount_due
            )
    
    def _due_dates_in_range(
        self, start_reference: datetime.date, end_reference: datetime.date
    ) -> list[datetime.date]:
        """
        Generate all due dates for this bill within a specified date range.
        
        This method generates the complete sequence of due dates starting from the
        bill's start_date, then filters to return only those within the specified
        range. This handles cases where start_reference is not itself a due date.
        
        Parameters
        ----------
        start_reference : datetime.date
            The start of the date range (inclusive). Can be any date.
        end_reference : datetime.date
            The end of the date range (inclusive). Can be any date.
            
        Returns
        -------
        list[datetime.date]
            A sorted list of all due dates within [start_reference, end_reference].
            Returns empty list if no due dates fall within the range.
        """

        # If the bill is not recurring, then we can just return the
        # due date.
        if not self.recurring:
            return [self.start_date]
        
        # If the bill is recurring, then we need to generate all due
        # dates in the range.

        # Initialize the list of due dates.
        due_dates = []

        # If the end reference is before the bill's start date, then
        # there are no due dates in the range.
        if end_reference < self.start_date:
            return []
        
        # If the start reference is after the bill's end date, then
        # there are no due dates in the range.
        if self.end_date is not None and start_reference > self.end_date:
            return []
        
        # Determine the effective start and end dates to begin
        # generating due dates. We cannot exceed the end date.
        current_due_date = self.start_date

        if self.end_date is not None:
            end_reference = min(end_reference, self.end_date)
        
        # Generate all due dates from start_date until we exceed
        # end_reference.
        while current_due_date <= end_reference:

            # Only include dates that fall within our requested range.
            if start_reference <= current_due_date <= end_reference:
                due_dates.append(current_due_date)
            
            # Move to the next due date in the sequence.
            current_due_date = self._next_due_date(current_due_date)
        
        return due_dates

    def _next_due_date(self, curr_due_date: datetime.date) -> datetime.date:
        """
        Calculate the next due date after the current due date,
        following the bill's frequency and interval.
        
        Parameters
        ----------
        curr_due_date: datetime.date
            The current due date. This must be a valid due date for a
            bill.
            
        Returns
        -------
        datetime.date
            The next due date.
        """

        # This function needs code to validate the current due date,
        # otherwise, it's just a function that increments the date by
        # the interval.

        next_due_date = self._increment_date(
            reference_date=curr_due_date,
            frequency=self.frequency,
            interval=self.interval
        )
        
        return next_due_date

    def _calculate_occurrences_in_range(
        self, start_date: datetime.date, end_date: datetime.date, 
        frequency: str, interval: int
    ) -> int:
        """
        Calculate the number of occurrences between start_date and
        end_date (inclusive).
        
        Parameters
        ----------
        start_date : datetime.date
            The first due date.
        end_date : datetime.date  
            The last possible due date.
        frequency : str
            The frequency ('daily', 'weekly', 'monthly', etc.).
        interval : int
            The interval between occurrences.
            
        Returns
        -------
        int
            The number of occurrences that fit in the range.
        """
        
        # Initialize the number of occurrences.
        occurrences = 0

        # Initialize the current date.
        current_date = start_date
        
        # Count occurrences by stepping through the sequence.
        while current_date <= end_date:

            # Increment the number of occurrences.
            occurrences += 1

            # Get the next due date using existing logic.
            current_date = self._increment_date(
                reference_date=current_date, frequency=frequency,
                interval=interval, num_intervals=1
            )
        
        return occurrences
    
    def _increment_date(
        self, reference_date: datetime.date, frequency: str, interval: int,
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

            next_due_date = self._increment_monthly(
                reference_date, num_months=effective_interval
            )

            return next_due_date

        elif frequency.lower() == 'quarterly':

            next_due_date = self._increment_monthly(
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
        
    def _increment_monthly(
        self, date: datetime.date, num_months: int=1
    ) -> datetime.date:
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