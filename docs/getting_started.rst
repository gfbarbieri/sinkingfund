Getting Started
===============

.. _getting-started-section:

This guide will help you get started with the Sinking Fund library. We'll
cover installation, understanding data input requirements, and walk
through a quick example to get you up and running.

Installation
------------

Basic Installation
~~~~~~~~~~~~~~~~~~

The Sinking Fund library has no required dependencies beyond Python 3.12+.
Install it using pip:

.. code-block:: bash

   pip install sinkingfund

With Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For enhanced functionality, you can install optional dependencies:

**Data Analysis and Plotting**

.. code-block:: bash

   pip install sinkingfund[analysis]  # pandas, matplotlib

**Jupyter Notebook Support**

.. code-block:: bash

   pip install sinkingfund[notebooks]  # ipykernel, jupyter

**Everything**

.. code-block:: bash

   pip install sinkingfund[all]

Development Installation
~~~~~~~~~~~~~~~~~~~~~~~~

For development or to contribute:

.. code-block:: bash

   git clone https://github.com/gfbarbieri/sinkingfund.git
   cd sinkingfund
   poetry install --with dev,analysis,notebook

For more detailed installation instructions, see :doc:`installation`.

Data Input and Data Structure
------------------------------

Understanding Bills
~~~~~~~~~~~~~~~~~~~

The foundation of sinking fund planning is defining your bills. A bill
represents a financial obligation that you need to save for. Bills can be
either one-time expenses or recurring obligations.

Bill Definition Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~

When defining bills, you need to specify:

- **bill_id**: A unique identifier for the bill (e.g., "auto_insurance").

