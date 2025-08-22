Examples
========

This section provides practical examples of using the Sinking Fund library.
Examples are derived from Jupyter notebooks to ensure they work correctly
with the actual codebase.

Notebook-Based Examples
-----------------------

Examples are maintained as Jupyter notebooks in the ``examples/`` directory
of the repository. This ensures:

- **Tested Code**: All examples are executable and verified to work
- **Interactive Exploration**: You can modify and experiment with the code
- **Up-to-Date**: Examples automatically reflect the current API

Available Example Notebooks
---------------------------

The following notebooks are available in the ``examples/`` directory:

**Core Functionality**

- ``sinkingfund.ipynb`` - Introduction to the main SinkingFund class
- ``load_bills.ipynb`` - Loading bill data from files
- ``load_envelopes.ipynb`` - Working with envelope collections

**Scheduling and Allocation**

- ``independent_scheduler.ipynb`` - Using the IndependentScheduler
- ``sorted_allocation.ipynb`` - Allocation strategies and priority handling

**Sample Data**

The ``examples/data/`` directory contains sample CSV files for testing:

- ``boa_fund.csv`` - Bank of America fund data
- ``boa_fund_2.csv`` - Additional BOA fund examples  
- ``schwab_fund.csv`` - Charles Schwab fund data

Creating Your Own Examples
--------------------------

To contribute examples:

1. Create a new Jupyter notebook in the ``examples/`` directory
2. Include clear explanations and working code
3. Test thoroughly to ensure compatibility with the current API
4. Submit as part of a pull request

Basic Usage Pattern
-------------------

For immediate reference, here's the basic import and usage pattern:

.. code-block:: python

   from sinkingfund import Bill
   from datetime import date
   
   # Create a bill
   bill = Bill(
       bill_id="example",
       service="Example Bill",
       amount_due=100.00,
       recurring=False,
       start_date=date(2025, 1, 15)
   )
   
   print(f"Created: {bill.service}")

For comprehensive examples, refer to the Jupyter notebooks in the
``examples/`` directory of the repository.
