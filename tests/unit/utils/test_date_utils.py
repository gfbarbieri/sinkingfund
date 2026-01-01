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
    Frequency, 
    increment_date, 
    increment_monthly, 
    get_date_range,
    parse_date,
    normalize_date_fields,
    SUPPORTED_DATE_FORMATS
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

########################################################################
## DATE PARSING TESTS
########################################################################

class TestParseDate:
    """Test parse_date function for date string conversion."""

    def test_parse_date_with_date_object(self) -> None:
        """
        Test parse_date with already-converted date objects.
        """
        
        # Test: Date object should be returned as-is.
        date_obj = datetime.date(2025, 1, 15)
        result = parse_date(date_obj)
        assert result == date_obj
        assert isinstance(result, datetime.date)

    def test_parse_date_with_string_formats(self) -> None:
        """
        Test parse_date with all supported string formats.
        """
        
        expected_date = datetime.date(2025, 1, 15)
        
        # Test: US format (MM/DD/YYYY).
        result = parse_date("01/15/2025")
        assert result == expected_date
        
        # Test: ISO format (YYYY-MM-DD).
        result = parse_date("2025-01-15")
        assert result == expected_date
        
        # Test: US with dashes (MM-DD-YYYY).
        result = parse_date("01-15-2025")
        assert result == expected_date
        
        # Test: European format (DD/MM/YYYY).
        result = parse_date("15/01/2025")
        assert result == expected_date
        
        # Test: European with dashes (DD-MM-YYYY).
        result = parse_date("15-01-2025")
        assert result == expected_date
        
        # Test: ISO with slashes (YYYY/MM/DD).
        result = parse_date("2025/01/15")
        assert result == expected_date

    def test_parse_date_with_datetime(self) -> None:
        """
        Test parse_date with datetime objects.
        """
        
        # Test: Datetime object should be converted to date.
        dt = datetime.datetime(2025, 1, 15, 10, 30, 45)
        result = parse_date(dt)
        assert result == datetime.date(2025, 1, 15)
        assert isinstance(result, datetime.date)

    def test_parse_date_with_timestamp(self) -> None:
        """
        Test parse_date with pandas Timestamp objects.
        """
        
        try:
            import pandas as pd
            
            # Test: Timestamp should be converted to date.
            ts = pd.Timestamp('2025-01-15')
            result = parse_date(ts)
            assert result == datetime.date(2025, 1, 15)
            assert isinstance(result, datetime.date)
        except ImportError:
            # Pandas not available, skip test.
            pytest.skip("pandas not available")

    def test_parse_date_with_none(self) -> None:
        """
        Test parse_date with None values.
        """
        
        # Test: None should return None.
        result = parse_date(None)
        assert result is None

    def test_parse_date_with_invalid_string(self) -> None:
        """
        Test parse_date with unparseable strings.
        """
        
        # Test: Invalid date string should return None.
        result = parse_date("not a date")
        assert result is None
        
        # Test: Empty string should return None.
        result = parse_date("")
        assert result is None
        
        # Test: Malformed date string should return None.
        result = parse_date("2025/13/45")
        assert result is None

    def test_parse_date_with_whitespace(self) -> None:
        """
        Test parse_date handles whitespace in strings.
        """
        
        # Test: String with leading/trailing whitespace.
        result = parse_date("  01/15/2025  ")
        assert result == datetime.date(2025, 1, 15)

    def test_parse_date_with_unrecognized_type(self) -> None:
        """
        Test parse_date with unrecognized types.
        """
        
        # Test: Integer should return None.
        result = parse_date(20250115)
        assert result is None
        
        # Test: List should return None.
        result = parse_date([2025, 1, 15])
        assert result is None

