"""
Independent Scheduler
=====================

This scheduler is independent of the allocation strategy. It simply
schedules payments to envelopes based on the due date of the bill and
the interval of the envelope.

The independent scheduler is useful for scenarios where the user wants
to schedule payments to envelopes based on the due date of the bill
and the interval of the envelope.

The formula for the independent scheduler is:

    cash_flow = (amount_due / interval) * days

where:
- cash_flow is the amount of money to be paid to the envelope.
- amount_due is the amount of money due to the bill.
- interval is the number of days in the interval.
- days is the number of days in the interval.

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
    Handles payment scheduling across multiple envelopes,
    optimizing for payment smoothing and opportunity cost.
    """
    
    def __init__(self):
        pass
    
    def schedule(
            self, envelopes: list[Envelope], start_date: datetime.date
        ) -> None:
        """
        Create a schedule of contributions and payouts (cash flows)
        towards a bill for each interval from the current date to the
        due date. The total amount contributed must be equal to the
        amount of the bill.

        Parameters
        ----------
        envelopes: list[Envelope]
            The envelopes to schedule payments for
        start_date: datetime.date
            The date to start the contribution schedule. In practice,
            this date will likely represent the date of your last
            contribution or a date when you receive income regularly.
        """

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
            intervals = sorted(self.calculate_intervals(
                start_date=start_date, end_date=bill.due_date,
                interval=envelope.interval
            ))

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

            for i, (days, amount) in enumerate(interval_contrib):

                # If there is any difference, add it to the first
                # contribution.
                amount = round(amount + (diff if i == 0 else 0), 2)

                # If the amount is zero, then do not add a cash flow.
                # It is possible to do this before this loop because
                # we know the daily contribution is zero.
                if amount == 0:
                    continue

                # Create the date of the contribution.
                date = start_date + datetime.timedelta(days=(i * days))

                # Create the contribution.
                cash_flow = CashFlow(
                    bill_id=bill.bill_id, date=date, amount=amount
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
        Calculate the daily contribution for a bill.

        Parameters
        ----------
        remaining: float
            The remaining amount to allocate.
        due_date: datetime.date
            The due date of the bill.
        curr_date: datetime.date
            The current date.
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
        Calculate the number of days in each interval from start_date to
        end_date.

        Parameters
        ----------
        start_date: datetime.date
            The starting date of the period.
        end_date: datetime.date
            The ending date of the period.
        interval: int
            The number of days in each interval.

        Returns
        -------
        list[int]
            A list where each element represents the number of days in
            an interval.
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