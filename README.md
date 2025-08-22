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

### Basic Workflow

```python
import datetime

from sinkingfund import SinkingFund

# Create your sinking fund.
fund = SinkingFund(
    start_date=datetime.date.today(),
    end_date=datetime.date(2024, 12, 31),
    balance=1000.00
)

# Define your bills.
property_tax = {
    bill_id="prop_tax",
    service="Property Tax",
    amount_due=3600.00,
    recurring=True,
    start_date=datetime.date(2024, 11, 1),  # The bill's first due date.
    frequency="annual",
    interval=1  # Once a year.
}

car_insurance = {
    bill_id="car_ins", 
    service="Car Insurance",
    amount_due=750.00,
    recurring=True,
    start_date=datetime.date(2024, 4, 24),
    frequency="monthly",
    interval=6  # Every 6 months.
}

# Use quick start to get a full daily contribution schedule with
# defaults.
report = fund.quick_start(bill_source=[property_tax, car_insurance])
```

### Loading Bills from CSV

You can load bills from a CSV file with the following format:

```python
from sinkingfund import SinkingFund

# Create fund and add bills.
fund = SinkingFund(
    start_date=datetime.date.today(),
    end_date=datetime.date(2024, 12, 31),
    balance=2000.00
)

fund.create_bills(bill_source='data/bills.csv')
```

**Required CSV columns:**
- `bill_id`: Unique identifier for the bill.
- `service`: Name of the service or expense.
- `amount_due`: Amount of the bill.
- `recurring`: Boolean (True/False) if bill repeats.
- `due_date`: When the bill is due (mm/dd/yyyy).
- `start_date`: For recurring bills (mm/dd/yyyy).
- `end_date`: Optional end date (mm/dd/yyyy).
- `frequency`: One of "daily", "weekly", "monthly", "quarterly", "annual".
- `interval`: Number of frequency units between occurrences.

## Key Concepts

### Bills and Bill Instances

The system distinguishes between:

- **`Bill`**: The definition of an expense, including its recurrence pattern.
- **`BillInstance`**: A specific occurrence of a bill with a concrete due date and amount.

### Allocation Strategies

Multiple allocation strategies are available:

```python
# Due date priority (default) - fund urgent bills first.
fund.set_allocation_strategy("sorted", sort_key="cascade")

# Smallest bills first - reduce number of obligations quickly.  
fund.set_allocation_strategy("sorted", sort_key="debt_snowball")

# Equal percentage across all bills.
fund.set_allocation_strategy("proportional")
```

### Schedulers

Schedulers determine how contributions are distributed over time:

- **`IndependentScheduler`**: Evenly distributes contributions across available time periods.

```python
# Even distribution for each envelope independently.
fund.set_scheduler("independent")
fund.create_schedules()
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

# Note: Tests are not yet implemented.
```

## TODO

- [ ] Add unit tests for allocator, scheduler, and manager modules.
- [ ] Add integration tests for the core SinkingFund class.
- [ ] Add linter tests (ruff).
- [ ] Add code formatter tests (black, ruff).
- [ ] I am learning about pre-commit hooks and would like to use them to run tests, linter, and formatter on every commit.
- [ ] Upgrade Sphinx documentation to easily convert example Jupyter notebooks into documentation pages.
- [ ] Create example notebooks for general use and specific bill types.
- [ ] Migrate to a database approach instead of current memory-based approach for scalability.
- [ ] Build feature to include interest in balances.
- [ ] Build feature to use interest on balances to in calculating the contribution schedules.

## License

MIT License - see LICENSE file for details.