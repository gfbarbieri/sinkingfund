User Guide
==========

This guide walks you through the core concepts and workflows of the
Sinking Fund library for digital envelope budgeting.

Core Concepts
-------------

Digital Envelope Budgeting
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Digital envelope budgeting is a money management method where you
allocate funds to virtual "envelopes" for specific expenses. This
library automates the process for bills and recurring expenses.

Bills and Bill Instances
~~~~~~~~~~~~~~~~~~~~~~~~

- **Bill**: A template representing a recurring or one-time expense
- **BillInstance**: A specific occurrence of a bill with a due date

Envelopes
~~~~~~~~~

Envelopes represent targeted savings accounts for specific bills.
Each envelope tracks:

- Target amount (from the bill)
- Current balance
- Contribution schedule

Cash Flow Schedules
~~~~~~~~~~~~~~~~~~~

Cash flow schedules define when and how much to contribute to each
envelope to reach the target amount by the due date.

Basic Workflow
--------------

The SinkingFund class provides a unified API for the complete workflow. Here's
how to use it:

1. Create Your Sinking Fund
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Start by creating a SinkingFund with your planning period and initial
balance:

.. code-block:: python

   from sinkingfund import SinkingFund
   from datetime import date
   
   # Create sinking fund for 2025 with $5,000 initial balance.
   fund = SinkingFund(
       start_date=date(2025, 1, 1),
       end_date=date(2025, 12, 31),
       balance=5000.00
   )

2. Add Your Bills
~~~~~~~~~~~~~~~~~

Define and add your bills. The `add_bills()` method accepts a list of bills,
a single bill dictionary, or a file path. Envelopes are automatically
created for bill instances in the planning period:

.. code-block:: python

   # Option 1: Load multiple bills at once.
   bills = [
       {
           "bill_id": "auto_insurance",
           "service": "Auto Insurance",
           "amount_due": 450.00,
           "recurring": True,
           "start_date": date(2025, 3, 15),
           "frequency": "quarterly"
       },
       {
           "bill_id": "property_tax",
           "service": "Property Tax",
           "amount_due": 2400.00,
           "recurring": True,
           "start_date": date(2025, 12, 1),
           "frequency": "annual"
       }
   ]
   fund.add_bills(bills)
   
   # Option 2: Add a single bill (automatically creates envelopes).
   fund.add_bills({
       "bill_id": "electric",
       "service": "Electric Bill",
       "amount_due": 150.00,
       "recurring": True,
       "start_date": date(2025, 1, 1),
       "frequency": "monthly"
   })
   
   # Option 3: Add from a CSV/Excel/JSON file.
   # fund.add_bills("bills.csv")

3. Generate Your Report
~~~~~~~~~~~~~~~~~~~~~~~

The easiest way is to use `quick_report()` which does everything in one
call:

.. code-block:: python

   # Generate complete report with bi-weekly contributions.
   report = fund.quick_report(contribution_interval=14, active_only=True)
   
   # The report shows daily account balances, contributions, and payouts.
   for date, data in list(report.items())[:5]:
       print(f"{date}: Balance=${data['account_balance']['total']}, "
             f"Contributions=${data['contributions']['total']}")

