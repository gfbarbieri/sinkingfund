Examples
========

This section provides practical examples of using the Sinking Fund library
for common financial planning scenarios.

Example 1: Basic Quarterly Insurance
-------------------------------------

Save for a quarterly insurance bill with automated scheduling:

.. code-block:: python

   from sinkingfund import Bill, Envelope
   from sinkingfund.schedules import IndependentScheduler
   from datetime import date
   from decimal import Decimal
   
   # Create quarterly insurance bill
   insurance = Bill(
       bill_id="auto_insurance",
       service="Auto Insurance Premium", 
       amount_due=450.00,
       recurring=True,
       start_date=date(2025, 3, 15),
       frequency="quarterly"
   )
   
   # Get next bill instance
   next_bill = insurance.next_instance()
   print(f"Next bill due: {next_bill.due_date} for ${next_bill.amount_due}")
   
   # Create envelope with 3-month saving period
   envelope = Envelope(
       bill_instance=next_bill,
       initial_allocation=Decimal("50.00"),  # Starting amount
       start_contrib_date=date(2025, 1, 1),
       end_contrib_date=date(2025, 3, 10)    # Save until 5 days before due
   )
   
   # Generate contribution schedule
   scheduler = IndependentScheduler()
   scheduler.schedule([envelope])
   
   # Check daily contribution needed
   daily_amount = envelope.schedule.cash_flows_in_range(
       start_date=date(2025, 1, 1),
       end_date=date(2025, 1, 1)
   )[0].amount if envelope.schedule.cash_flows_in_range(
       start_date=date(2025, 1, 1), 
       end_date=date(2025, 1, 1)
   ) else Decimal("0.00")
   
   print(f"Daily contribution needed: ${daily_amount}")
   print(f"Remaining to save: ${envelope.remaining()}")

Example 2: Multiple Bills with Allocation
------------------------------------------

Manage multiple bills and allocate available funds strategically:

.. code-block:: python

   from sinkingfund import Bill, Envelope
   from sinkingfund.allocation import ProportionalAllocator
   from sinkingfund.managers import AllocationManager, BillManager, EnvelopeManager
   from datetime import date
   from decimal import Decimal
   
   # Create multiple bills
   bills = [
       Bill(
           bill_id="insurance",
           service="Auto Insurance",
           amount_due=450.00,
           recurring=True,
           start_date=date(2025, 3, 15),
           frequency="quarterly"
       ),
       Bill(
           bill_id="property_tax",
           service="Property Tax",
           amount_due=2400.00,
           recurring=True,
           start_date=date(2025, 11, 1),
           frequency="yearly"
       ),
       Bill(
           bill_id="hoa",
           service="HOA Fee",
           amount_due=85.00,
           recurring=True,
           start_date=date(2025, 2, 1),
           frequency="monthly"
       )
   ]
   
   # Set up managers
   bill_manager = BillManager()
   envelope_manager = EnvelopeManager()
   bill_manager.add_bills(bills)
   
   # Create envelopes for next 6 months of bills
   end_date = date(2025, 7, 31)
   upcoming_instances = bill_manager.get_upcoming_instances(
       start_date=date(2025, 1, 1),
       end_date=end_date
   )
   
   envelopes = []
   for instance in upcoming_instances:
       envelope = Envelope(
           bill_instance=instance,
           initial_allocation=Decimal("0.00"),
           start_contrib_date=date(2025, 1, 1),
           end_contrib_date=instance.due_date
       )
       envelopes.append(envelope)
       envelope_manager.add_envelope(envelope)
   
   print(f"Created {len(envelopes)} envelopes for upcoming bills")
   
   # Allocate monthly budget of $800
   allocator = ProportionalAllocator()
   allocation_manager = AllocationManager(allocator)
   
   monthly_budget = Decimal("800.00")
   result = allocation_manager.allocate(envelopes, monthly_budget)
   
   print(f"\\nAllocation Results:")
   for envelope in result.envelopes:
       bill_name = envelope.bill_instance.bill.service
       allocated = envelope.get_balance_as_of_date(date.today())
       remaining = envelope.remaining()
       print(f"  {bill_name}: ${allocated} allocated, ${remaining} remaining")

Example 3: Annual Planning with CSV Data
-----------------------------------------

Load bill data from a CSV file and plan for the entire year:

.. code-block:: python

   from sinkingfund.utils import load_bill_data_from_file
   from sinkingfund import Bill, Envelope
   from sinkingfund.managers import BillManager, EnvelopeManager
   from sinkingfund.schedules import IndependentScheduler
   from datetime import date
   from decimal import Decimal
   
   # Sample CSV content (bills.csv):
   # bill_id,service,amount_due,recurring,start_date,frequency
   # insurance,Auto Insurance,450.00,true,2025-03-15,quarterly
   # tax,Property Tax,2400.00,true,2025-11-01,yearly  
   # utilities,Electric Bill,120.00,true,2025-01-15,monthly
   
   # Load bills from CSV
   bills_data = load_bill_data_from_file("bills.csv")
   bills = [Bill(**data) for data in bills_data]
   
   # Set up annual planning
   bill_manager = BillManager()
   envelope_manager = EnvelopeManager()
   bill_manager.add_bills(bills)
   
   # Get all bills for the year
   year_start = date(2025, 1, 1)
   year_end = date(2025, 12, 31)
   
   annual_instances = bill_manager.get_upcoming_instances(
       start_date=year_start,
       end_date=year_end
   )
   
   # Create envelopes and schedules
   scheduler = IndependentScheduler()
   envelopes = []
   
   for instance in annual_instances:
       # Start saving 3 months before due date (or now if less than 3 months)
       start_saving = max(
           year_start,
           date(instance.due_date.year, 
                max(1, instance.due_date.month - 3), 
                1)
       )
       
       envelope = Envelope(
           bill_instance=instance,
           initial_allocation=Decimal("0.00"),
           start_contrib_date=start_saving,
           end_contrib_date=instance.due_date
       )
       envelopes.append(envelope)
   
   # Generate all schedules
   scheduler.schedule(envelopes)
   
   # Annual summary
   total_bills = sum(env.bill_instance.amount_due for env in envelopes)
   total_monthly = total_bills / 12
   
   print(f"Annual Planning Summary:")
   print(f"  Total bills for year: ${total_bills:,.2f}")
   print(f"  Average monthly saving needed: ${total_monthly:,.2f}")
   print(f"  Number of envelopes: {len(envelopes)}")
   
   # Monthly breakdown
   for month in range(1, 13):
       month_date = date(2025, month, 1)
       month_bills = [
           env for env in envelopes 
           if env.bill_instance.due_date.month == month
       ]
       month_total = sum(env.bill_instance.amount_due for env in month_bills)
       
       if month_total > 0:
           print(f"  {month_date.strftime('%B')}: ${month_total:,.2f} due")

