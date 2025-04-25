"""
Independent Scheduler
=====================

The Independent Scheduler provides a straightforward approach to
scheduling contributions for sinking fund envelopes without considering
interactions between different bills.

Mathematical Concept
-------------------

The core principle behind the Independent Scheduler is simple equal
distribution of contributions across available time periods. For each
bill, the scheduler:

#. Calculates the total days available between the start date and the
bill's due date
#. Divides the remaining amount by available days to determine the daily
# contribution rate
#. Groups these daily contributions into intervals based on the
# envelope's contribution frequency

The contribution formula is:

.. math::

   \\text{daily\\_contribution} = \\frac{\\text{remaining\\_amount}}{\\text{days\\_until\\_due}}
   
   \\text{interval\\_contribution} = \\text{daily\\_contribution} \\times \\text{interval\\_days}

Where:

* ``remaining_amount`` is the amount still needed to fully fund the
bill.
* ``days_until_due`` is the number of days between the start date and
the bill's due date.
* ``interval_days`` is the number of days in each contribution interval
(e.g., 7 for weekly, 14 for bi-weekly).

Operation Details
----------------

The scheduler processes each envelope independently through these steps:

#. Identifies the next instance of the bill associated with the
envelope.
#. Calculates the number and size of intervals between the start date
and due date.
#. Determines the daily contribution amount needed to fully fund the
bill.
#. Creates a series of cash flows representing contributions at each
interval.
#. Adds a final negative cash flow representing the bill payment on
the due date.
#. Handles partial intervals at the end of the schedule if the time
period doesn't divide evenly.

The scheduler also includes a special adjustment to ensure exact
funding. Since rounding can cause small discrepancies between the sum
of contributions and the bill amount, any difference is added to the
first contribution to ensure the total exactly matches the required
amount.

Advantages
---------

* **Simplicity**: Easy to understand and implement.
* **Predictability**: Creates regular, consistent contributions for
each bill.
* **Bill-Level Smoothing**: Each bill has evenly distributed
contributions.
* **Independence**: Changes to one bill don't affect the
contribution schedule of others.

When to Use
----------

The Independent Scheduler is ideal for:

* Users who want to understand exactly how much they're contributing
to each bill at each interval.
* Scenarios where bills should be treated separately without
interactions.
* Situations where bill-level contribution consistency is more
important than total outflow smoothing.
* Simple sinking fund setups with few bills.

Comparison with Other Schedulers
-------------------------------

Unlike the LP Scheduler which optimizes for smooth total contributions
across all bills (potentially creating variable per-bill contributions),
the Independent Scheduler optimizes for smooth contributions at the
individual bill level.

This means:

* Each bill receives consistent contributions across time periods.
* The total outflow may vary more from period to period.
* The allocation pattern is more intuitive and easier to understand.
* No complex mathematical optimization is required.

Example
-------

.. code-block:: python

   from sinkingfund.schedules.indep_scheduler import IndependentScheduler
    
   # Initialize the scheduler.
   scheduler = IndependentScheduler()
    
   # Schedule contributions for multiple envelopes.
   scheduler.schedule(
       envelopes=my_envelopes, start_date=datetime.date.today()
   )

"""

########################################################################
## IMPORTS
########################################################################

import datetime

from .base import BaseScheduler
from ..models.cash_flow import CashFlow
from ..models.envelope import Envelope

########################################################################
## INDEPENDENT SCHEDULER
########################################################################

