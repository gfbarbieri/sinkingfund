Examples
========

.. _examples-section:

This section provides practical, executable examples of using the Sinking
Fund library. All examples are derived from Jupyter notebooks in the
``examples/`` directory, ensuring they work correctly with the actual
codebase.

Notebook-Based Examples
-----------------------

Examples are maintained as Jupyter notebooks to ensure:

- **Tested Code**: All examples are executable and verified to work.
- **Interactive Exploration**: You can modify and experiment with the code.
- **Up-to-Date**: Examples automatically reflect the current API.
- **Reproducible**: Notebooks can be run independently to reproduce results.

Each notebook is automatically converted to a standalone documentation
section. When you add a new notebook to the ``examples/`` directory and
rebuild the documentation, it will automatically appear as a new section
here.

Available Examples
------------------

The following examples are automatically generated from Jupyter notebooks
in the ``examples/`` directory. Each notebook becomes a standalone
section in the documentation.

Tutorials & Getting Started
---------------------------

These tutorials are designed for users new to the Sinking Fund library.
They provide step-by-step guidance from basic concepts to generating your
first report.

.. toctree::
   :maxdepth: 1
   :caption: Tutorials & Getting Started:

   examples/your_first_sinking_fund
   examples/understanding_bills_vs_envelopes
   examples/quick_start_csv_to_report

.. _example-your-first-sinking-fund:

Your First Sinking Fund
~~~~~~~~~~~~~~~~~~~~~~~

Step-by-step tutorial from zero to first report. Create a single bill,
envelope, and generate a schedule with minimal setup and maximum clarity.

See :doc:`examples/your_first_sinking_fund` for the full notebook.

.. _example-understanding-bills-vs-envelopes:

Understanding Bills vs. Envelopes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Conceptual differences with side-by-side examples. Learn when to use each,
their relationship, and common mistakes to avoid.

See :doc:`examples/understanding_bills_vs_envelopes` for the full notebook.

.. _example-quick-start-csv-to-report:

Quick Start: From CSV to Report in 5 Minutes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fastest path to results. Load bills from CSV and generate a report with
defaults using minimal code for maximum output.

See :doc:`examples/quick_start_csv_to_report` for the full notebook.

Manager Workflows
-----------------

These notebooks demonstrate how to use the manager classes to coordinate
bill loading, envelope creation, and fund allocation. Essential for
understanding the manager pattern and batch operations.

.. toctree::
   :maxdepth: 1
   :caption: Manager Workflows:

   examples/billmanager_loading_and_managing
   examples/envelopemanager_coordinating_multiple_envelopes
   examples/allocationmanager_choosing_strategy

.. _example-billmanager-loading-and-managing:

BillManager: Loading and Managing Multiple Bills
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Loading bills from multiple sources (CSV, Excel, JSON, dictionaries),
generating instances for planning periods, and managing bill collections
with validation.

See :doc:`examples/billmanager_loading_and_managing` for the full
notebook.

.. _example-envelopemanager-coordinating-multiple-envelopes:

EnvelopeManager: Coordinating Multiple Envelopes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Creating envelopes from bill instances, setting non-overlapping
contribution periods, and batch operations with duplicate prevention.

See :doc:`examples/envelopemanager_coordinating_multiple_envelopes` for
the full notebook.

.. _example-allocationmanager-choosing-strategy:

AllocationManager: Choosing the Right Strategy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Comparing sorted vs. proportional allocation, custom sort keys and
weighting functions, and understanding allocation results and metadata.

See :doc:`examples/allocationmanager_choosing_strategy` for the full
notebook.

Real-World Use Cases
--------------------

These notebooks demonstrate practical applications of the Sinking Fund
system for real-world financial planning scenarios. Perfect for seeing
how the system works in practice.

.. toctree::
   :maxdepth: 1
   :caption: Real-World Use Cases:

   examples/planning_for_annual_expenses
   examples/debt_payoff_strategies
   examples/family_budget_coordination

.. _example-planning-for-annual-expenses:

Planning for Annual Expenses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Planning for property taxes, insurance premiums, annual subscriptions,
and other once-per-year expenses. Optimizing contributions across the
year to have funds ready when needed.

See :doc:`examples/planning_for_annual_expenses` for the full notebook.

.. _example-debt-payoff-strategies:

Debt Payoff Strategies
~~~~~~~~~~~~~~~~~~~~~~~

Demonstrating debt snowball (smallest first) and avalanche (highest
interest first) strategies using sorted allocation for debt
prioritization and tracking progress toward debt freedom.

See :doc:`examples/debt_payoff_strategies` for the full notebook.

.. _example-family-budget-coordination:

Family Budget Coordination
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Managing 20+ bills across categories, balancing urgent vs. long-term
goals, and generating family-friendly reports for comprehensive budget
coordination.

See :doc:`examples/family_budget_coordination` for the full notebook.

Model Deep Dives
----------------

These notebooks provide detailed exploration of core model classes and
their capabilities. Perfect for understanding the building blocks of the
sinking fund system.

.. toctree::
   :maxdepth: 1
   :caption: Model Deep Dives:

   examples/working_with_bill_objects
   examples/envelope_lifecycle_management
   examples/cashflow_and_schedule_patterns

.. _example-working-with-bill-objects:

Working with Bill Objects
~~~~~~~~~~~~~~~~~~~~~~~~~

