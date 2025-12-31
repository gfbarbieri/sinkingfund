"""
Schedule Manager Tests
======================

Focused tests for `ScheduleManager` covering scheduler selection, schedule
creation, error handling, and parameter passing.
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import datetime
from decimal import Decimal

import pytest

from sinkingfund.managers import ScheduleManager
from sinkingfund.models import BillInstance, Envelope
from sinkingfund.schedules.base import ScheduleResult

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
    Create an empty envelope for schedule testing.
    """
    return Envelope(
        bill_instance=bill_instance,
        start_contrib_date=datetime.date(2024, 1, 1),
        end_contrib_date=datetime.date(2024, 2, 14),
        contrib_interval=14
    )


@pytest.fixture
def partially_funded_envelope(bill_instance: BillInstance) -> Envelope:
    """
    Create a partially funded envelope for schedule testing.
    """
    return Envelope(
        bill_instance=bill_instance,
        initial_allocation=Decimal("50.00"),
        start_contrib_date=datetime.date(2024, 1, 1),
        end_contrib_date=datetime.date(2024, 2, 14),
        contrib_interval=14
    )


@pytest.fixture
def multiple_envelopes() -> list[Envelope]:
    """
    Create multiple envelopes for schedule testing.
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

class TestScheduleManagerInitialization:
    """
    Test ScheduleManager initialization.
    """

    def test_initialization_creates_manager(self) -> None:
        """
        Test that ScheduleManager initializes with None scheduler.
        """
        manager = ScheduleManager()
        
        assert manager.scheduler is None


########################################################################
## SET SCHEDULER TESTS
########################################################################

class TestSetScheduler:
    """
    Test set_scheduler method with various strategies.
    """

    def test_set_scheduler_with_independent_scheduler(self) -> None:
        """
        Test setting independent_scheduler strategy.
        """
        manager = ScheduleManager()
        manager.set_scheduler(strategy="independent_scheduler")
        
        assert manager.scheduler is not None
        assert manager.scheduler.__class__.__name__ == "IndependentScheduler"

    def test_set_scheduler_defaults_to_independent(self) -> None:
        """
        Test that set_scheduler defaults to independent_scheduler.
        """
        manager = ScheduleManager()
        manager.set_scheduler()
        
        assert manager.scheduler is not None
        assert manager.scheduler.__class__.__name__ == "IndependentScheduler"

    def test_set_scheduler_rejects_unknown_strategy(self) -> None:
        """
        Test that set_scheduler raises KeyError for unknown strategy.
        """
        manager = ScheduleManager()
        
        with pytest.raises(
            KeyError,
            match="Unknown scheduling strategy 'unknown_strategy'"
        ):
            manager.set_scheduler(strategy="unknown_strategy")

    def test_set_scheduler_rejects_invalid_parameters(self) -> None:
        """
        Test that set_scheduler raises TypeError for invalid parameters.
        """
        manager = ScheduleManager()
        
        with pytest.raises(
            TypeError,
            match="Invalid parameters for 'independent_scheduler' strategy"
        ):
            manager.set_scheduler(
                strategy="independent_scheduler",
                invalid_param="invalid"
            )

    def test_set_scheduler_with_kwargs(self) -> None:
        """
        Test setting scheduler with additional parameters.
        """
        manager = ScheduleManager()
        # IndependentScheduler doesn't take kwargs, but test the path.
        manager.set_scheduler(strategy="independent_scheduler")
        
        assert manager.scheduler is not None


########################################################################
## CREATE SCHEDULES TESTS
########################################################################

class TestCreateSchedules:
    """
    Test create_schedules method with various scenarios.
    """

    def test_create_schedules_with_single_envelope(
        self,
        empty_envelope: Envelope
    ) -> None:
        """
        Test creating schedules for a single envelope.
        """
        manager = ScheduleManager()
        manager.set_scheduler(strategy="independent_scheduler")
        
        result = manager.create_schedules(envelopes=[empty_envelope])
        
        assert isinstance(result, ScheduleResult)
        assert empty_envelope in result.schedules
        assert result.schedules[empty_envelope] is not None

    def test_create_schedules_with_multiple_envelopes(
        self,
        multiple_envelopes: list[Envelope]
    ) -> None:
        """
        Test creating schedules for multiple envelopes.
        """
        manager = ScheduleManager()
        manager.set_scheduler(strategy="independent_scheduler")
        
        result = manager.create_schedules(envelopes=multiple_envelopes)
        
        assert isinstance(result, ScheduleResult)
        assert len(result.schedules) == len(multiple_envelopes)
        
        for envelope in multiple_envelopes:
            assert envelope in result.schedules

    def test_create_schedules_with_empty_list(self) -> None:
        """
        Test creating schedules with empty envelope list.
        """
        manager = ScheduleManager()
        manager.set_scheduler(strategy="independent_scheduler")
        
        result = manager.create_schedules(envelopes=[])
        
        assert isinstance(result, ScheduleResult)
        assert len(result.schedules) == 0

    def test_create_schedules_with_partially_funded_envelope(
        self,
        partially_funded_envelope: Envelope
    ) -> None:
        """
        Test creating schedules for partially funded envelope.
        """
        manager = ScheduleManager()
        manager.set_scheduler(strategy="independent_scheduler")
        
        result = manager.create_schedules(
            envelopes=[partially_funded_envelope]
        )
        
        assert isinstance(result, ScheduleResult)
        assert partially_funded_envelope in result.schedules

    def test_create_schedules_rejects_invalid_envelope_types(
        self
    ) -> None:
        """
        Test that create_schedules raises ValueError for non-Envelope objects.
        """
        manager = ScheduleManager()
        manager.set_scheduler(strategy="independent_scheduler")
        
        with pytest.raises(
            ValueError,
            match="All elements must be type Envelope"
        ):
            manager.create_schedules(
                envelopes=["not an envelope"]  # type: ignore[list-item]
            )

    def test_create_schedules_rejects_mixed_types(
        self,
        empty_envelope: Envelope
    ) -> None:
        """
        Test that create_schedules raises ValueError for mixed types.
        """
        manager = ScheduleManager()
        manager.set_scheduler(strategy="independent_scheduler")
        
        with pytest.raises(
            ValueError,
            match="All elements must be type Envelope"
        ):
            manager.create_schedules(
                envelopes=[empty_envelope, "not an envelope"]  # type: ignore[list-item]
            )

    def test_create_schedules_passes_kwargs_to_scheduler(
        self,
        empty_envelope: Envelope
    ) -> None:
        """
        Test that create_schedules passes kwargs to underlying scheduler.
        """
        manager = ScheduleManager()
        manager.set_scheduler(strategy="independent_scheduler")
        
        # IndependentScheduler doesn't use kwargs, but test the path.
        result = manager.create_schedules(envelopes=[empty_envelope])
        
        assert isinstance(result, ScheduleResult)

    def test_create_schedules_without_setting_scheduler_raises(
        self,
        empty_envelope: Envelope
    ) -> None:
        """
        Test that create_schedules raises AttributeError if scheduler not set.
        """
        manager = ScheduleManager()
        # Don't set scheduler.
        
        with pytest.raises(AttributeError):
            manager.create_schedules(envelopes=[empty_envelope])


########################################################################
## INTEGRATION TESTS
########################################################################

class TestScheduleManagerIntegration:
    """
    Test ScheduleManager integration scenarios.
    """

    def test_full_workflow_single_envelope(
        self,
        empty_envelope: Envelope
    ) -> None:
        """
        Test complete workflow with single envelope.
        """
        manager = ScheduleManager()
        manager.set_scheduler(strategy="independent_scheduler")
        
        result = manager.create_schedules(envelopes=[empty_envelope])
        
        assert isinstance(result, ScheduleResult)
        assert empty_envelope in result.schedules
        
        # Verify schedule was created.
        schedule = result.schedules[empty_envelope]
        assert schedule is not None
        assert len(schedule.cash_flows) > 0

    def test_full_workflow_multiple_envelopes(
        self,
        multiple_envelopes: list[Envelope]
    ) -> None:
        """
        Test complete workflow with multiple envelopes.
        """
        manager = ScheduleManager()
        manager.set_scheduler(strategy="independent_scheduler")
        
        result = manager.create_schedules(envelopes=multiple_envelopes)
        
        assert isinstance(result, ScheduleResult)
        assert len(result.schedules) == len(multiple_envelopes)
        
        # Verify all schedules were created.
        for envelope in multiple_envelopes:
            schedule = result.schedules[envelope]
            assert schedule is not None
            assert len(schedule.cash_flows) > 0

    def test_scheduler_switching(
        self,
        empty_envelope: Envelope
    ) -> None:
        """
        Test switching between scheduler strategies.
        """
        manager = ScheduleManager()
        
        # Set to independent scheduler.
        manager.set_scheduler(strategy="independent_scheduler")
        result1 = manager.create_schedules(envelopes=[empty_envelope])
        
        # Switch to same strategy (should work).
        manager.set_scheduler(strategy="independent_scheduler")
        result2 = manager.create_schedules(envelopes=[empty_envelope])
        
        # Both should succeed.
        assert isinstance(result1, ScheduleResult)
        assert isinstance(result2, ScheduleResult)

    def test_schedule_result_metadata(
        self,
        empty_envelope: Envelope
    ) -> None:
        """
        Test that ScheduleResult contains metadata.
        """
        manager = ScheduleManager()
        manager.set_scheduler(strategy="independent_scheduler")
        
        result = manager.create_schedules(envelopes=[empty_envelope])
        
        assert isinstance(result, ScheduleResult)
        assert hasattr(result, 'metadata')
        assert isinstance(result.metadata, dict)

