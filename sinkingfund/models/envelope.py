"""
Envelope Model
==============

The Envelope model implements digital envelope budgeting for sinking
fund management, creating dedicated savings containers for specific
future expenses with temporal tracking and balance projections.

Core Abstractions
-----------------

**Targeted Savings Container**: Each envelope represents a dedicated
savings account for a single bill instance, isolating funds to prevent
misallocation across different financial obligations. This mirrors the
physical envelope budgeting method where cash is separated into labeled
containers.

**Temporal Balance Tracking**: Envelopes maintain both static initial
allocations and dynamic scheduled contributions over time, enabling
precise balance projections at any future date. This temporal awareness
supports long-term financial planning and cash flow optimization.

**Contribution Window Management**: Each envelope defines start and end
contribution dates, establishing clear savings periods that align with
bill payment schedules and planning horizons. This prevents over-saving
and optimizes fund utilization.

Key Features
------------

* **Bill Instance Association**: Links each envelope to a specific bill
  occurrence with defined amounts and due dates, ensuring targeted
  savings for actual financial obligations.
* **Multi-Source Funding**: Combines initial balance allocations with
  scheduled contribution streams, supporting both lump-sum transfers
  and regular savings patterns.
* **Date-Aware Balance Queries**: Projects envelope balances at any
  point in time by combining initial allocations with scheduled
  contributions up to that date.
* **Funding Status Tracking**: Determines whether envelopes will be
  fully funded by their target dates, enabling early intervention for
  underfunded obligations.
* **Schedule Integration**: Accepts complete contribution schedules from
  scheduling algorithms, maintaining separation between savings logic
  and schedule generation.

Examples
--------

Creating an envelope for a quarterly insurance bill:

.. code-block:: python

   from decimal import Decimal
   from datetime import date
   
   # Bill due March 15th for $450
   bill_instance = BillInstance(
       bill_id="auto_insurance",
       service="Quarterly Auto Insurance", 
       due_date=date(2025, 3, 15),
       amount_due=Decimal("450.00")
   )
   
   envelope = Envelope(
       bill_instance=bill_instance,
       initial_allocation=Decimal("100.00"),
       start_contrib_date=date(2025, 1, 1),
       end_contrib_date=date(2025, 3, 14)
   )

Querying envelope balances over time:

.. code-block:: python

   # Check current funding status
   current = envelope.current_balance(date(2025, 2, 1))
   remaining = envelope.remaining(date(2025, 2, 1))
   
   print(f"Current balance: ${current}")
   print(f"Still needed: ${remaining}")
   
   # Check if fully funded by due date
   if envelope.is_fully_funded(bill_instance.due_date):
       print("Envelope will be fully funded on time")

Integrating with contribution schedules:

.. code-block:: python

   # Scheduler creates contribution plan
   schedule = scheduler.create_bi_weekly_schedule(
       target_amount=remaining,
       start_date=envelope.start_contrib_date,
       end_date=envelope.end_contrib_date
   )
   
   # Assign schedule to envelope
   envelope.set_schedule(schedule)
   
   # Project final balance
   final_balance = envelope.current_balance(bill_instance.due_date)

"""

########################################################################
## IMPORTS
########################################################################

import datetime

from decimal import Decimal
from typing import Literal, Optional, Union

from .bills import BillInstance
from .cash_flow import CashFlowSchedule

########################################################################
## ENVELOPE MODEL
########################################################################

