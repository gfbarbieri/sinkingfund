![Sinking Fund](assets/main_image.png)

# SinkingFund

A Python library for systematic bill payment planning using envelope-based sinking fund methodology.

## What is a Sinking Fund?

A sinking fund is a strategic savings approach where you set aside money regularly to prepare for future expenses. Unlike emergency funds (which cover unexpected costs), sinking funds are for anticipated expenses that might otherwise disrupt your budget, such as:

- Annual insurance premiums.
- Property taxes.
- Car maintenance and registration.
- Holiday gifts and travel.
- Home repairs and maintenance.
- Subscription renewals.
- Medical expenses.
- Professional development.

## Features

- **Bill Management**: Define one-time or recurring expenses with precise scheduling.
- **Envelope System**: Allocate savings into virtual "envelopes" for specific expenses.
- **Allocation Strategies**: Choose how to prioritize funding across multiple expenses.
- **Contribution Scheduling**: Automatically calculate contribution schedules.
- **Strategy Comparison**: Compare different allocation approaches without modifying data.
- **Reporting**: Generate detailed daily account reports and cash flow summaries.

## Documentation

- **[Full Documentation](https://sinkingfund.readthedocs.io/)** - Complete API reference, guides, and tutorials
- **[Examples](https://sinkingfund.readthedocs.io/en/latest/examples.html)** - Interactive Jupyter notebook examples
- **[API Reference](https://sinkingfund.readthedocs.io/en/latest/api_reference.html)** - Detailed API documentation

## Installation

### Basic Installation (Pure Python, No Dependencies)
```bash
pip install sinkingfund
```

### With Optional Dependencies

For data analysis and plotting:
```bash
pip install sinkingfund[analysis]  # pandas, matplotlib.
```

For Jupyter notebook support:
```bash
pip install sinkingfund[notebooks]  # ipykernel, jupyter.
```

For everything:
```bash
pip install sinkingfund[all]
```

### Development Installation
```bash
git clone https://github.com/gfbarbieri/sinkingfund.git
cd sinkingfund
poetry install --with dev,analysis,notebook
```

### Requirements

**Core Library**: Python 3.12+ (no additional dependencies).

**Optional Dependencies** (install via extras):
```
# Generated with: poetry export -f requirements.txt --output requirements.txt --without-hashes --with analysis,notebook
# Full requirements.txt includes all optional dependencies for development/testing

# Optional extras available:
# pip install sinkingfund[analysis]     - pandas, matplotlib.
# pip install sinkingfund[notebooks]    - jupyter support.
# pip install sinkingfund[all]          - everything.
```

## Quick Start

For more detailed examples and tutorials, see the [Examples section](https://sinkingfund.readthedocs.io/en/latest/examples.html) in the documentation.

### Basic Workflow

```python
from datetime import date

from sinkingfund import SinkingFund

# Create your sinking fund.
fund = SinkingFund(
    start_date=date(2025, 1, 1),
    end_date=date(2025, 12, 31),
    balance=1000.00
)

# Define your bills.
property_tax = {
    "bill_id": "prop_tax",
    "service": "Property Tax",
    "amount_due": 3600.00,
    "recurring": True,
    "start_date": date(2025, 11, 1),  # The bill's first due date.
    "frequency": "annual",
    "interval": 1  # Once a year.
}

car_insurance = {
    "bill_id": "car_ins", 
    "service": "Car Insurance",
    "amount_due": 750.00,
    "recurring": True,
    "start_date": date(2025, 4, 24),
    "frequency": "monthly",
    "interval": 6  # Every 6 months.
}

# Add bills to the fund (creates envelopes automatically).
fund.add_bills([property_tax, car_insurance])

# Generate a complete report with allocation and scheduling.
report = fund.quick_report()
```

### Loading Bills from CSV

You can load bills from a CSV file with the following format:

```python
from datetime import date

from sinkingfund import SinkingFund

# Create fund and add bills.
fund = SinkingFund(
    start_date=date(2025, 1, 1),
    end_date=date(2025, 12, 31),
    balance=2000.00
)

fund.add_bills('data/bills.csv')
```

**Required CSV columns:**
- `bill_id`: Unique identifier for the bill.
- `service`: Name of the service or expense.
- `amount_due`: Amount of the bill.
- `recurring`: Boolean (True/False) if bill repeats.
- `due_date`: When the bill is due (see Date Input Formats below).
- `start_date`: For recurring bills (see Date Input Formats below).
- `end_date`: Optional end date (see Date Input Formats below).
- `frequency`: One of "daily", "weekly", "monthly", "quarterly", "annual".
- `interval`: Number of frequency units between occurrences.

## Key Concepts

### Date Input Formats

The library supports multiple date string formats for flexibility when loading bills from files or providing dates programmatically. Dates can be provided as:

- **Date objects**: `datetime.date(2025, 1, 15)`
- **Date strings** in any of these formats:
  - `01/15/2025` (US format: MM/DD/YYYY)
  - `2025-01-15` (ISO format: YYYY-MM-DD)
  - `01-15-2025` (US with dashes)
  - `15/01/2025` (European format: DD/MM/YYYY)
  - `15-01-2025` (European with dashes)
  - `2025/01/15` (ISO with slashes)

When loading from CSV, Excel, or JSON files, the library automatically detects and converts date strings to `datetime.date` objects. The same conversion happens when providing dates in dictionaries.

**Example:**
```python
# All of these work:
fund.add_bills({
    'bill_id': 'tax',
    'service': 'Property Tax',
    'amount_due': 3600.00,
    'recurring': False,
    'due_date': '01/15/2025'  # String format
})

fund.add_bills({
    'bill_id': 'tax',
    'service': 'Property Tax',
    'amount_due': 3600.00,
    'recurring': False,
    'due_date': datetime.date(2025, 1, 15)  # Date object
})
```

### Bills and Bill Instances

The system distinguishes between:

- **`Bill`**: The definition of an expense, including its recurrence pattern.
- **`BillInstance`**: A specific occurrence of a bill with a concrete due date and amount.

### Allocation Strategies

Multiple allocation strategies are available:

```python
# Due date priority (default) - fund urgent bills first.
fund.allocate(strategy="sorted", sort_key="cascade")

# Smallest bills first - reduce number of obligations quickly.  
fund.allocate(strategy="sorted", sort_key="debt_snowball")

# Equal percentage across all bills.
fund.allocate(strategy="proportional")
```

### Schedulers

Schedulers determine how contributions are distributed over time:

- **`IndependentScheduler`**: Evenly distributes contributions across available time periods.

```python
# Even distribution for each envelope independently.
fund.schedule(strategy="independent_scheduler")
```

## Architecture

The library follows a modular design with clear separation of concerns:

### Core Models
- **`SinkingFund`**: Main orchestration class and API entry point.
- **`Bill`**: Financial obligation definitions.
- **`Envelope`**: Saving containers for specific bills.
- **`CashFlow`**: Money movement tracking (contributions/payments).

### Managers (Business Logic)
- **`BillManager`**: Bill lifecycle and instance generation.
- **`EnvelopeManager`**: Envelope operations and balance tracking.
- **`AllocationManager`**: Strategy-based fund allocation.
- **`ScheduleManager`**: Contribution scheduling coordination.

### Strategies (Pluggable Algorithms)
- **`BaseAllocator`**: Abstract allocation strategy interface.
- **`SortedAllocator`**: Priority-based allocation (cascade, debt snowball).
- **`ProportionalAllocator`**: Percentage-based allocation.
- **`BaseScheduler`**: Abstract scheduling strategy interface.
- **`IndependentScheduler`**: Per-envelope scheduling.

### Utilities
- **`loaders`**: CSV and data file processing.
- **`date_utils`**: Date arithmetic and range generation.
- **`format_registry`**: File format detection and parsing.

## Example Applications

- **Personal budgeting** for irregular expenses.
- **Family financial planning** (holidays, vacations, taxes).
- **Small business cash flow management**.
- **Non-profit budget allocation**.
- **Real estate investment planning** (maintenance, taxes, insurance).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
git clone https://github.com/gfbarbieri/sinkingfund.git
cd sinkingfund
poetry install --with dev,analysis,notebook

# Run all example notebooks to verify they work:
poetry run python scripts/run_notebooks.py

# Or use the shell script:
./scripts/run_notebooks.sh
```

**Running Example Notebooks**

To test all example notebooks at once:

```bash
# Python script (recommended - better error reporting):
poetry run python scripts/run_notebooks.py

# Or shell script:
./scripts/run_notebooks.sh
```

The script will execute all notebooks in the `examples/` directory and report which ones pass or fail, with detailed error messages for any failures.

## Roadmap

The following roadmap outlines planned improvements across features, documentation, examples, and testing. Each section lists the top 3 priorities with explicit implementation details.

### Features

1. **Investible Cash Calculation**
   - **Method**: Add `calculate_investible_cash()` to `SinkingFund` class in `sinkingfund/models/sinkingfund.py`
   - **Signature**: `def calculate_investible_cash(self, start_date: datetime.date, end_date: datetime.date) -> dict[str, Decimal]`
   - **Return Structure**: 
     ```python
     {
         'investible_cash': Decimal,      # Cash not committed to bills in period
         'dedicated_cash': Decimal,       # Cash committed to bills due in period
         'total_free_cash': Decimal,      # Total cash available (investible + dedicated)
         'period_start': datetime.date,
         'period_end': datetime.date
     }
     ```
   - **Implementation**: Iterate through date range, sum all contributions and payouts, identify bills with `due_date` within period, calculate envelope balances at period end, separate cash into investible (not needed for bills) vs dedicated (needed for bills)
   - **Integration**: Extend `build_daily_account_report()` return dict to optionally include investible cash metrics, or add as separate method callable after report generation

2. **Interest on Balances**
   - **Envelope Changes**: Add `interest_rate: Decimal` parameter to `Envelope.__init__()` in `sinkingfund/models/envelope.py`, default `Decimal("0.00")`
   - **New Method**: Add `calculate_interest_earned(as_of_date: datetime.date) -> Decimal` to `Envelope` class that computes compound interest on balance from `start_contrib_date` to `as_of_date` using daily compounding
   - **Balance Update**: Modify `Envelope.get_balance_as_of_date()` to include interest earned: `balance = initial_allocation + contributions + interest_earned`
   - **SinkingFund Changes**: Add `interest_rate: float | Decimal = 0.0` parameter to `SinkingFund.__init__()`, pass to envelopes during `create_envelopes()`
   - **Manager Update**: Modify `EnvelopeManager.create_envelopes()` to accept and propagate `interest_rate` parameter

3. **Interest-Aware Contribution Scheduling**
   - **Scheduler Changes**: Modify `IndependentScheduler.schedule()` in `sinkingfund/schedules/indep_scheduler.py` to accept `interest_rate: Decimal` parameter
   - **Calculation Update**: Adjust contribution amount formula to account for expected interest: `required_contribution = (remaining_amount - expected_interest) / num_contributions`
   - **Interest Projection**: Add helper method `_project_interest_earned()` that calculates expected interest from current date to bill due date using envelope's interest rate
   - **Integration**: Update `ScheduleManager.create_schedules()` to pass `interest_rate` from envelope to scheduler

### Documentation

1. **Sphinx Notebook Integration**
   - **Configuration**: Add `nbsphinx` extension to `docs/conf.py` in `extensions` list
   - **Notebook Directives**: Convert existing notebooks in `examples/` to Sphinx pages using `.. nbsphinx::` directive in `docs/examples.rst`
   - **Build Process**: Update `docs/Makefile` to include notebook execution and conversion steps
   - **Specific Files**: Convert `examples/your_first_sinking_fund.ipynb`, `examples/quick_start_csv_to_report.ipynb`, and `examples/envelopemanager_coordinating_multiple_envelopes.ipynb` as initial examples

2. **Expanded API Reference**
   - **Method Docstrings**: Enhance all public methods in `SinkingFund` class with complete parameter descriptions, return type details, and 3+ usage examples
   - **Cross-References**: Add `:class:`, `:meth:`, and `:ref:` directives linking related components (e.g., `AllocationManager` methods referenced from `SinkingFund.allocate_balance()`)
   - **File Updates**: Expand `docs/api/managers.rst`, `docs/api/schedules.rst`, and `docs/api/allocation.rst` with detailed examples for each public method

3. **Advanced Usage Guides**
   - **New File**: Create `docs/advanced_usage.rst` with sections: "Multi-Year Planning", "Multiple Sinking Fund Coordination", "External System Integration"
   - **Content**: Include code examples showing `SinkingFund` instances with `start_date`/`end_date` spanning multiple years, combining results from multiple fund instances, and exporting data to CSV/JSON formats
   - **Integration**: Add reference in `docs/index.rst` under "Advanced Topics" section

### Examples

1. **General Use Case Notebooks**
   - **File**: Create `examples/complete_workflow_from_setup_to_analysis.ipynb`
   - **Sections**: (1) Bill creation from CSV, (2) Envelope setup with multiple allocation strategies, (3) Schedule generation, (4) Report analysis with pandas, (5) Visualization with matplotlib
   - **File**: Enhance `examples/quick_start_csv_to_report.ipynb` with error handling, validation examples, and edge cases

2. **Bill Type-Specific Examples**
   - **File**: Create `examples/insurance_premiums_planning.ipynb` showing semi-annual and annual insurance bills with different due dates
   - **File**: Create `examples/property_tax_planning.ipynb` demonstrating annual property tax with quarterly contribution planning
   - **File**: Create `examples/subscription_management.ipynb` showing monthly recurring subscriptions with different billing cycles

3. **Advanced Workflow Examples**
   - **File**: Create `examples/strategy_comparison_analysis.ipynb` comparing `sorted` vs `proportional` allocation strategies side-by-side with visualization
   - **File**: Create `examples/multi_fund_coordination.ipynb` showing coordination of separate sinking funds for different purposes (personal vs business)
   - **File**: Create `examples/long_term_planning_5year.ipynb` demonstrating 5-year planning horizon with multiple recurring bills

### Testing

1. **Unit Test Coverage**
   - **File**: Create `tests/unit/managers/test_allocation_manager.py` with tests for `AllocationManager.set_allocator()`, `AllocationManager.allocate()`, and all strategy combinations
   - **File**: Create `tests/unit/managers/test_schedule_manager.py` with tests for `ScheduleManager.set_scheduler()`, `ScheduleManager.create_schedules()`, and scheduler strategy selection
   - **File**: Expand `tests/unit/managers/test_envelope_manager.py` to cover `get_balance_as_of_date()` edge cases, `total_cash_flow_on_date()` with various exclude parameters, and envelope removal scenarios
   - **Target**: Achieve 90%+ code coverage for `sinkingfund/managers/` directory

2. **Integration Tests**
   - **File**: Expand `tests/integration/test_basic_workflow.py` with test methods:
     - `test_quick_report_full_workflow()`: Validate `quick_report()` end-to-end with multiple bills
     - `test_allocation_strategy_switching()`: Test switching between allocation strategies without data loss
     - `test_scheduler_strategy_switching()`: Test switching between scheduler strategies
     - `test_build_daily_account_report_with_active_only()`: Validate `active_only` parameter behavior
   - **File**: Create `tests/integration/test_report_generation.py` with tests for report structure validation and data consistency checks

3. **Code Quality Automation**
   - **File**: Create `.pre-commit-config.yaml` in project root with hooks:
     - `ruff check --fix` for linting
     - `ruff format` for formatting
     - `pytest` for running tests (optional, can be manual)
   - **Installation**: Add `pre-commit` to `pyproject.toml` under `[tool.poetry.group.dev.dependencies]`
   - **Documentation**: Add section to `README.md` under "Development Setup" explaining `pre-commit install` command

## License

MIT License - see LICENSE file for details.