Creating one-time and recurring bills programmatically, generating bill
instances for date ranges, and understanding calendar-aware date
calculations including month-end adjustments and leap year handling.

See :doc:`examples/working_with_bill_objects` for the full notebook.

.. _example-envelope-lifecycle-management:

Envelope Lifecycle Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Creating envelopes, setting contribution windows, tracking balances over
time, checking funding status, and understanding the relationship between
initial allocations and scheduled contributions.

See :doc:`examples/envelope_lifecycle_management` for the full notebook.

.. _example-cashflow-and-schedule-patterns:

CashFlow and CashFlowSchedule Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Creating individual cash flows, building schedules, querying by date
ranges, and aggregating and analyzing cash flow patterns for both
contributions and payments.

See :doc:`examples/cashflow_and_schedule_patterns` for the full notebook.

.. note::
   To add a new notebook, see the :ref:`creating-new-examples` section
   below for detailed step-by-step instructions.

Sample Data
-----------

The examples in this documentation use dictionary-based bill data to
demonstrate functionality. You can create bills from CSV files, Excel
files, JSON files, or Python dictionaries. See the individual example
notebooks for specific data formats and usage patterns.

Creating and Removing Examples
------------------------------

.. _creating-new-examples:

Step-by-Step Instructions
~~~~~~~~~~~~~~~~~~~~~~~~~~

To add a new example notebook to the documentation:

**Step 1: Create the Notebook**

Create a new Jupyter notebook in the ``examples/`` directory with a
descriptive filename (use underscores, not spaces):

.. code-block:: bash

   examples/my_new_example.ipynb

**Step 2: Write the Notebook**

Structure your notebook with:

- **Markdown cells** for explanations and documentation
- **Code cells** with working, tested code
- **Clear examples** that demonstrate specific features or workflows
- **Descriptive titles** in the first markdown cell (this becomes the
  section title)

Example notebook structure:

.. code-block:: markdown

   # My New Example Title
   
   This example demonstrates...
   
   ## Setup
   
   ```python
   from sinkingfund import ...
   ```
   
   ## Main Example
   
   ```python
   # Your example code here
   ```

**Step 3: Test the Notebook**

Before adding to documentation:

- Run all cells to ensure they execute without errors
- Verify outputs are correct and meaningful
- Check that the code works with the current API version
- Test with different scenarios if applicable

**Step 4: Add to Documentation**

Edit ``docs/examples.rst`` and add your notebook in two places:

1. **Add to the toctree** (around line 33-41):

   .. code-block:: rst

      .. toctree::
         :maxdepth: 1
         :caption: Example Notebooks:

         examples/your_first_sinking_fund
         examples/my_new_example    # Add this line (no .ipynb extension)

2. **Add a description section** (after the toctree, around line 43+):

   .. code-block:: rst

      .. _example-my-new-example:

      My New Example Title
      ~~~~~~~~~~~~~~~~~~~~

      Brief description of what this example demonstrates.

      See :doc:`examples/my_new_example` for the full notebook.

**Step 5: Rebuild Documentation**

Rebuild the Sphinx documentation:

.. code-block:: bash

   cd docs
   make html

   # Or using sphinx-build directly:
   sphinx-build -b html . _build/html

The notebook will be automatically converted to HTML by nbsphinx and
appear in the documentation.

**Step 6: Verify**

- Check that the notebook appears in the Examples section
- Verify all code cells and outputs are displayed correctly
- Test that cross-references work
- Ensure the notebook renders properly in the HTML output

Notebook Best Practices
~~~~~~~~~~~~~~~~~~~~~~~

- **Clear Structure**: Use markdown headers to organize content
- **Self-Contained**: Include all necessary imports and setup
- **Documented**: Explain what each section demonstrates
- **Tested**: Ensure all code runs successfully
- **Current**: Use the latest API patterns and methods
- **Focused**: Each notebook should demonstrate a specific concept or
  workflow

The documentation build process will automatically:

- Convert the notebook to a documentation page
- Include all code cells and outputs
- Preserve markdown explanations
- Execute code cells (if ``nbsphinx_execute = 'auto'`` in conf.py)
- Create cross-references for linking

Removing Examples
~~~~~~~~~~~~~~~~~

If you need to remove a notebook from the documentation:

**Step 1: Remove the Notebook File**

Delete the notebook file from the ``examples/`` directory:

.. code-block:: bash

   rm examples/my_old_example.ipynb

**Step 2: Remove from Documentation**

Edit ``docs/examples.rst`` and remove the notebook in two places:

1. **Remove from the toctree** (around line 33-41):

   Remove the line::

      examples/my_old_example

2. **Remove the description section** (after the toctree):

   Remove the entire section including the label, title, description, and
   :doc: reference::

      .. _example-my-old-example:

      My Old Example Title
      ~~~~~~~~~~~~~~~~~~~~

      Description...

      See :doc:`examples/my_old_example` for the full notebook.

**Step 3: Rebuild Documentation**

Rebuild the documentation to verify the notebook is removed:

.. code-block:: bash

   cd docs
   make html

The build will succeed without warnings once all references are removed.

**Note**: If you only remove the notebook file but leave the references in
``examples.rst``, the build will still succeed but show warnings about
missing documents. It's best to remove both the file and the references
together.

For more information on the notebook format and best practices, see the
development documentation.
