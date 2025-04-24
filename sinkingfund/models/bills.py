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

@dataclass(frozen=True)
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

@dataclass
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
    recurring: bool
        Whether the bill is recurring.
    start_date: datetime.date
        The date of the first due date.
    frequency: str
        The frequency of the bill. For example, 'monthly', 'quarterly',
        'annual', etc.
    interval: int
        The interval of the bill. For example, if the bill is bi-weekly,
        the interval is 2 and the frequency is weekly. If the bill is
        monthly, the interval is 1 and the frequency is monthly.
    end_date: Optional[datetime.date]
        The optional end date of the bill.
    """

    bill_id: str
    service: str
    amount_due: float
    recurring: bool
    due_date: Optional[datetime.date]=None
    start_date: Optional[datetime.date]=None
    end_date: Optional[datetime.date]=None
    frequency: Optional[str]=None
    interval: Optional[int]=1

    def next_instance(
        self, reference_date: datetime.date, return_last: bool=False
    ) -> BillInstance | None:
        """
        Get the next instance of the bill.

        Parameters
        ----------
        reference_date: datetime.date
            The reference date.
        return_last: bool
            Whether to return the last instance of the bill.

        Returns
        -------
        BillInstance | None
            The next instance of the bill or None if the bill is not
            recurring and the reference date is before the due date or
            after the end date.
        """

        # If the bill is recurring:
        # 
        # 1. Check if the passed reference date is before the recurring
        # bill's end date. If it is, then the bill does not have a next
        # instance. In this case, the user chooses whether to return the
        # last instance or None.
        # 
        # 2. If the recurring bill's start date is before the reference
        # date, then the next instance is the first instance. The first
        # instance is due on the recurring bill's start date.
        # 
        # 3. Otherwise, we need to build the list of due dates until the
        # reference date, then get the next due date. If the next due
        # date is after the end date, then the bill does not have a next
        # instance and we are back to the user's choice of returning the
        # last instance or None.
        # 
        # If the bill is not recurring:
        # 
        # 1. If the reference date is after the due date, then the bill
        # does not have a next instance. In that case, the user decides
        # whether to return the last instance or None.
        # 
        # 2. If the reference date is before or on the due date, then
        # the  only instance is the due date. Return the instance with
        # the due date.

        ################################################################
        ## RECURRING BILLS
        ################################################################

        if self.recurring == True:

            # 1. If the bill is recurring and an end date was set.
            if self.end_date is not None and reference_date > self.end_date:
                
                # If the users wants the last instance, then we need to
                # find the last instance.
                if return_last == True:
                    last_date = self.start_date
                    next_date = self._next_due_date(last_date)

                    while next_date <= self.end_date:
                        last_date = next_date
                        next_date = self._next_due_date(last_date)

                    return BillInstance(
                        bill_id=self.bill_id,
                        service=self.service,
                        due_date=last_date,
                        amount_due=self.amount_due
                    )
                else:
                    return None
            
            # 2. If the bill is recurring and the reference date is
            # before or on the start date.
            elif reference_date <= self.start_date:
                return BillInstance(
                    bill_id=self.bill_id,
                    service=self.service,
                    due_date=self.start_date,
                    amount_due=self.amount_due
                )
            
            # 3. Otherwise, we need to build the list of due dates until
            # the reference date, then get the next due date.
            else:
                current_date = self.start_date
                prev_date = None

                while current_date <= reference_date:
                    prev_date = current_date
                    current_date = self._next_due_date(current_date)

                # Re-check if the found date is after the end date. If
                # the user wants the last instance, then return the
                # previous instance, which is the last valid instance.
                # Otherwise, return None.
                if self.end_date is not None and current_date > self.end_date:
                    if return_last == True:
                        return BillInstance(
                            bill_id=self.bill_id,
                            service=self.service,
                            due_date=prev_date,
                            amount_due=self.amount_due
                        )
                    else:
                        return None
                
                # Otherwise, return the next due date.
                return BillInstance(
                    bill_id=self.bill_id,
                    service=self.service,
                    due_date=current_date,
                    amount_due=self.amount_due
                )

        ################################################################
        ## NON-RECURRING BILLS
        ################################################################

        elif self.recurring == False:
            if (
                (reference_date > self.due_date and return_last) or
                (reference_date <= self.due_date)
            ):
                return BillInstance(
                    bill_id=self.bill_id,
                    service=self.service,
                    due_date=self.due_date,
                    amount_due=self.amount_due
                )
            else:
                return None

    def _next_due_date(self, date: datetime.date) -> datetime.date:
        """
        Calculate the next due date after the given date.
        
        Parameters
        ----------
        date: datetime.date
            The reference date.
            
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
        if self.frequency.lower() == 'daily':

            next_due_date = date + datetime.timedelta(days=self.interval)

            return next_due_date

        elif self.frequency.lower() == 'weekly':

            # The next due date is the start date plus the interval
            # times 7 days.
            next_due_date = date + datetime.timedelta(days=7 * self.interval)

            return next_due_date

        elif self.frequency.lower() == 'monthly':

            next_due_date = self._increment_monthly(
                date, num_months=self.interval
            )

            return next_due_date

        elif self.frequency.lower() == 'quarterly':

            next_due_date = self._increment_monthly(
                date, num_months=3 * self.interval
            )
            
            return next_due_date

        elif self.frequency.lower() == 'annual':

            # Simply replace the date by incrementing the date by the
            # interval. This accomplishes the goal of landing on the
            # same day of the year as the start date. Otherwise, control
            # for leap years.
            try:
                return date.replace(year=date.year + self.interval)
            except ValueError:
                return date.replace(year=date.year + self.interval, day=28)
        else:
            raise ValueError(f"Unknown frequency: {self.frequency}")
    
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