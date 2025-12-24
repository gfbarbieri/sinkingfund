"""
Sorted Allocation Strategy Tests
=================================

Comprehensive tests for SortedAllocator covering multiple input mixes
(different orderings), zero/negative amounts, and ordering invariants.
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Any

import pytest

from sinkingfund.allocation import SortedAllocator
from sinkingfund.models import BillInstance, Envelope

########################################################################
## FIXTURES
########################################################################

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
def early_bill_instance() -> BillInstance:
    """
    Create an early due date bill instance for testing.
    
    Returns
    -------
    BillInstance
        Bill instance with $100.00 due on January 15, 2024.
    """
    return BillInstance(
        bill_id="early_bill",
        service="Early Bill",
        due_date=datetime.date(2024, 1, 15),
        amount_due=Decimal("100.00")
    )


@pytest.fixture
def late_bill_instance() -> BillInstance:
    """
    Create a late due date bill instance for testing.
    
    Returns
    -------
    BillInstance
        Bill instance with $200.00 due on April 1, 2024.
    """
    return BillInstance(
        bill_id="late_bill",
        service="Late Bill",
        due_date=datetime.date(2024, 4, 1),
        amount_due=Decimal("200.00")
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


@pytest.fixture
def envelope_early(early_bill_instance: BillInstance) -> Envelope:
    """
    Create an envelope for the early bill.
    
    Parameters
    ----------
    early_bill_instance : BillInstance
        The bill instance for this envelope.
        
    Returns
    -------
    Envelope
        Envelope with no initial allocation.
    """
    return Envelope(bill_instance=early_bill_instance)


@pytest.fixture
def envelope_late(late_bill_instance: BillInstance) -> Envelope:
    """
    Create an envelope for the late bill.
    
    Parameters
    ----------
    late_bill_instance : BillInstance
        The bill instance for this envelope.
        
    Returns
    -------
    Envelope
        Envelope with no initial allocation.
    """
    return Envelope(bill_instance=late_bill_instance)

########################################################################
## CASCADE (DUE DATE) SORTING TESTS
########################################################################

class TestCascadeSorting:
    """
    Test cascade (due date) sorting with various input mixes.
    """

    def test_cascade_single_envelope(
        self, envelope_small: Envelope
    ) -> None:
        """
        Test cascade allocation with a single envelope.
        """
        allocator = SortedAllocator("cascade")
        result = allocator.allocate(
            envelopes=[envelope_small],
            balance=Decimal("100.00")
        )
        
        # Test: Single envelope should receive full allocation up to
        # amount due.
        assert result.envelopes[envelope_small] == Decimal("50.00")

    def test_cascade_earliest_gets_funded_first(
        self,
        envelope_early: Envelope,
        envelope_medium: Envelope,
        envelope_late: Envelope
    ) -> None:
        """
        Test that earliest due date gets funded first in cascade
        allocation.
        """
        allocator = SortedAllocator("cascade")
        result = allocator.allocate(
            envelopes=[envelope_early, envelope_medium, envelope_late],
            balance=Decimal("200.00")
        )
        
        # Test: Early bill (Jan 15, $100) should be fully funded.
        assert result.envelopes[envelope_early] == Decimal("100.00")
        # Test: Medium bill (Feb 15, $150) should get remaining $100.
        assert result.envelopes[envelope_medium] == Decimal("100.00")
        # Test: Late bill (Apr 1, $200) should get nothing.
        assert result.envelopes[envelope_late] == Decimal("0.00")

    def test_cascade_ordering_invariant(
        self,
        envelope_early: Envelope,
        envelope_medium: Envelope,
        envelope_late: Envelope
    ) -> None:
        """
        Test that cascade allocation produces same results regardless of
        input envelope ordering.
        """
        allocator = SortedAllocator("cascade")
        balance = Decimal("200.00")
        
        # Test: Allocate with one ordering.
        result1 = allocator.allocate(
            envelopes=[envelope_early, envelope_medium, envelope_late],
            balance=balance
        )
        
        # Test: Allocate with different ordering.
        result2 = allocator.allocate(
            envelopes=[envelope_late, envelope_early, envelope_medium],
            balance=balance
        )
        
        # Test: Each envelope should receive the same allocation
        # regardless of input order.
        assert result1.envelopes[envelope_early] == (
            result2.envelopes[envelope_early]
        )
        assert result1.envelopes[envelope_medium] == (
            result2.envelopes[envelope_medium]
        )
        assert result1.envelopes[envelope_late] == (
            result2.envelopes[envelope_late]
        )

    def test_cascade_sufficient_balance_all_funded(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope
    ) -> None:
        """
        Test cascade allocation when balance is sufficient for all
        envelopes.
        """
        allocator = SortedAllocator("cascade")
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_medium],
            balance=Decimal("200.00")
        )
        
        # Test: Both envelopes should be fully funded.
        assert result.envelopes[envelope_small] == Decimal("50.00")
        assert result.envelopes[envelope_medium] == Decimal("150.00")

    def test_cascade_insufficient_balance_partial_funding(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope,
        envelope_large: Envelope
    ) -> None:
        """
        Test cascade allocation when balance is insufficient for all
        envelopes.
        """
        allocator = SortedAllocator("cascade")
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_medium, envelope_large],
            balance=Decimal("100.00")
        )
        
        # Test: Small bill (earliest, $50) should be fully funded.
        assert result.envelopes[envelope_small] == Decimal("50.00")
        # Test: Medium bill (next, $150) should get remaining $50.
        assert result.envelopes[envelope_medium] == Decimal("50.00")
        # Test: Large bill (latest, $500) should get nothing.
        assert result.envelopes[envelope_large] == Decimal("0.00")

    def test_cascade_same_due_date_order_preserved(
        self,
        envelope_small: Envelope
    ) -> None:
        """
        Test that envelopes with same due date maintain relative order.
        """
        # Create two bills with same due date.
        bill1 = BillInstance(
            bill_id="bill1",
            service="Bill 1",
            due_date=datetime.date(2024, 2, 1),
            amount_due=Decimal("50.00")
        )
        bill2 = BillInstance(
            bill_id="bill2",
            service="Bill 2",
            due_date=datetime.date(2024, 2, 1),
            amount_due=Decimal("100.00")
        )
        env1 = Envelope(bill_instance=bill1)
        env2 = Envelope(bill_instance=bill2)
        
        allocator = SortedAllocator("cascade")
        result = allocator.allocate(
            envelopes=[env1, env2],
            balance=Decimal("75.00")
        )
        
        # Test: First envelope should be fully funded first.
        assert result.envelopes[env1] == Decimal("50.00")
        # Test: Second envelope should get remaining.
        assert result.envelopes[env2] == Decimal("25.00")

########################################################################
## DEBT SNOWBALL (AMOUNT) SORTING TESTS
########################################################################

class TestDebtSnowballSorting:
    """
    Test debt snowball (amount-based) sorting with various input mixes.
    """

    def test_debt_snowball_single_envelope(
        self, envelope_small: Envelope
    ) -> None:
        """
        Test debt snowball allocation with a single envelope.
        """
        allocator = SortedAllocator("debt_snowball")
        result = allocator.allocate(
            envelopes=[envelope_small],
            balance=Decimal("100.00")
        )
        
        # Test: Single envelope should receive full allocation up to
        # amount due.
        assert result.envelopes[envelope_small] == Decimal("50.00")

    def test_debt_snowball_smallest_gets_funded_first(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope,
        envelope_large: Envelope
    ) -> None:
        """
        Test that smallest amount gets funded first in debt snowball
        allocation.
        """
        allocator = SortedAllocator("debt_snowball")
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_medium, envelope_large],
            balance=Decimal("200.00")
        )
        
        # Test: Small bill ($50) should be fully funded.
        assert result.envelopes[envelope_small] == Decimal("50.00")
        # Test: Medium bill ($150) should get remaining $150.
        assert result.envelopes[envelope_medium] == Decimal("150.00")
        # Test: Large bill ($500) should get nothing.
        assert result.envelopes[envelope_large] == Decimal("0.00")

    def test_debt_snowball_ordering_invariant(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope,
        envelope_large: Envelope
    ) -> None:
        """
        Test that debt snowball allocation produces same results
        regardless of input envelope ordering.
        """
        allocator = SortedAllocator("debt_snowball")
        balance = Decimal("200.00")
        
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
        # regardless of input order.
        assert result1.envelopes[envelope_small] == (
            result2.envelopes[envelope_small]
        )
        assert result1.envelopes[envelope_medium] == (
            result2.envelopes[envelope_medium]
        )
        assert result1.envelopes[envelope_large] == (
            result2.envelopes[envelope_large]
        )

    def test_debt_snowball_sufficient_balance_all_funded(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope
    ) -> None:
        """
        Test debt snowball allocation when balance is sufficient for all
        envelopes.
        """
        allocator = SortedAllocator("debt_snowball")
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_medium],
            balance=Decimal("200.00")
        )
        
        # Test: Both envelopes should be fully funded.
        assert result.envelopes[envelope_small] == Decimal("50.00")
        assert result.envelopes[envelope_medium] == Decimal("150.00")

    def test_debt_snowball_insufficient_balance_partial_funding(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope,
        envelope_large: Envelope
    ) -> None:
        """
        Test debt snowball allocation when balance is insufficient for
        all envelopes.
        """
        allocator = SortedAllocator("debt_snowball")
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_medium, envelope_large],
            balance=Decimal("100.00")
        )
        
        # Test: Small bill ($50) should be fully funded.
        assert result.envelopes[envelope_small] == Decimal("50.00")
        # Test: Medium bill ($150) should get remaining $50.
        assert result.envelopes[envelope_medium] == Decimal("50.00")
        # Test: Large bill ($500) should get nothing.
        assert result.envelopes[envelope_large] == Decimal("0.00")

    def test_debt_snowball_same_amount_order_preserved(
        self,
        envelope_small: Envelope
    ) -> None:
        """
        Test that envelopes with same amount maintain relative order.
        """
        # Create two bills with same amount.
        bill1 = BillInstance(
            bill_id="bill1",
            service="Bill 1",
            due_date=datetime.date(2024, 2, 1),
            amount_due=Decimal("50.00")
        )
        bill2 = BillInstance(
            bill_id="bill2",
            service="Bill 2",
            due_date=datetime.date(2024, 2, 15),
            amount_due=Decimal("50.00")
        )
        env1 = Envelope(bill_instance=bill1)
        env2 = Envelope(bill_instance=bill2)
        
        allocator = SortedAllocator("debt_snowball")
        result = allocator.allocate(
            envelopes=[env1, env2],
            balance=Decimal("75.00")
        )
        
        # Test: First envelope should be fully funded first.
        assert result.envelopes[env1] == Decimal("50.00")
        # Test: Second envelope should get remaining.
        assert result.envelopes[env2] == Decimal("25.00")

########################################################################
## REVERSE SORTING TESTS
########################################################################

class TestReverseSorting:
    """
    Test reverse sorting with various input mixes.
    """

    def test_cascade_reverse_latest_gets_funded_first(
        self,
        envelope_early: Envelope,
        envelope_medium: Envelope,
        envelope_late: Envelope
    ) -> None:
        """
        Test that reverse cascade allocates to latest due date first.
        """
        allocator = SortedAllocator("cascade", reverse=True)
        result = allocator.allocate(
            envelopes=[envelope_early, envelope_medium, envelope_late],
            balance=Decimal("200.00")
        )
        
        # Test: Late bill (Apr 1, $200) should be fully funded.
        assert result.envelopes[envelope_late] == Decimal("200.00")
        # Test: Medium and early bills should get nothing.
        assert result.envelopes[envelope_medium] == Decimal("0.00")
        assert result.envelopes[envelope_early] == Decimal("0.00")

    def test_debt_snowball_reverse_largest_gets_funded_first(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope,
        envelope_large: Envelope
    ) -> None:
        """
        Test that reverse debt snowball allocates to largest amount
        first.
        """
        allocator = SortedAllocator("debt_snowball", reverse=True)
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_medium, envelope_large],
            balance=Decimal("200.00")
        )
        
        # Test: Large bill ($500) should get full $200.
        assert result.envelopes[envelope_large] == Decimal("200.00")
        # Test: Medium and small bills should get nothing.
        assert result.envelopes[envelope_medium] == Decimal("0.00")
        assert result.envelopes[envelope_small] == Decimal("0.00")

    def test_reverse_ordering_invariant(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope,
        envelope_large: Envelope
    ) -> None:
        """
        Test that reverse allocation produces same results regardless of
        input envelope ordering.
        """
        allocator = SortedAllocator("debt_snowball", reverse=True)
        balance = Decimal("200.00")
        
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
        # regardless of input order.
        assert result1.envelopes[envelope_small] == (
            result2.envelopes[envelope_small]
        )
        assert result1.envelopes[envelope_medium] == (
            result2.envelopes[envelope_medium]
        )
        assert result1.envelopes[envelope_large] == (
            result2.envelopes[envelope_large]
        )

########################################################################
## CUSTOM SORT KEY TESTS
########################################################################

class TestCustomSortKey:
    """
    Test custom sort key functions with various input mixes.
    """

    def test_custom_sort_key_function(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope,
        envelope_large: Envelope
    ) -> None:
        """
        Test allocation with a custom sort key function.
        """
        def custom_sort(envelope: Envelope, **kwargs: Any) -> float:
            """
            Custom sort key that prioritizes by service name.
            """
            # Sort alphabetically by service name.
            return envelope.bill_instance.service
        
        allocator = SortedAllocator(custom_sort)
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_medium, envelope_large],
            balance=Decimal("200.00")
        )
        
        # Test: Should allocate in alphabetical order of service names.
        # "Large Bill" < "Medium Bill" < "Small Bill" alphabetically.
        # So Large should get funded first.
        assert result.envelopes[envelope_large] == Decimal("200.00")
        assert result.envelopes[envelope_medium] == Decimal("0.00")
        assert result.envelopes[envelope_small] == Decimal("0.00")

    def test_custom_sort_key_ordering_invariant(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope
    ) -> None:
        """
        Test that custom sort key produces same results regardless of
        input envelope ordering.
        """
        def custom_sort(envelope: Envelope, **kwargs: Any) -> Decimal:
            """
            Custom sort key based on bill amount.
            """
            return envelope.bill_instance.amount_due
        
        allocator = SortedAllocator(custom_sort)
        balance = Decimal("200.00")
        
        # Test: Allocate with one ordering.
        result1 = allocator.allocate(
            envelopes=[envelope_small, envelope_medium],
            balance=balance
        )
        
        # Test: Allocate with different ordering.
        result2 = allocator.allocate(
            envelopes=[envelope_medium, envelope_small],
            balance=balance
        )
        
        # Test: Each envelope should receive the same allocation
        # regardless of input order.
        assert result1.envelopes[envelope_small] == (
            result2.envelopes[envelope_small]
        )
        assert result1.envelopes[envelope_medium] == (
            result2.envelopes[envelope_medium]
        )

    def test_custom_sort_key_with_kwargs(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope
    ) -> None:
        """
        Test custom sort key that uses keyword arguments.
        """
        def custom_sort(
            envelope: Envelope, priority: dict[str, int], **kwargs: Any
        ) -> int:
            """
            Custom sort key that uses priority mapping from kwargs.
            """
            bill_id = envelope.bill_instance.bill_id
            return priority.get(bill_id, 99)
        
        priority_map = {
            "medium_bill": 1,
            "small_bill": 2
        }
        
        allocator = SortedAllocator(custom_sort)
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_medium],
            balance=Decimal("200.00"),
            priority=priority_map
        )
        
        # Test: Medium bill (priority 1) should be funded first.
        assert result.envelopes[envelope_medium] == Decimal("150.00")
        # Test: Small bill (priority 2) should get remaining.
        assert result.envelopes[envelope_small] == Decimal("50.00")

########################################################################
## EDGE CASE TESTS
########################################################################

class TestEdgeCases:
    """
    Test edge cases including zero balance, boundary conditions, and
    special scenarios.
    """

    def test_zero_balance(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope
    ) -> None:
        """
        Test allocation with zero balance.
        """
        allocator = SortedAllocator("cascade")
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_medium],
            balance=Decimal("0.00")
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
        allocator = SortedAllocator("cascade")
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_medium],
            balance=Decimal("0.01")
        )
        
        # Test: First envelope should get the small amount.
        assert result.envelopes[envelope_small] == Decimal("0.01")
        # Test: Second envelope should get nothing.
        assert result.envelopes[envelope_medium] == Decimal("0.00")

    def test_very_large_balance(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope
    ) -> None:
        """
        Test allocation with very large balance.
        """
        allocator = SortedAllocator("cascade")
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_medium],
            balance=Decimal("1000000.00")
        )
        
        # Test: Both envelopes should be fully funded.
        assert result.envelopes[envelope_small] == Decimal("50.00")
        assert result.envelopes[envelope_medium] == Decimal("150.00")

    def test_single_envelope_ordering(
        self, envelope_small: Envelope
    ) -> None:
        """
        Test that single envelope allocation is consistent.
        """
        allocator = SortedAllocator("cascade")
        result1 = allocator.allocate(
            envelopes=[envelope_small],
            balance=Decimal("100.00")
        )
        result2 = allocator.allocate(
            envelopes=[envelope_small],
            balance=Decimal("100.00")
        )
        
        # Test: Results should be identical.
        assert result1.envelopes[envelope_small] == (
            result2.envelopes[envelope_small]
        )

    def test_exact_balance_match(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope
    ) -> None:
        """
        Test allocation when balance exactly matches total amount due.
        """
        allocator = SortedAllocator("cascade")
        total_due = envelope_small.bill_instance.amount_due + (
            envelope_medium.bill_instance.amount_due
        )
        result = allocator.allocate(
            envelopes=[envelope_small, envelope_medium],
            balance=total_due
        )
        
        # Test: Both envelopes should be fully funded.
        assert result.envelopes[envelope_small] == Decimal("50.00")
        assert result.envelopes[envelope_medium] == Decimal("150.00")

    def test_balance_less_than_first_envelope(
        self,
        envelope_medium: Envelope,
        envelope_large: Envelope
    ) -> None:
        """
        Test allocation when balance is less than first envelope amount.
        """
        allocator = SortedAllocator("cascade")
        result = allocator.allocate(
            envelopes=[envelope_medium, envelope_large],
            balance=Decimal("50.00")
        )
        
        # Test: First envelope should get partial funding.
        assert result.envelopes[envelope_medium] == Decimal("50.00")
        # Test: Second envelope should get nothing.
        assert result.envelopes[envelope_large] == Decimal("0.00")

    def test_ordering_invariant_with_many_envelopes(
        self,
        envelope_small: Envelope,
        envelope_medium: Envelope,
        envelope_large: Envelope
    ) -> None:
        """
        Test ordering invariance with multiple envelopes in different
        orders.
        """
        allocator = SortedAllocator("cascade")
        balance = Decimal("300.00")
        
        # Test: Multiple different orderings should produce same results.
        orders = [
            [envelope_small, envelope_medium, envelope_large],
            [envelope_large, envelope_small, envelope_medium],
            [envelope_medium, envelope_large, envelope_small],
            [envelope_medium, envelope_small, envelope_large],
        ]
        
        results = []
        for order in orders:
            result = allocator.allocate(envelopes=order, balance=balance)
            results.append(result)
        
        # Test: All results should have same allocations for each
        # envelope.
        for i in range(1, len(results)):
            assert results[0].envelopes[envelope_small] == (
                results[i].envelopes[envelope_small]
            )
            assert results[0].envelopes[envelope_medium] == (
                results[i].envelopes[envelope_medium]
            )
            assert results[0].envelopes[envelope_large] == (
                results[i].envelopes[envelope_large]
            )

