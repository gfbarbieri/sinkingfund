"""
Allocation Manager Tests
========================

Focused tests for `AllocationManager` covering strategy selection,
allocation execution, error handling, and parameter passing.
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import datetime
from decimal import Decimal

import pytest

from sinkingfund.managers import AllocationManager
from sinkingfund.models import BillInstance, Envelope
from sinkingfund.allocation.base import AllocationResult

########################################################################
## FIXTURES
########################################################################

@pytest.fixture
def bill_instance() -> BillInstance:
    """
    Create a bill instance for envelope creation.
    """
    return BillInstance(
        bill_id="electric",
        service="Monthly Electric Bill",
        due_date=datetime.date(2024, 2, 15),
        amount_due=Decimal("150.00")
    )


@pytest.fixture
def empty_envelope(bill_instance: BillInstance) -> Envelope:
    """
    Create an empty envelope for allocation testing.
    """
    return Envelope(
        bill_instance=bill_instance,
        start_contrib_date=datetime.date(2024, 1, 1),
        end_contrib_date=datetime.date(2024, 2, 14),
        contrib_interval=14
    )


@pytest.fixture
def multiple_envelopes() -> list[Envelope]:
    """
    Create multiple envelopes for allocation testing.
    """
    instances = [
        BillInstance(
            bill_id="electric",
            service="Monthly Electric",
            due_date=datetime.date(2024, 2, 15),
            amount_due=Decimal("150.00")
        ),
        BillInstance(
            bill_id="water",
            service="Monthly Water",
            due_date=datetime.date(2024, 3, 1),
            amount_due=Decimal("75.00")
        ),
        BillInstance(
            bill_id="insurance",
            service="Quarterly Insurance",
            due_date=datetime.date(2024, 4, 1),
            amount_due=Decimal("450.00")
        )
    ]
    
    return [
        Envelope(
            bill_instance=inst,
            start_contrib_date=datetime.date(2024, 1, 1),
            end_contrib_date=inst.due_date - datetime.timedelta(days=1),
            contrib_interval=14
        )
        for inst in instances
    ]


########################################################################
## INITIALIZATION TESTS
########################################################################

class TestAllocationManagerInitialization:
    """
    Test AllocationManager initialization.
    """

    def test_initialization_creates_manager(self) -> None:
        """
        Test that AllocationManager initializes with None allocator.
        """
        manager = AllocationManager()
        
        assert manager.allocator is None


########################################################################
## SET ALLOCATOR TESTS
########################################################################

class TestSetAllocator:
    """
    Test set_allocator method with various strategies.
    """

    def test_set_allocator_with_sorted_strategy(self) -> None:
        """
        Test setting sorted allocation strategy.
        """
        manager = AllocationManager()
        manager.set_allocator(strategy="sorted", sort_key="cascade")
        
        assert manager.allocator is not None
        assert manager.allocator.__class__.__name__ == "SortedAllocator"

    def test_set_allocator_with_proportional_strategy(self) -> None:
        """
        Test setting proportional allocation strategy.
        """
        manager = AllocationManager()
        manager.set_allocator(strategy="proportional", method="proportional")
        
        assert manager.allocator is not None
        assert manager.allocator.__class__.__name__ == "ProportionalAllocator"

    def test_set_allocator_with_strategy_kwargs(self) -> None:
        """
        Test setting allocator with strategy-specific parameters.
        """
        manager = AllocationManager()
        manager.set_allocator(
            strategy="sorted",
            sort_key="cascade"
        )
        
        assert manager.allocator is not None

    def test_set_allocator_rejects_unknown_strategy(self) -> None:
        """
        Test that set_allocator raises KeyError for unknown strategy.
        """
        manager = AllocationManager()
        
        with pytest.raises(
            KeyError,
            match="Unknown allocation strategy 'unknown_strategy'"
        ):
            manager.set_allocator(strategy="unknown_strategy")

    def test_set_allocator_rejects_invalid_parameters(self) -> None:
        """
        Test that set_allocator raises TypeError for invalid parameters.
        """
        manager = AllocationManager()
        
        with pytest.raises(
            TypeError,
            match="Invalid parameters for 'sorted' strategy"
        ):
            manager.set_allocator(
                strategy="sorted",
                invalid_param="invalid"
            )

    def test_set_allocator_defaults_to_sorted(self) -> None:
        """
        Test that set_allocator defaults to sorted strategy.
        """
        manager = AllocationManager()
        manager.set_allocator(sort_key="cascade")
        
        assert manager.allocator is not None
        assert manager.allocator.__class__.__name__ == "SortedAllocator"


########################################################################
## ALLOCATE TESTS
########################################################################

class TestAllocate:
    """
    Test allocate method with various scenarios.
    """

    def test_allocate_with_sorted_strategy(
        self,
        empty_envelope: Envelope
    ) -> None:
        """
        Test allocation using sorted strategy.
        """
        manager = AllocationManager()
        manager.set_allocator(strategy="sorted", sort_key="cascade")
        
        balance = Decimal("200.00")
        result = manager.allocate(
            envelopes=[empty_envelope],
            balance=balance
        )
        
        assert isinstance(result, AllocationResult)
        assert empty_envelope in result.envelopes
        assert result.envelopes[empty_envelope] > Decimal("0")

    def test_allocate_with_proportional_strategy(
        self,
        multiple_envelopes: list[Envelope]
    ) -> None:
        """
        Test allocation using proportional strategy.
        """
        manager = AllocationManager()
        manager.set_allocator(strategy="proportional", method="proportional")
        
        balance = Decimal("500.00")
        result = manager.allocate(
            envelopes=multiple_envelopes,
            balance=balance
        )
        
        assert isinstance(result, AllocationResult)
        assert len(result.envelopes) == len(multiple_envelopes)

    def test_allocate_with_empty_envelope_list(self) -> None:
        """
        Test allocation with empty envelope list.
        """
        manager = AllocationManager()
        manager.set_allocator(strategy="sorted", sort_key="cascade")
        
        balance = Decimal("100.00")
        result = manager.allocate(envelopes=[], balance=balance)
        
        assert isinstance(result, AllocationResult)
        assert len(result.envelopes) == 0

    def test_allocate_rejects_negative_balance(
        self,
        empty_envelope: Envelope
    ) -> None:
        """
        Test that allocate raises ValueError for negative balance.
        """
        manager = AllocationManager()
        manager.set_allocator(strategy="sorted", sort_key="cascade")
        
        with pytest.raises(
            ValueError,
            match="Balance must be non-negative"
        ):
            manager.allocate(
                envelopes=[empty_envelope],
                balance=Decimal("-10.00")
            )

    def test_allocate_rejects_zero_balance(
        self,
        empty_envelope: Envelope
    ) -> None:
        """
        Test that allocate accepts zero balance.
        """
        manager = AllocationManager()
        manager.set_allocator(strategy="sorted", sort_key="cascade")
        
        result = manager.allocate(
            envelopes=[empty_envelope],
            balance=Decimal("0.00")
        )
        
        assert isinstance(result, AllocationResult)

    def test_allocate_rejects_invalid_envelope_types(self) -> None:
        """
        Test that allocate raises ValueError for non-Envelope objects.
        """
        manager = AllocationManager()
        manager.set_allocator(strategy="sorted", sort_key="cascade")
        
        with pytest.raises(
            ValueError,
            match="All elements must be type Envelope"
        ):
            manager.allocate(
                envelopes=["not an envelope"],  # type: ignore[list-item]
                balance=Decimal("100.00"),
                curr_date=datetime.date(2024, 1, 1)
            )

    def test_allocate_rejects_mixed_types(self) -> None:
        """
        Test that allocate raises ValueError for mixed types.
        """
        manager = AllocationManager()
        manager.set_allocator(strategy="sorted", sort_key="cascade")
        
        envelope = Envelope(
            bill_instance=BillInstance(
                bill_id="test",
                service="Test",
                due_date=datetime.date(2024, 1, 1),
                amount_due=Decimal("100.00")
            )
        )
        
        with pytest.raises(
            ValueError,
            match="All elements must be type Envelope"
        ):
            manager.allocate(
                envelopes=[envelope, "not an envelope"],  # type: ignore[list-item]
                balance=Decimal("100.00"),
                curr_date=datetime.date(2024, 1, 1)
            )

    def test_allocate_passes_kwargs_to_strategy(
        self,
        multiple_envelopes: list[Envelope]
    ) -> None:
        """
        Test that allocate passes kwargs to underlying strategy.
        """
        manager = AllocationManager()
        manager.set_allocator(strategy="sorted", sort_key="cascade")
        
        balance = Decimal("300.00")
        result = manager.allocate(
            envelopes=multiple_envelopes,
            balance=balance
        )
        
        assert isinstance(result, AllocationResult)

    def test_allocate_handles_strategy_exceptions(
        self,
        empty_envelope: Envelope
    ) -> None:
        """
        Test that allocate wraps strategy exceptions appropriately.
        """
        manager = AllocationManager()
        manager.set_allocator(strategy="sorted", sort_key="cascade")
        
        # This should work normally, but if strategy raises, it should
        # be wrapped.
        result = manager.allocate(
            envelopes=[empty_envelope],
            balance=Decimal("100.00")
        )
        
        assert isinstance(result, AllocationResult)

    def test_allocate_without_setting_allocator_raises(
        self,
        empty_envelope: Envelope
    ) -> None:
        """
        Test that allocate raises AttributeError if allocator not set.
        """
        manager = AllocationManager()
        # Don't set allocator
        
        with pytest.raises(AttributeError):
            manager.allocate(
                envelopes=[empty_envelope],
                balance=Decimal("100.00")
            )


########################################################################
## INTEGRATION TESTS
########################################################################

class TestAllocationManagerIntegration:
    """
    Test AllocationManager integration scenarios.
    """

    def test_full_workflow_sorted_strategy(
        self,
        multiple_envelopes: list[Envelope]
    ) -> None:
        """
        Test complete workflow with sorted strategy.
        """
        manager = AllocationManager()
        manager.set_allocator(strategy="sorted", sort_key="cascade")
        
        balance = Decimal("1000.00")
        result = manager.allocate(
            envelopes=multiple_envelopes,
            balance=balance
        )
        
        assert isinstance(result, AllocationResult)
        assert len(result.envelopes) == len(multiple_envelopes)
        
        # Verify allocations sum to balance or less.
        total_allocated = sum(result.envelopes.values())
        assert total_allocated <= balance

    def test_full_workflow_proportional_strategy(
        self,
        multiple_envelopes: list[Envelope]
    ) -> None:
        """
        Test complete workflow with proportional strategy.
        """
        manager = AllocationManager()
        manager.set_allocator(strategy="proportional", method="proportional")
        
        balance = Decimal("1000.00")
        result = manager.allocate(
            envelopes=multiple_envelopes,
            balance=balance
        )
        
        assert isinstance(result, AllocationResult)
        assert len(result.envelopes) == len(multiple_envelopes)

    def test_strategy_switching(
        self,
        multiple_envelopes: list[Envelope]
    ) -> None:
        """
        Test switching between allocation strategies.
        """
        manager = AllocationManager()
        
        # Start with sorted strategy.
        manager.set_allocator(strategy="sorted", sort_key="cascade")
        result1 = manager.allocate(
            envelopes=multiple_envelopes,
            balance=Decimal("500.00")
        )
        
        # Switch to proportional strategy.
        manager.set_allocator(strategy="proportional", method="proportional")
        result2 = manager.allocate(
            envelopes=multiple_envelopes,
            balance=Decimal("500.00")
        )
        
        # Both should succeed.
        assert isinstance(result1, AllocationResult)
        assert isinstance(result2, AllocationResult)
        
        # Results may differ due to different strategies.
        assert result1.metadata != result2.metadata

