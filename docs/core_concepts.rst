Core Concepts
==============

.. _core-concepts-section:

This section builds up the core concepts of the Sinking Fund library from
the ground up. We start with the primitive models that represent basic
financial concepts, then introduce managers that coordinate operations,
followed by scheduling components, and finally the SinkingFund model that
orchestrates everything.

Models
------

.. _models-section:

The foundation of the Sinking Fund library consists of **primitive models**
that represent core financial concepts. These models are immutable value
objects that ensure data integrity and provide type-safe interfaces for
financial calculations.

Understanding these models is essential because they form the building
blocks for all other components in the system.

Bills
~~~~~

The :class:`~sinkingfund.models.Bill` class represents a financial
obligation definition. Bills can be either one-time expenses or recurring
obligations with configurable schedules.

**Key Characteristics:**

- **Bill Definition**: A Bill defines the template for a financial
  obligation, including its amount, recurrence pattern, and lifecycle.

- **Recurrence Support**: Recurring bills can repeat on daily, weekly,
  monthly, quarterly, or annual schedules with configurable intervals.

- **Calendar-Aware**: Bill date calculations handle calendar complexities
  like month-end dates, leap years, and varying month lengths.

- **Instance Generation**: Bills can generate specific occurrences
  (BillInstances) for any date range, enabling timeline planning.

**Example:**

.. code-block:: python

   from datetime import date
   from sinkingfund import Bill

   # Recurring quarterly bill.
   insurance = Bill(
       bill_id="auto_insurance",
       service="Quarterly Auto Insurance",
       amount_due=450.00,
       recurring=True,
       start_date=date(2025, 1, 15),
       frequency="quarterly"
   )

   # Generate instances for the year.
   instances = insurance.instances_in_range(
       start_reference=date(2025, 1, 1),
       end_reference=date(2025, 12, 31)
   )

For detailed information, see :class:`~sinkingfund.models.Bill`.

Bill Instances
~~~~~~~~~~~~~~

A **:class:`~sinkingfund.models.BillInstance`** represents a specific
occurrence of a bill with a concrete due date and amount. While a Bill
defines the template, a BillInstance represents an actual payment
obligation on a specific date.

**Key Characteristics:**

- **Concrete Dates**: Each BillInstance has a specific due date, making it
  suitable for timeline planning and envelope creation.

- **Amount Tracking**: The amount_due is fixed for each instance,
  enabling precise funding calculations.

- **Bill Association**: Each instance is linked to its parent Bill,
  maintaining the relationship between template and occurrence.

**Example:**

.. code-block:: python

   from datetime import date
   from sinkingfund import Bill

   bill = Bill(
       bill_id="rent",
       service="Monthly Rent",
       amount_due=1200.00,
       recurring=True,
       start_date=date(2025, 1, 1),
       frequency="monthly"
   )

   # Get the next instance after a reference date.
   next_instance = bill.next_instance(reference_date=date(2025, 3, 15))
   # Returns BillInstance for April 1, 2025.

For detailed information, see :class:`~sinkingfund.models.BillInstance`.

Envelopes
~~~~~~~~~

An **:class:`~sinkingfund.models.Envelope`** is a digital envelope for
targeted savings toward a specific bill instance. It implements the
envelope budgeting pattern, creating isolated savings containers that
accumulate money over time for specific future expenses.

**Key Characteristics:**

- **Targeted Savings**: Each envelope is associated with a specific
  BillInstance, ensuring funds are allocated for a particular expense.

- **Temporal Balance Tracking**: Envelopes track both initial allocations
  and scheduled contributions, enabling balance projections at any
  future date.

- **Contribution Windows**: Envelopes define start and end contribution
  dates, establishing clear savings periods.

- **Funding Status**: Envelopes can determine whether they will be fully
  funded by their target dates.

**Example:**

.. code-block:: python

   from decimal import Decimal
   from datetime import date
   from sinkingfund import Envelope, BillInstance

   # Create envelope for a bill instance.
   envelope = Envelope(
       bill_instance=BillInstance(
           bill_id="insurance",
           amount_due=Decimal("450.00"),
           due_date=date(2025, 3, 15)
       ),
       initial_allocation=Decimal("100.00"),
       start_contrib_date=date(2025, 1, 1),
       end_contrib_date=date(2025, 3, 14)
   )

   # Check funding status.
   remaining = envelope.remaining_amount
   is_funded = envelope.is_fully_funded

For detailed information, see :class:`~sinkingfund.models.Envelope`.

Cash Flows
~~~~~~~~~~

A **:class:`~sinkingfund.models.CashFlow`** represents an individual
monetary transaction within the sinking fund system. Cash flows can be
contributions (positive amounts) or payments (negative amounts).

**Key Characteristics:**

- **Transaction Recording**: Each CashFlow immutably records a single
  monetary transaction with amount, date, and description.

- **Directional Flow**: Positive amounts represent contributions, negative
  amounts represent payments.

- **Bill Association**: Cash flows can be linked to specific bills for
  audit trails and reporting.