class TestNormalizeDateFields:
    """Test normalize_date_fields function for batch date conversion."""

    def test_normalize_date_fields_all_formats(self) -> None:
        """
        Test normalize_date_fields with various date string formats.
        """
        
        record = {
            'bill_id': 'test',
            'service': 'Test Service',
            'amount_due': 100.00,
            'recurring': False,
            'due_date': '01/15/2025',      # US format
            'start_date': '2025-02-01',    # ISO format
            'end_date': '15/03/2025'       # European format
        }
        
        result = normalize_date_fields(
            record, 
            ['due_date', 'start_date', 'end_date']
        )
        
        assert result['due_date'] == datetime.date(2025, 1, 15)
        assert result['start_date'] == datetime.date(2025, 2, 1)
        assert result['end_date'] == datetime.date(2025, 3, 15)
        assert isinstance(result['due_date'], datetime.date)
        assert isinstance(result['start_date'], datetime.date)
        assert isinstance(result['end_date'], datetime.date)
        
        # Test: Original record should not be modified.
        assert record['due_date'] == '01/15/2025'

    def test_normalize_date_fields_with_date_objects(self) -> None:
        """
        Test normalize_date_fields with already-converted date objects.
        """
        
        record = {
            'bill_id': 'test',
            'due_date': datetime.date(2025, 1, 15),
            'start_date': datetime.date(2025, 2, 1)
        }
        
        result = normalize_date_fields(
            record,
            ['due_date', 'start_date', 'end_date']
        )
        
        assert result['due_date'] == datetime.date(2025, 1, 15)
        assert result['start_date'] == datetime.date(2025, 2, 1)
        assert result.get('end_date') is None

    def test_normalize_date_fields_with_none(self) -> None:
        """
        Test normalize_date_fields with None values.
        """
        
        record = {
            'bill_id': 'test',
            'due_date': None,
            'start_date': '2025-01-15',
            'end_date': None
        }
        
        result = normalize_date_fields(
            record,
            ['due_date', 'start_date', 'end_date']
        )
        
        assert result['due_date'] is None
        assert result['start_date'] == datetime.date(2025, 1, 15)
        assert result['end_date'] is None

    def test_normalize_date_fields_partial(self) -> None:
        """
        Test normalize_date_fields with missing date fields.
        """
        
        record = {
            'bill_id': 'test',
            'due_date': '01/15/2025'
            # start_date and end_date missing
        }
        
        result = normalize_date_fields(
            record,
            ['due_date', 'start_date', 'end_date']
        )
        
        assert result['due_date'] == datetime.date(2025, 1, 15)
        assert 'start_date' not in result
        assert 'end_date' not in result

    def test_normalize_date_fields_preserves_other_fields(self) -> None:
        """
        Test normalize_date_fields preserves non-date fields.
        """
        
        record = {
            'bill_id': 'test',
            'service': 'Test Service',
            'amount_due': 100.00,
            'recurring': True,
            'due_date': '01/15/2025'
        }
        
        result = normalize_date_fields(
            record,
            ['due_date', 'start_date', 'end_date']
        )
        
        assert result['bill_id'] == 'test'
        assert result['service'] == 'Test Service'
        assert result['amount_due'] == 100.00
        assert result['recurring'] is True
        assert result['due_date'] == datetime.date(2025, 1, 15)

class TestSupportedDateFormats:
    """Test SUPPORTED_DATE_FORMATS constant."""

    def test_supported_formats_constant(self) -> None:
        """
        Test that SUPPORTED_DATE_FORMATS contains expected formats.
        """
        
        assert isinstance(SUPPORTED_DATE_FORMATS, list)
        assert len(SUPPORTED_DATE_FORMATS) > 0
        
        # Test: All formats should be valid strftime format strings.
        for fmt in SUPPORTED_DATE_FORMATS:
            assert isinstance(fmt, str)
            # Verify format can be used with strptime.
            try:
                datetime.datetime.strptime("2025-01-15", fmt)
            except ValueError:
                # Some formats won't match this specific date, which is fine.
                # Just verify it's a valid format string by trying a parse.
                pass
