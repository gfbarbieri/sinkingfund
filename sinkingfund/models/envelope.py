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

from .bills import BillInstance
from .cash_flow import CashFlow

########################################################################
## ENVELOPE MODEL
########################################################################

class Envelope:
    """
    An envelope is a financial tool that represents a pool of money
    that is allocated to a bill.

    Parameters
    ----------
    bill: BillInstance
        The bill instance that the envelope is for.
    allocated: float
        The amount allocated to the bill. Set during allocation of
        existing account balance.

    Attributes
    ----------
    bill: BillInstance
        The bill instance that the envelope is for.
    allocated: float
        The amount allocated to the bill. Set during allocation of
        existing account balance.
    remaining: float
        The remaining amount due on the bill. Set during allocation of
        existing account balance.
    schedule: list[CashFlow]
        The schedule of contributions and payouts (cash flows) towards
        the bill.
    """

    def __init__(self, bill: BillInstance, allocated: float=0.0):
        """
        Initialize the envelope.
        """

        self.bill = bill
        self.allocated = allocated
        self.schedule: list[CashFlow] = []

        # BUSINESS LOGIC: The remaining amount due on the bill is the
        # amount due minus the amount allocated. This is the amount
        # that needs to be paid off by the envelope.
        self.remaining = bill.amount_due - allocated

    def total_sched_contribs(self) -> float:
        """
        Calculate the total contributions made to the envelope.
        """

        total_contributions = sum(
            cash_flow.amount for cash_flow in self.schedule
            if cash_flow.amount > 0
        )

        return total_contributions
    
    def total_sched_bill_payments(self) -> float:
        """
        Calculate the total payouts made from the envelope.
        """

        total_payouts = sum(
            cash_flow.amount for cash_flow in self.schedule
            if cash_flow.amount < 0
        )

        return total_payouts
    
    def first_sched_contribs(self) -> CashFlow | None:
        """
        Get the first contribution made to the envelope.
        """

        first_contrib = min([
            cash_flow.date for cash_flow in self.schedule
            if cash_flow.amount > 0
        ])

        return first_contrib
    
    def last_sched_contribs(self) -> CashFlow | None:
        """
        Get the last contribution made to the envelope.
        """

        last_contrib = max([
            cash_flow.date for cash_flow in self.schedule
            if cash_flow.amount > 0
        ])

        return last_contrib
    
    def first_sched_bill_payments(self) -> CashFlow | None:
        """
        Get the first payout made from the envelope.
        """

        first_payout = min([
            cash_flow.date for cash_flow in self.schedule
            if cash_flow.amount < 0
        ])

        return first_payout
    
    def last_sched_bill_payments(self) -> CashFlow | None:
        """
        Get the last payout made from the envelope.
        """

        last_payout = max([
            cash_flow.date for cash_flow in self.schedule
            if cash_flow.amount < 0
        ])

        return last_payout

    def get_sched_contribs(
        self, start_reference: datetime.date, end_reference: datetime.date
    ) -> list[CashFlow]:
        """
        Get the contributions for the envelope.
        """

        contribs = [
            cash_flow for cash_flow in self.schedule
            if cash_flow.amount > 0
            and start_reference <= cash_flow.date <= end_reference
        ]

        return contribs
    
    def get_sched_bill_payments(
        self, start_reference: datetime.date, end_reference: datetime.date
    ) -> list[CashFlow]:
        """
        Get the bill payments for the envelope.
        """

        bill_payments = [
            cash_flow for cash_flow in self.schedule
            if cash_flow.amount < 0
            and start_reference <= cash_flow.date <= end_reference
        ]
        
        return bill_payments

    def get_sched_cash_flows(
        self, start_reference: datetime.date, end_reference: datetime.date
    ) -> list[CashFlow]:
        """
        Get the cash flows for the envelope.
        """

        cash_flows = [
            cash_flow for cash_flow in self.schedule
            if start_reference <= cash_flow.date <= end_reference
        ]

        return cash_flows