- **service**: A descriptive name for the bill (e.g., "Quarterly Auto
  Insurance").

- **amount_due**: The amount of money required for this bill.

- **recurring**: Whether the bill repeats over time (True) or is a
  one-time expense (False).

For **one-time bills**, you also need:

- **due_date**: The date when the bill is due.

For **recurring bills**, you need:

- **start_date**: The date of the first occurrence.

- **frequency**: How often the bill repeats. Valid values are:
  "daily", "weekly", "monthly", "quarterly", "annual".

- **interval**: The multiplier for the frequency (e.g., interval=2 with
  frequency="weekly" creates a bi-weekly bill). Defaults to 1.

- **end_date** or **occurrences**: Either specify when the bill stops
  recurring (end_date) or how many times it occurs (occurrences).

Programmatic Bill Definition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can define bills programmatically using dictionaries or Bill objects:

.. code-block:: python

   from datetime import date
   from sinkingfund import Bill

   # One-time bill.
   property_tax = Bill(
       bill_id="prop_tax",
       service="Property Tax",
       amount_due=3600.00,
       recurring=False,
       due_date=date(2025, 11, 1)
   )

   # Recurring monthly bill.
   car_insurance = Bill(
       bill_id="car_ins",
       service="Car Insurance",
       amount_due=750.00,
       recurring=True,
       start_date=date(2025, 4, 24),
       frequency="monthly",
       interval=6  # Every 6 months.
   )

File-Based Bill Loading
~~~~~~~~~~~~~~~~~~~~~~~

You can also load bills from CSV, Excel, or JSON files. The library
automatically detects the file format and parses it appropriately.

**CSV Format**

Required columns for CSV files:

- ``bill_id``: Unique identifier
- ``service``: Service name
- ``amount_due``: Amount (numeric)
- ``recurring``: Boolean (True/False)
- ``due_date``: Date (mm/dd/yyyy) for one-time bills
- ``start_date``: Date (mm/dd/yyyy) for recurring bills
- ``frequency``: One of "daily", "weekly", "monthly", "quarterly",
  "annual"
- ``interval``: Number (optional, defaults to 1)

Example CSV content:

.. code-block:: text

   bill_id,service,amount_due,recurring,start_date,frequency,interval
   auto_ins,Car Insurance,750.00,True,2025-04-24,monthly,6
   prop_tax,Property Tax,3600.00,False,2025-11-01,,,

**Loading from Files**

.. code-block:: python

   from sinkingfund import SinkingFund
   from datetime import date

   fund = SinkingFund(
       start_date=date(2025, 1, 1),
       end_date=date(2025, 12, 31),
       balance=5000.00
   )

   # Add bills from CSV.
   fund.add_bills("data/bills.csv")

   # Or add from Excel.
   fund.add_bills("data/bills.xlsx")

   # Or add from JSON.
   fund.add_bills("data/bills.json")

For more details on file formats and data loading, see the
:doc:`api/utils` section in the API reference.

Quick Example
-------------

Let's walk through a complete example that demonstrates the core workflow
of the Sinking Fund library. This example will:

1. Create a sinking fund for annual planning
2. Define bills for property tax and car insurance
3. Add bills (envelopes are automatically created)
4. Generate a complete report with allocation and scheduling

Complete Workflow Example
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from datetime import date
   from decimal import Decimal
   from sinkingfund import SinkingFund

   # Step 1: Create sinking fund for annual planning.
   fund = SinkingFund(
       start_date=date(2025, 1, 1),
       end_date=date(2025, 12, 31),
       balance=Decimal("5000.00")
   )

   # Step 2: Define bills.
   bills = [
       {
           "bill_id": "prop_tax",
           "service": "Property Tax",
           "amount_due": 3600.00,
           "recurring": True,
           "start_date": date(2025, 11, 1),
           "frequency": "annual",
           "interval": 1
       },
       {
           "bill_id": "car_ins",
           "service": "Car Insurance",
           "amount_due": 750.00,
           "recurring": True,
           "start_date": date(2025, 4, 24),
           "frequency": "monthly",
           "interval": 6  # Every 6 months.
       }
   ]

   # Step 3: Add bills to the fund (automatically creates envelopes).
   fund.add_bills(bills)

   # Step 4: Generate a quick report with default settings.
   # This automatically:
   # - Allocates available funds using sorted strategy.
   # - Sets contribution intervals to 14 days (bi-weekly).
   # - Creates contribution schedules.
   # - Generates daily account report.
   report = fund.quick_report(
       contribution_interval=14,
       active_only=True
   )

   # Step 5: Examine the report.
   # The report is a dictionary keyed by date.
   for report_date, daily_data in list(report.items())[:5]:
       print(f"\nDate: {report_date}")
       print(f"  Account Balance: ${daily_data['account_balance']['total']}")
       print(f"  Contributions: ${daily_data['contributions']['total']}")
       print(f"  Payouts: ${daily_data['payouts']['total']}")

Manual Workflow Example
~~~~~~~~~~~~~~~~~~~~~~~

For more control, you can perform each step manually:

.. code-block:: python

   from datetime import date
   from decimal import Decimal
   from sinkingfund import SinkingFund

   # Create sinking fund.
   fund = SinkingFund(
       start_date=date(2025, 1, 1),
       end_date=date(2025, 12, 31),
       balance=Decimal("5000.00")
   )

   # Add bills (automatically creates envelopes for bill instances).
   fund.add_bills([
       {
           "bill_id": "prop_tax",
           "service": "Property Tax",
           "amount_due": 3600.00,
           "recurring": True,
           "start_date": date(2025, 11, 1),
           "frequency": "annual"
       }
   ])

   # Note: Envelopes are automatically created by add_bills().
   # If you need to manually create envelopes, get bill instances first.
   instances = fund.get_bill_instances()
   fund.create_envelopes(instances)

   # Allocate funds using sorted strategy (priority-based by due date).
   fund.allocate(strategy="sorted", sort_key="cascade")

   # Set contribution dates (bi-weekly contributions).
   fund.update_contribution_dates(contribution_interval=14)

   # Create contribution schedules.
   fund.schedule(strategy="independent_scheduler")

   # Generate daily account report.
   report = fund.report(active_only=True)

Next Steps
----------

Now that you've completed the quick start, you're ready to explore more
advanced features:

- **Learn Core Concepts**: Understand the models, managers, schedules,
  and allocation strategies in detail. See :doc:`core_concepts`.

- **Explore Examples**: See practical examples for different use cases.
  See :doc:`examples`.

- **Review API Reference**: Dive deep into the API documentation for
  all classes and methods. See :doc:`api_reference`.

- **Customize Your Workflow**: Learn about different allocation
  strategies and scheduling options to optimize your financial planning.