class Envelope:
    """
    Digital envelope for targeted savings toward a specific bill
    instance with temporal balance tracking and contribution scheduling.
    
    This class implements the envelope budgeting pattern for sinking
    funds, creating isolated savings containers that accumulate money
    over time for specific future expenses. Each envelope tracks both
    initial balance allocations and scheduled contributions to project
    funding status at any point in time.
    
    Parameters
    ----------
    bill_instance : BillInstance
        The specific bill occurrence this envelope saves toward. Defines
        the target amount and due date for funding calculations.
    initial_allocation : Decimal, optional
        Lump-sum amount allocated to this envelope at initialization,
        typically from existing account balances. Default is Decimal("0").
    start_contrib_date : datetime.date, optional
        First date when scheduled contributions begin. If None, no
        contribution window is defined. Should align with planning
        periods and bill payment schedules.
    end_contrib_date : datetime.date, optional
        Last date when scheduled contributions occur. If None, no
        contribution window is defined. Typically set to bill due date
        or end of planning period.
        
    Attributes
    ----------
    bill_instance : BillInstance
        Target bill for this envelope's savings.
    initial_allocation : Decimal
        Initial lump-sum funding amount.
    start_contrib_date : datetime.date or None
        Beginning of contribution window.
    end_contrib_date : datetime.date or None
        End of contribution window.
    schedule : CashFlowSchedule
        Complete contribution schedule assigned by scheduling
        algorithms.
        
    Raises
    ------
    ValueError
        If initial_allocation is negative, or if contribution dates are
        provided but end_date is before start_date.
        
    Examples
    --------
    Create envelope with initial allocation:
    
    .. code-block:: python
    
       from decimal import Decimal
       from datetime import date
       
       envelope = Envelope(
           bill_instance=insurance_bill,
           initial_allocation=Decimal("200.00"),
           start_contrib_date=date(2025, 1, 1),
           end_contrib_date=date(2025, 3, 14)
       )
       
    Create envelope for immediate scheduling:
    
    .. code-block:: python
    
       # No initial allocation, will be funded entirely through
       # scheduled contributions.
       envelope = Envelope(
           bill_instance=utility_bill,
           start_contrib_date=date(2025, 1, 15),
           end_contrib_date=date(2025, 2, 28)
       )
    """
    
    def __init__(
        self,
        bill_instance: BillInstance,
        initial_allocation: Union[Decimal, float] = None,
        start_contrib_date: Optional[datetime.date] = None,
        end_contrib_date: Optional[datetime.date] = None,
        contrib_interval: Optional[int] = None,
    ) -> None:
        """
        Initialize envelope with bill association and funding
        parameters.
        
        Validates input parameters and establishes the envelope's
        funding structure. Contribution dates define the window for
        scheduled savings, while initial allocation provides immediate
        funding.
        """
        
        # Assign default for mutable Decimal to prevent shared
        # references.
        if initial_allocation is None:
            initial_allocation = Decimal("0.00")
            
        # BUSINESS GOAL: Prevent negative allocations that would
        # indicate accounting errors or misunderstanding of envelope
        # purpose.
        if initial_allocation < 0:
            raise ValueError("initial_allocation cannot be negative.")
        
        if isinstance(initial_allocation, float):
            initial_allocation = Decimal(str(initial_allocation))
        
        # BUSINESS GOAL: Ensure contribution windows are logically
        # ordered to prevent scheduling conflicts and unclear savings
        # periods.
        if (start_contrib_date is not None and end_contrib_date is not None 
            and end_contrib_date < start_contrib_date):
            raise ValueError(
                "end_contrib_date cannot be before start_contrib_date."
            )
        
        self.bill_instance = bill_instance
        self.initial_allocation = initial_allocation
        self.start_contrib_date = start_contrib_date
        self.end_contrib_date = end_contrib_date
        self.contrib_interval = contrib_interval
        self.schedule: CashFlowSchedule = CashFlowSchedule()

    def remaining(
        self, as_of_date: Optional[datetime.date] = None
    ) -> Decimal:
        """
        Calculate remaining amount needed to fully fund this envelope.
        
        Determines how much additional money is required by comparing
        the target bill amount against the envelope's projected balance
        as of the specified date.
        
        Parameters
        ----------
        as_of_date : datetime.date, optional
            Date for balance calculation. If None, uses today's date.
            
        Returns
        -------
        Decimal
            Amount still needed to reach bill target. Returns
            Decimal("0") if envelope is already fully funded or
            overfunded.
            
        Examples
        --------
        .. code-block:: python
        
           # Check funding gap today.
           gap = envelope.remaining()
           
           # Check funding gap on specific date.
           gap_feb = envelope.remaining(date(2025, 2, 15))
           
           if gap > 0:
               print(f"Need ${gap} more")
        """
        
        # Set default to today's date.
        if as_of_date is None:
            as_of_date = self.start_contrib_date
        
        # BUSINESS GOAL: Ensure that the remaining amount is always
        # non-negative.
        current = self.get_balance_as_of_date(as_of_date=as_of_date)
        target = self.bill_instance.amount_due
        
        # Return zero if already fully funded to prevent negative
        # remaining.
        remaining = max(Decimal("0.00"), target - current)
        
        return remaining
    
    def get_balance_as_of_date(
        self, as_of_date: Optional[datetime.date]=None,
        exclude: Literal['contributions', 'payouts'] | None=None
    ) -> Decimal:
        """
        Project envelope balance as of a specific date.
        
        Combines initial allocation with all scheduled contributions
        that occur on or before the specified date to calculate the
        total envelope balance at that point in time.
        
        Parameters
        ----------
        as_of_date : datetime.date, optional
            Date for balance projection. If None, uses today's date.
        exclude : Literal['contributions', 'payouts'] | None, optional
            Exclude contributions or payouts from the balance
            calculation. If None, both are included.
            
        Returns
        -------
        Decimal
            Projected envelope balance including initial allocation
            and contributions through the specified date.
            
        Examples
        --------
        .. code-block:: python
        
           # Current balance today.
           current = envelope.current_balance()
           
           # Projected balance on bill due date.
           final = envelope.current_balance(bill_instance.due_date)
           
           # Balance at specific milestone.
           mid_month = envelope.current_balance(date(2025, 2, 15))
        """
        
        # Set default to today's date.
        if as_of_date is None:
            as_of_date = self.start_contrib_date
        
        # BUSINESS GOAL: Sum the contributions that have occurred
        # up to the as_of_date. Payouts are excluded in case the date
        # passed is at least the due date of the bill.
        flows = self.schedule.total_amount_as_of_date(
            as_of_date=as_of_date, exclude=exclude
        )
        
        # Return the sum of the initial allocation and the scheduled
        # contributions.
        balance = self.initial_allocation + flows
        
        return balance
    
    def total_cash_flow_on_date(
        self, date: datetime.date,
        exclude: Literal['contributions', 'payouts'] | None=None
    ) -> Decimal:
        """
        Get the total contributions made on a specific date.
        """

        # BUSINESS GOAL: Get the cash flows for the given date.
        cash_flows = self.schedule.cash_flows_in_range(
            start_date=date, end_date=date, exclude=exclude
        )

        # BUSINESS GOAL: Get the total amount of the cash flows.
        total = sum([cf.amount for cf in cash_flows])
        
        return total

    def is_fully_funded(
        self, as_of_date: Optional[datetime.date] = None
    ) -> bool:
        """
        Check if envelope will be fully funded by a specific date.
        
        Determines whether the envelope's projected balance meets or
        exceeds the bill's target amount, indicating successful funding
        without requiring additional contributions.
        
        Parameters
        ----------
        as_of_date : datetime.date, optional
            Date to check funding status. If None, uses today's date.
            
        Returns
        -------
        bool
            True if envelope balance meets or exceeds bill amount,
            False if additional funding is still needed.
            
        Examples
        --------
        .. code-block:: python
        
           # Check if funded today
           if envelope.is_fully_funded():
               print("Envelope is ready!")
               
           # Check if will be funded by due date
           if envelope.is_fully_funded(bill_instance.due_date):
               print("On track for full funding")
           else:
               print("Need to increase contributions")
        """
        
        # Set default to today's date.
        if as_of_date is None:
            as_of_date = self.start_contrib_date
            
        # BUSINESS GOAL: Ensure that the envelope is fully funded.
        is_fully_funded = (
            self.get_balance_as_of_date(as_of_date=as_of_date)
            >= self.bill_instance.amount_due
        )
        
        return is_fully_funded

    def set_cash_flow_schedule(self, schedule: CashFlowSchedule) -> None:
        """
        Assign contribution schedule to this envelope.
        
        Replaces the envelope's current schedule with a new one,
        typically called by schedule managers after generating
        optimized contribution plans.
        
        Parameters
        ----------
        schedule : Schedule
            Complete contribution schedule with cash flows and dates.
            A copy is made to prevent external modifications.
            
        Examples
        --------
        .. code-block:: python
        
           # Scheduler creates optimized plan
           schedule = scheduler.create_bi_weekly_schedule(
               target_amount=envelope.remaining(),
               start_date=envelope.start_contrib_date,
               end_date=envelope.end_contrib_date
           )
           
           # Assign to envelope
           envelope.set_schedule(schedule)
        """
        
        self.schedule = schedule.copy()