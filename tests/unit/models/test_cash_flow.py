"""
Cash Flow Model Tests
=====================

Comprehensive tests for CashFlow and CashFlowSchedule models covering
validation, ordering, timeline operations, and aggregation functions.
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import datetime
from decimal import Decimal

import pytest

from sinkingfund.models import CashFlow, CashFlowSchedule

########################################################################
## CASH FLOW TESTS
########################################################################

class TestCashFlow:
    """
    Test CashFlow model validation and behavior.
    """

    def test_cash_flow_creation_positive(self) -> None:
        """
        Test creating a positive cash flow (contribution).
        """

        # Create a positive cash flow.
        cash_flow = CashFlow(
            bill_id="electric",
            date=datetime.date(2024, 1, 15),
            amount=Decimal("50.00")
        )
        
        # Test: Assert that the cash flow has the correct attributes.
        assert cash_flow.bill_id == "electric"
        assert cash_flow.date == datetime.date(2024, 1, 15)
        assert cash_flow.amount == Decimal("50.00")

    def test_cash_flow_creation_negative(self) -> None:
        """
        Test creating a negative cash flow (payment).
        """

        # Create a negative cash flow.
        cash_flow = CashFlow(
            bill_id="electric",
            date=datetime.date(2024, 2, 15),
            amount=Decimal("-150.00")
        )
        
        # Test: Assert that the cash flow has the correct attributes.
        assert cash_flow.amount == Decimal("-150.00")

    def test_cash_flow_validates_empty_bill_id(self) -> None:
        """
        Test that CashFlow rejects empty bill_id.
        """

        # Test: Empty bill_id raises a ValueError.
        with pytest.raises(
            ValueError, match="bill_id cannot be empty or whitespace."
        ):
            CashFlow(
                bill_id="",
                date=datetime.date(2024, 1, 15),
                amount=Decimal("50.00")
            )
        
        # Test: Whitespace bill_id raises a ValueError.
        with pytest.raises(
            ValueError, match="bill_id cannot be empty or whitespace."
        ):
            CashFlow(
                bill_id="   ",
                date=datetime.date(2024, 1, 15),
                amount=Decimal("50.00")
            )

    def test_cash_flow_validates_amount_type(self) -> None:
        """
        Test that CashFlow validates amount as Decimal.
        """

        # Test: Valid Decimal input.
        cash_flow = CashFlow(
            bill_id="test",
            date=datetime.date(2024, 1, 15),
            amount=Decimal("50.00")
        )
        assert isinstance(cash_flow.amount, Decimal)

    def test_cash_flow_ordering(self) -> None:
        """
        Test that CashFlow objects are ordered by date.
        """

        # Test: Earlier date is less than later date.
        earlier = CashFlow(
            bill_id="test",
            date=datetime.date(2024, 1, 15),
            amount=Decimal("50.00")
        )

        later = CashFlow(
            bill_id="test",
            date=datetime.date(2024, 2, 15),
            amount=Decimal("50.00")
        )
        
        assert earlier < later
        assert later > earlier
        assert earlier != later

    def test_cash_flow_equality(self) -> None:
        """
        Test CashFlow equality semantics.
        """

        # Test: Cash flows with the same bill_id, date, and amount are
        # equal; cash flows with different amounts are not equal.
        cash_flow1 = CashFlow(
            bill_id="electric",
            date=datetime.date(2024, 1, 15),
            amount=Decimal("50.00")
        )

        cash_flow2 = CashFlow(
            bill_id="electric",
            date=datetime.date(2024, 1, 15),
            amount=Decimal("50.00")
        )

        cash_flow3 = CashFlow(
            bill_id="electric",
            date=datetime.date(2024, 1, 15),
            amount=Decimal("60.00")
        )
        
        assert cash_flow1 == cash_flow2
        assert cash_flow1 != cash_flow3

    def test_cash_flow_immutability(self) -> None:
        """
        Test that CashFlow is immutable (frozen dataclass).
        """

        # Create a cash flow.
        cash_flow = CashFlow(
            bill_id="electric",
            date=datetime.date(2024, 1, 15),
            amount=Decimal("50.00")
        )
        
        # Should not be able to modify fields.
        with pytest.raises(AttributeError):
            cash_flow.amount = Decimal("100.00")
        
        with pytest.raises(AttributeError):
            cash_flow.date = datetime.date(2024, 2, 15)

########################################################################
## CASH FLOW SCHEDULE TESTS
########################################################################

class TestCashFlowSchedule:
    """
    Test CashFlowSchedule collection and operations.
    """

    def test_empty_schedule_creation(self) -> None:
        """
        Test creating an empty cash flow schedule.
        """

        # Create an empty cash flow schedule.
        schedule = CashFlowSchedule()
        
        # Test: Assert that the schedule is empty and has a total of 0.
        assert len(schedule.cash_flows) == 0
        assert (
            schedule.total_amount_as_of_date(
                as_of_date=datetime.date(2024, 1, 1)
            ) == Decimal("0.00")
        )

    def test_schedule_creation_with_cash_flows(
        self,
        cash_flow_schedule: CashFlowSchedule
    ) -> None:
        """
        Test creating a schedule with initial cash flows.
        """

        # Test: Assert that the schedule has the correct number of cash
        # flows.
        assert len(cash_flow_schedule.cash_flows) == 2

    def test_schedule_add_cash_flow(self) -> None:
        """
        Test adding cash flows to a schedule.
        """

        # Create an empty cash flow schedule.
        schedule = CashFlowSchedule()

        # Create a cash flow.
        cash_flow = CashFlow(
            bill_id="electric",
            date=datetime.date(2024, 1, 15),
            amount=Decimal("50.00")
        )
        
        # Add the cash flow to the schedule.
        schedule.add_cash_flows(cash_flow)

        # Test: Assert that the schedule has the correct number of cash
        # flows.
        assert len(schedule.cash_flows) == 1
        assert schedule.cash_flows[0] == cash_flow

    def test_schedule_automatic_sorting(self) -> None:
        """
        Test that schedule automatically sorts cash flows by date.
        """

        # Create two cash flows.
        later_flow = CashFlow(
            bill_id="electric",
            date=datetime.date(2024, 2, 15),
            amount=Decimal("50.00")
        )

        earlier_flow = CashFlow(
            bill_id="electric", 
            date=datetime.date(2024, 1, 15),
            amount=Decimal("50.00")
        )
        
        # Create a schedule and add the cash flows.
        schedule = CashFlowSchedule()
        schedule.add_cash_flows([later_flow, earlier_flow])
        
        # Test: Assert that the cash flows are sorted by date.
        assert schedule.cash_flows[0] == earlier_flow
        assert schedule.cash_flows[1] == later_flow

    def test_schedule_total_calculation(
        self,
        cash_flow_schedule: CashFlowSchedule,
        small_amount: Decimal,
        medium_amount: Decimal
    ) -> None:
        """
        Test total calculation across all cash flows.
        """

        # Test: Assert that the total is the sum of the cash flows.
        # Note: Use date that includes both cash flows (not after latest)
        actual_total = cash_flow_schedule.total_amount_as_of_date(
            as_of_date=datetime.date(2024, 2, 28)
        )
        expected_total = small_amount + (-medium_amount)
        assert actual_total == expected_total

    def test_schedule_total_in_range(
        self,
        cash_flow_schedule: CashFlowSchedule,
        small_amount: Decimal
    ) -> None:
        """
        Test total calculation within date range.
        """

        # Test: Only include the first cash flow (January 15).
        total_jan = cash_flow_schedule.total_amount_in_range(
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 1, 31)
        )
        assert total_jan == small_amount
        
        # Test: Include both cash flows.
        total_all = cash_flow_schedule.total_amount_in_range(
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 2, 28)
        )
        # Compare with total as of latest cash flow date
        assert total_all == cash_flow_schedule.total_amount_as_of_date(
            as_of_date=datetime.date(2024, 2, 28)
        )
        
        # Test: Include no cash flows.
        total_none = cash_flow_schedule.total_amount_in_range(
            start_date=datetime.date(2024, 3, 1),
            end_date=datetime.date(2024, 3, 31)
        )
        assert total_none == Decimal("0.00")

    def test_schedule_cash_flows_in_range(
        self,
        cash_flow_schedule: CashFlowSchedule
    ) -> None:
        """
        Test filtering cash flows by date range.
        """

        # Test: Get only January cash flows.
        jan_flows = cash_flow_schedule.cash_flows_in_range(
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 1, 31)
        )
        assert len(jan_flows) == 1
        assert jan_flows[0].date == datetime.date(2024, 1, 15)
        
        # Test: Get all cash flows.
        all_flows = cash_flow_schedule.cash_flows_in_range(
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 12, 31)
        )
        assert len(all_flows) == 2
        
        # Test: Get no cash flows.
        no_flows = cash_flow_schedule.cash_flows_in_range(
            start_date=datetime.date(2024, 3, 1),
            end_date=datetime.date(2024, 3, 31)
        )
        assert len(no_flows) == 0

    def test_schedule_balance_calculation(
        self,
        cash_flow_schedule: CashFlowSchedule,
        small_amount: Decimal
    ) -> None:
        """
        Test running balance calculation.
        """

        # Test: Balance after first cash flow.
        balance_jan = cash_flow_schedule.total_amount_as_of_date(
            datetime.date(2024, 1, 20)
        )
        assert balance_jan == small_amount
        
        # Test: Balance after both cash flows.
        balance_feb = cash_flow_schedule.total_amount_as_of_date(
            datetime.date(2024, 2, 20)
        )
        total_balance = cash_flow_schedule.total_amount_as_of_date(
            as_of_date=datetime.date(2024, 2, 28)
        )
        assert balance_feb == total_balance
        
        # Test: Balance before any cash flows.
        balance_before = cash_flow_schedule.total_amount_as_of_date(
            datetime.date(2024, 1, 1)
        )
        assert balance_before == Decimal("0.00")

    def test_schedule_date_filtering(
        self,
        cash_flow_schedule: CashFlowSchedule
    ) -> None:
        """
        Test date filtering and cash flow access.
        """

        # Test: Get cash flow dates in range
        dates = cash_flow_schedule.cash_flow_dates_in_range(
            start_date=datetime.date(2024, 1, 10),
            end_date=datetime.date(2024, 2, 20)
        )
        
        # Test: Should include both cash flow dates
        assert len(dates) == 2
        assert datetime.date(2024, 1, 15) in dates
        assert datetime.date(2024, 2, 15) in dates

########################################################################
## CASH FLOW INTEGRATION TESTS
########################################################################

class TestCashFlowIntegration:
    """
    Test CashFlow and CashFlowSchedule integration scenarios.
    """

    def test_envelope_contribution_schedule(self) -> None:
        """
        Test modeling an envelope contribution schedule.
        """
        
        # Create bi-weekly contributions for 2 months.
        contributions = []
        contrib_date = datetime.date(2024, 1, 1)
        
        # 4 bi-weekly contributions.
        for _ in range(4):

            contributions.append(
                CashFlow(
                    bill_id="insurance",
                    date=contrib_date,
                    amount=Decimal("75.00")
                )
            )

            # Add 14 days for bi-weekly.
            contrib_date = contrib_date + datetime.timedelta(days=14)
        
        # Add the final payment.
        payment = CashFlow(
            bill_id="insurance",
            date=datetime.date(2024, 3, 1),
            amount=Decimal("-300.00")
        )
        
        # Create a schedule with the cash flows.
        all_flows = contributions + [payment]
        schedule = CashFlowSchedule()
        schedule.add_cash_flows(all_flows)

        # Test: Verify contribution phase builds up balance.
        balance_after_contributions = schedule.total_amount_as_of_date(
            datetime.date(2024, 2, 28)
        )
        assert balance_after_contributions == Decimal("300.00")
        
        # Verify payment brings balance to zero.
        final_balance = schedule.total_amount_as_of_date(
             datetime.date(2024, 3, 31)
        )
        assert final_balance == Decimal("0.00")