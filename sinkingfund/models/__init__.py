"""
Models Package
==============

The models package defines the core domain objects for the sinking fund
system. These immutable value objects and data classes represent the
fundamental business concepts and provide type-safe interfaces for
manipulating financial data throughout the application.

Core Abstractions
-----------------

**Domain Modeling**: Clean representation of business concepts using
immutable data classes with validation, ensuring data integrity and
predictable behavior across system boundaries.

**Value Objects**: Bills, envelopes, and cash flows are modeled as
value objects with equality semantics, enabling safe sharing and
comparison operations without reference-based identity concerns.

**Type Safety**: Comprehensive type annotations and validation provide
compile-time and runtime safety for financial calculations and date
arithmetic operations.

**Monetary Precision**: All monetary amounts use Decimal arithmetic
to ensure accurate financial calculations without floating-point
rounding errors.

Key Components
--------------

- **Bill**: Represents a payment obligation with support for both
  one-time and recurring bills with configurable schedules.
- **BillInstance**: Specific occurrence of a bill with concrete due
  date and amount, used for timeline planning.
- **Envelope**: Payment savings container that tracks contribution
  schedules and funding progress toward bill obligations.
- **CashFlow**: Individual cash flow event with amount, date, and
  descriptive information for financial tracking.
- **CashFlowSchedule**: Collection of cash flows with timeline
  operations and aggregation capabilities.

Examples
--------

Creating and working with bills:

.. code-block:: python

   from datetime import date
   from decimal import Decimal
   from sinkingfund.models import Bill, BillInstance

   # Create a recurring monthly bill.
   electric_bill = Bill(
       bill_id="electric",
       service="Electric Utility",
       amount_due=Decimal("150.00"),
       recurring=True,
       start_date=date(2024, 1, 15),
       frequency="monthly"
   )

   # Generate instances for planning period.
   instances = electric_bill.instances_in_range(
       start_reference=date(2024, 1, 1),
       end_reference=date(2024, 6, 30)
   )
   # Returns BillInstance objects for Jan-Jun 2024

   # Get next instance for forward planning.
   next_instance = electric_bill.next_instance(
       reference_date=date(2024, 3, 15)
   )
   # Returns BillInstance for April 15, 2024.

Managing envelopes and contributions:

.. code-block:: python

   from sinkingfund.models import Envelope

   # Create envelope for bill instance.
   envelope = Envelope(
       bill_instance=instances[0],
       start_contrib_date=date(2024, 1, 1),
       contrib_interval=14,
       current_balance=Decimal("75.00")
   )

   # Check funding status.
   if envelope.is_fully_funded:
       print("Envelope ready for payment")
   else:
       remaining = envelope.remaining_amount
       print(f"Need ${remaining} more")

Cash flow analysis:

.. code-block:: python

   from sinkingfund.models import CashFlow, CashFlowSchedule

   # Create individual cash flows.
   flows = [
       CashFlow(
           amount=Decimal("-150.00"),
           flow_date=date(2024, 1, 15),
           description="Electric bill payment"
       ),
       CashFlow(
           amount=Decimal("75.00"),
           flow_date=date(2024, 1, 1),
           description="Envelope contribution"
       )
   ]

   # Create schedule for analysis.
   schedule = CashFlowSchedule(cash_flows=flows)
   
   # Analyze cash flow patterns.
   monthly_total = schedule.total_in_range(
       start_date=date(2024, 1, 1),
       end_date=date(2024, 1, 31)
   )
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

# BUSINESS GOAL: Provide core domain objects for systematic financial
# modeling with type safety and monetary precision.
from .bills import Bill, BillInstance
from .cash_flow import CashFlow, CashFlowSchedule
from .envelope import Envelope

########################################################################
## PUBLIC API
########################################################################

# DESIGN CHOICE: Alphabetical ordering in public API for consistent
# interface presentation and predictable imports.
__all__ = [
    "Bill",
    "BillInstance",
    "CashFlow",
    "CashFlowSchedule",
    "Envelope",
]