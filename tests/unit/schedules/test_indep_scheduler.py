"""
Independent Scheduler Tests
===========================

Comprehensive tests for IndependentScheduler covering scheduling edge cases,
empty inputs, boundary dates, and contribution calculations.
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import datetime
from decimal import Decimal

import pytest

from sinkingfund.models import BillInstance, Envelope, CashFlow
from sinkingfund.schedules.indep_scheduler import IndependentScheduler

########################################################################
## SCHEDULE METHOD TESTS
########################################################################

class TestScheduleMethod:
    """
    Test the main schedule method with various edge cases and scenarios.
    """

    def test_empty_envelope_list(self) -> None:
        """
        Test that scheduling with an empty envelope list returns an empty
        dictionary.
        """

        # Create scheduler and empty envelope list.
        scheduler = IndependentScheduler()
        envelopes = []

        # Test: Schedule should return empty dict.
        schedules = scheduler.schedule(envelopes=envelopes)
        assert schedules == {}
        assert len(schedules) == 0

    def test_single_envelope_basic_schedule(
        self, empty_envelope: Envelope
    ) -> None:
        """
        Test scheduling a single envelope with standard parameters.
        """

        # Create scheduler and schedule the envelope.
        scheduler = IndependentScheduler()
        schedules = scheduler.schedule(envelopes=[empty_envelope])

        # Test: Should return one schedule.
        assert len(schedules) == 1
        assert empty_envelope in schedules

        # Test: Schedule should have cash flows.
        schedule = schedules[empty_envelope]
        assert len(schedule.cash_flows) > 0

        # Test: Should have positive contributions and negative payment.
        contributions = [
            cf for cf in schedule.cash_flows if cf.amount > 0
        ]
        payments = [cf for cf in schedule.cash_flows if cf.amount < 0]

        assert len(contributions) > 0
        assert len(payments) == 1

        # Test: Total contributions should equal remaining amount.
        total_contributions = sum(cf.amount for cf in contributions)
        remaining = (
            empty_envelope.bill_instance.amount_due
            - empty_envelope.initial_allocation
        )
        assert abs(total_contributions - remaining) < Decimal("0.01")

        # Test: Payment should equal bill amount.
        assert abs(payments[0].amount) == empty_envelope.bill_instance.amount_due

    def test_fully_funded_envelope(
        self, bill_instance: BillInstance
    ) -> None:
        """
        Test scheduling an envelope that is already fully funded.
        """

        # Create envelope with initial allocation equal to bill amount.
        envelope = Envelope(
            bill_instance=bill_instance,
            initial_allocation=bill_instance.amount_due,
            start_contrib_date=datetime.date(2024, 1, 1),
            end_contrib_date=datetime.date(2024, 2, 14),
            contrib_interval=14
        )

        # Create scheduler and schedule the envelope.
        scheduler = IndependentScheduler()
        schedules = scheduler.schedule(envelopes=[envelope])

        # Test: Should return schedule.
        assert envelope in schedules

        # Test: Should have only payment, no contributions.
        schedule = schedules[envelope]
        contributions = [
            cf for cf in schedule.cash_flows if cf.amount > 0
        ]
        payments = [cf for cf in schedule.cash_flows if cf.amount < 0]

        assert len(contributions) == 0
        assert len(payments) == 1

    def test_past_due_bill(self) -> None:
        """
        Test scheduling an envelope for a bill that is past due.
        """

        # Create bill instance with past due date.
        past_due_bill = BillInstance(
            bill_id="past_due",
            service="Past Due Bill",
            due_date=datetime.date(2023, 12, 31),
            amount_due=Decimal("100.00")
        )

        # Create envelope with start date after due date.
        envelope = Envelope(
            bill_instance=past_due_bill,
            start_contrib_date=datetime.date(2024, 1, 1),
            end_contrib_date=datetime.date(2024, 1, 15),
            contrib_interval=7
        )

        # Create scheduler and schedule the envelope.
        scheduler = IndependentScheduler()
        schedules = scheduler.schedule(envelopes=[envelope])

        # Test: Should return schedule.
        assert envelope in schedules

        # Test: Should have payment but contributions may be zero or full
        # amount.
        schedule = schedules[envelope]
        assert len(schedule.cash_flows) > 0

        # Test: Payment should be present.
        payments = [cf for cf in schedule.cash_flows if cf.amount < 0]
        assert len(payments) == 1

    def test_bill_due_today(self) -> None:
        """
        Test scheduling an envelope for a bill due on the start date.
        
        Note: This edge case currently causes an IndexError when
        start_date == end_date because there are no contribution
        intervals. This test documents the current behavior.
        """

        # Create bill instance due today.
        today = datetime.date(2024, 1, 1)
        bill_due_today = BillInstance(
            bill_id="due_today",
            service="Bill Due Today",
            due_date=today,
            amount_due=Decimal("200.00")
        )

        # Create envelope with start date equal to due date.
        envelope = Envelope(
            bill_instance=bill_due_today,
            start_contrib_date=today,
            end_contrib_date=today,
            contrib_interval=1
        )

        # Create scheduler and schedule the envelope.
        scheduler = IndependentScheduler()

        # Test: Currently raises IndexError when no intervals exist.
        # This edge case should be handled by the scheduler.
        with pytest.raises(IndexError):
            scheduler.schedule(envelopes=[envelope])

    def test_very_short_contribution_period(self) -> None:
        """
        Test scheduling with a very short contribution period (1 day).
        
        Note: When start_date == end_date, there are no contribution
        intervals, which currently causes an IndexError. This test
        documents the current behavior.
        """

        # Create bill instance.
        bill = BillInstance(
            bill_id="short_period",
            service="Short Period Bill",
            due_date=datetime.date(2024, 1, 2),
            amount_due=Decimal("50.00")
        )

        # Create envelope with 1-day contribution period where
        # start == end (no contribution window).
        envelope = Envelope(
            bill_instance=bill,
            start_contrib_date=datetime.date(2024, 1, 1),
            end_contrib_date=datetime.date(2024, 1, 1),
            contrib_interval=1
        )

        # Create scheduler and schedule the envelope.
        scheduler = IndependentScheduler()

        # Test: Currently raises IndexError when no intervals exist.
        # This edge case should be handled by the scheduler.
        with pytest.raises(IndexError):
            scheduler.schedule(envelopes=[envelope])

    def test_valid_single_day_period(self) -> None:
        """
        Test scheduling with a valid single-day contribution period
        (start != end, but period is 1 day).
        """

        # Create bill instance.
        bill = BillInstance(
            bill_id="valid_short",
            service="Valid Short Period Bill",
            due_date=datetime.date(2024, 1, 2),
            amount_due=Decimal("50.00")
        )

        # Create envelope with valid 1-day contribution period
        # (start != end).
        envelope = Envelope(
            bill_instance=bill,
            start_contrib_date=datetime.date(2024, 1, 1),
            end_contrib_date=datetime.date(2024, 1, 2),
            contrib_interval=1
        )

        # Create scheduler and schedule the envelope.
        scheduler = IndependentScheduler()
        schedules = scheduler.schedule(envelopes=[envelope])

        # Test: Should return schedule.
        assert envelope in schedules

        # Test: Should have contributions and payment.
        schedule = schedules[envelope]
        assert len(schedule.cash_flows) > 0

        # Test: Total should equal bill amount.
        total_positive = sum(
            cf.amount for cf in schedule.cash_flows if cf.amount > 0
        )
        remaining = bill.amount_due - envelope.initial_allocation
        assert abs(total_positive - remaining) < Decimal("0.01")

    def test_start_date_equals_end_date(self) -> None:
        """
        Test scheduling when start and end contribution dates are equal.
        
        Note: This edge case currently causes an IndexError when
        start_date == end_date because there are no contribution
        intervals. This test documents the current behavior.
        """

        # Create bill instance.
        bill = BillInstance(
            bill_id="same_dates",
            service="Same Dates Bill",
            due_date=datetime.date(2024, 1, 15),
            amount_due=Decimal("75.00")
        )

        # Create envelope with same start and end dates.
        same_date = datetime.date(2024, 1, 10)
        envelope = Envelope(
            bill_instance=bill,
            start_contrib_date=same_date,
            end_contrib_date=same_date,
            contrib_interval=7
        )

        # Create scheduler and schedule the envelope.
        scheduler = IndependentScheduler()

        # Test: Currently raises IndexError when no intervals exist.
        # This edge case should be handled by the scheduler.
        with pytest.raises(IndexError):
            scheduler.schedule(envelopes=[envelope])

    def test_multiple_envelopes(self) -> None:
        """
        Test scheduling multiple envelopes simultaneously.
        """

        # Create multiple bill instances.
        bill1 = BillInstance(
            bill_id="bill1",
            service="Bill 1",
            due_date=datetime.date(2024, 2, 15),
            amount_due=Decimal("100.00")
        )

        bill2 = BillInstance(
            bill_id="bill2",
            service="Bill 2",
            due_date=datetime.date(2024, 3, 15),
            amount_due=Decimal("200.00")
        )

        # Create multiple envelopes.
        envelope1 = Envelope(
            bill_instance=bill1,
            start_contrib_date=datetime.date(2024, 1, 1),
            end_contrib_date=datetime.date(2024, 2, 14),
            contrib_interval=14
        )

        envelope2 = Envelope(
            bill_instance=bill2,
            start_contrib_date=datetime.date(2024, 1, 1),
            end_contrib_date=datetime.date(2024, 3, 14),
            contrib_interval=14
        )

        # Create scheduler and schedule both envelopes.
        scheduler = IndependentScheduler()
        schedules = scheduler.schedule(envelopes=[envelope1, envelope2])

        # Test: Should return schedules for both envelopes.
        assert len(schedules) == 2
        assert envelope1 in schedules
        assert envelope2 in schedules

        # Test: Each schedule should be independent.
        schedule1 = schedules[envelope1]
        schedule2 = schedules[envelope2]

        assert len(schedule1.cash_flows) > 0
        assert len(schedule2.cash_flows) > 0

    def test_different_contribution_intervals(self) -> None:
        """
        Test scheduling with different contribution interval sizes.
        """

        # Create bill instance.
        bill = BillInstance(
            bill_id="interval_test",
            service="Interval Test Bill",
            due_date=datetime.date(2024, 2, 1),
            amount_due=Decimal("300.00")
        )

        # Test different intervals.
        intervals = [1, 7, 14, 30]

        for interval in intervals:
            envelope = Envelope(
                bill_instance=bill,
                start_contrib_date=datetime.date(2024, 1, 1),
                end_contrib_date=datetime.date(2024, 1, 31),
                contrib_interval=interval
            )

            scheduler = IndependentScheduler()
            schedules = scheduler.schedule(envelopes=[envelope])

            # Test: Should create valid schedule.
            assert envelope in schedules
            schedule = schedules[envelope]

            # Test: Should have contributions and payment.
            contributions = [
                cf for cf in schedule.cash_flows if cf.amount > 0
            ]
            assert len(contributions) > 0

            # Test: Total should equal remaining amount.
            total = sum(cf.amount for cf in contributions)
            remaining = bill.amount_due - envelope.initial_allocation
            assert abs(total - remaining) < Decimal("0.01")

    def test_partial_interval_at_end(self) -> None:
        """
        Test scheduling when the period doesn't divide evenly by interval.
        """

        # Create bill instance.
        bill = BillInstance(
            bill_id="partial",
            service="Partial Interval Bill",
            due_date=datetime.date(2024, 1, 20),
            amount_due=Decimal("100.00")
        )

        # Create envelope with period that doesn't divide evenly by 7.
        # 19 days from Jan 1 to Jan 20 = 2 full weeks + 5 days.
        envelope = Envelope(
            bill_instance=bill,
            start_contrib_date=datetime.date(2024, 1, 1),
            end_contrib_date=datetime.date(2024, 1, 19),
            contrib_interval=7
        )

        # Create scheduler and schedule the envelope.
        scheduler = IndependentScheduler()
        schedules = scheduler.schedule(envelopes=[envelope])

        # Test: Should return schedule.
        assert envelope in schedules

        # Test: Should handle partial interval correctly.
        schedule = schedules[envelope]
        contributions = [
            cf for cf in schedule.cash_flows if cf.amount > 0
        ]

        # Test: Should have contributions for full intervals plus partial.
        assert len(contributions) >= 2

        # Test: Total should equal remaining amount.
        total = sum(cf.amount for cf in contributions)
        remaining = bill.amount_due - envelope.initial_allocation
        assert abs(total - remaining) < Decimal("0.01")

    def test_zero_remaining_amount(self) -> None:
        """
        Test scheduling when remaining amount is zero (fully funded).
        """

        # Create bill instance.
        bill = BillInstance(
            bill_id="zero_remaining",
            service="Zero Remaining Bill",
            due_date=datetime.date(2024, 2, 15),
            amount_due=Decimal("150.00")
        )

        # Create envelope with initial allocation equal to bill amount.
        envelope = Envelope(
            bill_instance=bill,
            initial_allocation=Decimal("150.00"),
            start_contrib_date=datetime.date(2024, 1, 1),
            end_contrib_date=datetime.date(2024, 2, 14),
            contrib_interval=14
        )

        # Create scheduler and schedule the envelope.
        scheduler = IndependentScheduler()
        schedules = scheduler.schedule(envelopes=[envelope])

        # Test: Should return schedule.
        assert envelope in schedules

        # Test: Should have only payment, no contributions.
        schedule = schedules[envelope]
        contributions = [
            cf for cf in schedule.cash_flows if cf.amount > 0
        ]
        payments = [cf for cf in schedule.cash_flows if cf.amount < 0]

        assert len(contributions) == 0
        assert len(payments) == 1

########################################################################
## CALCULATE DAILY CONTRIBUTION TESTS
########################################################################

class TestCalculateDailyContribution:
    """
    Test the calculate_daily_contribution method with edge cases.
    """

    def test_normal_calculation(self) -> None:
        """
        Test normal daily contribution calculation.
        """

        # Create scheduler.
        scheduler = IndependentScheduler()

        # Test: 100 dollars over 10 days = 10 per day.
        remaining = Decimal("100.00")
        due_date = datetime.date(2024, 1, 11)
        curr_date = datetime.date(2024, 1, 1)

        daily_contrib = scheduler.calculate_daily_contribution(
            remaining=remaining,
            due_date=due_date,
            curr_date=curr_date
        )

        assert daily_contrib == Decimal("10.00")

    def test_past_due_bill(self) -> None:
        """
        Test calculation for a past-due bill.
        """

        # Create scheduler.
        scheduler = IndependentScheduler()

        # Test: Past-due bill should return full remaining amount.
        remaining = Decimal("100.00")
        due_date = datetime.date(2024, 1, 1)
        curr_date = datetime.date(2024, 1, 5)

        daily_contrib = scheduler.calculate_daily_contribution(
            remaining=remaining,
            due_date=due_date,
            curr_date=curr_date
        )

        assert daily_contrib == remaining

    def test_bill_due_today(self) -> None:
        """
        Test calculation for a bill due today.
        """

        # Create scheduler.
        scheduler = IndependentScheduler()

        # Test: Bill due today should return full remaining amount.
        remaining = Decimal("150.00")
        today = datetime.date(2024, 1, 15)
        due_date = today
        curr_date = today

        daily_contrib = scheduler.calculate_daily_contribution(
            remaining=remaining,
            due_date=due_date,
            curr_date=curr_date
        )

        assert daily_contrib == remaining

    def test_zero_remaining_amount(self) -> None:
        """
        Test calculation with zero remaining amount.
        """

        # Create scheduler.
        scheduler = IndependentScheduler()

        # Test: Zero remaining should return zero.
        remaining = Decimal("0.00")
        due_date = datetime.date(2024, 1, 31)
        curr_date = datetime.date(2024, 1, 1)

        daily_contrib = scheduler.calculate_daily_contribution(
            remaining=remaining,
            due_date=due_date,
            curr_date=curr_date
        )

        assert daily_contrib == Decimal("0.00")

    def test_single_day_period(self) -> None:
        """
        Test calculation for a single-day contribution period.
        """

        # Create scheduler.
        scheduler = IndependentScheduler()

        # Test: 1 day period should return full amount.
        remaining = Decimal("75.00")
        due_date = datetime.date(2024, 1, 2)
        curr_date = datetime.date(2024, 1, 1)

        daily_contrib = scheduler.calculate_daily_contribution(
            remaining=remaining,
            due_date=due_date,
            curr_date=curr_date
        )

        assert daily_contrib == remaining

    def test_fractional_daily_contribution(self) -> None:
        """
        Test calculation that results in fractional daily contribution.
        """

        # Create scheduler.
        scheduler = IndependentScheduler()

        # Test: 100 dollars over 3 days = 33.33... per day.
        remaining = Decimal("100.00")
        due_date = datetime.date(2024, 1, 4)
        curr_date = datetime.date(2024, 1, 1)

        daily_contrib = scheduler.calculate_daily_contribution(
            remaining=remaining,
            due_date=due_date,
            curr_date=curr_date
        )

        # Test: Should be approximately 33.33.
        expected = Decimal("100.00") / Decimal("3")
        assert abs(daily_contrib - expected) < Decimal("0.01")

    def test_large_amount_long_period(self) -> None:
        """
        Test calculation with large amount over long period.
        """

        # Create scheduler.
        scheduler = IndependentScheduler()

        # Test: Large amount over long period.
        remaining = Decimal("10000.00")
        due_date = datetime.date(2024, 12, 31)
        curr_date = datetime.date(2024, 1, 1)

        daily_contrib = scheduler.calculate_daily_contribution(
            remaining=remaining,
            due_date=due_date,
            curr_date=curr_date
        )

        # Test: Should calculate correctly.
        expected = Decimal("10000.00") / Decimal("365")
        assert abs(daily_contrib - expected) < Decimal("0.01")

########################################################################
## CALCULATE CONTRIBUTION INTERVALS TESTS
########################################################################

class TestCalculateContributionIntervals:
    """
    Test the calculate_contribution_intervals method with edge cases.
    """

    def test_even_division(self) -> None:
        """
        Test interval calculation when period divides evenly.
        """

        # Create scheduler.
        scheduler = IndependentScheduler()

        # Test: 14 days with 7-day interval = 2 intervals.
        start_date = datetime.date(2024, 1, 1)
        end_date = datetime.date(2024, 1, 15)
        interval = 7

        intervals = scheduler.calculate_contribution_intervals(
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )

        assert intervals == [7, 7]

    def test_partial_interval(self) -> None:
        """
        Test interval calculation with partial interval at end.
        """

        # Create scheduler.
        scheduler = IndependentScheduler()

        # Test: 19 days with 7-day interval = 2 full + 5 partial.
        start_date = datetime.date(2024, 1, 1)
        end_date = datetime.date(2024, 1, 20)
        interval = 7

        intervals = scheduler.calculate_contribution_intervals(
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )

        assert intervals == [7, 7, 5]

    def test_start_equals_end(self) -> None:
        """
        Test interval calculation when start and end dates are equal.
        """

        # Create scheduler.
        scheduler = IndependentScheduler()

        # Test: Same start and end date returns empty list (0 days).
        same_date = datetime.date(2024, 1, 15)
        interval = 7

        intervals = scheduler.calculate_contribution_intervals(
            start_date=same_date,
            end_date=same_date,
            interval=interval
        )

        assert intervals == []

    def test_period_shorter_than_interval(self) -> None:
        """
        Test interval calculation when period is shorter than interval.
        """

        # Create scheduler.
        scheduler = IndependentScheduler()

        # Test: 3 days with 7-day interval = 1 partial interval of 3.
        start_date = datetime.date(2024, 1, 1)
        end_date = datetime.date(2024, 1, 4)
        interval = 7

        intervals = scheduler.calculate_contribution_intervals(
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )

        assert intervals == [3]

    def test_single_day_period(self) -> None:
        """
        Test interval calculation for a single-day period.
        """

        # Create scheduler.
        scheduler = IndependentScheduler()

        # Test: 1 day period.
        start_date = datetime.date(2024, 1, 1)
        end_date = datetime.date(2024, 1, 2)
        interval = 7

        intervals = scheduler.calculate_contribution_intervals(
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )

        assert intervals == [1]

    def test_interval_size_one(self) -> None:
        """
        Test interval calculation with interval size of 1.
        """

        # Create scheduler.
        scheduler = IndependentScheduler()

        # Test: 5 days with 1-day interval = 5 intervals of 1.
        start_date = datetime.date(2024, 1, 1)
        end_date = datetime.date(2024, 1, 6)
        interval = 1

        intervals = scheduler.calculate_contribution_intervals(
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )

        assert intervals == [1, 1, 1, 1, 1]

    def test_large_interval(self) -> None:
        """
        Test interval calculation with large interval size.
        """

        # Create scheduler.
        scheduler = IndependentScheduler()

        # Test: 20 days with 30-day interval = 1 partial interval.
        start_date = datetime.date(2024, 1, 1)
        end_date = datetime.date(2024, 1, 21)
        interval = 30

        intervals = scheduler.calculate_contribution_intervals(
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )

        assert intervals == [20]

    def test_multiple_full_intervals(self) -> None:
        """
        Test interval calculation with multiple full intervals.
        """

        # Create scheduler.
        scheduler = IndependentScheduler()

        # Test: 28 days with 7-day interval = 4 full intervals.
        start_date = datetime.date(2024, 1, 1)
        end_date = datetime.date(2024, 1, 29)
        interval = 7

        intervals = scheduler.calculate_contribution_intervals(
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )

        assert intervals == [7, 7, 7, 7]

    def test_exact_interval_match(self) -> None:
        """
        Test interval calculation when period exactly matches interval.
        """

        # Create scheduler.
        scheduler = IndependentScheduler()

        # Test: 7 days with 7-day interval = 1 full interval.
        start_date = datetime.date(2024, 1, 1)
        end_date = datetime.date(2024, 1, 8)
        interval = 7

        intervals = scheduler.calculate_contribution_intervals(
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )

        assert intervals == [7]

