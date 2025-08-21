"""
Pytest Configuration and Common Fixtures
=========================================

This module provides common test fixtures and configuration for the
sinkingfund test suite. Fixtures follow the user's style guide with
comprehensive documentation and standard pytest patterns.

The fixtures support testing scenarios across models, managers, and
integration workflows while maintaining data isolation between tests.
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import datetime
import pytest

from decimal import Decimal

from sinkingfund.models import (
    Bill, 
    BillInstance, 
    Envelope, 
    CashFlow, 
    CashFlowSchedule,
    SinkingFund
)

########################################################################
## DATE FIXTURES
########################################################################

@pytest.fixture
def base_date() -> datetime.date:
    """
    Provide a consistent base date for relative date calculations.
    
    Returns
    -------
    datetime.date
        January 1, 2024, used as the reference point for most test
        scenarios.
        
    Notes
    -----
    DESIGN CHOICE: Using 2024 provides a leap year for comprehensive
    date arithmetic testing while being recent enough to avoid legacy
    calendar edge cases.
    """
    return datetime.date(2024, 1, 1)


@pytest.fixture
def start_date() -> datetime.date:
    """
    Standard start date for planning periods in tests.
    
    Returns
    -------
    datetime.date
        January 1, 2024.
    """
    return datetime.date(2024, 1, 1)


@pytest.fixture
def end_date() -> datetime.date:
    """
    Standard end date for planning periods in tests.
    
    Returns
    -------
    datetime.date
        December 31, 2024.
    """
    return datetime.date(2024, 12, 31)

########################################################################
## MONETARY FIXTURES
########################################################################

@pytest.fixture
def small_amount() -> Decimal:
    """
    Small monetary amount for basic testing scenarios.
    
    Returns
    -------
    Decimal
        $50.00, suitable for simple calculations and validations.
    """
    return Decimal("50.00")


@pytest.fixture
def medium_amount() -> Decimal:
    """
    Medium monetary amount for realistic testing scenarios.
    
    Returns
    -------
    Decimal
        $150.00, representing typical monthly bills like utilities.
    """
    return Decimal("150.00")


@pytest.fixture
def large_amount() -> Decimal:
    """
    Large monetary amount for comprehensive testing scenarios.
    
    Returns
    -------
    Decimal
        $1200.00, representing major expenses like insurance premiums.
    """
    return Decimal("1200.00")

########################################################################
## BILL FIXTURES
########################################################################

@pytest.fixture
def one_time_bill(medium_amount: Decimal) -> Bill:
    """
    Create a one-time bill for testing non-recurring scenarios.
    
    Parameters
    ----------
    medium_amount : Decimal
        The amount due for this bill.
        
    Returns
    -------
    Bill
        One-time car registration bill due March 15, 2024.
    """
    return Bill(
        bill_id="car_registration",
        service="Annual Car Registration",
        amount_due=medium_amount,
        recurring=False,
        due_date=datetime.date(2024, 3, 15)
    )

@pytest.fixture
def monthly_bill(medium_amount: Decimal) -> Bill:
    """
    Create a monthly recurring bill for testing periodic scenarios.
    
    Parameters
    ----------
    medium_amount : Decimal
        The amount due for each occurrence.
        
    Returns
    -------
    Bill
        Monthly electric bill starting January 15, 2024.
    """
    return Bill(
        bill_id="electric",
        service="Monthly Electric Bill",
        amount_due=medium_amount,
        recurring=True,
        start_date=datetime.date(2024, 1, 15),
        frequency="monthly",
        interval=1
    )

@pytest.fixture
def quarterly_bill(large_amount: Decimal) -> Bill:
    """
    Create a quarterly bill for testing longer-term scenarios.
    
    Parameters
    ----------
    large_amount : Decimal
        The amount due for each quarter.
        
    Returns
    -------
    Bill
        Quarterly insurance bill starting March 1, 2024.
    """
    return Bill(
        bill_id="insurance",
        service="Quarterly Insurance Premium",
        amount_due=large_amount,
        recurring=True,
        start_date=datetime.date(2024, 3, 1),
        frequency="monthly",
        interval=3
    )

########################################################################
## BILL INSTANCE FIXTURES
########################################################################

@pytest.fixture
def bill_instance(monthly_bill: Bill) -> BillInstance:
    """
    Create a bill instance for testing envelope and cash flow scenarios.
    
    Parameters
    ----------
    monthly_bill : Bill
        The parent bill for this instance.
        
    Returns
    -------
    BillInstance
        Instance for February 15, 2024 electric bill.
    """
    return BillInstance(
        bill_id=monthly_bill.bill_id,
        service=monthly_bill.service,
        due_date=datetime.date(2024, 2, 15),
        amount_due=monthly_bill.amount_due
    )

########################################################################
## ENVELOPE FIXTURES
########################################################################

@pytest.fixture
def empty_envelope(bill_instance: BillInstance) -> Envelope:
    """
    Create an empty envelope for testing funding scenarios.
    
    Parameters
    ----------
    bill_instance : BillInstance
        The bill instance this envelope will fund.
        
    Returns
    -------
    Envelope
        Envelope with no initial allocation or contributions.
    """
    return Envelope(
        bill_instance=bill_instance,
        start_contrib_date=datetime.date(2024, 1, 1),
        end_contrib_date=datetime.date(2024, 2, 14),
        contrib_interval=14
    )

@pytest.fixture
def partially_funded_envelope(
    bill_instance: BillInstance, 
    small_amount: Decimal
) -> Envelope:
    """
    Create a partially funded envelope for testing balance calculations.
    
    Parameters
    ----------
    bill_instance : BillInstance
        The bill instance this envelope will fund.
    small_amount : Decimal
        Initial allocation amount.
        
    Returns
    -------
    Envelope
        Envelope with $50 initial allocation.
    """
    return Envelope(
        bill_instance=bill_instance,
        initial_allocation=small_amount,
        start_contrib_date=datetime.date(2024, 1, 1),
        end_contrib_date=datetime.date(2024, 2, 14),
        contrib_interval=14
    )

########################################################################
## CASH FLOW FIXTURES
########################################################################

@pytest.fixture
def contribution_cash_flow(small_amount: Decimal) -> CashFlow:
    """
    Create a positive cash flow representing an envelope contribution.
    
    Parameters
    ----------
    small_amount : Decimal
        The contribution amount.
        
    Returns
    -------
    CashFlow
        Positive cash flow for January 15, 2024.
    """
    return CashFlow(
        bill_id="electric",
        date=datetime.date(2024, 1, 15),
        amount=small_amount
    )

@pytest.fixture
def payment_cash_flow(medium_amount: Decimal) -> CashFlow:
    """
    Create a negative cash flow representing a bill payment.
    
    Parameters
    ----------
    medium_amount : Decimal
        The payment amount (will be negated).
        
    Returns
    -------
    CashFlow
        Negative cash flow for February 15, 2024.
    """
    return CashFlow(
        bill_id="electric",
        date=datetime.date(2024, 2, 15),
        amount=-medium_amount
    )

@pytest.fixture
def cash_flow_schedule(
    contribution_cash_flow: CashFlow, 
    payment_cash_flow: CashFlow
) -> CashFlowSchedule:
    """
    Create a cash flow schedule with both contributions and payments.
    
    Parameters
    ----------
    contribution_cash_flow : CashFlow
        Positive cash flow for contributions.
    payment_cash_flow : CashFlow
        Negative cash flow for payments.
        
    Returns
    -------
    CashFlowSchedule
        Schedule containing both cash flows.
    """
    return CashFlowSchedule(
        cash_flows=[contribution_cash_flow, payment_cash_flow]
    )

########################################################################
## SINKING FUND FIXTURES
########################################################################

@pytest.fixture
def empty_sinking_fund(
    start_date: datetime.date, 
    end_date: datetime.date
) -> SinkingFund:
    """
    Create an empty sinking fund for testing initialization scenarios.
    
    Parameters
    ----------
    start_date : datetime.date
        Planning period start date.
    end_date : datetime.date
        Planning period end date.
        
    Returns
    -------
    SinkingFund
        Empty sinking fund with zero balance.
    """
    return SinkingFund(
        start_date=start_date,
        end_date=end_date,
        balance=0.0
    )

@pytest.fixture
def funded_sinking_fund(
    start_date: datetime.date, 
    end_date: datetime.date,
    large_amount: Decimal
) -> SinkingFund:
    """
    Create a funded sinking fund for testing allocation scenarios.
    
    Parameters
    ----------
    start_date : datetime.date
        Planning period start date.
    end_date : datetime.date
        Planning period end date.
    large_amount : Decimal
        Initial fund balance.
        
    Returns
    -------
    SinkingFund
        Sinking fund with substantial initial balance.
    """
    return SinkingFund(
        start_date=start_date,
        end_date=end_date,
        balance=float(large_amount)
    )

########################################################################
## COLLECTION FIXTURES
########################################################################

@pytest.fixture
def multiple_bills(
    one_time_bill: Bill, 
    monthly_bill: Bill, 
    quarterly_bill: Bill
) -> list[Bill]:
    """
    Create a diverse collection of bills for testing complex scenarios.
    
    Parameters
    ----------
    one_time_bill : Bill
        One-time expense.
    monthly_bill : Bill
        Monthly recurring expense.
    quarterly_bill : Bill
        Quarterly recurring expense.
        
    Returns
    -------
    list[Bill]
        Collection of bills with different patterns.
    """
    return [one_time_bill, monthly_bill, quarterly_bill]

########################################################################
## UTILITY FIXTURES
########################################################################

@pytest.fixture
def date_range(
    start_date: datetime.date, 
    end_date: datetime.date
) -> tuple[datetime.date, datetime.date]:
    """
    Provide a standard date range for testing time-bounded operations.
    
    Parameters
    ----------
    start_date : datetime.date
        Range start.
    end_date : datetime.date
        Range end.
        
    Returns
    -------
    tuple[datetime.date, datetime.date]
        Date range tuple for testing.
    """
    return (start_date, end_date)