class IndependentScheduler(BaseScheduler):
    """
    A scheduler that creates even contribution schedules for each bill
    independently without considering interactions between bills.
    
    This scheduler follows a straightforward mathematical approach by:
    
    #. Calculating the daily contribution rate for each bill by dividing
       the remaining amount by the days until due date
       
    #. Grouping these daily contributions into intervals based on the
       envelope's contribution frequency
       
    #. Ensuring exact funding by adding any rounding differences to the
       first contribution
    
    The IndependentScheduler creates predictable, regular payments for
    each bill with consistent contribution amounts at each interval.
    This approach optimizes for bill-level contribution smoothness
    rather than total outflow smoothness across all bills.
    
    The key advantages of this scheduler include:
    
    * Simple, predictable contribution schedules for each bill
    * Easy-to-understand contribution logic without complex optimization
    * Bill-level contribution consistency
    * Independence between bills (changes to one bill don't affect
    others)
    
    This scheduler is ideal for users who want clear visibility into how
    much they're contributing to each specific bill at each interval and
    prefer consistency at the individual bill level over optimizing for
    smooth total outflows.
    
    Example
    -------
    
    .. code-block:: python
    
       scheduler = IndependentScheduler()
       scheduler.schedule(
           envelopes=my_envelopes, start_date=datetime.date.today()
       )
    
    Notes
    -----
    Unlike more complex schedulers, the IndependentScheduler does not
    attempt to optimize total contributions across all bills, which can
    result in varying total outflows from period to period when multiple
    bills are involved.
    """
    
    def __init__(self):
        pass
    
    def schedule(
            self, envelopes: list[Envelope], start_date: datetime.date
        ) -> None:
        """
        Create evenly distributed contribution schedules for each
        envelope independently.
        
        This method processes each envelope separately to create a
        schedule of cash flows that:
        
        #. Evenly distributes contributions from the start date to the
        bill's due date.
        #. Respects the envelope's specified contribution interval.
        #. Ensures the total contributions exactly match the remaining
        amount needed.
        
        For each envelope, the scheduler:
        
        #. Identifies the next bill instance.
        #. Calculates contribution intervals between start date and due
        date.
        #. Determines the daily contribution rate by dividing the
        remaining amount by days until due.
        #. Creates appropriately sized cash flows for each interval
        period.
        #. Adds a final negative cash flow for the bill payment.
        
        Parameters
        ----------
        envelopes : list[Envelope]
            The envelopes to create contribution schedules for. Each
            envelope should have a valid bill and a defined contribution
            interval.
            
        start_date : datetime.date
            The date to begin the contribution schedule. This serves as
            the reference point for all timing calculations and the date
            of the first contribution.
        
        Returns
        -------
        None
            The method modifies the provided envelopes in-place by
            setting their schedule attribute with the calculated cash
            flows.
        
        Notes
        -----
        * Envelopes without a valid next bill instance are skipped.
        * The schedule handles partial intervals at the end of the
        period.
        * Rounding differences are added to the first contribution.
        * A negative cash flow equal to the bill amount is added on the
        due date.
        """

        cash_flows = []

        for envelope in envelopes:

            # For each envelope, get the next instance of the bill.
            bill = envelope.bill.next_instance(reference_date=start_date)

            # Skip over envelopes that do not have a next instance of
            # the bill. This occurs if bills are listed in envelopes
            # that do not have a next instance at the current date.
            if bill is None:
                continue

            # Calculate the number of intervals between the current
            # date and the due date. Intervals are the number of days
            # between cash flows.
            # intervals = sorted(self.calculate_intervals(
            #     start_date=start_date, end_date=bill.due_date,
            #     interval=envelope.interval
            # ))
            intervals = self.calculate_intervals(
                start_date=start_date, end_date=bill.due_date,
                interval=envelope.interval
            )

            # Calculate the cash flow required to pay off the bill in
            # the given time frame.
            daily_contrib = self.daily_contribution(
                remaining=envelope.remaining, due_date=bill.due_date,
                curr_date=start_date
            )

            # The interval contribution is the daily contribution
            # multiplied by the interval.
            interval_contrib = [
                (interval, interval * daily_contrib) for interval in intervals
            ]

            # Determine if the total number of contributions is equal
            # to the amount due. If there is any difference, we are
            # going to add it to the first contribution made. This is
            # an arbitrary decision, but it is a way to ensure that the
            # total amount contributed is equal to the amount due.
            diff = (
                envelope.remaining -
                sum(contrib[1] for contrib in interval_contrib)
            )

            # Create the full cash flow schedule, including
            # contributions and payouts. The due date of the
            # contribution is the current date plus the interval. The
            # current date is a datetime.date object, so we need to add
            # the interval to it as a timedelta.
            cash_flows = []
            current_date = start_date

            for i, (days, amount) in enumerate(interval_contrib):

                # If there is any difference, add it to the first
                # contribution.
                amount = round(amount + (diff if i == 0 else 0), 2)

                # If the amount is zero, then do not add a cash flow.
                # It is possible to do this before this loop because
                # we know the daily contribution is zero.
                if amount == 0:
                    continue

                # Update the date using the actual interval size for
                # this period. current_date is already set to start_date
                # for the first iteration
                if i > 0:
                    current_date = current_date + datetime.timedelta(days=days)

                # Create the contribution.
                cash_flow = CashFlow(
                    bill_id=bill.bill_id, date=current_date, amount=amount
                )

                # Add the contribution to the list of contributions.
                cash_flows.append(cash_flow)

            # Add the total amount due to the list of cash flows.
            cash_flows.append(
                CashFlow(
                    bill_id=bill.bill_id, date=bill.due_date,
                    amount=-envelope.bill.amount_due
                )
            )

            # Set the schedule of cash flows.
            envelope.schedule = cash_flows

    def daily_contribution(
            self,
            remaining: float,
            due_date: datetime.date,
            curr_date: datetime.date
        ) -> float:
        """
        Calculate the daily contribution amount needed to fully fund a
        bill by its due date.
        
        This method determines how much needs to be contributed each day
        to accumulate the remaining amount by the due date. It handles
        edge cases such as past-due bills and bills due on the current
        date.
        
        The calculation is straightforward: the remaining amount divided
        by the number of days until the due date. The result is rounded
        to two decimal places for currency precision.
        
        Parameters
        ----------
        remaining : float
            The remaining amount needed to fully fund the bill. This
            represents the difference between the bill amount and any
            existing allocation.
            
        due_date : datetime.date
            The date when the bill payment is due. This is used to
            calculate the available contribution period.
            
        curr_date : datetime.date
            The current date from which to begin contributions. This is
            typically the start date specified in the schedule method.
        
        Returns
        -------
        float
            The calculated daily contribution amount rounded to two
            decimal places. If the bill is already due (due_date <=
            curr_date), returns either the remaining amount (if on due
            date) or zero (if past due).
        
        Notes
        -----
        * Past-due bills return a contribution of zero, treating them as
        already paid.
        * Bills due today return the full remaining amount.
        * The result is rounded to 2 decimal places for currency values.
        * This is a key calculation that determines the smoothness of
        contributions across the available time period.
        """

        # If the bill is due before the current date, then the bill is
        # in the past and we will treat it as if it has already been
        # paid, thus the daily savings is zero.
        # 
        # Otherwise, calculate the number of days remaining until the
        # bill is due.
        days_remaining = max(0, (due_date - curr_date).days)
        
        # Calculate the daily savings for the bill. Round to 2 decimal
        # places to reflect the fact that we are dealing with dollars
        # and avoid floating point precision issues. If the number of
        # days remaining is zero, then the daily savings is the
        # remaining amount.
        if days_remaining == 0:
            contribution = remaining
        else:
            contribution = round(remaining / days_remaining, 2)

        return contribution

    def calculate_intervals(
            self, start_date: datetime.date, end_date: datetime.date,
            interval: int
        ) -> list[int]:
        """
        Calculate the sequence of interval periods between two dates.
        
        This method breaks down the time period between start_date and
        end_date into a series of intervals based on the specified
        interval length. It handles both full intervals and any partial
        interval at the end of the period.
        
        The calculation:
        #. Determines the total number of days between the dates.
        #. Calculates how many complete intervals fit in this period.
        #. Identifies any remaining days as a partial final interval.
        
        Parameters
        ----------
        start_date : datetime.date
            The beginning date of the time period. This is typically the
            contribution start date.
            
        end_date : datetime.date
            The ending date of the time period. This is typically the
            bill's due date.
            
        interval : int
            The number of days in each regular interval (e.g., 7 for
            weekly, 14 for bi-weekly contributions).
        
        Returns
        -------
        list[int]
            A list of interval lengths in days. Most intervals will be
            equal to the specified interval length, but the last
            interval may be shorter if the total period is not evenly
            divisible by the interval.
        
        Notes
        -----

        * The returned list will contain the interval length repeated
        for each full interval.
        * If there are remaining days that don't form a complete
        interval, a final element with that number of days is added.
        * This supports the creation of appropriate cash flows that
        respect the envelope's contribution frequency while ensuring
        the bill is fully funded by the due date.
        
        """
        # Calculate the number of days between the start and end dates.
        num_days = (end_date - start_date).days

        # Build the intervals as a list of full intervals plus any
        # remaining days as a partial interval. Integer division is used
        # to get the number of full intervals, and the modulo operator
        # is used to get the remaining days, if any.
        full_intervals = num_days // interval
        remaining_days = num_days % interval
        
        # Build the list of intervals and add the remaining interval if
        # there are any remaining days.
        intervals = [interval] * full_intervals

        if remaining_days > 0:
            intervals.append(remaining_days)

        return intervals
    
    def aggregate_cash_flows(
        self, cash_flows: list[CashFlow], start_date: datetime.date,
        interval: int
    ) -> list[CashFlow]:
        """
        Aggregate cash flows into a single cash flow per interval
        period. This is done by summing up all contributions for each
        interval period and creating a single cash flow for the total
        amount in that interval.

        Parameters
        ----------
        cash_flows : list
            List of CashFlow objects.
        start_date : datetime.date
            Start date.
        interval : int
            Contribution interval in days.

        Returns
        -------
        list
            List of CashFlow objects.
        """

        # Initialize dictionary to track total contributions per
        # interval period.
        int_contribs = {}
        bill_id = cash_flows[0].bill_id

        # Step 1: Sum up all contributions by interval period.
        #
        # The first interval has index 0, the second has index 1, etc.
        # They represent the number of days since the start date. If
        # the interval is 14 days, interval index 0 is the first 14 day
        # period, interval index 1 is the second 14 day period, etc.
        # When the loop is done, interval_contributions will have a key
        # for each interval index, and the value will be the total
        # contribution for that interval. The interval index tells us
        # that it belongs to the interval index-th interval, regardless
        # of the exact date of the contribution.
        for cf in cash_flows:

            # Calculate days since start date.
            days_since_start = (cf.date - start_date).days
            
            # Determine to which interval period this contribution
            # belongs. The integer division by the interval length
            # gives the index of the interval, which is enough to
            # determine which interval the contribution belongs to.
            int_idx = days_since_start // interval
            
            # Add this contribution to the interval sum. Initialize to 0
            # if this is the first contribution to this interval.
            if int_idx not in int_contribs:
                int_contribs[int_idx] = 0

            # Add the contribution to the interval's total.
            int_contribs[int_idx] += cf.amount

        # Step 2: Create one aggregated cash flow per interval period.
        agg_flows = []

        for int_idx, total_amount in sorted(int_contribs.items()):

            # Calculate the date for this interval. This approach puts
            # all contributions on the first day of the interval. This
            # avoids complications with partial intervals, but comes
            # at the cost of paying off the bill earlier than the due
            # date by the contribution interval size.
            int_date = (
                start_date + datetime.timedelta(days=int_idx * interval)
            )

            # Create a single cash flow for the total amount in this
            # interval. If the total amount is negative, we do not add
            # a cash flow because it means that the bill is paid off.
            if total_amount > 0:

                # Create the cash flow object. We round the amount to 2
                # decimal places to avoid floating point precision
                # issues. However, this is not a perfect solution, and
                # can lead to errors in the sum of the contributions.
                agg_flows.append(
                    CashFlow(
                        bill_id=bill_id,
                        date=int_date,
                        amount=round(total_amount, 2)
                    )
                )

        return agg_flows