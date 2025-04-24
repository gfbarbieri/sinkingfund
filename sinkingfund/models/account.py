"""
Account Model
=============

The Account model serves as the central hub for a sinking fund,
coordinating envelopes and tracking the overall financial status through
time.

An Account represents a complete sinking fund - a collection of
envelopes working together to manage future expenses along with their
associated cash flows. Think of it as a digital representation of a
savings account dedicated to your future planned expenses, allowing
you to:

#. Track Balances: Monitor your overall sinking fund balance and how
it's divided among different financial obligations.
#. Project Future States: Forecast your account balance over time as
contributions are made and bills are paid.
#. Visualize Cash Flows: See both inflows (contributions) and
outflows (payments) on a timeline.
#. Analyze Funding Adequacy: Determine if your contribution schedule
will fully fund all planned expenses by their due dates.

The Account model maintains:

* A collection of Envelopes (each tied to a specific Bill).
* A timeline of AccountState snapshots showing balance changes over
time.
* Methods to query important dates (first/last contributions, payment
dates).
* Calculations for total scheduled contributions and payments.

Core capabilities include:
* State Projection: Calculating daily account states from the first to
last cash flow.
* Cash Flow Management: Aggregating all scheduled cash flows across all
envelopes.
* Date Boundary Identification: Finding the first and last dates for
various financial events.
* Balance Analysis: Breaking down how the account balance is allocated
across different obligations.

This model enables a comprehensive view of your sinking fund strategy,
allowing you to validate that your saving approach will meet your
financial goals over time.

"""

########################################################################
## IMPORTS
########################################################################

import datetime

from dataclasses import dataclass
from typing import List

from .envelope import Envelope
from .cash_flow import CashFlow

########################################################################
## ACCOUNT STATE
########################################################################

@dataclass(frozen=True)
class AccountState:
    """
    An account state is a snapshot of the account at a given date.

    Attributes
    ----------
    date: datetime.date
        The date of the account state.
    balance: float
        The balance of the account.
    credits: float
        The credits (contributions) of the account.
    debits: float
        The debits (payments) of the account.
    """

    date: datetime.date
    balance: float
    credits: float
    debits: float

########################################################################
## MODELS
########################################################################

