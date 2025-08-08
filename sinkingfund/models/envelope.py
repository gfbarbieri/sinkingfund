"""
Envelope Model
==============

The envelope model represents a core concept in envelope-based
budgeting, where money is allocated into separate "envelopes" for
specific purposes.

In traditional envelope budgeting, a person would cash their paycheck
and physically distribute the money into different envelopes labeled for
various expense categories (rent, groceries, utilities, etc.). When a
bill came due, they would only spend the money from the appropriate
envelope. Once an envelope was empty, no more could be spent in that
category until the next budgeting period.

In a sinking fund context, envelopes serve a slightly different purpose.
Rather than representing regular monthly expenses, sinking fund
envelopes accumulate money over time for future, often irregular
expenses. Each envelope:

#. Is linked to a specific bill or expense.
#. Tracks how much has been allocated for that expense and how much is
still needed before the bill is due.

Benefits of the envelope approach for sinking funds:

* Visualization: Makes abstract future expenses tangible by creating
dedicated pools of money.
* Prioritization: Helps prioritize which expenses to fund first when
* Prevention of "borrowing": Discourages using money allocated for
one purpose to cover another expense.
* Tracking progress: Shows progress toward fully funding each planned
expense.
* Peace of mind: Reduces financial anxiety by knowing that money is
being set aside for future obligations.

This Envelope class serves as the digital equivalent of physical
envelopes, tracking the allocation, remaining amounts, and associated
bills for each expense in your sinking fund strategy.

"""

########################################################################
## IMPORTS
########################################################################

import datetime

from dataclasses import dataclass

from .bills import Bill, BillInstance
from .cash_flow import CashFlow

########################################################################
## ENVELOPE MODEL
########################################################################

@dataclass
class Envelope:
    """
    An envelope is a financial tool that represents a pool of money
    that is allocated to a bill.

    Parameters
    ----------
    bill: Bill
        The bill that the envelope is for.
    contrib_interval: int
        The interval over which contributions are made to the envelope
        towards paying off the bill.

    Attributes
    ----------
    bill: Bill
        The bill that the envelope is for.
    interval: int
        The interval over which contributions are made to the envelope
        towards paying off the bill.
    remaining: float
        The remaining amount due on the bill. Set during allocation of
        existing account balance.
    allocated: float
        The amount allocated to the bill. Set during allocation of
        existing account balance.
    schedule: list[CashFlow]
        The schedule of contributions and payouts (cash flows) towards
        the bill.
    """

    bill: Bill
    remaining: float
    allocated: float=0
    interval: int=1
    schedule: list[CashFlow] | None=None

    def next_instance(
        self, reference_date: datetime.date, inclusive: bool=False
    ) -> BillInstance | None:
        """
        Get the next instance of the bill. This method extends the
        `Bill.next_instance` method by making a correction for the
        amount allocated to the bill.

        Parameters
        ----------
        reference_date: datetime.date
            The date to get the next instance of the bill.
        inclusive: bool
            If True, includes bills due exactly on the reference date.
            If False, only returns bills due after the reference date.

        Returns
        -------
        BillInstance | None
            The next instance of the bill.
        """

        # 1. Get the next instance of the bill.
        bill_instance = self.bill.next_instance(
            reference_date=reference_date, inclusive=inclusive
        )

        # 2. If there is a next instance, and a balance was allocated
        # to the bill, then we need to subtract that from the amount
        # due. This is stored in the `remaining` attribute.
        if bill_instance is not None and self.remaining is not None:
            bill_instance.amount_due = self.remaining

        return bill_instance