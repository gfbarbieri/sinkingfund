"""
Allocation Package
==================

The allocation package provides sophisticated fund distribution algorithms
for envelope-based sinking fund management. These allocation strategies
implement diverse mathematical approaches to optimize fund distribution
across payment envelopes, enabling systematic and strategic financial
planning based on different optimization criteria and priorities.

Core Abstractions
-----------------

**Strategy Pattern Implementation**: All allocation algorithms implement
a common interface (BaseAllocator) enabling interchangeable distribution
strategies without modifying client code. This supports flexible
financial planning approaches based on changing priorities and goals.

**Mathematical Optimization**: Each strategy employs distinct mathematical
models for fund distribution including proportional weighting, priority
ordering, constraint satisfaction, and multi-criteria optimization to
achieve specific financial objectives.

**Envelope-Centric Design**: Allocation algorithms operate directly on
envelope collections, modifying funding levels in-place while respecting
envelope constraints, contribution schedules, and payment deadlines.

**Validation and Safety**: Comprehensive input validation, constraint
checking, and error handling ensure allocation integrity and provide
clear feedback for invalid scenarios or constraint violations.

Key Components
--------------

- **BaseAllocator**: Abstract base class defining the common interface
  for all allocation strategies with consistent method signatures and
  validation requirements.
- **SortedAllocator**: Priority-based allocation using envelope ordering
  criteria such as due dates, amounts, or custom sorting functions for
  systematic waterfall distribution.
- **ProportionalAllocator**: Mathematical proportional distribution
  based on funding needs, bill amounts, or time-based weighting with
  configurable minimum allocation thresholds.

Allocation Strategies
---------------------

**Sorted (Priority-Based) Allocation**:
- Waterfall distribution based on envelope ordering criteria.
- Supports due date priority, amount-based sorting, custom comparisons.
- Ensures urgent obligations receive funding priority.
- Optimal for deadline-driven financial planning.

**Proportional (Mathematical) Allocation**:
- Distribution proportional to funding needs or bill amounts.
- Configurable weighting factors and minimum allocation limits.
- Ensures all envelopes receive proportionate funding.
- Optimal for balanced financial approach across obligations.

**Future Strategies**:
- Constraint-based optimization with resource limits.
- Multi-criteria decision analysis for complex scenarios.
- Dynamic rebalancing based on changing priorities.

Examples
--------

Basic allocation workflow:

.. code-block:: python

   from decimal import Decimal
   from sinkingfund.allocation import SortedAllocator, ProportionalAllocator
   from sinkingfund.models import Envelope

   # Create allocation strategies.
   waterfall_allocator = SortedAllocator()
   proportional_allocator = ProportionalAllocator(
       min_allocation=Decimal("10.00")
   )

   # Available funds for distribution.
   available_balance = Decimal("1000.00")
   
   # Priority-based allocation (earliest due dates first).
   waterfall_allocator.allocate(
       envelopes=envelope_collection, balance=available_balance
   )
   
   # Reset and try proportional allocation.
   for envelope in envelope_collection:
       envelope.current_balance = Decimal("0.00")
   
   proportional_allocator.allocate(
       envelopes=envelope_collection, balance=available_balance
   )
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

# BUSINESS GOAL: Provide flexible fund distribution algorithms for
# systematic envelope-based financial planning and optimization.
from .proportional import ProportionalAllocator
from .sorted import SortedAllocator

########################################################################
## PUBLIC API
########################################################################

# DESIGN CHOICE: Alphabetical ordering in public API ensures consistent
# interface presentation and predictable import behavior.
__all__ = [
    "ProportionalAllocator", 
    "SortedAllocator",
]