@dataclass
class Account:
    """
    An account is a collection of envelopes.

    Parameters
    ----------
    init_date: datetime.date
        The initial date of the account.
    addnl_balance: float
        The balance in addition to the amount allocated to the
        envelopes. For a sinking fund, this is the amount of money
        that is not allocated to the envelopes but exists in the
        account.
    envelopes: list[Envelope] | None
        The envelopes in the account.
    """

    init_date: datetime.date=datetime.date.today()
    addnl_balance: float=0.0
    envelopes: list[Envelope] | None=None
    states: List[AccountState]=None
        
    def project_account(self) -> List[AccountState]:
        """
        Project account states from the first to last cash flow.

        Returns
        -------
        List[AccountState]
            The projected account states.
        """

        # Start date is the earliest cash flow in any envelope. End
        # date is the latest cash flow in any envelope.
        start_date = self._first_sched_cash_flow()
        end_date = self._last_sched_cash_flow()

        # Initialize with the current state of the account.
        # 
        # The starting balance is the total amount allocated to all
        # envelopes plus the additional balance in the account not
        # allocated to envelopes.
        #
        # The starting date is the earliest cash flow in any envelope.
        current_date = start_date
        current_balance = (
            sum(e.allocated for e in self.envelopes) + self.addnl_balance
        )
        
        # Build the daily states of the account.
        daily_states = []
        
        while current_date <= end_date:

            # Get scheduled cash flows for the current date.
            sched_flows = self._get_sched_cash_flows(date=current_date)
            
            # Calculate total contributions and payments. Contributions
            # are positive (debits) and payments are negative (credits).
            debits = sum(c.amount for c in sched_flows if c.amount > 0)
            credits = sum(c.amount for c in sched_flows if c.amount < 0)
            
            # Update current balance after all accounting for all of the
            # scheduled cash flows.
            current_balance = round(current_balance + debits + credits, 2)
            
            # Create account state.
            state = AccountState(
                date=current_date,
                balance=current_balance,
                credits=credits,
                debits=debits
            )
            daily_states.append(state)
            
            # Update the date for the next iteration.
            current_date += datetime.timedelta(days=1)
        
        # Save the states.
        self.states = daily_states

    def _get_envelopes(self, bill_id: str | None=None) -> list[Envelope]:
        """
        Get the envelopes.
        """

        # If a bill ID is passed, then get the envelope. Otherwise, look
        # over all envelopes.
        if bill_id is not None:
            return [e for e in self.envelopes if e.bill.bill_id == bill_id]
        else:
            return self.envelopes

    def _get_sched_cash_flows(
        self, bill_id: str | None=None, date: datetime.date | None=None
    ) -> list[CashFlow]:
        """
        Get the cash flows.

        Parameters
        ----------
        bill_id: str | None
            The bill ID for which to get the cash flows.
        date: datetime.date | None
            The date for which to get the cash flows.

        Returns
        -------
        list[CashFlow]
            The cash flows.
        """

        # Get the envelopes.
        envelopes = self._get_envelopes(bill_id=bill_id)

        # Get the cash flows on a specific date.
        if date is not None:
            return [
                cf for e in envelopes for cf in e.schedule if cf.date == date
            ]
        else:
            return [cf for e in envelopes for cf in e.schedule]

    def _first_sched_cash_flow(
        self, bill_id: str | None=None
    ) -> datetime.date:
        """
        The first cash flow date.

        Parameters
        ----------
        bill_id: str | None
            The bill ID for which to get the first cash flow. If the
            bill ID is not provided, then the first cash flow date for
            the account is returned. If the wrong bill ID is passed,
            then None is returned, an error is not raised.

        Returns
        -------
        datetime.date
            The date of the first cash flow.
        """

        # Get the relevant envelopes.
        envelopes = self._get_envelopes(bill_id=bill_id)

        # If there are no envelopes, then return None. This is likely
        # because the wrong bill ID was passed.
        if len(envelopes) == 0:
            return None
        
        # Get the date of the earliest cash flow.
        return min(cf.date for e in envelopes for cf in e.schedule)
    
    def _last_sched_cash_flow(self, bill_id: str | None=None) -> datetime.date:
        """
        The last cash flow date.

        Parameters
        ----------
        bill_id: str | None
            The bill ID for which to get the last cash flow.

        Returns
        -------
        datetime.date
            The date of the last cash flow.
        """

        # Get the relevant envelopes.
        envelopes = self._get_envelopes(bill_id=bill_id)

        # If there are no envelopes, then return None. This is likely
        # because the wrong bill ID was passed.
        if len(envelopes) == 0:
            return None

        # Get the date of the latest cash flow.
        return max(cf.date for e in envelopes for cf in e.schedule)
    
    def _first_sched_contrib(self, bill_id: str | None=None) -> datetime.date:
        """
        The first contribution date.

        Parameters
        ----------
        bill_id: str | None
            The bill ID for which to get the first contribution.

        Returns
        -------
        datetime.date | None
            The date of the first contribution.
        """

        # Get the relevant envelopes.
        envelopes = self._get_envelopes(bill_id=bill_id)

        # The first contribution is the envelope with the earliest
        # cash flow date where the cash flow has an amount greater than
        # zero.
        contribs = [
            cf.date for e in envelopes for cf in e.schedule if cf.amount > 0
        ]

        # If there are contributions, then return the earliest date.
        # This occurs when the wrong bill ID is passed or when there
        # are no contributions scheduled for the bill.
        if len(contribs) > 0:
            return min(contribs)
        else:
            return None
    
    def _last_sched_contrib(self, bill_id: str | None=None) -> datetime.date:
        """
        The last contribution date.

        Parameters
        ----------
        bill_id: str | None
            The bill ID for which to get the last contribution.

        Returns
        -------
        datetime.date | None
            The date of the last contribution.
        """

        # Get the relevant envelopes.
        envelopes = self._get_envelopes(bill_id=bill_id)

        # The last contribution is the envelope with the latest
        # cash flow date. If a bill ID is passed, then we will return
        # the latest cash flow for the envelope associated with that
        # date.
        contribs = [
            cf.date for e in envelopes for cf in e.schedule if cf.amount > 0
        ]

        # If there are contributions, then return the earliest date.
        # This occurs when the wrong bill ID is passed or when there
        # are no contributions scheduled for the bill.
        if len(contribs) > 0:
            return max(contribs)
        else:
            return None
    
    def _total_sched_contribs(self) -> float:
        """
        The total contributions.

        Returns
        -------
        float
            The total contributions.
        """

        # Get the total contributions.
        contribs = [
            cf.amount for e in self.envelopes for cf in e.schedule
            if cf.amount > 0
        ]

        return sum(contribs)
    
    def _first_sched_bill_payment(
        self, bill_id: str | None=None
    ) -> datetime.date:
        """
        The first bill payment date.

        Parameters
        ----------
        bill_id: str | None
            The bill ID for which to get the first bill payment.

        Returns
        -------
        datetime.date | None
            The date of the first bill payment.
        """

        # Get the relevant envelopes.
        envelopes = self._get_envelopes(bill_id=bill_id)

        # Get the date of the earliest bill payment.
        payments = [
            cf.date for e in envelopes for cf in e.schedule if cf.amount < 0
        ]

        # If there are payments, then return the earliest date.
        # Otherwise, return None. This occurs when the wrong bill ID is
        # passed or when there are no bill payments scheduled for the
        # bill.
        if len(payments) > 0:
            return min(payments)
        else:
            return None
    
    def _last_sched_bill_payment(
        self, bill_id: str | None=None
    ) -> datetime.date:
        """
        The last bill payment date.

        Parameters
        ----------
        bill_id: str | None
            The bill ID for which to get the last bill payment.

        Returns
        -------
        datetime.date | None
            The date of the last bill payment.
        """

        # Get the relevant envelopes.
        envelopes = self._get_envelopes(bill_id=bill_id)

        # Get the date of the latest bill payment.
        payments = [
            cf.date for e in envelopes for cf in e.schedule if cf.amount < 0
        ]

        # If there are payments, then return the latest date. Otherwise,
        # return None. This occurs when the wrong bill ID is passed or
        # when there are no bill payments scheduled for the bill.
        if len(payments) > 0:
            return max(payments)
        else:
            return None

    def _total_sched_bill_payments(self) -> float:
        """
        The total bill payments.

        Returns
        -------
        float
            The total bill payments.
        """

        # Get the total bill payments.
        payments = [
            cf.amount for e in self.envelopes for cf in e.schedule
            if cf.amount < 0
        ]

        return sum(payments)

    def _balance_allocation(self) -> dict[str, tuple[float, float]]:
        """
        The balance allocation.

        Returns
        -------
        dict[str, tuple[float, float]]
            The balance allocation.
        """

        allocs = {
            e.bill.bill_id: (e.allocated, e.remaining)
            for e in self.envelopes
        }

        return allocs