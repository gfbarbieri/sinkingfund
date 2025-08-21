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

1. Define Your Bills
~~~~~~~~~~~~~~~~~~~~

Start by creating bills for your recurring expenses:

.. code-block:: python

   from sinkingfund import Bill
   from datetime import date
   
   # Quarterly insurance
   insurance = Bill(
       bill_id="auto_insurance",
       service="Auto Insurance",
       amount_due=450.00,
       recurring=True,
       start_date=date(2025, 3, 15),
       frequency="quarterly"
   )
   
   # Annual property tax
   property_tax = Bill(
       bill_id="property_tax",
       service="Property Tax",
       amount_due=2400.00,
       recurring=True,
       start_date=date(2025, 12, 1),
       frequency="yearly"
   )

2. Create Envelopes
~~~~~~~~~~~~~~~~~~~

Create savings envelopes for upcoming bill instances:

.. code-block:: python

   from sinkingfund import Envelope
   from decimal import Decimal
   
   # Get the next insurance bill
   next_insurance = insurance.next_instance()
   
   # Create envelope for it
   insurance_envelope = Envelope(
       bill_instance=next_insurance,
       initial_allocation=Decimal("50.00"),
       start_contrib_date=date(2025, 1, 1),
       end_contrib_date=date(2025, 3, 14)
   )

3. Generate Contribution Schedules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create schedules to determine when and how much to save:

.. code-block:: python

   from sinkingfund.schedules import IndependentScheduler
   
   scheduler = IndependentScheduler()
   
   # Generate contribution schedule
   scheduler.schedule([insurance_envelope])
   
   # Check the schedule
   schedule = insurance_envelope.schedule
   total_needed = schedule.total_amount_as_of_date(date(2025, 3, 14))
   print(f"Total contributions needed: ${total_needed}")

4. Track Progress
~~~~~~~~~~~~~~~~~

Monitor your envelope funding progress:

.. code-block:: python

   # Check current status
   remaining = insurance_envelope.remaining()
   fully_funded = insurance_envelope.is_fully_funded()
   
   print(f"Remaining to save: ${remaining}")
   print(f"Fully funded: {fully_funded}")
   
   # Get balance on a specific date
   balance = insurance_envelope.get_balance_as_of_date(date(2025, 2, 15))
   print(f"Balance on Feb 15: ${balance}")

Advanced Features
-----------------

Loading Bills from Files
~~~~~~~~~~~~~~~~~~~~~~~~~

Load bill definitions from CSV, Excel, or JSON files:

.. code-block:: python

   from sinkingfund.utils import load_bill_data_from_file
   
   # Load from CSV
   bills_data = load_bill_data_from_file("bills.csv")
   
   # Convert to Bill objects
   bills = [Bill(**bill_data) for bill_data in bills_data]

Allocation Strategies
~~~~~~~~~~~~~~~~~~~~~

Use different strategies to allocate available funds across envelopes:

.. code-block:: python

   from sinkingfund.allocation import ProportionalAllocator
   from sinkingfund.managers import AllocationManager
   from decimal import Decimal
   
   # Create allocator
   allocator = ProportionalAllocator()
   manager = AllocationManager(allocator)
   
   # Allocate $500 across all envelopes
   available_funds = Decimal("500.00")
   result = manager.allocate(envelopes, available_funds)
   
   print(f"Allocated to {len(result.envelopes)} envelopes")

Multiple Envelope Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Manage collections of envelopes efficiently:

.. code-block:: python

   from sinkingfund.managers import EnvelopeManager, BillManager
   
   # Create managers
   bill_manager = BillManager()
   envelope_manager = EnvelopeManager()
   
   # Add bills
   bill_manager.add_bills([insurance, property_tax])
   
   # Create envelopes for upcoming bills
   upcoming_bills = bill_manager.get_upcoming_instances(
       start_date=date(2025, 1, 1),
       end_date=date(2025, 12, 31)
   )
   
   # Convert to envelopes
   for bill_instance in upcoming_bills:
       envelope = Envelope(
           bill_instance=bill_instance,
           initial_allocation=Decimal("0.00"),
           start_contrib_date=date(2025, 1, 1),
           end_contrib_date=bill_instance.due_date
       )
       envelope_manager.add_envelope(envelope)

Best Practices
--------------

1. **Start Early**: Begin contributing to envelopes well before due dates
2. **Regular Reviews**: Check envelope balances monthly
3. **Adjust as Needed**: Update contribution amounts based on actual income
4. **Track Everything**: Use the cash flow schedules to monitor progress
5. **Plan Ahead**: Create envelopes for bills 3-6 months in advance

Common Patterns
---------------

Monthly Budget Review
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get all envelopes that need funding
   underfunded = [env for env in envelopes if not env.is_fully_funded()]
   
   # Calculate total shortfall
   total_needed = sum(env.remaining() for env in underfunded)
   
   print(f"Need ${total_needed} across {len(underfunded)} envelopes")

Quarterly Planning
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get all bills due in next quarter
   quarter_end = date(2025, 6, 30)
   upcoming = bill_manager.get_bills_due_by(quarter_end)
   
   # Create planning report
   for bill in upcoming:
       envelope = envelope_manager.get_envelope_for_bill(bill.bill_id)
       if envelope:
           print(f"{bill.service}: ${envelope.remaining()} remaining")

This guide provides the foundation for effective sinking fund management.
For detailed API documentation, see the :doc:`api_reference`.
