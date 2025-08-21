"""
CashFlow Model
==============

The CashFlow model represents monetary transactions within a sinking
fund system, capturing the temporal and quantitative aspects of money
movement for precise financial planning and tracking.

Core Abstractions
-----------------

**Transaction Recording**: Each CashFlow instance immutably records a
single monetary transaction, linking it to a specific financial
obligation (bill_id), timing (date), and magnitude (amount). This
creates an audit trail for financial planning decisions.

**Directional Money Flow**: The sign convention enables modeling both
accumulation and disbursement phases. Positive amounts represent
contributions building toward future expenses, while negative amounts
represent the eventual payments when obligations come due.

**Temporal Precision**: By anchoring each transaction to a specific
date, the system can project future account balances, calculate
required savings rates, and optimize contribution timing relative to
payment deadlines.

Key Features
------------

* **Immutable Transaction Records**: Frozen dataclass ensures financial
  data integrity once recorded, preventing accidental modifications
  that could compromise planning accuracy.
* **Bidirectional Cash Flow**: Single model handles both savings
  accumulation (+) and bill payments (-) through signed amounts.
* **Bill Association**: Links each transaction to its originating
  financial obligation for clear audit trails and reporting.
* **Natural Ordering**: Automatic chronological sorting enables
  efficient timeline analysis and balance calculations.

Examples
--------

Creating contribution cash flows:

.. code-block:: python

   from decimal import Decimal
   from datetime import date

   # Bi-weekly car insurance contributions.
   contribution = CashFlow(
       bill_id="car_insurance",
       date=date(2025, 1, 15),
       amount=Decimal("75.00")
   )

Creating payment cash flows:

.. code-block:: python

   # Final payment when bill comes due.
   payment = CashFlow(
       bill_id="car_insurance", 
       date=date(2025, 6, 15),
       amount=Decimal("-450.00")
   )

Timeline analysis:

.. code-block:: python

   flows = [contribution1, contribution2, payment]

   # Chronological order via dataclass ordering.
   flows.sort()
   
   running_balance = Decimal("0")
   
   for flow in flows:
       running_balance += flow.amount
       print(f"{flow.date}: {running_balance}")

"""

########################################################################
## IMPORTS
########################################################################

import datetime

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterator, Literal

########################################################################
## CASHFLOW MODEL
########################################################################

@dataclass(frozen=True, order=True)
class CashFlow:
    """
    Immutable record of a monetary transaction within a sinking fund
    system.
    
    This class captures the essential attributes of any financial
    transaction: what bill it relates to, when it occurs, and how much
    money is involved. The frozen dataclass ensures data integrity
    while automatic ordering enables chronological analysis.
    
    Parameters
    ----------
    bill_id : str
        Unique identifier linking this transaction to a specific
        financial obligation. Must be non-empty.
    date : datetime.date
        When this transaction occurs. Used for timeline calculations
        and ordering cash flows chronologically.
    amount : Decimal
        Monetary value of the transaction. Positive values represent
        inflows (contributions, savings), negative values represent
        outflows (payments, withdrawals).
        
    Raises
    ------
    ValueError
        If bill_id is empty or amount is not a valid monetary value.
        
    Notes
    -----
    DESIGN CHOICE: Using Decimal instead of float prevents floating-
    point precision errors that could accumulate in financial
    calculations over time.
    
    BUSINESS GOAL: Immutable transactions create a reliable audit
    trail for financial planning decisions and prevent accidental
    modifications that could compromise balance calculations.
    
    Examples
    --------
    Create a bi-weekly contribution:
    
    .. code-block:: python
    
       from decimal import Decimal
       from datetime import date
       
       contribution = CashFlow(
           bill_id="auto_insurance",
           date=date(2025, 1, 15), 
           amount=Decimal("87.50")
       )
       
    Create a payment when bill comes due:
    
    .. code-block:: python
    
       payment = CashFlow(
           bill_id="auto_insurance",
           date=date(2025, 6, 15),
           amount=Decimal("-525.00")
       )
       
    Chronological sorting for timeline analysis:
    
    .. code-block:: python
    
       flows = [payment, contribution]
       flows.sort()  # Automatically sorted by date
       assert flows[0].date < flows[1].date
    """
    
    # INVARIANT: Primary sorting key for chronological ordering.
    # Secondary keys (bill_id, amount) provide deterministic ordering
    # when multiple transactions occur on the same date.
    date: datetime.date
    bill_id: str
    amount: Decimal
    
    def __post_init__(self) -> None:
        """
        Validate cash flow data immediately after construction.
        
        Raises
        ------
        ValueError
            If bill_id is empty or whitespace-only, or if amount
            cannot be converted to a valid Decimal value.
            
        Notes
        -----
        Validation runs once at construction time rather than on every
        property access, ensuring data integrity with minimal
        performance overhead.
        """

        # BUSINESS GOAL: Prevent silent failures from empty identifiers
        # that could cause incorrect bill associations.
        if not self.bill_id or not self.bill_id.strip():
            raise ValueError("bill_id cannot be empty or whitespace")
        
        # DESIGN CHOICE: Explicit Decimal validation catches conversion
        # errors early rather than allowing invalid monetary values to
        # propagate through the system.
        try:

            if not isinstance(self.amount, Decimal):
                # Convert to Decimal if not already, triggering
                # validation.
                object.__setattr__(self, 'amount', Decimal(str(self.amount)))

        except (ValueError, TypeError) as e:
            raise ValueError(f"amount must be a valid monetary value: {e}")
    
    @property 
    def is_inflow(self) -> bool:
        """
        Check if this cash flow represents money coming into the fund.
        
        Returns
        -------
        bool
            True if amount is positive (contribution/deposit),
            False if amount is zero or negative.
            
        Examples
        --------
        .. code-block:: python
        
           contribution = CashFlow("rent", date.today(), Decimal("500"))
           payment = CashFlow("rent", date.today(), Decimal("-1200"))
           
           assert contribution.is_inflow is True
           assert payment.is_inflow is False
        """

        return self.amount > 0
    
    @property
    def is_outflow(self) -> bool:
        """
        Check if this cash flow represents money leaving the fund.
        
        Returns
        -------
        bool
            True if amount is negative (payment/withdrawal),
            False if amount is zero or positive.
            
        Examples
        --------
        .. code-block:: python
        
           payment = CashFlow(
               "utilities", date.today(), Decimal("-150")
           )
           contribution = CashFlow(
               "utilities", date.today(), Decimal("50")
           )
           
           assert payment.is_outflow is True
           assert contribution.is_outflow is False
        """

        return self.amount < 0
    
