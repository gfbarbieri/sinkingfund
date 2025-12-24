"""
Envelope Manager Tests
======================

Focused tests for `EnvelopeManager` covering envelope registration,
duplicate validation, contribution scheduling, allocation and schedule
assignment, and cash-flow aggregation helpers.
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import datetime
from decimal import Decimal

import pytest

from sinkingfund.managers import EnvelopeManager
from sinkingfund.models import (
    BillInstance,
    CashFlow,
    CashFlowSchedule,
    Envelope,
)
from sinkingfund.allocation.base import AllocationResult


########################################################################
## FIXTURES
########################################################################

@pytest.fixture
def one_time_bill_instance() -> BillInstance:
    """
    Create a simple one-time bill instance for envelope tests.
    """

    return BillInstance(
        bill_id="car_registration",
        service="Annual Car Registration",
        due_date=datetime.date(2024, 3, 15),
        amount_due=Decimal("125.00"),
    )


@pytest.fixture
def recurring_bill_instances() -> list[BillInstance]:
    """
    Create a pair of recurring bill instances for envelope tests.
    """

    return [
        BillInstance(
            bill_id="electric",
            service="Monthly Electric Bill",
            due_date=datetime.date(2024, 3, 15),
            amount_due=Decimal("150.00"),
        ),
        BillInstance(
            bill_id="electric",
            service="Monthly Electric Bill",
            due_date=datetime.date(2024, 4, 15),
            amount_due=Decimal("145.00"),
        ),
    ]


########################################################################
## ADD AND REMOVE ENVELOPES
########################################################################

class TestEnvelopeManagerAddAndRemove:
    """
    Test adding and removing envelopes within the manager.
    """

    def test_add_single_and_multiple_envelopes(
        self,
        one_time_bill_instance: BillInstance,
        recurring_bill_instances: list[BillInstance],
    ) -> None:
        """
        Test adding a single envelope and then a list of envelopes.
        """

        manager = EnvelopeManager()

        # Create envelopes from bill instances.
        envelopes = manager.create_envelopes(
            [one_time_bill_instance] + recurring_bill_instances
        )

        # Add a single envelope.
        manager.add_envelopes(envelopes[0])
        assert len(manager.envelopes) == 1

        # Add remaining envelopes via list input.
        manager.add_envelopes(envelopes[1:])
        assert len(manager.envelopes) == 3

    def test_add_envelopes_empty_list_is_noop(self) -> None:
        """
        Test that adding an empty list of envelopes is a no-op.
        """

        manager = EnvelopeManager()

        manager.add_envelopes([])
        assert len(manager.envelopes) == 0

    def test_add_envelopes_rejects_unsupported_type(self) -> None:
        """
        Test that add_envelopes rejects unsupported input types.
        """

        manager = EnvelopeManager()

        with pytest.raises(
            TypeError,
            match="Expected list\\[Envelope] or Envelope\\.",
        ):
            manager.add_envelopes("not an envelope")  # type: ignore[arg-type]

    def test_add_envelopes_rejects_duplicate_against_existing(
        self,
        one_time_bill_instance: BillInstance,
    ) -> None:
        """
        Test that adding an envelope with duplicate bill_id and due_date.
        """

        manager = EnvelopeManager()
        envelope = Envelope(bill_instance=one_time_bill_instance)
        manager.add_envelopes(envelope)

        duplicate = Envelope(bill_instance=one_time_bill_instance)

        with pytest.raises(
            ValueError,
            match=(
                "Envelope already exists for bill 'car_registration' "
                "due on 2024-03-15\\. Cannot add duplicate envelope\\."
            ),
        ):
            manager.add_envelopes(duplicate)

    def test_remove_envelope_success_and_missing(
        self,
        recurring_bill_instances: list[BillInstance],
    ) -> None:
        """
        Test removing an existing envelope and handling missing envelope.
        """

        manager = EnvelopeManager()
        envelopes = manager.create_envelopes(recurring_bill_instances)
        manager.add_envelopes(envelopes)

        # Remove existing envelope.
        manager.remove_envelope(
            bill_id="electric",
            due_date=datetime.date(2024, 3, 15),
        )
        assert len(manager.envelopes) == 1

        # Attempt to remove a non-existent envelope.
        with pytest.raises(
            ValueError,
            match=(
                "Envelope with bill_id 'unknown' does not exist. "
                "Cannot remove non-existent envelope\\."
            ),
        ):
            manager.remove_envelope(
                bill_id="unknown",
                due_date=datetime.date(2024, 3, 15),
            )


########################################################################
## ENVELOPE CREATION
########################################################################

class TestEnvelopeManagerCreateEnvelopes:
    """
    Test EnvelopeManager.create_envelopes.
    """

    def test_create_envelopes_from_bill_instances(
        self,
        recurring_bill_instances: list[BillInstance],
    ) -> None:
        """
        Test creating envelopes from bill instances list.
        """

        manager = EnvelopeManager()

        # Empty input returns empty list.
        assert manager.create_envelopes([]) == []

        envelopes = manager.create_envelopes(recurring_bill_instances)

        assert len(envelopes) == 2
        assert envelopes[0].bill_instance is recurring_bill_instances[0]
        assert envelopes[1].bill_instance is recurring_bill_instances[1]

########################################################################
## CONTRIBUTION SCHEDULING
########################################################################

class TestEnvelopeManagerSetContribDates:
    """
    Test contribution scheduling behavior and edge cases.
    """

    def test_set_contrib_dates_validates_positive_interval(self) -> None:
        """
        Test that non-positive contrib_interval raises ValueError.
        """

        manager = EnvelopeManager()

        with pytest.raises(
            ValueError,
            match="contrib_interval must be positive, got 0",
        ):
            manager.set_contrib_dates(
                start_contrib_date=datetime.date(2024, 1, 1),
                contrib_interval=0,
            )

    def test_set_contrib_dates_with_no_envelopes_is_noop(self) -> None:
        """
        Test that calling set_contrib_dates with no envelopes is a no-op.
        """

        manager = EnvelopeManager()

        manager.set_contrib_dates(
            start_contrib_date=datetime.date(2024, 1, 1),
            contrib_interval=14,
        )

        assert manager.envelopes == []

    def test_set_contrib_dates_for_fully_funded_and_underfunded(
        self,
        recurring_bill_instances: list[BillInstance],
    ) -> None:
        """
        Test scheduling for fully-funded and underfunded envelopes.
        """

        start = datetime.date(2024, 1, 1)
        manager = EnvelopeManager()

        # First envelope is fully funded as of start date.
        fully_funded = Envelope(
            bill_instance=recurring_bill_instances[0],
            initial_allocation=Decimal("150.00"),
        )

        # Second envelope is underfunded.
        underfunded = Envelope(
            bill_instance=recurring_bill_instances[1],
            initial_allocation=Decimal("0.00"),
        )

        manager.add_envelopes([fully_funded, underfunded])

        manager.set_contrib_dates(
            start_contrib_date=start,
            contrib_interval=14,
        )

        # Fully-funded envelope receives nominal scheduling.
        assert fully_funded.start_contrib_date == start
        assert fully_funded.end_contrib_date == datetime.date(2024, 3, 15)

        # Underfunded envelope should have a start date that is greater
        # than the first due date and aligned to contrib_interval steps
        # from the global start date.
        assert underfunded.start_contrib_date > datetime.date(2024, 3, 15)
        assert underfunded.end_contrib_date == datetime.date(2024, 4, 15)

        delta_days = (underfunded.start_contrib_date - start).days
        assert delta_days % 14 == 0

    def test_set_contrib_dates_for_single_underfunded_envelope(
        self,
        one_time_bill_instance: BillInstance,
    ) -> None:
        """
        Test scheduling for a single underfunded envelope.
        """

        start = datetime.date(2024, 1, 1)
        manager = EnvelopeManager()
        envelope = Envelope(
            bill_instance=one_time_bill_instance,
            initial_allocation=Decimal("0.00"),
        )
        manager.add_envelopes(envelope)

        manager.set_contrib_dates(
            start_contrib_date=start,
            contrib_interval=7,
        )

        assert envelope.start_contrib_date == start
        assert envelope.end_contrib_date == datetime.date(2024, 3, 15)
        assert envelope.contrib_interval == 7

########################################################################
## ALLOCATIONS AND SCHEDULES
########################################################################

class TestEnvelopeManagerAllocationsAndSchedules:
    """
    Test setting allocations and schedules on managed envelopes.
    """

    def test_set_allocations_with_dict(
        self,
        one_time_bill_instance: BillInstance,
        recurring_bill_instances: list[BillInstance],
    ) -> None:
        """
        Test set_allocations when provided a plain dictionary.
        """

        manager = EnvelopeManager()
        envelopes = manager.create_envelopes(
            [one_time_bill_instance] + recurring_bill_instances
        )
        manager.add_envelopes(envelopes)

        allocations = {
            envelopes[0]: Decimal("25.00"),
            envelopes[1]: Decimal("50.00"),
            envelopes[2]: Decimal("75.00"),
        }

        manager.set_allocations(allocations)

        for envelope, expected in allocations.items():
            found = manager._find_envelope(
                bill_id=envelope.bill_instance.bill_id,
                due_date=envelope.bill_instance.due_date,
            )
            assert found.initial_allocation == expected

    def test_set_allocations_with_allocation_result(
        self,
        one_time_bill_instance: BillInstance,
    ) -> None:
        """
        Test set_allocations when provided an AllocationResult.
        """

        manager = EnvelopeManager()
        envelope = Envelope(bill_instance=one_time_bill_instance)
        manager.add_envelopes(envelope)

        allocations = {envelope: Decimal("100.00")}
        result = AllocationResult(envelopes=allocations, metadata={})

        manager.set_allocations(result)

        found = manager._find_envelope(
            bill_id="car_registration",
            due_date=datetime.date(2024, 3, 15),
        )
        assert found.initial_allocation == Decimal("100.00")

    def test_set_schedules_assigns_cash_flow_schedules(
        self,
        recurring_bill_instances: list[BillInstance],
    ) -> None:
        """
        Test that set_schedules assigns schedules to envelopes.
        """

        manager = EnvelopeManager()
        envelopes = manager.create_envelopes(recurring_bill_instances)
        manager.add_envelopes(envelopes)

        schedule_first = CashFlowSchedule()
        schedule_first.add_cash_flows(
            CashFlow(
                bill_id="electric",
                date=datetime.date(2024, 1, 15),
                amount=Decimal("75.00"),
            ),
        )

        schedule_second = CashFlowSchedule()
        schedule_second.add_cash_flows(
            CashFlow(
                bill_id="electric",
                date=datetime.date(2024, 2, 15),
                amount=Decimal("70.00"),
            ),
        )

        manager.set_schedules(
            {
                envelopes[0]: schedule_first,
                envelopes[1]: schedule_second,
            }
        )

        first = manager._find_envelope(
            bill_id="electric",
            due_date=datetime.date(2024, 3, 15),
        )
        second = manager._find_envelope(
            bill_id="electric",
            due_date=datetime.date(2024, 4, 15),
        )

        assert first.schedule is schedule_first
        assert second.schedule is schedule_second

########################################################################
## BALANCE AND CASH FLOW HELPERS
########################################################################

class TestEnvelopeManagerBalanceAndCashFlows:
    """
    Test helper methods that aggregate balances and cash flows.
    """

    def test_get_balance_as_of_date_skips_before_start(
        self,
        one_time_bill_instance: BillInstance,
    ) -> None:
        """
        Test that balances skip envelopes before their start date.
        """

        manager = EnvelopeManager()
        envelope = Envelope(
            bill_instance=one_time_bill_instance,
            initial_allocation=Decimal("50.00"),
            start_contrib_date=datetime.date(2024, 2, 1),
            end_contrib_date=datetime.date(2024, 3, 15),
        )
        manager.add_envelopes(envelope)

        as_of = datetime.date(2024, 1, 15)

        balances = manager.get_balance_as_of_date(as_of_date=as_of)
        assert balances == {as_of: {}}

    def test_get_balance_as_of_date_includes_active_envelopes(
        self,
        one_time_bill_instance: BillInstance,
    ) -> None:
        """
        Test that balances are included once envelopes are active.
        """

        manager = EnvelopeManager()
        envelope = Envelope(
            bill_instance=one_time_bill_instance,
            initial_allocation=Decimal("25.00"),
            start_contrib_date=datetime.date(2024, 1, 1),
            end_contrib_date=datetime.date(2024, 3, 15),
        )

        # Add a small contribution schedule for determinism.
        cash_flow_schedule = CashFlowSchedule()
        cash_flow_schedule.add_cash_flows(
            CashFlow(
                bill_id="car_registration",
                date=datetime.date(2024, 1, 10),
                amount=Decimal("25.00"),
            )
        )
        envelope.schedule = cash_flow_schedule

        manager.add_envelopes(envelope)

        as_of = datetime.date(2024, 1, 20)
        balances = manager.get_balance_as_of_date(as_of_date=as_of)

        expected_balance = envelope.get_balance_as_of_date(as_of_date=as_of)

        assert balances[as_of]["car_registration"] == expected_balance

    def test_total_cash_flow_on_date_skips_before_start(
        self,
        one_time_bill_instance: BillInstance,
    ) -> None:
        """
        Test that total cash flows skip envelopes before their start date.
        """

        manager = EnvelopeManager()
        envelope = Envelope(
            bill_instance=one_time_bill_instance,
            initial_allocation=Decimal("0.00"),
            start_contrib_date=datetime.date(2024, 2, 1),
            end_contrib_date=datetime.date(2024, 3, 15),
        )
        manager.add_envelopes(envelope)

        date = datetime.date(2024, 1, 15)
        cash_flows = manager.total_cash_flow_on_date(date=date)

        assert cash_flows == {date: {}}

    def test_total_cash_flow_on_date_includes_active_envelopes(
        self,
        one_time_bill_instance: BillInstance,
    ) -> None:
        """
        Test that total cash flows include active envelopes.
        """

        manager = EnvelopeManager()
        envelope = Envelope(
            bill_instance=one_time_bill_instance,
            initial_allocation=Decimal("0.00"),
            start_contrib_date=datetime.date(2024, 1, 1),
            end_contrib_date=datetime.date(2024, 3, 15),
        )

        cash_flow_schedule = CashFlowSchedule()
        cash_flow_schedule.add_cash_flows(
            [
                CashFlow(
                    bill_id="car_registration",
                    date=datetime.date(2024, 1, 10),
                    amount=Decimal("20.00"),
                ),
                CashFlow(
                    bill_id="car_registration",
                    date=datetime.date(2024, 1, 10),
                    amount=Decimal("5.00"),
                ),
            ]
        )
        envelope.schedule = cash_flow_schedule

        manager.add_envelopes(envelope)

        date = datetime.date(2024, 1, 10)
        cash_flows = manager.total_cash_flow_on_date(date=date)

        expected_total = envelope.total_cash_flow_on_date(date=date)

        assert cash_flows[date]["car_registration"] == expected_total