4. Manual Workflow (Optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For more control, you can perform each step manually:

.. code-block:: python

   # Note: Envelopes are automatically created by add_bills().
   # If you need to manually create envelopes, get bill instances first.
   instances = fund.get_bill_instances()
   fund.create_envelopes(instances)
   
   # Allocate funds using sorted strategy.
   fund.allocate(strategy="sorted", sort_key="cascade")
   
   # Set contribution dates (bi-weekly).
   fund.update_contribution_dates(contribution_interval=14)
   
   # Create schedules.
   fund.schedule(strategy="independent_scheduler")
   
   # Generate report.
   report = fund.report(active_only=True)
   
   # Access envelopes for detailed tracking.
   envelopes = fund.get_envelopes()
   for envelope in envelopes:
       print(f"{envelope.bill_instance.service}: "
             f"${envelope.initial_allocation} allocated")

Advanced Features
-----------------

Loading Bills from Files
~~~~~~~~~~~~~~~~~~~~~~~~~

The SinkingFund API supports loading bills directly from files:

.. code-block:: python

   from sinkingfund import SinkingFund
   from datetime import date
   
   fund = SinkingFund(
       start_date=date(2025, 1, 1),
       end_date=date(2025, 12, 31),
       balance=5000.00
   )
   
   # Add from CSV, Excel, or JSON files.
   fund.add_bills("bills.csv")
   # or
   fund.add_bills("bills.xlsx")
   # or
   fund.add_bills("bills.json")

Allocation Strategies
~~~~~~~~~~~~~~~~~~~~~

Use different allocation strategies when allocating funds:

.. code-block:: python

   # Sorted allocation (priority-based, earliest due date first).
   fund.allocate(strategy="sorted", sort_key="cascade")
   
   # Proportional allocation (distribute proportionally by amount).
   fund.allocate(strategy="proportional", method="proportional")
   
   # Debt snowball (smallest amount first).
   fund.allocate(strategy="sorted", sort_key="debt_snowball", reverse=False)

Managing Bills and Envelopes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can add, update, and delete bills with automatic envelope management:

.. code-block:: python

   # Add a new bill (automatically creates envelopes).
   fund.add_bills({
       "bill_id": "water",
       "service": "Water Bill",
       "amount_due": 75.00,
       "recurring": True,
       "start_date": date(2025, 2, 1),
       "frequency": "monthly"
   })
   
   # Update an existing bill (recreates envelopes).
   fund.update_bill("electric", {"amount_due": 175.00})
   
   # Delete a bill and its envelopes.
   fund.delete_bills(["old_bill"])
   
   # Delete a bill but keep envelopes (if needed).
   fund.delete_bills(["temp_bill"], remove_envelopes=False)

Accessing Envelopes
~~~~~~~~~~~~~~~~~~~

You can access envelopes to track detailed progress:

.. code-block:: python

   # Get all envelopes.
   envelopes = fund.get_envelopes()
   
   # Get a specific envelope.
   envelope = fund.get_envelope(
       bill_id="property_tax",
       due_date=date(2025, 11, 1)
   )
   
   if envelope:
       print(f"Allocated: ${envelope.initial_allocation}")
       print(f"Remaining: ${envelope.remaining_amount}")
       print(f"Fully funded: {envelope.is_fully_funded}")

.. note::
   For advanced use cases requiring direct access to managers, allocation
   strategies, or schedulers, see the :doc:`api_reference`. These components
   are internal implementation details and most users should interact with
   them through the SinkingFund API.

Best Practices
--------------

1. **Start Early**: Begin contributing to envelopes well before due dates
2. **Regular Reviews**: Check envelope balances monthly
3. **Adjust as Needed**: Update contribution amounts based on actual income
4. **Track Everything**: Use the cash flow schedules to monitor progress
5. **Plan Ahead**: Create envelopes for bills 3-6 months in advance

Updating Balance and Regenerating Reports
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can update your balance and regenerate reports with different options:

.. code-block:: python

   # Update balance after receiving funds.
   fund.update_balance(6000.00)
   
   # Option 1: Regenerate report using quick_report with new settings.
   report = fund.quick_report(
       allocation_strategy="proportional",
       contribution_interval=7,
       active_only=True
   )
   
   # Option 2: Manual workflow - allocate with new balance, then regenerate.
   fund.allocate(strategy="sorted")
   fund.update_contribution_dates(contribution_interval=7)
   fund.schedule(strategy="independent_scheduler")
   report = fund.report(active_only=True)

State Management
~~~~~~~~~~~~~~~~

Keep your sinking fund state consistent:

.. code-block:: python

   # Validate state consistency.
   is_valid, issues = fund.validate_state()
   if not is_valid:
       for issue in issues:
           print(f"Issue: {issue}")
   
   # Sync envelopes with bills (removes orphaned envelopes).
   fund.sync_envelopes_with_bills()

Common Patterns
---------------

Monthly Budget Review
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from sinkingfund import SinkingFund
   from datetime import date
   
   fund = SinkingFund(
       start_date=date(2025, 1, 1),
       end_date=date(2025, 12, 31),
       balance=5000.00
   )
   fund.add_bills("bills.csv")
   fund.quick_report()
   
   # Get all envelopes that need funding.
   envelopes = fund.get_envelopes()
   underfunded = [
       env for env in envelopes 
       if not env.is_fully_funded
   ]
   
   # Calculate total shortfall.
   total_needed = sum(env.remaining_amount for env in underfunded)
   
   print(f"Need ${total_needed} across {len(underfunded)} envelopes")

Quarterly Planning
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Generate report for the quarter.
   report = fund.report(active_only=True)
   
   # Filter for dates in the quarter.
   quarter_end = date(2025, 6, 30)
   quarter_dates = [
       d for d in report.keys() 
       if d <= quarter_end
   ]
   
   # Analyze quarterly contributions and payouts.
   quarter_contribs = sum(
       report[d]['contributions']['total'] 
       for d in quarter_dates
   )
   quarter_payouts = sum(
       report[d]['payouts']['total'] 
       for d in quarter_dates
   )
   
   print(f"Q2 Contributions: ${quarter_contribs}")
   print(f"Q2 Payouts: ${quarter_payouts}")

This guide provides the foundation for effective sinking fund management.
For detailed API documentation, see the :doc:`api_reference`.
