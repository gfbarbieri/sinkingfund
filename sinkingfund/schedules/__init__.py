"""
Schedule Package
================

The schedules package provides sophisticated cash flow scheduling
algorithms for sinking fund management. These schedulers implement
advanced optimization strategies to systematically coordinate envelope
funding schedules, ensuring optimal cash flow distribution and timing
for meeting payment obligations.

Core Abstractions
-----------------

**Schedule Optimization**: Advanced algorithms that analyze envelope
collections and generate optimized cash flow schedules to minimize
funding gaps while respecting contribution constraints and timing
requirements.

**Cash Flow Coordination**: Intelligent scheduling that considers
inter-envelope dependencies, contribution frequencies, and payment
deadlines to create cohesive funding timelines.

**Strategy Implementation**: Pluggable scheduling algorithms with
different optimization approaches (independent scheduling, constraint
optimization, priority-based allocation) for diverse use cases.

Key Components
--------------

- **IndependentScheduler**: Generates cash flow schedules for envelope
  collections using independent per-envelope optimization, suitable
  for straightforward scheduling scenarios without complex dependencies.

Scheduling Concepts
-------------------

**Independent Scheduling**: Each envelope receives an optimized cash
flow schedule computed independently of other envelopes. This approach
works well when envelopes have distinct contribution patterns and
minimal interdependencies.

**Constraint-Based Optimization**: Future schedulers may implement
advanced constraint satisfaction to handle complex scenarios with
shared funding sources, contribution limits, and timing dependencies.

Examples
--------

Basic envelope scheduling:

.. code-block:: python

   from datetime import date
   from decimal import Decimal
   from sinkingfund.schedules import IndependentScheduler
   from sinkingfund.models import Envelope, BillInstance

   # Create envelope collection.
   envelopes = [
       Envelope(
           bill_instance=BillInstance(
               bill_id="electric",
               amount_due=Decimal("150.00"),
               due_date=date(2024, 6, 15)
           ),
           start_contrib_date=date(2024, 1, 1),
           contrib_interval=14
       ),
       Envelope(
           bill_instance=BillInstance(
               bill_id="insurance",
               amount_due=Decimal("300.00"),
               due_date=date(2024, 7, 1)
           ),
           start_contrib_date=date(2024, 1, 1),
           contrib_interval=7
       )
   ]

   # Generate optimized schedules.
   scheduler = IndependentScheduler()
   schedule_dict = {}
   scheduler.schedule(envelopes, schedule_dict)

   # Access generated cash flow schedules.
   for envelope, schedule in schedule_dict.items():
       print(f"Envelope {envelope.bill_instance.bill_id}:")
       for flow in schedule.cash_flows:
           print(f"  {flow.flow_date}: ${flow.amount}")

Advanced scheduling with configuration:

.. code-block:: python

   # Create scheduler with custom configuration.
   scheduler = IndependentScheduler()
   
   # Generate schedules with envelope modifications in-place
   schedule_results = {}
   scheduler.schedule(envelope_collection, schedule_results)
   
   # Analyze scheduling results.
   total_contributions = sum(
       schedule.total_amount() for schedule in schedule_results.values()
   )
   
   # Validate schedule feasibility.
   for envelope, schedule in schedule_results.items():
       if envelope.is_fully_funded:
           print(f"Envelope {envelope.bill_instance.bill_id} fully funded")
       else:
           remaining = envelope.remaining_amount
           print(f"Envelope needs ${remaining} more.")
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

# BUSINESS GOAL: Provide advanced cash flow scheduling algorithms
# for optimized sinking fund management and payment coordination.
from .indep_scheduler import IndependentScheduler

########################################################################
## PUBLIC API
########################################################################

# DESIGN CHOICE: Explicit public API ensures controlled exposure
# of scheduling algorithms and clear module interface.
__all__ = [
    "IndependentScheduler",
]