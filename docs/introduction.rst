Introduction
============

.. _introduction-section:

Purpose and Overview
--------------------

What is a Sinking Fund?
~~~~~~~~~~~~~~~~~~~~~~~

A sinking fund is a strategic financial planning method where you
systematically set aside money over time to prepare for anticipated
future expenses. Unlike emergency funds (which cover unexpected costs),
sinking funds are specifically designed for known, upcoming expenses
that might otherwise disrupt your budget when they come due.

Traditional sinking fund planning involves:

- **Identifying Future Expenses**: Recognizing bills and expenses that
  will occur in the future, such as annual insurance premiums, property
  taxes, or car maintenance.

- **Calculating Required Savings**: Determining how much money needs to
  be saved by the time each expense comes due.

- **Creating Savings Plans**: Establishing regular contribution schedules
  that accumulate funds gradually rather than requiring large lump-sum
  payments.

- **Tracking Progress**: Monitoring savings progress toward each expense
  to ensure adequate funding by the due date.

The Digital Envelope Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This library implements the **envelope budgeting** approach for sinking
funds, a method that creates separate "envelopes" (virtual savings
containers) for each future expense. Just as physical envelope budgeting
uses labeled envelopes to separate cash for different spending
categories, digital envelope budgeting creates isolated savings accounts
for specific bills.

Each envelope:

- **Targets a Specific Bill**: Is associated with a particular bill
  instance (e.g., "March 2025 property tax payment").

- **Tracks Savings Progress**: Monitors how much has been saved toward
  the bill's amount due.

- **Manages Contribution Schedules**: Defines when and how much to
  contribute over time.

- **Projects Future Balances**: Calculates expected balance at any future
  date based on scheduled contributions.

Why Use This Module?
~~~~~~~~~~~~~~~~~~~~

The Sinking Fund library automates the complex calculations and
coordination required for effective sinking fund management:

**Automated Calculations**
   Manual sinking fund planning requires calculating contribution
   schedules, tracking multiple envelopes, and ensuring bills are fully
   funded by their due dates. This library handles all these
   calculations automatically, reducing errors and saving time.

**Multiple Allocation Strategies**
   Different financial situations call for different allocation
   approaches. The library provides multiple strategies (priority-based,
   proportional, custom) so you can choose the method that best fits
   your financial goals.

**Comprehensive Reporting**
   Generate detailed daily account reports showing contributions,
   payouts, and balances over time, enabling clear visibility into your
   financial planning.

Key Features
------------

Automated Fund Allocation
~~~~~~~~~~~~~~~~~~~~~~~~~~

The library provides sophisticated algorithms for distributing available
funds across multiple envelopes based on your priorities:

- **Priority-Based Allocation**: Fund urgent bills first using due date
  priority, amount-based sorting, or custom criteria.

- **Proportional Distribution**: Allocate funds proportionally based on
  bill amounts, funding needs, or time-based weighting.

- **Flexible Strategy Selection**: Choose allocation strategies at
  runtime and compare different approaches without modifying your data.

See the :doc:`allocation strategies <api/allocation>` section in the
API reference for detailed information.

Bill Management
~~~~~~~~~~~~~~~

Comprehensive bill lifecycle management supports both one-time and
recurring expenses:

- **Recurring Bills**: Define bills that repeat on schedules (daily,
  weekly, monthly, quarterly, annual) with configurable intervals.

- **Bill Instance Generation**: Automatically generate specific bill
  occurrences (BillInstances) for any date range, handling calendar
  complexities like month-end dates and leap years.

- **Multi-Source Loading**: Load bills from CSV, Excel, or JSON files
  with automatic format detection and data validation.

- **Bill Validation**: Comprehensive validation ensures bill
  configurations are correct and prevents duplicate bill definitions.

See :class:`~sinkingfund.managers.BillManager` in the API reference for
detailed information.

Contribution Scheduling
~~~~~~~~~~~~~~~~~~~~~~~

Automated scheduling algorithms generate optimal contribution schedules
for each envelope:

- **Independent Scheduling**: Create even contribution schedules for
  each bill independently, optimizing for predictable per-bill
  contributions.

- **Calendar-Aware Calculations**: Proper handling of month-end dates,
  leap years, and varying month lengths ensures accurate scheduling.

- **Flexible Contribution Intervals**: Support for daily, weekly,
  bi-weekly, or custom contribution frequencies.

- **Automatic Schedule Generation**: Algorithms calculate contribution
  amounts and dates automatically based on available time and funding
  needs.

See the :doc:`schedules section <core_concepts>` for detailed
information.

Cash Flow Analysis
~~~~~~~~~~~~~~~~~~

Project and analyze cash flows over time:

- **Daily Account Reports**: Generate detailed reports showing account
  balances, contributions, and payouts for each day in your planning
  period.

- **Balance Projections**: Calculate expected balances at any future
  date by combining initial allocations with scheduled contributions.

- **Funding Status Tracking**: Determine whether envelopes will be
  fully funded by their due dates, enabling early intervention for
  underfunded obligations.

- **Multi-Envelope Coordination**: Track total contributions and payouts
  across all envelopes to understand overall cash flow patterns.

Key Components
--------------

