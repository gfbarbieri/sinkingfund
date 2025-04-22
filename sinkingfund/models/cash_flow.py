"""
CashFlow Model
==============

The CashFlow model represents the movement of money into or out of a
sinking fund over time, tracking both the timing and magnitude of
financial transactions.

In a sinking fund system, understanding the flow of money is crucial for
proper planning and allocation. A CashFlow instance captures three
essential pieces of information:

1. Which bill it relates to (bill_id) - connecting the transaction to a
specific financial obligation.
2. When the transaction occurs (date) - establishing the timeline for
financial planning.
3. How much money is involved (amount) - quantifying the financial
impact.

The directionality of a CashFlow is represented by the sign of the
amount:
- Positive amounts (+) represent inflows: contributions, deposits, or
money being added to the sinking fund.
- Negative amounts (-) represent outflows: payments, withdrawals, or
money being removed from the sinking fund.

This dual-direction capability allows CashFlow objects to model the
complete lifecycle of funds:
- Regular contributions building up savings for a future expense.
- The eventual withdrawal when the expense comes due.
- Partial payments or installments spread over time.

By tracking these cash flows, the sinking fund system can:
- Project future balances at any point in time.
- Calculate how much to save regularly to meet future obligations.
- Visualize the timing of inflows and outflows.
- Analyze cash flow patterns to optimize budgeting strategies.

This immutable (frozen) dataclass ensures that once created, a CashFlow
record remains consistent and reliable for financial tracking and
planning purposes.

"""

########################################################################
## IMPORTS
########################################################################

import datetime

from dataclasses import dataclass

########################################################################
## CASHFLOW
########################################################################

@dataclass(frozen=True)
class CashFlow:
    """
    A cash flow class contains information about a cash flow to be
    made to a bill. Cash flows can be positive or negative. In the
    context of a sinking fund, positive cash flows are contributions or
    savings (debits) and negative cash flows are payments or withdrawals
    (credits).

    Attributes
    ----------
    bill_id: str
        The id of the bill.
    date: datetime.date
        The date of the cash flow.
    amount: float
        The amount of the cash flow.
    """

    bill_id: str
    date: datetime.date
    amount: float