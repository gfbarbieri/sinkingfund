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
- **Contribution Scheduling**: Automatically calculate optimal contribution schedules.
- **Cash Flow Projection**: Visualize account balances and payments over time.
- **Funding Analysis**: Determine if your contribution plan will fully cover upcoming expenses.
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
pip install sinkingfund[analysis]  # pandas, matplotlib, plotly.
```

For advanced optimization features:
```bash  
pip install sinkingfund[optimization]  # pulp for linear programming.
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
poetry install --with dev,analysis,optimization,notebook
```

### Requirements

**Core Library**: Python 3.12+ (no additional dependencies).

**Optional Dependencies** (install via extras):
```
# Generated with: poetry export -f requirements.txt --output requirements.txt --without-hashes --with analysis,optimization,notebook
# Core library has no required dependencies - pure Python!
# Full requirements.txt includes all optional dependencies for development/testing

# Optional extras available:
# pip install sinkingfund[analysis]     - pandas, matplotlib, plotly.
# pip install sinkingfund[optimization] - pulp for advanced scheduling.
# pip install sinkingfund[notebooks]    - jupyter support.
# pip install sinkingfund[all]          - everything.
```

## Quick Start

### Simple Example

```python
import datetime
from sinkingfund import SinkingFund
from sinkingfund.models.bills import Bill

# Create your sinking fund
fund = SinkingFund(
    start_date=datetime.date.today(),
    end_date=datetime.date(2024, 12, 31),
    initial_balance=1000.00
)

# Define your bills
property_tax = Bill(
    bill_id="prop_tax",
    service="Property Tax",
    amount_due=3600.00,
    recurring=True,
    start_date=datetime.date(2024, 11, 1),
    frequency="annual",
    interval=1
)

car_insurance = Bill(
    bill_id="car_ins", 
    service="Car Insurance",
    amount_due=750.00,
    recurring=True,
    start_date=datetime.date(2024, 4, 24),
    frequency="monthly",
    interval=6  # Every 6 months.
)

# Add bills to the fund.
fund.add_bills([property_tax, car_insurance])

# Create envelopes with bi-weekly contributions.
fund.create_envelopes(contrib_interval=14)  # Every 14 days.

# Allocate current balance using cascade strategy (by due date).
fund.allocate_funds(strategy="cascade")

# Generate contribution schedules.
fund.schedule_contributions(scheduler="independent")

# Get funding status.
status = fund.get_funding_status()
print(f"Total needed: ${status['total_needed']:.2f}")
print(f"Currently allocated: ${status['total_allocated']:.2f}")
print(f"Funding gap: ${status['funding_gap']:.2f}")

# Generate daily account report.
report = fund.build_daily_account_report()
print(f"Account balance on Dec 31: ${report[datetime.date(2024, 12, 31)]['account_balance']['total']:.2f}")
```

### Loading Bills from CSV

You can load bills from a CSV file with the following format:

```python
from sinkingfund import SinkingFund
from sinkingfund.utils.loaders import load_bills_from_csv

# Load bills from CSV.
bills = load_bills_from_csv("bills.csv")

# Create fund and add bills.
fund = SinkingFund(
    start_date=datetime.date.today(),
    end_date=datetime.date(2024, 12, 31),
    initial_balance=2000.00
)
fund.add_bills(bills)
fund.create_envelopes(contrib_interval=14)
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
fund.allocate_funds(strategy="cascade")

# Smallest bills first - reduce number of obligations quickly.  
fund.allocate_funds(strategy="debt_snowball")

# Equal percentage across all bills.
fund.allocate_funds(strategy="proportional")

# Custom prioritization function.
def priority_sort(envelope):
    priorities = {"rent": 1, "utilities": 2, "subscription": 3}
    for service, priority in priorities.items():
        if service.lower() in envelope.bill.service.lower():
            return priority
    return 99  # Default low priority

fund.allocate_funds(strategy="sorted", sort_key=priority_sort)
```

### Schedulers

Schedulers determine how contributions are distributed over time:

- **`IndependentScheduler`**: Evenly distributes contributions across available time periods.
- **`SmoothedScheduler`**: Normalizes contributions across multiple bills for consistent totals.

```python
# Even distribution for each envelope independently.
fund.schedule_contributions(scheduler="independent")

# Smooth out total contributions across all envelopes.
fund.schedule_contributions(scheduler="smoothed")
```

### Strategy Comparison

Compare different allocation strategies without modifying your data:

```python
# Compare strategies.
results = fund.compare_allocation_strategies([
    "cascade", 
    "debt_snowball", 
    "proportional"
])

for strategy, result in results.items():
    print(f"{strategy}: {result.strategy_metadata}")
```

## Advanced Usage

### Cash Flow Analysis

```python
# Get contribution timeline across all envelopes.
timeline = fund.get_contribution_timeline()

# Get cash flow dates with activity.
active_dates = fund.get_cash_flow_dates()

# Filter daily report to only days with activity.
active_report = {
    date: data for date, data in fund.build_daily_account_report().items()
    if data['contributions']['count'] > 0 or data['payouts']['count'] > 0
}
```

### Visualization (with analysis extras)

```python
# Requires: pip install sinkingfund[analysis].
import matplotlib.pyplot as plt

# Plot account balance over time.
report = fund.build_daily_account_report()
dates = list(report.keys())
balances = [report[date]['account_balance']['total'] for date in dates]

plt.figure(figsize=(12, 6))
plt.plot(dates, balances, linewidth=2)
plt.title('Sinking Fund Account Balance Over Time')
plt.xlabel('Date')
plt.ylabel('Account Balance ($)')
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
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
poetry install --with dev,analysis,optimization,notebook

# Run tests.
poetry run pytest

# Code formatting.
poetry run black sinkingfund/
poetry run ruff check sinkingfund/

# Type checking.
poetry run mypy sinkingfund/
```

## License

MIT License - see LICENSE file for details.

## Changelog

### v0.1.0
- Initial release.
- Core envelope-based sinking fund functionality.
- Multiple allocation strategies (cascade, debt snowball, proportional).
- Independent contribution scheduling.
- CSV bill loading
- Comprehensive cash flow reporting
- Strategy comparison without data modification