**Example:**

.. code-block:: python

   from decimal import Decimal
   from datetime import date
   from sinkingfund import CashFlow

   # Contribution.
   contribution = CashFlow(
       amount=Decimal("75.00"),
       flow_date=date(2025, 1, 15),
       description="Bi-weekly contribution",
       bill_id="insurance"
   )

   # Payment.
   payment = CashFlow(
       amount=Decimal("-450.00"),
       flow_date=date(2025, 3, 15),
       description="Insurance payment",
       bill_id="insurance"
   )

For detailed information, see :class:`~sinkingfund.models.CashFlow`.

Cash Flow Schedules
~~~~~~~~~~~~~~~~~~~~

A **:class:`~sinkingfund.models.CashFlowSchedule`** is a collection of
cash flows with timeline operations and aggregation capabilities. It
represents a complete contribution or payment schedule for an envelope.

**Key Characteristics:**

- **Timeline Operations**: Schedules can query cash flows within date
  ranges, calculate totals, and project balances.

- **Chronological Ordering**: Cash flows are automatically sorted
  chronologically for efficient timeline analysis.

- **Aggregation**: Schedules provide methods to calculate total amounts,
  count transactions, and analyze cash flow patterns.

**Example:**

.. code-block:: python

   from sinkingfund import CashFlowSchedule, CashFlow
   from decimal import Decimal
   from datetime import date

   flows = [
       CashFlow(amount=Decimal("75.00"), flow_date=date(2025, 1, 1)),
       CashFlow(amount=Decimal("75.00"), flow_date=date(2025, 1, 15)),
       CashFlow(amount=Decimal("75.00"), flow_date=date(2025, 2, 1))
   ]

   schedule = CashFlowSchedule(cash_flows=flows)
   total = schedule.total_amount()  # Decimal("225.00")

For detailed information, see
:class:`~sinkingfund.models.CashFlowSchedule`.

Managers
--------

.. _managers-section:

.. note::
   Manager classes are **internal implementation details** of the SinkingFund
   class. Most users should interact with the system through the
   :class:`~sinkingfund.models.SinkingFund` API, which provides a unified
   interface for all operations. The managers are documented here for advanced
   users who need to understand the internal architecture or extend the
   system.

Manager classes provide high-level orchestration and coordination between
different components of the sinking fund system. They implement the manager
pattern to encapsulate business logic, validation, and workflow coordination
while maintaining clean separation of concerns from core domain models.

The SinkingFund class uses these managers internally to coordinate operations.
Direct use of managers is only recommended for advanced use cases or system
extensions.

Allocation Manager
~~~~~~~~~~~~~~~~~~

The **:class:`~sinkingfund.managers.AllocationManager`** coordinates fund
allocation strategies, enabling runtime selection of allocation
algorithms and providing a unified interface for fund distribution.

**Key Responsibilities:**

- **Strategy Selection**: Dynamically selects allocation strategies
  (sorted, proportional, custom) based on configuration.

- **Fund Distribution**: Coordinates the allocation of available funds
  across envelope collections using the selected strategy.

- **Result Management**: Returns allocation results with metadata about
  the allocation process.

**Note:** The SinkingFund class uses AllocationManager internally. Most
users should use the :meth:`~sinkingfund.models.SinkingFund.allocate` method
instead of creating AllocationManager directly.

For detailed information, see
:class:`~sinkingfund.managers.AllocationManager`.

Bill Manager
~~~~~~~~~~~~

The **:class:`~sinkingfund.managers.BillManager`** manages bill
collections, lifecycle operations, and instance generation for specified
time ranges.

**Key Responsibilities:**

- **Bill Registry**: Maintains a validated collection of bill
  definitions with uniqueness constraints.

- **Multi-Source Loading**: Supports loading bills from various data
  sources (files, dictionaries, programmatic creation) with automatic
  format detection.

- **Instance Generation**: Creates bill instances for specified time
  ranges with intelligent next-instance prediction.

- **Validation**: Enforces business rules for bill uniqueness and data
  integrity.

**Note:** The SinkingFund class uses BillManager internally. Most users
should use the :meth:`~sinkingfund.models.SinkingFund.add_bills` and
:meth:`~sinkingfund.models.SinkingFund.get_bill_instances` methods instead
of creating BillManager directly.

For detailed information, see
:class:`~sinkingfund.managers.BillManager`.

Envelope Manager
~~~~~~~~~~~~~~~~

The **:class:`~sinkingfund.managers.EnvelopeManager`** manages envelope
collections, contribution scheduling, and balance tracking operations.

**Key Responsibilities:**

- **Envelope Creation**: Creates envelopes from bill instances with
  configurable contribution parameters.

- **Contribution Scheduling**: Implements non-overlapping contribution
  periods for bill instances from the same recurring bill.

- **Balance Tracking**: Provides date-aware balance queries and cash
  flow aggregation across envelope collections.

- **Duplicate Prevention**: Validates envelope uniqueness and prevents
  conflicting commitments.

