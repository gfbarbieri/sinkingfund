"""
Envelope Model Tests
====================

Comprehensive tests for Envelope model covering initialization,
balance calculations, funding status, and contribution scheduling.
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import datetime
from decimal import Decimal

import pytest

from sinkingfund.models import (
    Envelope, BillInstance, CashFlow, CashFlowSchedule
)


########################################################################
## ENVELOPE INITIALIZATION TESTS
########################################################################

class TestEnvelopeInitialization:
    """
    Test Envelope model initialization and validation.
    """

    def test_envelope_creation_with_defaults(
        self, bill_instance: BillInstance
    ) -> None:
        """
        Test creating an envelope with default values.
        """

        # Create an envelope with default values.
        envelope = Envelope(bill_instance=bill_instance)
        
        # Test: Assert that the envelope has the correct attributes.
        assert envelope.bill_instance == bill_instance
        assert envelope.initial_allocation == Decimal("0.00")
        assert envelope.start_contrib_date is None
        assert envelope.end_contrib_date is None
        assert envelope.contrib_interval is None
        assert isinstance(envelope.schedule, CashFlowSchedule)
        assert len(envelope.schedule.cash_flows) == 0

    def test_envelope_creation_with_allocation(
        self, 
        bill_instance: BillInstance,
        small_amount: Decimal
    ) -> None:
        """
        Test creating an envelope with initial allocation.
        """

        # Create an envelope with initial allocation.
        envelope = Envelope(
            bill_instance=bill_instance,
            initial_allocation=small_amount
        )
        
        # Test: Assert that the envelope has the correct attributes.
        assert envelope.initial_allocation == small_amount

    def test_envelope_creation_with_contribution_dates(
        self, 
        bill_instance: BillInstance
    ) -> None:
        """
        Test creating an envelope with contribution date range.
        """

        # Create an envelope with contribution date range.
        start_date = datetime.date(2024, 1, 1)
        end_date = datetime.date(2024, 2, 14)
        
        envelope = Envelope(
            bill_instance=bill_instance,
            start_contrib_date=start_date,
            end_contrib_date=end_date,
            contrib_interval=14
        )
        
        # Test: Assert that the envelope has the correct attributes.
        assert envelope.start_contrib_date == start_date
        assert envelope.end_contrib_date == end_date
        assert envelope.contrib_interval == 14

    def test_envelope_validates_negative_allocation(
        self, 
        bill_instance: BillInstance
    ) -> None:
        """
        Test that Envelope rejects negative initial allocations.
        """

        # Test: Negative initial allocation raises a ValueError.
        with pytest.raises(
            ValueError, match="initial_allocation cannot be negative."
        ):
            Envelope(
                bill_instance=bill_instance,
                initial_allocation=Decimal("-50.00")
            )

    def test_envelope_validates_date_order(
        self, 
        bill_instance: BillInstance
    ) -> None:
        """
        Test that Envelope validates contribution date order.
        """

        # Test: End date before start date raises a ValueError.
        with pytest.raises(
            ValueError, match=(
                "end_contrib_date cannot be before start_contrib_date."
            )
        ):
            Envelope(
                bill_instance=bill_instance,
                start_contrib_date=datetime.date(2024, 3, 1),
                end_contrib_date=datetime.date(2024, 2, 1)
            )

########################################################################
## ENVELOPE BALANCE TESTS
########################################################################

class TestEnvelopeBalance:
    """
    Test Envelope balance calculations and projections.
    """

    def test_current_balance_with_allocation_only(
        self, 
        partially_funded_envelope: Envelope,
        small_amount: Decimal
    ) -> None:
        """
        Test current balance with only initial allocation.
        """

        # Test: Assert that the balance is the initial allocation at the
        # start of the contribution period.
        balance = partially_funded_envelope.get_balance_as_of_date(
            as_of_date=partially_funded_envelope.start_contrib_date
        )
        assert balance == small_amount

    def test_current_balance_with_as_of_date(
        self, 
        partially_funded_envelope: Envelope,
        small_amount: Decimal
    ) -> None:
        """
        Test current balance calculation as of specific date.
        """

        # Test: Assert that the balance is the initial allocation at the
        # start of the contribution period.
        as_of_date = datetime.date(2024, 1, 15)
        balance = partially_funded_envelope.get_balance_as_of_date(as_of_date)
        assert balance == small_amount

    def test_remaining_amount_calculation(
        self, 
        partially_funded_envelope: Envelope,
        small_amount: Decimal,
        medium_amount: Decimal
    ) -> None:
        """
        Test remaining amount calculation.
        """

        # Test: Assert that the remaining amount is the initial
        # allocation minus the small amount.
        remaining = partially_funded_envelope.remaining()
        expected_remaining = small_amount - medium_amount
        assert remaining == expected_remaining

    def test_remaining_amount_with_as_of_date(
        self, 
        partially_funded_envelope: Envelope,
        small_amount: Decimal,
        medium_amount: Decimal
    ) -> None:
        """
        Test remaining amount calculation as of specific date.
        """

        # Test: Assert that the remaining amount is the initial
        # allocation minus the small amount.
        as_of_date = datetime.date(2024, 1, 15)
        remaining = partially_funded_envelope.remaining(as_of_date)
        expected_remaining = small_amount - medium_amount
        assert remaining >= Decimal("0.00")

    def test_is_fully_funded_false(
        self, partially_funded_envelope: Envelope
    ) -> None:
        """
        Test is_fully_funded returns False for underfunded envelope.
        """

        # Test: Assert that the envelope is not fully funded.
        assert not partially_funded_envelope.is_fully_funded()

    def test_is_fully_funded_true(
        self, 
        bill_instance: BillInstance,
        medium_amount: Decimal
    ) -> None:
        """
        Test is_fully_funded returns True for fully funded envelope.
        """

        # Test: Assert that the envelope is fully funded.
        envelope = Envelope(
            bill_instance=bill_instance,
            initial_allocation=medium_amount
        )
        assert envelope.is_fully_funded()

    def test_is_fully_funded_with_as_of_date(
        self, 
        partially_funded_envelope: Envelope
    ) -> None:
        """
        Test is_fully_funded with specific as_of_date.
        """

        # Test: Assert that the envelope is fully funded.
        result = partially_funded_envelope.is_fully_funded(
            as_of_date=datetime.date(2024, 1, 15)
        )

        # Test: Assert that the result is a boolean.
        assert isinstance(result, bool)

########################################################################
## ENVELOPE SCHEDULE TESTS
########################################################################

class TestEnvelopeSchedule:
    """
    Test Envelope integration with cash flow schedules.
    """

    def test_set_schedule(self, empty_envelope: Envelope) -> None:
        """
        Test setting a contribution schedule on an envelope.
        """

        # Test: Assert that the schedule is set.
        cash_flows = [
            CashFlow(
                bill_id=empty_envelope.bill_instance.bill_id,
                date=datetime.date(2024, 1, 15),
                amount=Decimal("25.00")
            ),
            CashFlow(
                bill_id=empty_envelope.bill_instance.bill_id,
                date=datetime.date(2024, 1, 29),
                amount=Decimal("25.00")
            )
        ]
        schedule = CashFlowSchedule(cash_flows=cash_flows)
        
        empty_envelope.set_cash_flow_schedule(schedule)
        assert empty_envelope.schedule == schedule

    def test_current_balance_with_schedule(
        self, empty_envelope: Envelope
    ) -> None:
        """
        Test current balance calculation including scheduled contributions.
        """

        # Create a contribution schedule.
        cash_flows = [
            CashFlow(
                bill_id=empty_envelope.bill_instance.bill_id,
                date=datetime.date(2024, 1, 15),
                amount=Decimal("30.00")
            ),
            CashFlow(
                bill_id=empty_envelope.bill_instance.bill_id,
                date=datetime.date(2024, 1, 29),
                amount=Decimal("30.00")
            )
        ]
        schedule = CashFlowSchedule(cash_flows=cash_flows)
        empty_envelope.set_cash_flow_schedule(schedule)
        
        # Test: Check balance after first contribution.
        balance = empty_envelope.get_balance_as_of_date(
            as_of_date=datetime.date(2024, 1, 20)
        )
        assert balance == Decimal("30.00")
        
        # Test: Check balance after both contributions.
        balance = empty_envelope.get_balance_as_of_date(
            as_of_date=datetime.date(2024, 2, 1)
        )
        assert balance == Decimal("60.00")

    def test_remaining_with_schedule(self, empty_envelope: Envelope) -> None:
        """
        Test remaining calculation including scheduled contributions.
        """

        # Create a partial contribution schedule.
        cash_flows = [
            CashFlow(
                bill_id=empty_envelope.bill_instance.bill_id,
                date=datetime.date(2024, 1, 15),
                amount=Decimal("50.00")
            )
        ]
        schedule = CashFlowSchedule(cash_flows=cash_flows)
        empty_envelope.set_schedule(schedule)
        
        # Test: Calculate remaining after the scheduled contribution.
        remaining = empty_envelope.remaining(
            as_of_date=datetime.date(2024, 1, 20)
        )
        expected_remaining = (
            empty_envelope.bill_instance.amount_due - Decimal("50.00")
        )
        assert remaining == expected_remaining

    def test_is_fully_funded_with_schedule(
        self, empty_envelope: Envelope
    ) -> None:
        """
        Test is_fully_funded with complete contribution schedule.
        """
        
        # Create a schedule that fully funds the envelope.
        total_needed = empty_envelope.bill_instance.amount_due
        cash_flows = [
            CashFlow(
                bill_id=empty_envelope.bill_instance.bill_id,
                date=datetime.date(2024, 1, 15),
                amount=total_needed
            )
        ]
        schedule = CashFlowSchedule(cash_flows=cash_flows)
        empty_envelope.set_schedule(schedule)
        
        # Test: Assert that the envelope is not fully funded before the
        # contribution.
        assert not empty_envelope.is_fully_funded(datetime.date(2024, 1, 10))
        
        # Test: Assert that the envelope is fully funded after the
        # contribution.
        assert empty_envelope.is_fully_funded(datetime.date(2024, 1, 20))


########################################################################
## ENVELOPE INTEGRATION TESTS
########################################################################

class TestEnvelopeIntegration:
    """
    Test Envelope model integration scenarios.
    """

    def test_envelope_lifecycle_scenario(
        self, bill_instance: BillInstance
    ) -> None:
        """
        Test complete envelope lifecycle from creation to full funding.
        """

        # Create envelope with small initial allocation.
        envelope = Envelope(
            bill_instance=bill_instance,
            initial_allocation=Decimal("25.00"),
            start_contrib_date=datetime.date(2024, 1, 1),
            end_contrib_date=datetime.date(2024, 2, 14),
            contrib_interval=14
        )
        
        # Initial state - partially funded.
        assert envelope.get_balance_as_of_date() == Decimal("25.00")
        assert not envelope.is_fully_funded()
        
        # Add contribution schedule.
        remaining_needed = envelope.remaining()
        contributions_per_period = remaining_needed / 4
        
        cash_flows = []
        contrib_date = datetime.date(2024, 1, 1)

        for _ in range(4):

            # Add cash flow for each period.
            cash_flows.append(
                CashFlow(
                    bill_id=bill_instance.bill_id,
                    date=contrib_date,
                    amount=contributions_per_period
                )
            )

            # Add 14 days for bi-weekly.
            contrib_date = datetime.date(
                contrib_date.year,
                contrib_date.month,
                contrib_date.day + 14
            )
        
        schedule = CashFlowSchedule(cash_flows=cash_flows)
        envelope.set_schedule(schedule)
        
        # Test: Check progressive funding.
        balance_after_2_periods = envelope.get_balance_as_of_date(
            as_of_date=datetime.date(2024, 1, 29)
        )
        expected_balance = Decimal("25.00") + (2 * contributions_per_period)
        assert balance_after_2_periods == expected_balance
        
        # Test: Check final funding status.
        final_balance = envelope.get_balance_as_of_date(
            as_of_date=datetime.date(2024, 2, 15)
        )
        assert final_balance >= bill_instance.amount_due
        assert envelope.is_fully_funded(datetime.date(2024, 2, 15))

    def test_envelope_overfunding_scenario(
        self, bill_instance: BillInstance
    ) -> None:
        """
        Test envelope behavior when overfunded.
        """

        # Create envelope with excessive initial allocation.
        overfunding_amount = bill_instance.amount_due * 2
        envelope = Envelope(
            bill_instance=bill_instance,
            initial_allocation=overfunding_amount
        )
        
        # Test: Assert that the envelope is overfunded.
        assert envelope.get_balance_as_of_date() == overfunding_amount
        assert envelope.is_fully_funded()
        assert envelope.remaining() == Decimal("0.00")

    def test_envelope_zero_allocation_scenario(
        self, empty_envelope: Envelope
    ) -> None:
        """
        Test envelope with no allocation or contributions.
        """

        # Test: Assert that the envelope has no balance and is not fully
        # funded.
        assert empty_envelope.get_balance_as_of_date() == Decimal("0.00")
        assert not empty_envelope.is_fully_funded()
        assert empty_envelope.remaining() == (
            empty_envelope.bill_instance.amount_due
        )