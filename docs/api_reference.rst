API Reference
=============

This section provides detailed documentation for all public APIs in the
Sinking Fund library.

Quick Reference
---------------

Core Classes
~~~~~~~~~~~~

.. list-table:: Essential Classes
   :header-rows: 1
   :widths: 25 75

   * - Class
     - Purpose
   * - :class:`~sinkingfund.models.Bill`
     - Represents a financial obligation template
   * - :class:`~sinkingfund.models.BillInstance`  
     - Specific occurrence of a bill with due date
   * - :class:`~sinkingfund.models.Envelope`
     - Digital envelope for targeted savings
   * - :class:`~sinkingfund.models.CashFlow`
     - Individual monetary transaction
   * - :class:`~sinkingfund.models.CashFlowSchedule`
     - Collection of cash flows over time
   * - :class:`~sinkingfund.models.SinkingFund`
     - Main orchestrator class

Manager Classes
~~~~~~~~~~~~~~~

.. list-table:: Management Classes
   :header-rows: 1
   :widths: 25 75

   * - Class
     - Purpose
   * - :class:`~sinkingfund.managers.BillManager`
     - Manages collections of bills
   * - :class:`~sinkingfund.managers.EnvelopeManager`
     - Manages collections of envelopes  
   * - :class:`~sinkingfund.managers.AllocationManager`
     - Coordinates fund allocation strategies
   * - :class:`~sinkingfund.managers.ScheduleManager`
     - Manages contribution scheduling

Allocation Strategies
~~~~~~~~~~~~~~~~~~~~~

.. list-table:: Allocation Algorithms
   :header-rows: 1
   :widths: 25 75

   * - Class
     - Strategy
   * - :class:`~sinkingfund.allocation.ProportionalAllocator`
     - Proportional allocation based on need
   * - :class:`~sinkingfund.allocation.SortedAllocator`
     - Priority-based allocation (waterfall, snowball)

Utility Functions
~~~~~~~~~~~~~~~~~

.. list-table:: Utility Modules
   :header-rows: 1
   :widths: 25 75

   * - Module
     - Purpose
   * - :mod:`~sinkingfund.utils.date_utils`
     - Calendar-aware date arithmetic
   * - :mod:`~sinkingfund.utils.loaders`
     - High-level data loading from files
   * - :mod:`~sinkingfund.utils.readers`
     - Low-level file format readers
   * - :mod:`~sinkingfund.utils.format_registry`
     - File format configuration
   * - :mod:`~sinkingfund.utils.file_utils`
     - File detection and path utilities

Detailed Documentation
----------------------

The following sections provide comprehensive API documentation for each
package in the library:

.. toctree::
   :maxdepth: 2

   api/models
   api/managers  
   api/allocation
   api/schedules
   api/utils

Common Usage Patterns
---------------------

Import Patterns
~~~~~~~~~~~~~~~

.. code-block:: python

   # Core models
   from sinkingfund import Bill, Envelope, CashFlow, SinkingFund
   
   # Managers for collections
   from sinkingfund.managers import (
       BillManager, EnvelopeManager, AllocationManager
   )
   
   # Allocation strategies
   from sinkingfund.allocation import (
       ProportionalAllocator, SortedAllocator
   )
   
   # Scheduling
   from sinkingfund.schedules import IndependentScheduler
   
   # Utilities
   from sinkingfund.utils import load_bill_data_from_file
   from sinkingfund.utils.date_utils import increment_date

Type Hints
~~~~~~~~~~

The library uses comprehensive type hints for better IDE support:

.. code-block:: python

   from sinkingfund import Bill, Envelope
   from decimal import Decimal
   from datetime import date
   from typing import List
   
   def create_envelopes(bills: List[Bill]) -> List[Envelope]:
       envelopes: List[Envelope] = []
       for bill in bills:
           instance = bill.next_instance()
           if instance:
               envelope = Envelope(
                   bill_instance=instance,
                   initial_allocation=Decimal("0.00"),
                   start_contrib_date=date.today(),
                   end_contrib_date=instance.due_date
               )
               envelopes.append(envelope)
       return envelopes

Error Handling
~~~~~~~~~~~~~~

The library uses specific exception types for different error conditions:

.. code-block:: python

   try:
       bill = Bill(
           bill_id="invalid",
           service="Test",
           amount_due=-100.00,  # Invalid negative amount
           recurring=False,
           start_date=date(2025, 1, 1)
       )
   except ValueError as e:
       print(f"Invalid bill configuration: {e}")
   
   try:
       data = load_bill_data_from_file("nonexistent.csv")
   except FileNotFoundError as e:
       print(f"File not found: {e}")

Performance Considerations
~~~~~~~~~~~~~~~~~~~~~~~~~~

For large collections of bills and envelopes:

- Use manager classes for efficient batch operations
- Consider date ranges when querying bill instances  
- Cache allocation results when processing multiple scenarios
- Use decimal arithmetic for precise monetary calculations
