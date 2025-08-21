Sinking Fund Documentation
===========================

A Python library for digital envelope budgeting and sinking fund management,
providing automated savings allocation, bill scheduling, and cash flow
optimization for personal financial planning.

Overview
--------

The Sinking Fund library implements digital envelope budgeting patterns
to help users systematically save for future expenses. It provides:

* **Automated Allocation**: Distribute available funds across multiple
  savings envelopes based on configurable strategies.
* **Bill Scheduling**: Track recurring and one-time bills with calendar-aware
  date arithmetic.
* **Cash Flow Planning**: Project future account balances and optimize
  contribution timing.
* **Data Integration**: Load bill definitions from CSV, Excel, and JSON files
  with robust data validation.

Quick Start
-----------

Install the package and create your first envelope:

.. code-block:: python

   from sinkingfund import Bill, Envelope
   from datetime import date
   from decimal import Decimal

   # Create a quarterly insurance bill
   insurance = Bill(
       bill_id="auto_insurance",
       service="Quarterly Auto Insurance",
       amount_due=450.00,
       recurring=True,
       start_date=date(2025, 1, 15),
       frequency="quarterly"
   )

   # Create an envelope to save for it
   envelope = Envelope(
       bill_instance=insurance.next_instance(),
       initial_allocation=Decimal("100.00"),
       start_contrib_date=date(2025, 1, 1),
       end_contrib_date=date(2025, 3, 14)
   )

   # Check funding status
   print(f"Remaining to save: ${envelope.remaining()}")
   print(f"Fully funded: {envelope.is_fully_funded()}")

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   user_guide
   api_reference
   examples
   testing

API Reference
-------------

.. toctree::
   :maxdepth: 3
   :caption: API Documentation:

   api/models
   api/managers
   api/allocation
   api/schedules
   api/utils

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

