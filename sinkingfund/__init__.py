"""
Sinking Fund Library
====================

A comprehensive Python library for systematic bill payment planning
using envelope-based sinking fund methodology. Provides sophisticated
fund allocation, contribution scheduling, and cash flow analysis for
personal financial management.

Quick Start
-----------

.. code-block:: python

   from datetime import date
   from decimal import Decimal
   
   from sinkingfund import SinkingFund

   # Create sinking fund for annual planning.
   fund = SinkingFund(
       start_date=date(2024, 1, 1),
       end_date=date(2024, 12, 31),
       balance=Decimal("10000.00")
   )

   # Complete workflow.
   fund.load_bills("bills.csv")
   fund.setup_envelopes(contrib_interval=14)
   fund.allocate_funds(strategy="sorted")

   # Analysis and reporting.
   projection = fund.get_cash_flow_projection()
   status = fund.get_funding_status()
   summary = fund.get_allocation_summary()

"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

# BUSINESS GOAL: Provide simple, intuitive API for sinking fund
# management while maintaining access to advanced components.

# Main integration interface.
from .models import (
    Bill, 
    BillInstance, 
    Envelope, 
    CashFlow, 
    CashFlowSchedule,
    SinkingFund
)

# Managers for advanced usage.
from .managers import (
    AllocationManager, 
    BillManager, 
    EnvelopeManager, 
    ScheduleManager
)

# Allocation strategies for custom workflows.
from .allocation import (
    ProportionalAllocator, 
    SortedAllocator
)

# Schedulers for advanced scheduling.
from .schedules import IndependentScheduler

# Utilities for specialized use cases.
from .utils import increment_date, load_bill_data_from_file

########################################################################
## PUBLIC API
########################################################################

# DESIGN CHOICE: Organize API by user journey. Most users start with
# SinkingFund, then may need models, then advanced components.
__all__ = [
    # Primary interface. Most users only need this.
    "SinkingFund",
    
    # Core models. For custom workflows.
    "Bill",
    "BillInstance", 
    "Envelope",
    "CashFlow",
    "CashFlowSchedule",
    
    # Advanced components. For power users.
    "AllocationManager",
    "BillManager", 
    "EnvelopeManager",
    "ScheduleManager",
    "ProportionalAllocator",
    "SortedAllocator", 
    "IndependentScheduler",
    
    # Utilities.
    "increment_date",
    "load_bill_data_from_file",
]