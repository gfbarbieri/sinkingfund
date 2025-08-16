"""
Manager Package
===============

The managers package provides high-level coordination classes that
orchestrate complex operations across the sinking fund system. These
managers implement the manager pattern to encapsulate business logic,
validation, and workflow coordination while maintaining clean separation
of concerns from core domain models.

Core Abstractions
-----------------

**Management Coordination**: Each manager specializes in a specific
aspect of sinking fund operations, providing focused interfaces for
complex workflows while abstracting implementation details from client
code.

**Cross-Component Integration**: Managers coordinate between multiple
domains (bills, envelopes, allocations, schedules) to implement
high-level business processes that span system boundaries.

**Validation and Error Handling**: Centralized validation logic with
comprehensive error checking, clear error messages, and graceful
failure modes to ensure data integrity and user feedback.

Key Components
--------------

- **AllocationManager**: Orchestrates fund distribution across envelope
  collections using pluggable allocation strategies.
- **BillManager**: Coordinates bill lifecycle operations including
  creation, validation, storage, and instance generation.
- **EnvelopeManager**: Manages envelope operations including creation,
  contribution scheduling, and duplicate prevention.
- **ScheduleManager**: Controls cash flow scheduling and timeline
  generation for systematic fund management.

Examples
--------

Integrated sinking fund workflow:

.. code-block:: python

   from datetime import date
   from decimal import Decimal
   from sinkingfund.managers import (
       BillManager, EnvelopeManager, AllocationManager
   )

   # Load and manage bills.
   bill_manager = BillManager()
   bills = bill_manager.create_bills("bills.csv")
   bill_manager.add_bills(bills)

   # Generate bill instances for planning period.
   instances = bill_manager.active_instances_in_range(
       start_reference=date(2024, 1, 1),
       end_reference=date(2024, 12, 31)
   )

   # Create and configure envelopes.
   envelope_manager = EnvelopeManager()
   envelopes = envelope_manager.create_envelopes(instances)
   envelope_manager.add_envelopes(envelopes)
   envelope_manager.set_contrib_dates(
       start_contrib_date=date(2024, 1, 1),
       contrib_interval=14
   )

   # Allocate available funds.
   allocation_manager = AllocationManager(strategy="sorted")
   allocation_manager.allocate(
       envelopes=envelope_manager.envelopes,
       balance=Decimal("5000.00")
   )

Specialized manager usage:

.. code-block:: python

   # Bill management with validation.
   bill_manager = BillManager()
   try:
       bills = bill_manager.create_bills(bill_data)
       bill_manager.add_bills(bills)
   except ValueError as e:
       print(f"Bill validation failed: {e}")

   # Envelope scheduling with business rules.
   envelope_manager = EnvelopeManager()
   envelope_manager.set_contrib_dates(
       start_contrib_date=date(2024, 1, 15),
       contrib_interval=7
   )
   # Non-overlapping contribution periods automatically assigned.

   # Flexible allocation strategies.
   proportional_manager = AllocationManager(
       strategy="proportional",
       min_allocation=Decimal("25.00")
   )
   proportional_manager.allocate(
       envelopes=envelopes,
       balance=available_funds,
       target_months=6
   )
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

# BUSINESS GOAL: Provide high-level coordination classes for complex
# sinking fund operations with clean separation of concerns.
from .allocation_manager import AllocationManager
from .bill_manager import BillManager
from .envelope_manager import EnvelopeManager
from .schedule_manager import ScheduleManager

########################################################################
## PUBLIC API
########################################################################

# DESIGN CHOICE: Explicit public API definition ensures controlled
# interface exposure and clear module boundaries.
__all__ = [
    "AllocationManager",
    "BillManager",
    "EnvelopeManager",
    "ScheduleManager",
]