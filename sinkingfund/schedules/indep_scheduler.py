"""
Independent Scheduler
=====================

The Independent Scheduler provides a straightforward approach to
scheduling contributions for sinking fund envelopes without considering
interactions between different bills.

Mathematical Concept
--------------------

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
-----------------

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
----------

* **Simplicity**: Easy to understand and implement.
* **Predictability**: Creates regular, consistent contributions for
  each bill.
* **Bill-Level Smoothing**: Each bill has evenly distributed
  contributions.
* **Independence**: Changes to one bill don't affect the
  contribution schedule of others.

When to Use
-----------

The Independent Scheduler is ideal for:

* Users who want to understand exactly how much they're contributing
  to each bill at each interval.
* Scenarios where bills should be treated separately without
  interactions.
* Situations where bill-level contribution consistency is more
  important than total outflow smoothing.
* Simple sinking fund setups with few bills.

Comparison with Other Schedulers
--------------------------------

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

from __future__ import annotations

import datetime
from decimal import Decimal, ROUND_HALF_UP

from .base import BaseScheduler
from ..models import Envelope, CashFlow, CashFlowSchedule
from ..utils import increment_date

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
        self, envelopes: list[Envelope]
    ) -> dict[Envelope, CashFlowSchedule]:
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
        
        Returns
        -------
        dict[Envelope, CashFlowSchedule]
            A dictionary mapping each envelope to its corresponding
            schedule.
        
        Notes
        -----
        * Envelopes without a valid next bill instance are skipped.
        * The schedule handles partial intervals at the end of the
          period.
        * Rounding differences are added to the last contribution to
          ensure exact funding.
        * A negative cash flow equal to the bill amount is added on the
          due date.
        """

        schedules = {}

        for envelope in envelopes:
            
            # BUSINESS GOAL: Create predictable, even contribution
            # schedules for each bill to help users budget
            # consistently.
            schedule = CashFlowSchedule()

            # DESIGN CHOICE: Calculate remaining amount equal to the
            # amount due minus the initial allocation. We will ignore
            # scheduled cash flows, since this function's purpose is to
            # create a schedule for the envelope. If you use the
            # envelopes.remaining() method, you will get the remaining
            # amount including scheduled cash flows.
            remaining = (
                envelope.bill_instance.amount_due - envelope.initial_allocation
            )

            # Calculate the cash flow required to pay off the bill in
            # the given time frame.
            daily_contrib = self.calculate_daily_contribution(
                remaining=remaining,
                due_date=envelope.bill_instance.due_date,
                curr_date=envelope.start_contrib_date,
            )

            # Break down the time period into contribution intervals
            # based on the envelope's preferred frequency.
            contrib_intervals = self.calculate_contribution_intervals(
                start_date=envelope.start_contrib_date,
                end_date=envelope.end_contrib_date,
                interval=envelope.contrib_interval
            )

            # The contribution at each interval is the daily
            # contribution times the interval.
            contrib_amounts = [
                (
                    interval, 
                    (daily_contrib * interval).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                )
                for interval in contrib_intervals
            ]

            # BUSINESS GOAL: Ensure exact funding by adjusting for
            # rounding differences. Any pennies lost to rounding are
            # added to the last contribution.
            diff = remaining - sum(
                contrib[1] for contrib in contrib_amounts
            )

            # DESIGN CHOICE: Add difference to the last contribution
            # rather than the first to maintain consistent early
            # payments.
            contrib_amounts[-1] = (
                contrib_amounts[-1][0], contrib_amounts[-1][1] + diff
            )

            # Create the contribution cash flows based on the calculated
            # amounts and timing.
            cash_flows = []
            
            curr_date = envelope.start_contrib_date

            for interval, amount in contrib_amounts:

                # PERFORMANCE: Only create cash flows for positive
                # amounts to avoid unnecessary zero-value entries.
                if amount > Decimal("0.00"):
                    cash_flow = CashFlow(
                        bill_id=envelope.bill_instance.bill_id,
                        date=curr_date,
                        amount=amount
                    )
                    cash_flows.append(cash_flow)

                # Move to the next contribution date.
                curr_date = increment_date(
                    reference_date=curr_date, frequency='daily',
                    interval=interval, num_intervals=1
                )

            # BUSINESS GOAL: Add the bill payment as a negative cash
            # flow to complete the envelope lifecycle.
            cash_flows.append(
                CashFlow(
                    bill_id=envelope.bill_instance.bill_id,
                    date=envelope.bill_instance.due_date,
                    amount=-envelope.bill_instance.amount_due
                )
            )

            # Add the cash flows to the schedule.
            schedule.add_cash_flows(cash_flows)

            # Add the schedule to the schedules dictionary.
            schedules[envelope] = schedule

        return schedules

    def calculate_daily_contribution(
            self,
            remaining: Decimal,
            due_date: datetime.date,
            curr_date: datetime.date
        ) -> Decimal:
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
        remaining : Decimal
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
        Decimal
            The calculated daily contribution amount. If the bill is
            already due (due_date <= curr_date), returns either the
            remaining amount (if on due date) or zero (if past due).
        
        Notes
        -----
        * Past-due bills return a contribution of zero, treating them as
          already paid.
        * Bills due today return the full remaining amount.
        * The result is rounded to 2 decimal places for currency values.
        * This is a key calculation that determines the smoothness of
          contributions across the available time period.
        """

        # BUSINESS GOAL: Calculate how much must be saved daily to
        # fully fund the bill by its due date.
        days_remaining = (due_date - curr_date).days

        # EDGE CASE: Handle bills that are due today or past due.
        if days_remaining <= 0:
            contribution = remaining
        else:
            contribution = remaining / days_remaining

        return contribution
    
    def calculate_contribution_intervals(
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

        # BUSINESS GOAL: Break the time period into manageable
        # contribution intervals that respect the user's preferred
        # payment frequency.
        num_days = (end_date - start_date).days

        # DESIGN CHOICE: Build the intervals as a list of full intervals
        # plus any remaining days as a partial interval. Integer
        # division is used to get the number of full intervals, and the
        # modulo operator is used to get the remaining days, if any.
        full_intervals = num_days // interval
        remaining_days = num_days % interval
        
        # PERFORMANCE: Pre-allocate the list for efficiency.
        intervals = [interval] * full_intervals

        # BUSINESS GOAL: Include partial intervals to ensure complete
        # coverage of the time period.
        if remaining_days > 0:
            intervals.append(remaining_days)

        return intervals