**Note:** The SinkingFund class uses EnvelopeManager internally. Most users
should use the :meth:`~sinkingfund.models.SinkingFund.create_envelopes` and
:meth:`~sinkingfund.models.SinkingFund.get_envelopes` methods instead of
creating EnvelopeManager directly.

For detailed information, see
:class:`~sinkingfund.managers.EnvelopeManager`.

Schedule Manager
~~~~~~~~~~~~~~~~

The **:class:`~sinkingfund.managers.ScheduleManager`** coordinates the
creation and application of contribution schedules for sinking fund
envelopes using various scheduling algorithms.

**Key Responsibilities:**

- **Strategy Selection**: Dynamically selects scheduling algorithms
  (independent scheduler, future schedulers) based on configuration.

- **Schedule Creation**: Delegates cash flow generation to specialized
  scheduler implementations.

- **Envelope Integration**: Ensures generated schedules are properly
  applied to corresponding envelopes.

**Note:** The SinkingFund class uses ScheduleManager internally. Most users
should use the :meth:`~sinkingfund.models.SinkingFund.schedule` method
instead of creating ScheduleManager directly.

For detailed information, see
:class:`~sinkingfund.managers.ScheduleManager`.

Schedules
---------

.. _schedules-section:

Scheduling components generate optimized contribution schedules for
envelopes based on available funds, timing constraints, and planning
objectives. Schedulers implement the strategy pattern, allowing different
scheduling algorithms to be plugged in without modifying core
management logic.

Independent Scheduler
~~~~~~~~~~~~~~~~~~~~~~

The **:class:`~sinkingfund.schedules.IndependentScheduler`** creates
even contribution schedules for each bill independently without
considering interactions between bills.

**Key Characteristics:**

- **Independent Processing**: Each envelope receives an optimized cash
  flow schedule computed independently of other envelopes.

- **Even Distribution**: Calculates daily contribution rates and groups
  them into intervals based on contribution frequency.

- **Predictable Payments**: Creates regular, consistent payments for
  each bill with smooth contribution amounts.

**Note:** The SinkingFund class uses schedulers internally through the
ScheduleManager. Most users should use the
:meth:`~sinkingfund.models.SinkingFund.schedule` method instead of creating
schedulers directly.

For detailed information, see
:class:`~sinkingfund.schedules.IndependentScheduler`.

SinkingFund Model
-----------------

.. _sinkingfund-model:

The **:class:`~sinkingfund.models.SinkingFund`** class is the main
orchestrator that coordinates all components of the sinking fund system.
It provides a unified API for the complete workflow from bill loading
to cash flow projection.

**Key Characteristics:**

- **Unified API**: Single interface for the complete sinking fund
  workflow, from bill loading to reporting.

- **Component Coordination**: Manages interaction between bill managers,
  envelope managers, allocation managers, and schedule managers.

- **Quick Reporting**: Generates comprehensive daily account reports
  with a single method call.

- **Workflow Automation**: Automates the complete planning process:
  loading bills, creating envelopes, allocating funds, and generating
  schedules.

**Core Workflow:**

1. **Initialize**: Create a SinkingFund with planning period and initial
   balance.

2. **Add Bills**: Add bills from files or programmatic definitions using
   ``add_bills()``. This method accepts a file path (str), a single bill
   dictionary, or a list of bill dictionaries. Envelopes are automatically
   created for bill instances in the planning period.

3. **Allocate Funds**: Distribute available funds across envelopes using
   selected allocation strategy with ``allocate()``.

4. **Schedule Contributions**: Set contribution dates and generate
   contribution schedules for each envelope with ``update_contribution_dates()``
   and ``schedule()``.

5. **Generate Reports**: Create daily account reports showing balances,
   contributions, and payouts with ``report()`` or ``quick_report()``. The
   ``quick_report()`` method performs steps 3-5 automatically.

**State Management:**

The SinkingFund API provides methods to maintain consistency:

- **Update Bills**: Use ``update_bill()`` to modify bill properties and
  automatically sync envelopes.

- **Delete Bills**: Use ``delete_bills()`` with automatic envelope cleanup.

- **Update Balance**: Use ``update_balance()`` to adjust account balance
  and sync the Reporter. After updating balance, call ``allocate()`` again
  or use ``quick_report()`` to regenerate the complete report.

- **Regenerate Reports**: Use ``quick_report()`` again with different
  options, or use the manual workflow (``allocate()`` → ``update_contribution_dates()``
  → ``schedule()`` → ``report()``) to regenerate reports with different
  allocation or scheduling options.

- **State Validation**: Use ``validate_state()`` to check consistency and
  ``sync_envelopes_with_bills()`` to fix orphaned envelopes.

**Example:**

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

   # Complete workflow in one call.
   report = fund.quick_report(
       contribution_interval=14,
       allocation_strategy="sorted",
       scheduler_strategy="independent_scheduler"
   )

For detailed information, see :class:`~sinkingfund.models.SinkingFund`.

