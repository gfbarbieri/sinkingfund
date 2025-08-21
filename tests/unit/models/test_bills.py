"""
Bill Model Tests
================

Comprehensive tests for Bill and BillInstance models covering
validation, date calculations, and recurring bill generation.
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import datetime
from decimal import Decimal

import pytest

from sinkingfund.models import Bill, BillInstance

########################################################################
## BILL INSTANCE TESTS
########################################################################

class TestBillInstance:
    """
    Test BillInstance model validation and behavior.
    """

    def test_valid_bill_instance_creation(self) -> None:
        """
        Test creating a valid bill instance with all required fields.
        """

        # Create a valid bill instance.
        instance = BillInstance(
            bill_id="test_bill",
            service="Test Service",
            due_date=datetime.date(2024, 3, 15),
            amount_due=Decimal("100.00")
        )

        # Assert that the bill instance was created correctly by
        # checking each field.
        assert instance.bill_id == "test_bill"
        assert instance.service == "Test Service"
        assert instance.due_date == datetime.date(2024, 3, 15)
        assert instance.amount_due == Decimal("100.00")

    def test_bill_instance_validates_empty_bill_id(self) -> None:
        """
        Test that BillInstance rejects empty bill_id.
        """
        
        # Test that an empty bill_id raises a ValueError.
        with pytest.raises(
            ValueError, match="bill_id cannot be empty or whitespace."
        ):
            BillInstance(
                bill_id="",
                service="Test Service",
                due_date=datetime.date(2024, 3, 15),
                amount_due=Decimal("100.00")
            )
        
        # Test that a bill_id with only whitespace raises a ValueError.
        with pytest.raises(
            ValueError, match="bill_id cannot be empty or whitespace."
        ):
            BillInstance(
                bill_id="   ",
                service="Test Service", 
                due_date=datetime.date(2024, 3, 15),
                amount_due=Decimal("100.00")
            )

    def test_bill_instance_validates_empty_service(self) -> None:
        """
        Test that BillInstance rejects empty service names.
        """
        
        # Test that an empty service raises a ValueError.
        with pytest.raises(
            ValueError, match="service cannot be empty or whitespace."
        ):
            BillInstance(
                bill_id="test_bill",
                service="",
                due_date=datetime.date(2024, 3, 15),
                amount_due=Decimal("100.00")
            )

    def test_bill_instance_validates_positive_amount(self) -> None:
        """
        Test that BillInstance requires positive amounts.
        """

        # Test that a zero amount raises a ValueError.
        with pytest.raises(
            ValueError, match="amount_due must be positive."
        ):
            BillInstance(
                bill_id="test_bill",
                service="Test Service",
                due_date=datetime.date(2024, 3, 15),
                amount_due=Decimal("0.00")
            )
        
        # Test that a negative amount raises a ValueError.
        with pytest.raises(
            ValueError, match="amount_due must be positive."
        ):
            BillInstance(
                bill_id="test_bill",
                service="Test Service",
                due_date=datetime.date(2024, 3, 15),
                amount_due=Decimal("-50.00")
            )

    def test_bill_instance_converts_numeric_amount(self) -> None:
        """
        Test that BillInstance accepts and converts numeric amounts.
        """

        # Create a bill instance with a numeric amount.
        instance = BillInstance(
            bill_id="test_bill",
            service="Test Service",
            due_date=datetime.date(2024, 3, 15),
            amount_due=100.50  # Float input.
        )
        
        # Assert that the amount was converted to a Decimal.
        assert isinstance(instance.amount_due, Decimal)
        assert instance.amount_due == Decimal("100.50")

########################################################################
## BILL TESTS
########################################################################

class TestBill:
    """
    Test Bill model validation and behavior.
    """

    def test_one_time_bill_creation(self) -> None:
        """
        Test creating a valid one-time bill.
        """

        # Create a one-time bill with a numeric amount.
        bill = Bill(
            bill_id="car_registration",
            service="Annual Car Registration",
            amount_due=125.00, # Numeric input, not Decimal.
            recurring=False, # Not recurring.
            due_date=datetime.date(2024, 3, 15) # Due date.
        )
        
        # Assert that the bill was created correctly by checking each
        # field. Tests that the amount was converted to a Decimal and
        # that the start_date and end_date are set to the due_date.
        assert bill.bill_id == "car_registration"
        assert bill.service == "Annual Car Registration"
        assert bill.amount_due == Decimal("125.00")
        assert bill.recurring is False
        assert bill.start_date == datetime.date(2024, 3, 15)
        assert bill.end_date == datetime.date(2024, 3, 15)
        assert bill.frequency is None
        assert bill.interval is None
        assert bill.occurrences == 1

    def test_recurring_bill_creation(self) -> None:
        """
        Test creating a valid recurring bill with finite occurrences.
        """

        # Create a recurring bill.
        bill = Bill(
            bill_id="electric",
            service="Monthly Electric Bill",
            amount_due=150.00, # Numeric input, not Decimal.
            recurring=True, # Recurring.
            start_date=datetime.date(2024, 1, 15), # Start date.
            frequency="monthly", # Frequency.
            interval=1, # Interval, so monthly every month.
            occurrences=12 # Occurrences, so 12 months.
        )
        
        # Assert that the bill was created correctly by checking each
        # field. Tests that the amount was converted to a Decimal and
        # that the start_date and end_date are set to the due_date.
        assert bill.bill_id == "electric"
        assert bill.service == "Monthly Electric Bill"
        assert bill.amount_due == Decimal("150.00")
        assert bill.recurring is True
        assert bill.start_date == datetime.date(2024, 1, 15)
        assert bill.end_date == datetime.date(2024, 12, 15)
        assert bill.frequency == "monthly"
        assert bill.interval == 1
        assert bill.occurrences == 12

    def test_bill_validates_empty_bill_id(self) -> None:
        """
        Test that Bill rejects empty bill_id.
        """

        # Test that an empty bill_id raises a ValueError.
        with pytest.raises(
            ValueError, match="bill_id cannot be empty or whitespace."
        ):
            Bill(
                bill_id="",
                service="Test Service",
                amount_due=100.00, # Numeric input, not Decimal.
                recurring=False,
                due_date=datetime.date(2024, 3, 15)
            )

    def test_bill_validates_positive_amount(self) -> None:
        """
        Test that Bill requires positive amounts.
        """

        # Test that a zero amount raises a ValueError.
        with pytest.raises(
            ValueError, match="amount_due must be positive."
        ):
            Bill(
                bill_id="test_bill",
                service="Test Service",
                amount_due=0.00, # Numeric input, not Decimal.
                recurring=False,
                due_date=datetime.date(2024, 3, 15)
            )

    def test_bill_validates_recurring_frequency(self) -> None:
        """
        Test that recurring bills require valid frequency.
        """

        # Test that a recurring bill with no frequency raises
        # ValueError.
        with pytest.raises(
            ValueError, match="Recurring bills must have a frequency."
        ):
            Bill(
                bill_id="test_bill",
                service="Test Service",
                amount_due=100.00, # Numeric input, not Decimal.
                recurring=True,
                start_date=datetime.date(2024, 3, 15),
                frequency=None, # No frequency!
                interval=1 # Interval is required for recurring bills.
            )

    def test_bill_validates_frequency_values(self) -> None:
        """
        Test that Bill validates frequency values.
        """

        # Create a list of valid frequencies.
        valid_frequencies = [
            "daily", "weekly", "monthly", "quarterly", "annual"
        ]
        
        # Test: Valid frequencies should not raise a ValueError.
        for freq in valid_frequencies:
            bill = Bill(
                bill_id="test_bill",
                service="Test Service",
                amount_due=100.00, # Numeric input, not Decimal.
                recurring=True,
                start_date=datetime.date(2024, 3, 15),
                frequency=freq,
                interval=1
            )
            assert bill.frequency == freq

        # Test: Invalid frequency should raise a ValueError.
        with pytest.raises(
            ValueError, match=(
                "Invalid frequency: invalid. Must be one of: "
                "daily, weekly, monthly, quarterly, annual."
            )
        ):
            Bill(
                bill_id="test_bill",
                service="Test Service",
                amount_due=100.00, # Numeric input, not Decimal.
                recurring=True,
                start_date=datetime.date(2024, 3, 15),
                frequency="invalid",
                interval=1
            )

    def test_bill_validates_positive_interval(self) -> None:
        """
        Test that Bill requires positive intervals.
        """

        # Test: A zero interval raises a ValueError.
        with pytest.raises(ValueError, match="interval must be positive."):
            Bill(
                bill_id="test_bill",
                service="Test Service",
                amount_due=100.00, # Numeric input, not Decimal.
                recurring=True,
                start_date=datetime.date(2024, 3, 15),
                frequency="monthly",
                interval=0
            )

    def test_bill_validates_date_order(self) -> None:
        """
        Test that Bill validates start and end date order.
        """

        # Test: End date before start date raises a ValueError.
        with pytest.raises(
            ValueError, match="end_date cannot be before start_date."
        ):
            Bill(
                bill_id="test_bill",
                service="Test Service",
                amount_due=100.00, # Numeric input, not Decimal.
                recurring=True,
                start_date=datetime.date(2024, 6, 15),
                end_date=datetime.date(2024, 3, 15), # End < start!
                frequency="monthly",
                interval=1
            )

    def test_bill_next_instance_one_time(self) -> None:
        """
        Test next_instance for one-time bills.
        """

        # Create a one-time bill.
        bill = Bill(
            bill_id="car_registration",
            service="Annual Car Registration",
            amount_due=125.00, # Numeric input, not Decimal.
            recurring=False,
            due_date=datetime.date(2024, 3, 15) # Use due_date.
        )
        
        # Test: Next instance reference date is before the due date,
        # so the next instance should be the due date. Assert that the 
        # next instance is not None and that it is the due date.
        next_instance = bill.next_instance(
            reference_date=datetime.date(2024, 2, 1)
        )

        assert next_instance is not None
        assert next_instance.due_date == datetime.date(2024, 3, 15)
        assert next_instance.amount_due == Decimal("125.00")
        
        # Test: Next instance reference date is the due date, but with
        # inclusive == True, it should return the an instance on the due
        # date. Assert that the next instance is not None and that it is
        # the due date.
        next_instance = bill.next_instance(
            reference_date=datetime.date(2024, 3, 15), inclusive=True
        )

        assert next_instance is not None
        assert next_instance.due_date == datetime.date(2024, 3, 15)
        assert next_instance.amount_due == Decimal("125.00")
        
        # Test: Next instance reference date is the due date, but with
        # inclusive == False, it should return None. Assert that the
        # next instance is None.
        next_instance = bill.next_instance(
            reference_date=datetime.date(2024, 3, 15), inclusive=False
        )

        assert next_instance is None
        
        # Test: Next instance reference date is after the due date, so
        # the next instance should be None. Assert that the next
        # instance is None.
        next_instance = bill.next_instance(
            reference_date=datetime.date(2024, 4, 1)
        )

        assert next_instance is None

    def test_bill_next_instance_monthly(self, monthly_bill: Bill) -> None:
        """
        Test next_instance for monthly recurring bills.
        """

        # Test: Next instance reference date is before the first
        # occurrence, so the next instance should be the first
        # occurrence. Assert that the next instance is not None and
        # that it is the first occurrence.
        next_instance = monthly_bill.next_instance(
            reference_date=datetime.date(2024, 1, 1)
        )

        assert next_instance is not None
        assert next_instance.due_date == datetime.date(2024, 1, 15)
        assert next_instance.amount_due == Decimal("150.00")
        
        # Test: Next instance reference date is the first occurrence,
        # but with inclusive == True, it should return the an instance
        # on the first occurrence. Assert that the next instance is not
        # None and that it is the first occurrence.
        next_instance = monthly_bill.next_instance(
            datetime.date(2024, 1, 15), inclusive=True
        )

        assert next_instance is not None
        assert next_instance.due_date == datetime.date(2024, 1, 15)
        assert next_instance.amount_due == Decimal("150.00")
        
        # Test: Next instance reference date is the first occurrence,
        # but with inclusive == False, it should return the next
        # occurrence. Assert that the next instance is not None and
        # that it is the next occurrence.
        next_instance = monthly_bill.next_instance(
            datetime.date(2024, 1, 15), inclusive=False
        )
        assert next_instance is not None
        assert next_instance.due_date == datetime.date(2024, 2, 15)
        assert next_instance.amount_due == Decimal("150.00")

        # Test: Next instance reference date is between occurrences,
        # so the next instance should be the next occurrence. Assert
        # that the next instance is not None and that it is the next
        # occurrence.
        next_instance = monthly_bill.next_instance(
            reference_date=datetime.date(2024, 1, 20)
        )

        assert next_instance is not None
        assert next_instance.due_date == datetime.date(2024, 2, 15)
        assert next_instance.amount_due == Decimal("150.00")

    def test_bill_instances_in_range_one_time(self) -> None:
        """
        Test instances_in_range for one-time bills.
        """

        # Create a one-time bill.
        bill = Bill(
            bill_id="car_registration", 
            service="Annual Car Registration",
            amount_due=125.00, # Numeric input, not Decimal.
            recurring=False,
            due_date=datetime.date(2024, 3, 15) # Use due_date.
        )
        
        # Test: Range includes due date. Assert that the number of
        # instances is 1 and that the first instance is the due date.
        instances = bill.instances_in_range(
            start_reference=datetime.date(2024, 1, 1),
            end_reference=datetime.date(2024, 12, 31)
        )
        assert len(instances) == 1
        assert instances[0].due_date == datetime.date(2024, 3, 15)
        assert instances[0].amount_due == Decimal("125.00")
        
        # Test: Range excludes due date. Assert that the number of
        # instances is 0.
        instances = bill.instances_in_range(
            start_reference=datetime.date(2024, 1, 1),
            end_reference=datetime.date(2024, 3, 14)
        )
        assert len(instances) == 0
        
        # Test: Range starts after due date. Assert that the number of
        # instances is 0.
        instances = bill.instances_in_range(
            start_reference=datetime.date(2024, 4, 1),
            end_reference=datetime.date(2024, 12, 31)
        )
        assert len(instances) == 0

    def test_bill_instances_in_range_monthly(self, monthly_bill: Bill) -> None:
        """
        Test instances_in_range for monthly recurring bills.
        """

        # Test: Full year range. Assert that the number of instances is
        # 12 and that the dates are correct.
        instances = monthly_bill.instances_in_range(
            start_reference=datetime.date(2024, 1, 1),
            end_reference=datetime.date(2024, 12, 31)
        )
        assert len(instances) == 12
        
        # Verify dates are correct.
        expected_dates = [
            datetime.date(2024, month, 15) for month in range(1, 13)
        ]
        actual_dates = [instance.due_date for instance in instances]
        assert actual_dates == expected_dates
        
        # Test: Partial range. Assert that the number of instances is
        # 4 and that the dates are correct.
        instances = monthly_bill.instances_in_range(
            start_reference=datetime.date(2024, 3, 1),
            end_reference=datetime.date(2024, 6, 30)
        )
        assert len(instances) == 4
        assert instances[0].due_date == datetime.date(2024, 3, 15)
        assert instances[-1].due_date == datetime.date(2024, 6, 15)

    def test_bill_instances_with_occurrences_limit(self) -> None:
        """
        Test instances_in_range respects occurrences limit.
        """

        # Create a recurring bill with a limited number of occurrences.
        bill = Bill(
            bill_id="limited_bill",
            service="Limited Subscription",
            amount_due=Decimal("50.00"),
            recurring=True,
            start_date=datetime.date(2024, 1, 15),
            frequency="monthly",
            interval=1,
            occurrences=3
        )
        
        # Test: Request more than occurrences limit. Assert that the
        # number of instances is 3 and that the dates are correct.
        instances = bill.instances_in_range(
            start_reference=datetime.date(2024, 1, 1),
            end_reference=datetime.date(2024, 12, 31)
        )
        assert len(instances) == 3
        assert instances[0].due_date == datetime.date(2024, 1, 15)
        assert instances[1].due_date == datetime.date(2024, 2, 15)
        assert instances[2].due_date == datetime.date(2024, 3, 15)

    def test_bill_instances_with_end_date_limit(self) -> None:
        """
        Test instances_in_range respects end_date limit.
        """

        # Create a recurring bill with an end_date.
        bill = Bill(
            bill_id="time_limited_bill",
            service="Time Limited Service",
            amount_due=Decimal("75.00"),
            recurring=True,
            start_date=datetime.date(2024, 1, 15),
            end_date=datetime.date(2024, 3, 31),
            frequency="monthly",
            interval=1
        )
        
        # Test: Request beyond end_date. Assert that the number of
        # instances is 3 and that the dates are correct.
        instances = bill.instances_in_range(
            start_reference=datetime.date(2024, 1, 1),
            end_reference=datetime.date(2024, 12, 31)
        )
        assert len(instances) == 3
        assert instances[-1].due_date == datetime.date(2024, 3, 15)

    def test_bill_count_in_range(self, monthly_bill: Bill) -> None:
        """
        Test count_in_range method.
        """

        # Test: Full year. Assert that the count is 12.
        count = monthly_bill.count_in_range(
            start_reference=datetime.date(2024, 1, 1),
            end_reference=datetime.date(2024, 12, 31)
        )
        assert count == 12
        
        # Test: Partial range. Assert that the count is 4.
        count = monthly_bill.count_in_range(
            start_reference=datetime.date(2024, 3, 1),
            end_reference=datetime.date(2024, 6, 30)
        )
        assert count == 4
        
        # Test: No occurrences. Assert that the count is 0.
        count = monthly_bill.count_in_range(
            start_reference=datetime.date(2023, 1, 1),
            end_reference=datetime.date(2023, 12, 31)
        )
        assert count == 0
