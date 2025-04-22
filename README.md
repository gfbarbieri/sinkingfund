# SinkingFund

A Python library for managing sinking funds - a financial strategy for systematically saving for future expenses.

## What is a Sinking Fund?

A sinking fund is a strategic savings approach where you set aside money regularly to prepare for future expenses. Unlike emergency funds (which cover unexpected costs), sinking funds are for anticipated expenses that might otherwise disrupt your budget, such as:

- Annual insurance premiums
- Property taxes 
- Car maintenance
- Holiday gifts
- Home repairs
- Subscription renewals
- Vacations

## Features

- **Bill Management**: Define one-time or recurring expenses with precise scheduling
- **Envelope System**: Allocate savings into virtual "envelopes" for specific expenses
- **Allocation Strategies**: Choose how to prioritize funding across multiple expenses
- **Contribution Scheduling**: Automatically calculate optimal contribution schedules
- **Cashflow Projection**: Visualize account balances and payments over time
- **Funding Analysis**: Determine if your contribution plan will fully cover upcoming expenses

## Installing Dependencies

Poetry:
```bash
poetry install
```

Pip with requirements.txt:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create requirements.txt file with poetry, if required.
```bash
poetry export -f requirements.txt --output requirements.txt
```

## Usage

### Quick Start

```python
import datetime
from sinkingfund.models.bills import Bill
from sinkingfund.models.envelope import Envelope
from sinkingfund.models.account import Account
from sinkingfund.allocation.sorted import SortedAllocator
from sinkingfund.schedules.indep_scheduler import IndependentScheduler

# Define your bills. The start date is the first bill due date. The
# frequency is the periodicity of the bill. The interval is the number
# of periods between contributions.
property_tax = Bill(
    bill_id="prop_tax",
    service="Property Tax",
    amount_due=3600.00,
    recurring=True,
    start_date=datetime.date(2023, 11, 1),
    frequency="annual",
    interval=1
)

car_insurance = Bill(
    bill_id="car_ins",
    service="Car Insurance",
    amount_due=750.00,
    recurring=True,
    start_date=datetime.date(2023, 4, 24),
    frequency="monthly",
    interval=6
)

# Create envelopes (containers) for each bill. Plan to contribute every
# 14 days towards paying off the bill.
envelopes = [
    Envelope(bill=property_tax, interval=14),
    Envelope(bill=car_insurance, interval=14)
]

# Allocate your current savings across the envelopes. Cascade
# allocation prioritizes by due date.
allocator = SortedAllocator(sort_key="cascade")

# Allocate the current balance across the envelopes. The balance is the
# current amount of money available to allocate in the sinking fund. The
# current date is the date to begin allocating and contributing to the
# envelopes.
allocator.allocate(
    envelopes=envelopes,
    balance=1000.00,
    curr_date=datetime.date.today()
)

# Create a contribution schedule for each envelope. The independent
# scheduler distributes contributions evenly across the available time
# periods.
scheduler = IndependentScheduler()

scheduler.schedule(
    envelopes=envelopes,
    start_date=datetime.date.today()
)

# The schedule is a list of cash flows, which are the contributions and
# payments to the envelopes.
print(envelopes[0].schedule)
```

### Loading Bills from CSV

You can load bills from a CSV file with the following format:

```python
from sinkingfund.utils.loader import (
    load_bills_from_csv, load_envelopes_from_csv
)

# Load bills from CSV.
bills = load_bills_from_csv("bills.csv")

# Create envelopes with regular contribution intervals (every 14 days).
envelopes = load_envelopes_from_csv("bills.csv", contrib_intervals=14)
```

Required CSV columns:
- `bill_id`: Unique identifier for the bill
- `service`: Name of the service or expense 
- `amount_due`: Amount of the bill
- `recurring`: Boolean (True/False) if bill repeats
- `due_date`: When the bill is due (mm/dd/yyyy)
- `start_date`: For recurring bills (mm/dd/yyyy)
- `end_date`: Optional end date (mm/dd/yyyy)
- `frequency`: One of "daily", "weekly", "monthly", "quarterly", "annual"
- `interval`: Number of frequency units between occurrences

## Key Concepts

### Bills and Bill Instances

The system distinguishes between:

- `Bill`: The definition of an expense, including its recurrence pattern.
- `BillInstance`: A specific occurrence of a bill with a concrete due date and amount.

### Allocation Strategies

Multiple allocation strategies are available:

- **Cascade (Waterfall)**: Prioritize bills by due date, ensuring urgent obligations are funded first.
- **Debt Snowball**: Fund smallest bills first to reduce the number of bills quickly.
- **Custom**: Implement your own prioritization logic with custom sorting functions.

```python
# Due date priority (default).
allocator = SortedAllocator(sort_key="cascade")

# Smallest bills first.
allocator = SortedAllocator(sort_key="debt_snowball")

# Custom prioritization.
def priority_sort(bill):
    priorities = {"rent": 1, "utilities": 2, "subscription": 3}
    for service, priority in priorities.items():
        if service.lower() in bill.service.lower():
            return priority
    return 99  # Default low priority

allocator = SortedAllocator(sort_key=priority_sort)
```

### Schedulers

Schedulers determine how contributions are distributed over time:

- **IndependentScheduler**: Evenly distributes contributions across the available time periods.
- **SmoothedScheduler**: Normalizes contributions across multiple bills to create a consistent total contribution amount.

## Models

The library consists of several key models:

- **Bills**: Define financial obligations (one-time or recurring).
- **Envelopes**: Containers for saving towards specific bills.
- **Account**: Aggregates envelopes and tracks the overall fund.
- **CashFlow**: Represents money movement (contributions or payments).

## Example Applications

- Personal budgeting for irregular expenses.
- Family financial planning (holidays, vacations, taxes).
- Small business cash flow management.
- Non-profit budget allocation.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