########################################################################
## CASH FLOW SCHEDULE
########################################################################

class CashFlowSchedule:
    """
    A schedule is a list of cash flows that represent the schedule of
    contributions to a bill.
    """

    def __init__(self) -> None:
        """
        Initialize the schedule.
        """

        self.cash_flows: list[CashFlow] = []

    def add_cash_flows(self, cash_flows: list[CashFlow] | CashFlow) -> None:
        """
        Add a cash flow to the schedule.
        """

        if isinstance(cash_flows, list):
            self.cash_flows.extend(cash_flows)
        else:
            self.cash_flows.append(cash_flows)

        self.cash_flows.sort(key=lambda cf: cf.date)
    
    def total_amount_as_of_date(
        self, as_of_date: datetime.date,
        exclude: Literal['contributions', 'payouts'] | None=None
    ) -> Decimal:
        """
        Sum all cash flows up to and including the specified date.
        """

        # DEFENSIVE: If the schedule has no cash flows, then the total
        # amount is 0. If the passed as_of_date exceeds the maximum date
        # in the cash flow schedule, then the amonut is 0.
        if (
            len(self.cash_flows) == 0
            or as_of_date > max([cf.date for cf in self.cash_flows])
        ):
            return Decimal('0.00')
        
        # BUSINESS GOAL: Calculate the total amount of cash flows up to
        # and including the specified date, with the ability to exclude
        # contributions or payouts.
        cash_flows = self.cash_flows_in_range(
            start_date=min([cf.date for cf in self.cash_flows]),
            end_date=as_of_date,
            exclude=exclude
        )

        total = sum([cf.amount for cf in cash_flows])

        return total
    
    def total_amount_in_range(
        self, start_date: datetime.date, end_date: datetime.date,
        exclude: Literal['contributions', 'payouts'] | None=None
    ) -> Decimal:
        """
        Total of all cash flows in a date range.
        """

        cash_flows = self.cash_flows_in_range(
            start_date=start_date, end_date=end_date, exclude=exclude
        )

        total = sum([cf.amount for cf in cash_flows])

        return total

    def cash_flow_dates_in_range(
        self, start_date: datetime.date, end_date: datetime.date,
        exclude: Literal['contributions', 'payouts'] | None=None
    ) -> list[datetime.date]:
        """
        Get the dates of all cash flows.
        """

        cash_flows = self.cash_flows_in_range(
            start_date=start_date, end_date=end_date, exclude=exclude
        )

        dates = [cf.date for cf in cash_flows]

        return dates
    
    def cash_flows_in_range(
        self, start_date: datetime.date, end_date: datetime.date,
        exclude: Literal['contributions', 'payouts'] | None=None
    ) -> list[CashFlow]:
        """
        Get cash flows within a date range.
        """

        if exclude == 'contributions':
            cash_flows = [
                cf for cf in self.cash_flows
                if start_date <= cf.date <= end_date
                and not cf.is_inflow
            ]
        elif exclude == 'payouts':
            cash_flows = [
                cf for cf in self.cash_flows
                if start_date <= cf.date <= end_date
                and not cf.is_outflow
            ]
        else:
            cash_flows = [
                cf for cf in self.cash_flows
                if start_date <= cf.date <= end_date
            ]

        return cash_flows
    
    def __len__(self) -> int:
        return len(self.cash_flows)
    
    def __iter__(self) -> Iterator[CashFlow]:
        return iter(self.cash_flows)