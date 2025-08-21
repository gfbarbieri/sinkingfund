"""
Date Utilities Tests
====================

Comprehensive tests for date arithmetic functions covering calendar-aware
calculations, month-end normalization, leap year handling, and edge cases
critical for financial calculations.
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import datetime
import pytest

from sinkingfund.utils.date_utils import (
    Frequency, increment_date, increment_monthly, get_date_range
)

########################################################################
## TEST CLASSES
########################################################################

class TestIncrementDate:
    """Test increment_date function with various frequencies and intervals."""

    def test_daily_increment_basic(self) -> None:
        """
        Test basic daily increments.
        """
        
        # Test: Single day increment.
        result = increment_date(
            reference_date=datetime.date(2024, 1, 15),
            frequency='daily',
            interval=1
        )
        assert result == datetime.date(2024, 1, 16)
        
        # Test: Multiple day increment.
        result = increment_date(
            reference_date=datetime.date(2024, 1, 15),
            frequency='daily',
            interval=7
        )
        assert result == datetime.date(2024, 1, 22)

    def test_daily_increment_with_num_intervals(self) -> None:
        """
        Test daily increments with multiple intervals.
        """
        
        # Test: 5 days, 3 times = 15 days total.
        result = increment_date(
            reference_date=datetime.date(2024, 1, 1),
            frequency='daily',
            interval=5,
            num_intervals=3
        )
        assert result == datetime.date(2024, 1, 16)

    def test_weekly_increment_basic(self) -> None:
        """
        Test basic weekly increments.
        """
        
        # Test: Single week increment.
        result = increment_date(
            reference_date=datetime.date(2024, 1, 15),
            frequency='weekly',
            interval=1
        )
        assert result == datetime.date(2024, 1, 22)
        
        # Test: Bi-weekly increment.
        result = increment_date(
            reference_date=datetime.date(2024, 1, 15),
            frequency='weekly',
            interval=2
        )
        assert result == datetime.date(2024, 1, 29)

    def test_monthly_increment_basic(self) -> None:
        """
        Test basic monthly increments.
        """
        
        # Test: Single month increment.
        result = increment_date(
            reference_date=datetime.date(2024, 1, 15),
            frequency='monthly',
            interval=1
        )
        assert result == datetime.date(2024, 2, 15)
        
        # Test: Multiple month increment.
        result = increment_date(
            reference_date=datetime.date(2024, 1, 15),
            frequency='monthly',
            interval=3
        )
        assert result == datetime.date(2024, 4, 15)

    def test_monthly_increment_month_end_normalization(self) -> None:
        """
        Test month-end date normalization for shorter months.
        """
        
        # Test: January 31st to February (28 days in non-leap year).
        result = increment_date(
            reference_date=datetime.date(2023, 1, 31),
            frequency='monthly',
            interval=1
        )
        assert result == datetime.date(2023, 2, 28)
        
        # Test: January 31st to February (29 days in leap year).
        result = increment_date(
            reference_date=datetime.date(2024, 1, 31),
            frequency='monthly',
            interval=1
        )
        assert result == datetime.date(2024, 2, 29)
        
        # Test: January 31st to April (30 days).
        result = increment_date(
            reference_date=datetime.date(2024, 1, 31),
            frequency='monthly',
            interval=3
        )
        assert result == datetime.date(2024, 4, 30)

    def test_quarterly_increment(self) -> None:
        """
        Test quarterly increments (3-month intervals).
        """
        
        # Test: Single quarter increment.
        result = increment_date(
            reference_date=datetime.date(2024, 1, 15),
            frequency='quarterly',
            interval=1
        )
        assert result == datetime.date(2024, 4, 15)
        
        # Test: Multiple quarter increment.
        result = increment_date(
            reference_date=datetime.date(2024, 1, 15),
            frequency='quarterly',
            interval=2
        )
        assert result == datetime.date(2024, 7, 15)

    def test_annual_increment_basic(self) -> None:
        """
        Test basic annual increments.
        """
        
        # Test: Single year increment.
        result = increment_date(
            reference_date=datetime.date(2024, 1, 15),
            frequency='annual',
            interval=1
        )
        assert result == datetime.date(2025, 1, 15)
        
        # Test: Multiple year increment.
        result = increment_date(
            reference_date=datetime.date(2024, 1, 15),
            frequency='annual',
            interval=2
        )
        assert result == datetime.date(2026, 1, 15)

    def test_annual_increment_leap_year_handling(self) -> None:
        """
        Test leap year February 29th handling in annual increments.
        """
        
        # Test: February 29th, 2024 (leap year) to 2025 (non-leap year).
        result = increment_date(
            reference_date=datetime.date(2024, 2, 29),
            frequency='annual',
            interval=1
        )
        assert result == datetime.date(2025, 2, 28)
        
        # Test: February 29th, 2024 to 2028 (both leap years).
        result = increment_date(
            reference_date=datetime.date(2024, 2, 29),
            frequency='annual',
            interval=4
        )
        assert result == datetime.date(2028, 2, 29)

    def test_frequency_enum_support(self) -> None:
        """
        Test using Frequency enum instead of strings.
        """
        
        # Test: Monthly with enum.
        result = increment_date(
            reference_date=datetime.date(2024, 1, 15),
            frequency=Frequency.MONTHLY,
            interval=1
        )
        assert result == datetime.date(2024, 2, 15)
        
        # Test: Weekly with enum.
        result = increment_date(
            reference_date=datetime.date(2024, 1, 15),
            frequency=Frequency.WEEKLY,
            interval=1
        )
        assert result == datetime.date(2024, 1, 22)

    def test_case_insensitive_frequency(self) -> None:
        """
        Test case-insensitive frequency strings.
        """
        
        # Test: Uppercase frequency.
        result = increment_date(
            reference_date=datetime.date(2024, 1, 15),
            frequency='MONTHLY',
            interval=1
        )
        assert result == datetime.date(2024, 2, 15)
        
        # Test: Mixed case frequency.
        result = increment_date(
            reference_date=datetime.date(2024, 1, 15),
            frequency='Monthly',
            interval=1
        )
        assert result == datetime.date(2024, 2, 15)

    def test_validation_errors(self) -> None:
        """
        Test input validation and error handling.
        """
        
        # Test: Invalid interval (zero).
        with pytest.raises(ValueError, match="interval must be positive"):
            increment_date(
                reference_date=datetime.date(2024, 1, 15),
                frequency='monthly',
                interval=0
            )
        
        # Test: Invalid interval (negative).
        with pytest.raises(ValueError, match="interval must be positive"):
            increment_date(
                reference_date=datetime.date(2024, 1, 15),
                frequency='monthly',
                interval=-1
            )
        
        # Test: Invalid num_intervals.
        with pytest.raises(ValueError, match="num_intervals must be positive"):
            increment_date(
                reference_date=datetime.date(2024, 1, 15),
                frequency='monthly',
                interval=1,
                num_intervals=0
            )
        
        # Test: Unsupported frequency.
        with pytest.raises(ValueError, match="Unsupported frequency"):
            increment_date(
                reference_date=datetime.date(2024, 1, 15),
                frequency='invalid',
                interval=1
            )

class TestIncrementMonthly:
    """Test increment_monthly function for month arithmetic."""

    def test_basic_month_increment(self) -> None:
        """
        Test basic monthly increments.
        """
        
        # Test: Single month forward.
        result = increment_monthly(
            date=datetime.date(2024, 1, 15),
            num_months=1
        )
        assert result == datetime.date(2024, 2, 15)
        
        # Test: Multiple months forward.
        result = increment_monthly(
            date=datetime.date(2024, 1, 15),
            num_months=6
        )
        assert result == datetime.date(2024, 7, 15)

    def test_month_increment_year_boundary(self) -> None:
        """
        Test month increments crossing year boundaries.
        """
        
        # Test: December to January next year.
        result = increment_monthly(
            date=datetime.date(2024, 12, 15),
            num_months=1
        )
        assert result == datetime.date(2025, 1, 15)
        
        # Test: February to next February.
        result = increment_monthly(
            date=datetime.date(2024, 2, 15),
            num_months=12
        )
        assert result == datetime.date(2025, 2, 15)

    def test_month_increment_day_normalization(self) -> None:
        """
        Test day normalization for months with different lengths.
        """
        
        # Test: January 31st to February (28 days).
        result = increment_monthly(
            date=datetime.date(2023, 1, 31),
            num_months=1
        )
        assert result == datetime.date(2023, 2, 28)
        
        # Test: March 31st to April (30 days).
        result = increment_monthly(
            date=datetime.date(2024, 3, 31),
            num_months=1
        )
        assert result == datetime.date(2024, 4, 30)
        
        # Test: January 31st to May (31 days).
        result = increment_monthly(
            date=datetime.date(2024, 1, 31),
            num_months=4
        )
        assert result == datetime.date(2024, 5, 31)

    def test_negative_month_increment(self) -> None:
        """
        Test backward month increments (negative values).
        """
        
        # Test: Single month backward.
        result = increment_monthly(
            date=datetime.date(2024, 2, 15),
            num_months=-1
        )
        assert result == datetime.date(2024, 1, 15)
        
        # Test: Year boundary backward.
        result = increment_monthly(
            date=datetime.date(2024, 1, 15),
            num_months=-1
        )
        assert result == datetime.date(2023, 12, 15)

class TestGetDateRange:
    """Test get_date_range function for date sequence generation."""

    def test_basic_date_range(self) -> None:
        """
        Test basic date range generation.
        """
        
        # Test: Simple 3-day range.
        result = get_date_range(
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 1, 3)
        )
        expected = [
            datetime.date(2024, 1, 1),
            datetime.date(2024, 1, 2),
            datetime.date(2024, 1, 3)
        ]
        assert result == expected

    def test_single_day_range(self) -> None:
        """
        Test date range with start and end on same day.
        """
        
        result = get_date_range(
            start_date=datetime.date(2024, 1, 15),
            end_date=datetime.date(2024, 1, 15)
        )
        expected = [datetime.date(2024, 1, 15)]
        assert result == expected

    def test_month_crossing_range(self) -> None:
        """
        Test date range crossing month boundaries.
        """
        
        # Test: January 30th to February 2nd.
        result = get_date_range(
            start_date=datetime.date(2024, 1, 30),
            end_date=datetime.date(2024, 2, 2)
        )
        expected = [
            datetime.date(2024, 1, 30),
            datetime.date(2024, 1, 31),
            datetime.date(2024, 2, 1),
            datetime.date(2024, 2, 2)
        ]
        assert result == expected

    def test_year_crossing_range(self) -> None:
        """
        Test date range crossing year boundaries.
        """
        
        # Test: December 30th to January 2nd.
        result = get_date_range(
            start_date=datetime.date(2023, 12, 30),
            end_date=datetime.date(2024, 1, 2)
        )
        expected = [
            datetime.date(2023, 12, 30),
            datetime.date(2023, 12, 31),
            datetime.date(2024, 1, 1),
            datetime.date(2024, 1, 2)
        ]
        assert result == expected

    def test_leap_year_range(self) -> None:
        """
        Test date range including February 29th in leap year.
        """
        
        result = get_date_range(
            start_date=datetime.date(2024, 2, 28),
            end_date=datetime.date(2024, 3, 1)
        )
        expected = [
            datetime.date(2024, 2, 28),
            datetime.date(2024, 2, 29),
            datetime.date(2024, 3, 1)
        ]
        assert result == expected

########################################################################
## INTEGRATION TESTS
########################################################################

class TestDateUtilsIntegration:
    """Test integration scenarios using multiple date utilities."""

    def test_bill_schedule_generation(self) -> None:
        """
        Test generating a typical bill payment schedule.
        """
        
        # Test: Monthly bill for 6 months.
        start_date = datetime.date(2024, 1, 15)
        dates = []
        
        current_date = start_date
        for _ in range(6):
            dates.append(current_date)
            current_date = increment_date(
                reference_date=current_date,
                frequency='monthly',
                interval=1
            )
        
        expected = [
            datetime.date(2024, 1, 15),
            datetime.date(2024, 2, 15),
            datetime.date(2024, 3, 15),
            datetime.date(2024, 4, 15),
            datetime.date(2024, 5, 15),
            datetime.date(2024, 6, 15)
        ]
        assert dates == expected

    def test_quarter_end_dates(self) -> None:
        """
        Test generating quarter-end dates for financial planning.
        """
        
        # Test: Quarterly dates starting January 31st.
        # Each calculation should be direct from the original date.
        start_date = datetime.date(2024, 1, 31)
        dates = []
        
        # Include the starting date
        dates.append(start_date)
        
        for i in range(1, 4):
            date = increment_date(
                reference_date=start_date,
                frequency='quarterly',
                interval=1,
                num_intervals=i
            )
            dates.append(date)
        
        # Should preserve original day (31st) when possible.
        expected = [
            datetime.date(2024, 1, 31),   # starting date
            datetime.date(2024, 4, 30),   # +3 months, April has 30 days
            datetime.date(2024, 7, 31),   # +6 months, July has 31 days  
            datetime.date(2024, 10, 31)   # +9 months, October has 31 days
        ]
        assert dates == expected

    def test_bi_weekly_payroll_schedule(self) -> None:
        """
        Test generating bi-weekly payroll schedule.
        """
        
        # Test: Bi-weekly for 8 weeks (4 pay periods).
        start_date = datetime.date(2024, 1, 5)  # First Friday
        dates = []
        
        current_date = start_date
        for _ in range(4):
            dates.append(current_date)
            current_date = increment_date(
                reference_date=current_date,
                frequency='weekly',
                interval=2
            )
        
        expected = [
            datetime.date(2024, 1, 5),
            datetime.date(2024, 1, 19),
            datetime.date(2024, 2, 2),
            datetime.date(2024, 2, 16)
        ]
        assert dates == expected