Example 4: Emergency Fund Integration
-------------------------------------

Combine sinking funds with emergency fund planning:

.. code-block:: python

   from sinkingfund import Bill, Envelope
   from datetime import date, timedelta
   from decimal import Decimal
   
   # Create irregular/emergency bills
   emergency_bills = [
       Bill(
           bill_id="car_maintenance",
           service="Car Maintenance",
           amount_due=800.00,
           recurring=False,  # One-time estimated expense
           start_date=date(2025, 6, 1)  # Estimated timing
       ),
       Bill(
           bill_id="home_repair",
           service="Home Repair Fund", 
           amount_due=1500.00,
           recurring=False,
           start_date=date(2025, 8, 1)
       )
   ]
   
   # Create "buffer" envelopes with longer time horizons
   emergency_envelopes = []
   
   for bill in emergency_bills:
       instance = bill.next_instance()
       
       # Give ourselves extra time for emergency items
       envelope = Envelope(
           bill_instance=instance,
           initial_allocation=Decimal("0.00"),
           start_contrib_date=date(2025, 1, 1),
           end_contrib_date=instance.due_date - timedelta(days=30)
       )
       emergency_envelopes.append(envelope)
   
   # Calculate conservative saving strategy
   for envelope in emergency_envelopes:
       bill_name = envelope.bill_instance.bill.service
       amount = envelope.bill_instance.amount_due
       
       # Calculate days to save
       days_to_save = (envelope.end_contrib_date - envelope.start_contrib_date).days
       daily_amount = amount / days_to_save
       
       print(f"{bill_name}:")
       print(f"  Target: ${amount}")
       print(f"  Daily savings: ${daily_amount:.2f}")
       print(f"  Save until: {envelope.end_contrib_date}")
       print()

Example 5: Progress Tracking and Reporting
-------------------------------------------

Monitor progress and generate reports:

.. code-block:: python

   from sinkingfund import Bill, Envelope
   from sinkingfund.models import CashFlow, CashFlowSchedule
   from datetime import date, timedelta
   from decimal import Decimal
   
   # Simulate an envelope with some contribution history
   bill = Bill(
       bill_id="vacation",
       service="Summer Vacation",
       amount_due=3000.00,
       recurring=False,
       start_date=date(2025, 7, 15)
   )
   
   instance = bill.next_instance()
   envelope = Envelope(
       bill_instance=instance,
       initial_allocation=Decimal("500.00"),
       start_contrib_date=date(2025, 1, 1),
       end_contrib_date=date(2025, 7, 10)
   )
   
   # Simulate contribution history
   schedule = CashFlowSchedule()
   
   # Add some past contributions
   past_contributions = [
       CashFlow(date(2025, 1, 15), Decimal("200.00")),
       CashFlow(date(2025, 2, 15), Decimal("200.00")),
       CashFlow(date(2025, 3, 15), Decimal("200.00")),
   ]
   
   for cf in past_contributions:
       schedule.add_cash_flows(cf)
   
   envelope.schedule = schedule
   
   # Progress tracking
   today = date(2025, 3, 20)
   current_balance = envelope.get_balance_as_of_date(today)
   remaining = envelope.remaining()
   target = envelope.bill_instance.amount_due
   
   progress_pct = (current_balance / target) * 100
   
   print(f"Vacation Fund Progress Report ({today}):")
   print(f"  Target Amount: ${target}")
   print(f"  Current Balance: ${current_balance}")
   print(f"  Remaining Needed: ${remaining}")
   print(f"  Progress: {progress_pct:.1f}%")
   
   # Time analysis
   days_elapsed = (today - envelope.start_contrib_date).days
   total_days = (envelope.end_contrib_date - envelope.start_contrib_date).days
   days_remaining = (envelope.end_contrib_date - today).days
   
   print(f"\\nTime Analysis:")
   print(f"  Days elapsed: {days_elapsed} of {total_days}")
   print(f"  Days remaining: {days_remaining}")
   
   # Projection
   if days_remaining > 0:
       daily_needed = remaining / days_remaining
       print(f"  Daily contribution needed: ${daily_needed:.2f}")
   
   # On-track analysis
   expected_progress = days_elapsed / total_days
   actual_progress = progress_pct / 100
   
   if actual_progress >= expected_progress:
       print(f"  Status: ✓ On track or ahead!")
   else:
       shortfall = (expected_progress - actual_progress) * target
       print(f"  Status: ⚠ Behind by ${shortfall:.2f}")

These examples demonstrate the flexibility and power of the Sinking Fund
library for various financial planning scenarios. For more details on any
specific feature, see the :doc:`api_reference`.
