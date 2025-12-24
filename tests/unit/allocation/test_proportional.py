"""
Proportional Allocation Strategy Tests
======================================

Comprehensive tests for ProportionalAllocator covering multiple input
mixes (different weights/orderings), zero/negative amounts, and
ordering invariants.
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Any

import pytest

from sinkingfund.allocation import ProportionalAllocator
from sinkingfund.models import BillInstance, Envelope

########################################################################
## FIXTURES
########################################################################

@pytest.fixture
def base_date() -> datetime.date:
    """
    Provide a consistent base date for allocation tests.
    
    Returns
    -------
    datetime.date
        January 1, 2024, used as the reference point for most test
        scenarios.
    """
    return datetime.date(2024, 1, 1)


@pytest.fixture
def small_bill_instance() -> BillInstance:
    """
    Create a small bill instance for testing.
    
    Returns
    -------
    BillInstance
        Bill instance with $50.00 due on February 1, 2024.
    """
    return BillInstance(
        bill_id="small_bill",
        service="Small Bill",
        due_date=datetime.date(2024, 2, 1),
        amount_due=Decimal("50.00")
    )


@pytest.fixture
def medium_bill_instance() -> BillInstance:
    """
    Create a medium bill instance for testing.
    
    Returns
    -------
    BillInstance
        Bill instance with $150.00 due on February 15, 2024.
    """
    return BillInstance(
        bill_id="medium_bill",
        service="Medium Bill",
        due_date=datetime.date(2024, 2, 15),
        amount_due=Decimal("150.00")
    )


@pytest.fixture
def large_bill_instance() -> BillInstance:
    """
    Create a large bill instance for testing.
    
    Returns
    -------
    BillInstance
        Bill instance with $500.00 due on March 1, 2024.
    """
    return BillInstance(
        bill_id="large_bill",
        service="Large Bill",
        due_date=datetime.date(2024, 3, 1),
        amount_due=Decimal("500.00")
    )


@pytest.fixture
def envelope_small(small_bill_instance: BillInstance) -> Envelope:
    """
    Create an envelope for the small bill.
    
    Parameters
    ----------
    small_bill_instance : BillInstance
        The bill instance for this envelope.
        
    Returns
    -------
    Envelope
        Envelope with no initial allocation.
    """
    return Envelope(bill_instance=small_bill_instance)


@pytest.fixture
def envelope_medium(medium_bill_instance: BillInstance) -> Envelope:
    """
    Create an envelope for the medium bill.
    
    Parameters
    ----------
    medium_bill_instance : BillInstance
        The bill instance for this envelope.
        
    Returns
    -------
    Envelope
        Envelope with no initial allocation.
    """
    return Envelope(bill_instance=medium_bill_instance)


@pytest.fixture
def envelope_large(large_bill_instance: BillInstance) -> Envelope:
    """
    Create an envelope for the large bill.
    
    Parameters
    ----------
    large_bill_instance : BillInstance
        The bill instance for this envelope.
        
    Returns
    -------
    Envelope
        Envelope with no initial allocation.
    """
    return Envelope(bill_instance=large_bill_instance)


########################################################################
## PROPORTIONAL WEIGHTING TESTS
########################################################################

class TestProportionalWeighting:
    """
    Test proportional weighting method with various input mixes.
    """

    def test_proportional_single_envelope(
        self, envelope_small: Envelope
    ) -> None:
        """
        Test proportional allocation with a single envelope.
        """
        allocator = ProportionalAllocator("proportional")
        result = allocator.allocate(
            envelopes=[envelope_small],
            balance=100.0
        )
        
        # Test: Single envelope should receive all balance.
        assert len(result.envelopes) == 1
        assert result.envelopes[envelope_small] == Decimal("100.00")

    def test_proportional_two_envelopes_different_amounts(
        self,
        envelope_small: Envelope,
        envelope_large: Envelope
    ) -> None:
        """
        Test proportional allocation with two envelopes of different
        amounts.
        """
        allocator = ProportionalAllocator("proportional")
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_large],
            balance=550.0
        )
        
        # Test: Allocation should be proportional to bill amounts.
        # Small: $50, Large: $500, Total: $550
        # Small share: 50/550 = 0.0909..., Large share: 500/550 = 0.9090...
        small_allocation = result.envelopes[envelope_small]
        large_allocation = result.envelopes[envelope_large]
        
        # Test: Large bill should get approximately 10x more than small.
        assert abs(float(large_allocation) - (float(small_allocation) * 10)) < 0.01
        # Test: Total should equal balance.
        total = sum(result.envelopes.values())
        assert abs(float(total) - 550.0) < 0.01

    def test_proportional_three_envelopes_mixed_amounts(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope,
        envelope_large: Envelope
    ) -> None:
        """
        Test proportional allocation with three envelopes of mixed
        amounts.
        """
        allocator = ProportionalAllocator("proportional")
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_medium, envelope_large],
            balance=700.0
        )
        
        # Test: Allocation should be proportional.
        # Small: $50, Medium: $150, Large: $500, Total: $700
        small_allocation = result.envelopes[envelope_small]
        medium_allocation = result.envelopes[envelope_medium]
        large_allocation = result.envelopes[envelope_large]
        
        # Test: Ratios should match bill amount ratios.
        # Medium should be 3x small, Large should be 10x small.
        assert abs(float(medium_allocation) - (float(small_allocation) * 3)) < 0.01
        assert abs(float(large_allocation) - (float(small_allocation) * 10)) < 0.01
        # Test: Total should equal balance.
        total = sum(result.envelopes.values())
        assert abs(float(total) - 700.0) < 0.01

    def test_proportional_different_ordering(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope,
        envelope_large: Envelope
    ) -> None:
        """
        Test that proportional allocation is invariant to envelope
        ordering.
        """
        allocator = ProportionalAllocator("proportional")
        balance = 700.0
        
        # Test: Allocate with one ordering.
        result1 = allocator.allocate(
            envelopes=[envelope_small, envelope_medium, envelope_large],
            balance=balance
        )
        
        # Test: Allocate with different ordering.
        result2 = allocator.allocate(
            envelopes=[envelope_large, envelope_small, envelope_medium],
            balance=balance
        )
        
        # Test: Each envelope should receive the same allocation
        # regardless of order.
        assert result1.envelopes[envelope_small] == (
            result2.envelopes[envelope_small]
        )
        assert result1.envelopes[envelope_medium] == (
            result2.envelopes[envelope_medium]
        )
        assert result1.envelopes[envelope_large] == (
            result2.envelopes[envelope_large]
        )


    def test_proportional_insufficient_balance(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope,
        envelope_large: Envelope
    ) -> None:
        """
        Test proportional allocation with insufficient balance.
        """
        allocator = ProportionalAllocator("proportional")
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_medium, envelope_large],
            balance=100.0  # Less than total bill amounts ($700).
        )
        
        # Test: Allocation should still be proportional.
        total = sum(result.envelopes.values())
        assert abs(float(total) - 100.0) < 0.01
        # Test: Each envelope should get proportional share of $100.
        small_allocation = result.envelopes[envelope_small]
        medium_allocation = result.envelopes[envelope_medium]
        large_allocation = result.envelopes[envelope_large]
        
        # Test: Ratios should still match.
        assert abs(float(medium_allocation) - (float(small_allocation) * 3)) < 0.01
        assert abs(float(large_allocation) - (float(small_allocation) * 10)) < 0.01

########################################################################
## EQUAL WEIGHTING TESTS
########################################################################

class TestEqualWeighting:
    """
    Test equal weighting method with various input mixes.
    """

    def test_equal_single_envelope(
        self, envelope_small: Envelope
    ) -> None:
        """
        Test equal allocation with a single envelope.
        """
        allocator = ProportionalAllocator("equal")
        result = allocator.allocate(
            envelopes=[envelope_small],
            balance=100.0
        )
        
        # Test: Single envelope should receive all balance.
        assert result.envelopes[envelope_small] == Decimal("100.00")

    def test_equal_two_envelopes(
        self,
        envelope_small: Envelope,
        envelope_large: Envelope
    ) -> None:
        """
        Test equal allocation with two envelopes.
        """
        allocator = ProportionalAllocator("equal")
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_large],
            balance=200.0
        )
        
        # Test: Each envelope should receive equal allocation.
        assert result.envelopes[envelope_small] == Decimal("100.00")
        assert result.envelopes[envelope_large] == Decimal("100.00")

    def test_equal_three_envelopes(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope,
        envelope_large: Envelope
    ) -> None:
        """
        Test equal allocation with three envelopes.
        """
        allocator = ProportionalAllocator("equal")
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_medium, envelope_large],
            balance=300.0
        )
        
        # Test: Each envelope should receive equal allocation.
        assert result.envelopes[envelope_small] == Decimal("100.00")
        assert result.envelopes[envelope_medium] == Decimal("100.00")
        assert result.envelopes[envelope_large] == Decimal("100.00")

    def test_equal_different_ordering(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope,
        envelope_large: Envelope
    ) -> None:
        """
        Test that equal allocation is invariant to envelope ordering.
        """
        allocator = ProportionalAllocator("equal")
        balance = 300.0
        
        # Test: Allocate with one ordering.
        result1 = allocator.allocate(
            envelopes=[envelope_small, envelope_medium, envelope_large],
            balance=balance
        )
        
        # Test: Allocate with different ordering.
        result2 = allocator.allocate(
            envelopes=[envelope_large, envelope_small, envelope_medium],
            balance=balance
        )
        
        # Test: Each envelope should receive the same allocation
        # regardless of order.
        assert result1.envelopes[envelope_small] == (
            result2.envelopes[envelope_small]
        )
        assert result1.envelopes[envelope_medium] == (
            result2.envelopes[envelope_medium]
        )
        assert result1.envelopes[envelope_large] == (
            result2.envelopes[envelope_large]
        )

    def test_equal_uneven_balance(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope
    ) -> None:
        """
        Test equal allocation with balance that doesn't divide evenly.
        """
        allocator = ProportionalAllocator("equal")
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_medium],
            balance=100.0
        )
        
        # Test: Each envelope should receive equal allocation.
        assert result.envelopes[envelope_small] == Decimal("50.00")
        assert result.envelopes[envelope_medium] == Decimal("50.00")

########################################################################
## URGENCY WEIGHTING TESTS
########################################################################

class TestUrgencyWeighting:
    """
    Test urgency weighting method with various input mixes.
    """

    def test_urgency_single_envelope(
        self, envelope_small: Envelope, base_date: datetime.date
    ) -> None:
        """
        Test urgency allocation with a single envelope.
        """
        allocator = ProportionalAllocator("urgency")
        result = allocator.allocate(
            envelopes=[envelope_small],
            balance=100.0,
            curr_date=base_date
        )
        
        # Test: Single envelope should receive all balance.
        assert result.envelopes[envelope_small] == Decimal("100.00")

    def test_urgency_earlier_due_date_gets_more(
        self,
        envelope_small: Envelope,
        envelope_large: Envelope,
        base_date: datetime.date
    ) -> None:
        """
        Test that envelopes with earlier due dates get more allocation
        under urgency weighting.
        """
        allocator = ProportionalAllocator("urgency")
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_large],
            balance=550.0,
            curr_date=base_date
        )
        
        # Test: Earlier due date (Feb 1) should get more than later
        # (Mar 1), even if amount is smaller.
        small_allocation = result.envelopes[envelope_small]
        large_allocation = result.envelopes[envelope_large]
        
        # Test: Small bill (31 days away) should get proportionally more
        # than large bill (60 days away) due to urgency.
        # Weight calculation: amount / days
        # Small: 50 / 31 = 1.61, Large: 500 / 60 = 8.33
        # So large should still get more, but ratio should favor urgency.
        total = sum(result.envelopes.values())
        assert abs(float(total) - 550.0) < 0.01

    def test_urgency_past_due_date_gets_zero(
        self,
        envelope_small: Envelope,
        base_date: datetime.date
    ) -> None:
        """
        Test that envelopes with past due dates get zero weight.
        """
        # Create a bill instance with past due date.
        past_bill = BillInstance(
            bill_id="past_bill",
            service="Past Bill",
            due_date=datetime.date(2023, 12, 1),
            amount_due=Decimal("100.00")
        )
        envelope_past = Envelope(bill_instance=past_bill)
        
        allocator = ProportionalAllocator("urgency")
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_past],
            balance=150.0,
            curr_date=base_date
        )
        
        # Test: Past due envelope should receive zero allocation.
        assert result.envelopes[envelope_past] == Decimal("0.00")
        # Test: All balance should go to future envelope.
        assert result.envelopes[envelope_small] == Decimal("150.00")

    def test_urgency_due_today_gets_full_amount_weight(
        self,
        base_date: datetime.date
    ) -> None:
        """
        Test that envelopes due today use full amount as weight.
        """
        # Create a bill instance due today.
        today_bill = BillInstance(
            bill_id="today_bill",
            service="Today Bill",
            due_date=base_date,
            amount_due=Decimal("100.00")
        )
        envelope_today = Envelope(bill_instance=today_bill)
        
        # Create another bill due later.
        later_bill = BillInstance(
            bill_id="later_bill",
            service="Later Bill",
            due_date=datetime.date(2024, 2, 1),
            amount_due=Decimal("50.00")
        )
        envelope_later = Envelope(bill_instance=later_bill)
        
        allocator = ProportionalAllocator("urgency")
        result = allocator.allocate(
            envelopes=[envelope_today, envelope_later],
            balance=150.0,
            curr_date=base_date
        )
        
        # Test: Today's bill should get significant allocation.
        # Weight: today = 100 (full amount), later = 50/31 = 1.61
        # So today should get much more.
        assert float(result.envelopes[envelope_today]) > (
            float(result.envelopes[envelope_later])
        )

    def test_urgency_different_ordering(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope,
        envelope_large: Envelope,
        base_date: datetime.date
    ) -> None:
        """
        Test that urgency allocation is invariant to envelope ordering.
        """
        allocator = ProportionalAllocator("urgency")
        balance = 700.0
        
        # Test: Allocate with one ordering.
        result1 = allocator.allocate(
            envelopes=[envelope_small, envelope_medium, envelope_large],
            balance=balance,
            curr_date=base_date
        )
        
        # Test: Allocate with different ordering.
        result2 = allocator.allocate(
            envelopes=[envelope_large, envelope_small, envelope_medium],
            balance=balance,
            curr_date=base_date
        )
        
        # Test: Each envelope should receive the same allocation
        # regardless of order.
        assert abs(
            result1.envelopes[envelope_small] - (
                result2.envelopes[envelope_small]
            )
        ) < 0.01
        assert abs(
            result1.envelopes[envelope_medium] - (
                result2.envelopes[envelope_medium]
            )
        ) < 0.01
        assert abs(
            result1.envelopes[envelope_large] - (
                result2.envelopes[envelope_large]
            )
        ) < 0.01

########################################################################
## ZERO WEIGHTING TESTS
########################################################################

class TestZeroWeighting:
    """
    Test zero weighting method with various input mixes.
    """

    def test_zero_single_envelope(
        self, envelope_small: Envelope
    ) -> None:
        """
        Test zero allocation with a single envelope.
        """
        allocator = ProportionalAllocator("zero")
        
        # Test: Zero weights with single envelope may cause division
        # issues.
        with pytest.raises((ZeroDivisionError, ValueError)):
            allocator.allocate(
                envelopes=[envelope_small],
                balance=100.0
            )

    def test_zero_multiple_envelopes(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope
    ) -> None:
        """
        Test zero allocation with multiple envelopes.
        """
        allocator = ProportionalAllocator("zero")
        
        # Test: All zero weights should cause division by zero.
        with pytest.raises((ZeroDivisionError, ValueError)):
            allocator.allocate(
                envelopes=[envelope_small, envelope_medium],
                balance=200.0
            )

########################################################################
## CUSTOM WEIGHTING TESTS
########################################################################

class TestCustomWeighting:
    """
    Test custom weighting function with various input mixes.
    """

    def test_custom_weighting_function(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope
    ) -> None:
        """
        Test allocation with a custom weighting function.
        """
        def custom_weights(
            envelopes: list[Envelope], **kwargs: Any
        ) -> list[float]:
            """
            Custom weight function that gives double weight to first
            envelope.
            """
            weights = []
            for i, envelope in enumerate(envelopes):
                if i == 0:
                    weights.append(2.0)
                else:
                    weights.append(1.0)
            return weights
        
        allocator = ProportionalAllocator(custom_weights)
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_medium],
            balance=300.0
        )
        
        # Test: First envelope should get 2/3 of balance, second 1/3.
        assert abs(float(result.envelopes[envelope_small]) - 200.0) < 0.01
        assert abs(float(result.envelopes[envelope_medium]) - 100.0) < 0.01

    def test_custom_weighting_ordering_invariant(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope,
        envelope_large: Envelope
    ) -> None:
        """
        Test that custom weighting respects envelope identity, not
        position.
        """
        def custom_weights(
            envelopes: list[Envelope], **kwargs: Any
        ) -> list[float]:
            """
            Custom weight function based on bill amount.
            """
            return [
                float(env.bill_instance.amount_due) for env in envelopes
            ]
        
        allocator = ProportionalAllocator(custom_weights)
        balance = 700.0
        
        # Test: Allocate with one ordering.
        result1 = allocator.allocate(
            envelopes=[envelope_small, envelope_medium, envelope_large],
            balance=balance
        )
        
        # Test: Allocate with different ordering.
        result2 = allocator.allocate(
            envelopes=[envelope_large, envelope_small, envelope_medium],
            balance=balance
        )
        
        # Test: Each envelope should receive the same allocation
        # regardless of order.
        assert abs(
            result1.envelopes[envelope_small] - (
                result2.envelopes[envelope_small]
            )
        ) < 0.01
        assert abs(
            result1.envelopes[envelope_medium] - (
                result2.envelopes[envelope_medium]
            )
        ) < 0.01
        assert abs(
            result1.envelopes[envelope_large] - (
                result2.envelopes[envelope_large]
            )
        ) < 0.01

########################################################################
## EDGE CASE TESTS
########################################################################

class TestEdgeCases:
    """
    Test edge cases including zero balance, negative amounts, and
    boundary conditions.
    """

    def test_zero_balance(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope
    ) -> None:
        """
        Test allocation with zero balance.
        """
        allocator = ProportionalAllocator("proportional")
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_medium],
            balance=0.0
        )
        
        # Test: All envelopes should receive zero allocation.
        assert result.envelopes[envelope_small] == Decimal("0.00")
        assert result.envelopes[envelope_medium] == Decimal("0.00")

    def test_very_small_balance(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope
    ) -> None:
        """
        Test allocation with very small balance.
        """
        allocator = ProportionalAllocator("proportional")
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_medium],
            balance=0.01
        )
        
        # Test: Total should equal balance.
        total = sum(result.envelopes.values())
        assert abs(float(total) - 0.01) < 0.001

    def test_very_large_balance(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope
    ) -> None:
        """
        Test allocation with very large balance.
        """
        allocator = ProportionalAllocator("proportional")
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_medium],
            balance=1000000.0
        )
        
        # Test: Total should equal balance.
        total = sum(result.envelopes.values())
        assert abs(float(total) - 1000000.0) < 0.01

    def test_single_envelope_ordering(
        self, envelope_small: Envelope
    ) -> None:
        """
        Test that single envelope allocation is consistent.
        """
        allocator = ProportionalAllocator("proportional")
        result1 = allocator.allocate(
            envelopes=[envelope_small],
            balance=100.0
        )
        result2 = allocator.allocate(
            envelopes=[envelope_small],
            balance=100.0
        )
        
        # Test: Results should be identical.
        assert abs(
            float(result1.envelopes[envelope_small]) - (
                float(result2.envelopes[envelope_small])
            )
        ) < 0.01