The Sinking Fund library is organized into several key component
categories, each serving a specific role in the financial planning
workflow. Understanding these components helps you navigate the library
effectively and choose the right tools for your needs.

Models
~~~~~~

The foundation of the system consists of **primitive models** that
represent core financial concepts:

- :class:`~sinkingfund.models.Bill`: Represents a financial
  obligation definition, supporting both one-time and recurring bills
  with configurable schedules.

- :class:`~sinkingfund.models.BillInstance`: A specific occurrence of
  a bill with a concrete due date and amount, used for timeline
  planning.

- :class:`~sinkingfund.models.Envelope`: A digital envelope for
  targeted savings toward a specific bill instance, tracking
  contributions and funding progress.

- :class:`~sinkingfund.models.CashFlow`: Individual monetary
  transaction representing contributions or payments.

- :class:`~sinkingfund.models.CashFlowSchedule`: Collection of cash
  flows with timeline operations and aggregation capabilities.

These models are immutable value objects that ensure data integrity and
provide type-safe interfaces for financial calculations. See the
:doc:`models section <core_concepts>` for detailed information.

Managers
~~~~~~~~

**Manager classes** provide high-level orchestration and coordination
between different components:

- :class:`~sinkingfund.managers.BillManager`: Manages bill
  collections, lifecycle operations, and instance generation for
  specified time ranges.

- :class:`~sinkingfund.managers.EnvelopeManager`: Manages envelope
  collections, contribution scheduling, and balance tracking operations.

- :class:`~sinkingfund.managers.AllocationManager`: Coordinates fund
  allocation strategies, enabling runtime selection of allocation
  algorithms.

- :class:`~sinkingfund.managers.ScheduleManager`: Controls cash flow
  scheduling and timeline generation for systematic fund management.

Managers implement the manager pattern to encapsulate business logic,
validation, and workflow coordination. See the :doc:`managers section
<core_concepts>` for detailed information.

Schedules
~~~~~~~~~

**Scheduling components** generate optimized contribution schedules:

- :class:`~sinkingfund.schedules.IndependentScheduler`: Generates
  independent contribution schedules for individual envelopes without
  considering interactions between bills.

Schedulers implement the strategy pattern, allowing different scheduling
algorithms to be plugged in without modifying core management logic.
See the :doc:`schedules section <core_concepts>` for detailed
information.

Allocation Strategies
~~~~~~~~~~~~~~~~~~~~~

**Allocation strategies** implement different algorithms for distributing
available funds:

- :class:`~sinkingfund.allocation.SortedAllocator`: Priority-based
  allocation using envelope ordering criteria (due dates, amounts, custom
  sorting).

- :class:`~sinkingfund.allocation.ProportionalAllocator`: Mathematical
  proportional distribution based on funding needs or bill amounts.

Allocation strategies implement a common interface, enabling
interchangeable distribution approaches. See the :doc:`allocation
strategies <api/allocation>` section for detailed information.

SinkingFund Model
~~~~~~~~~~~~~~~~~

The :class:`~sinkingfund.models.SinkingFund` class is the main
orchestrator that coordinates all components:

- **Unified API**: Provides a single interface for the complete sinking
  fund workflow from bill loading to cash flow projection.

- **Component Coordination**: Manages the interaction between bill
  managers, envelope managers, allocation managers, and schedule
  managers.

- **Quick Reporting**: Generates comprehensive daily account reports
  with a single method call.

- **Workflow Automation**: Automates the complete planning process:
  loading bills, creating envelopes, allocating funds, and generating
  schedules.

Most users will primarily interact with the SinkingFund class, using
managers and strategies for advanced customization. See the
:doc:`SinkingFund model <core_concepts>` section for detailed
information.

Use Cases
---------

The Sinking Fund library is designed for a wide range of financial
planning scenarios. Here are common use cases with links to relevant
examples:

Personal Budgeting for Irregular Expenses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Plan for irregular expenses that don't fit into monthly budgets:

- **Annual Insurance Premiums**: Save monthly for annual or
  semi-annual insurance payments.

- **Property Taxes**: Prepare for annual or semi-annual property tax
  payments.

- **Car Maintenance**: Set aside money for regular maintenance,
  registration, and unexpected repairs.

- **Holiday Expenses**: Plan ahead for holiday gifts, travel, and
  celebrations.

Family Financial Planning
~~~~~~~~~~~~~~~~~~~~~~~~~

Coordinate multiple financial goals across a family budget:

- **Multiple Bills**: Manage dozens of bills with different due dates
  and amounts.

- **Priority Management**: Use allocation strategies to prioritize
  urgent expenses while maintaining progress on long-term goals.

- **Cash Flow Optimization**: Ensure sufficient funds are available
  when bills come due without over-saving.

- **Contribution Planning**: Create realistic contribution schedules
  that fit within monthly income constraints.

Debt Payoff Planning
~~~~~~~~~~~~~~~~~~~~

Apply sinking fund principles to debt payoff strategies:

- **Debt Snowball Method**: Use sorted allocation to prioritize
  smallest debts first.

- **Debt Avalanche Method**: Use sorted allocation to prioritize
  highest interest rate debts first.

- **Multiple Debts**: Coordinate payments across multiple debts with
  different balances and interest rates.