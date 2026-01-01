"""
Bill Manager Tests
==================

Focused tests for `BillManager` covering bill registration, duplicate
validation, instance generation, and source handling logic.
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import datetime
import tempfile
from decimal import Decimal
from pathlib import Path

import pytest

from sinkingfund.managers import BillManager
from sinkingfund.models import Bill

########################################################################
## FIXTURES
########################################################################

@pytest.fixture
def one_time_bill() -> Bill:
    """
    Create a simple one-time bill for manager tests.
    """

    return Bill(
        bill_id="car_registration",
        service="Annual Car Registration",
        amount_due=125.00,
        recurring=False,
        due_date=datetime.date(2024, 3, 15),
    )

@pytest.fixture
def monthly_bill() -> Bill:
    """
    Create a simple monthly recurring bill for manager tests.
    """

    return Bill(
        bill_id="electric",
        service="Monthly Electric Bill",
        amount_due=150.00,
        recurring=True,
        start_date=datetime.date(2024, 1, 15),
        frequency="monthly",
        interval=1,
        occurrences=13,
    )


########################################################################
## ADD AND REMOVE BILLS
########################################################################

class TestBillManagerAddAndRemove:
    """
    Test adding and removing bills within the manager.
    """

    def test_add_single_and_multiple_bills(self, one_time_bill: Bill) -> None:
        """
        Test adding a single bill and then a list of bills.
        """

        manager = BillManager()

        # Add a single bill.
        manager.add_bills(one_time_bill)
        assert manager.get_bill_count() == 1

        # Add multiple bills via list input.
        second_bill = Bill(
            bill_id="gym",
            service="Gym Membership",
            amount_due=Decimal("45.00"),
            recurring=True,
            start_date=datetime.date(2024, 1, 5),
            frequency="monthly",
            interval=1,
        )

        manager.add_bills([second_bill])
        assert manager.get_bill_count() == 2

    def test_add_bills_empty_list_is_noop(self) -> None:
        """
        Test that adding an empty list of bills is a no-op.
        """

        manager = BillManager()
        manager.add_bills([])
        assert manager.get_bill_count() == 0

    def test_add_bills_rejects_unsupported_type(self) -> None:
        """
        Test that add_bills rejects unsupported input types.
        """

        manager = BillManager()

        with pytest.raises(
            TypeError,
            match="Expected list\\[Bill] or Bill\\.",
        ):
            manager.add_bills(("not", "a", "bill"))  # type: ignore[arg-type]

    def test_add_bills_rejects_duplicate_against_existing(
        self,
        one_time_bill: Bill,
    ) -> None:
        """
        Test that adding a bill with a duplicate bill_id is rejected.
        """

        manager = BillManager()
        manager.add_bills(one_time_bill)

        duplicate = Bill(
            bill_id=one_time_bill.bill_id,
            service="Duplicate Service",
            amount_due=Decimal("50.00"),
            recurring=False,
            due_date=datetime.date(2024, 4, 1),
        )

        with pytest.raises(
            ValueError,
            match=(
                "Bill with ID 'car_registration' already exists. "
                "Cannot add duplicate bill\\."
            ),
        ):
            manager.add_bills(duplicate)

    def test_remove_bill_success_and_missing(self, one_time_bill: Bill) -> None:
        """
        Test removing an existing bill and handling missing bill_id.
        """

        manager = BillManager()
        manager.add_bills(one_time_bill)

        # Remove existing bill.
        manager.remove_bill(one_time_bill.bill_id)
        assert manager.get_bill_count() == 0

        # Attempt to remove a bill that does not exist.
        with pytest.raises(
            ValueError,
            match="Bill with ID 'unknown' does not exist.",
        ):
            manager.remove_bill("unknown")

########################################################################
## BILL CREATION FROM SOURCES
########################################################################

class TestBillManagerCreateBills:
    """
    Test BillManager.create_bills and create_bills_from_data.
    """

    def test_create_bills_from_file_path(self) -> None:
        """
        Test creating bills from a CSV file via file path source.
        """

        manager = BillManager()

        # BUSINESS GOAL: Create temporary CSV file to exercise the
        # file-loading branch without relying on external example data.
        csv_content = (
            "bill_id,service,amount_due,recurring,due_date,start_date,"
            "end_date,frequency,interval,occurrences\n"
            "prop_tax,Property Tax,3600.00,True,,2025-11-01,,annual,1,\n"
            "car_ins,Car Insurance,750.00,True,,2025-04-24,,monthly,6,\n"
        )

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.csv', delete=False
        ) as tmp_file:
            tmp_file.write(csv_content)
            tmp_path = tmp_file.name

        try:
            bills = manager.create_bills(tmp_path)

            assert isinstance(bills, list)
            assert bills
            assert all(isinstance(bill, Bill) for bill in bills)
        finally:
            # Clean up temporary file.
            Path(tmp_path).unlink(missing_ok=True)

    def test_create_bills_from_dict_list(self) -> None:
        """
        Test creating bills from a list of dictionaries.
        """

        manager = BillManager()
        data = [
            {
                "bill_id": "internet",
                "service": "Internet Service",
                "amount_due": Decimal("80.00"),
                "recurring": True,
                "start_date": datetime.date(2024, 1, 10),
                "frequency": "monthly",
                "interval": 1,
            }
        ]

        bills = manager.create_bills(data)

        assert len(bills) == 1
        assert bills[0].bill_id == "internet"
        assert bills[0].amount_due == Decimal("80.00")

    def test_create_bills_rejects_unsupported_source_type(self) -> None:
        """
        Test that create_bills rejects unsupported source types.
        """

        manager = BillManager()

        with pytest.raises(
            ValueError,
            match="Expected str \\(file path\\) or list\\[dict] \\(bill data\\)\\.",
        ):
            manager.create_bills(123)  # type: ignore[arg-type]

    def test_create_bills_from_data_empty_and_invalid_records(self) -> None:
        """
        Test create_bills_from_data with empty input and invalid records.
        """

        manager = BillManager()

        # Empty input returns empty list.
        assert manager.create_bills_from_data([]) == []

        # Missing required field triggers KeyError via Bill constructor.
        invalid_record = [
            {
                "service": "Missing ID Service",
                "amount_due": Decimal("10.00"),
                "recurring": False,
                "due_date": datetime.date(2024, 5, 1),
            }
        ]

        with pytest.raises(KeyError, match="bill_id"):
            manager.create_bills_from_data(invalid_record)

    def test_create_bills_from_data_normalizes_nonrecurring_dates(self) -> None:
        """
        Test that create_bills_from_data normalizes non-recurring bill
        dates (due_date → start_date and end_date).
        """
        
        manager = BillManager()
        
        # Test: Create data with non-recurring bill that has only due_date
        # (no start_date or end_date). This simulates data from CSV files.
        data = [
            {
                "bill_id": "registration",
                "service": "Car Registration",
                "amount_due": 125.00,
                "recurring": False,
                "due_date": datetime.date(2024, 3, 15),
                # No start_date or end_date.
            }
        ]
        
        # Test: Create bills from data.
        bills = manager.create_bills_from_data(data)
        
        # Test: Verify bill was created correctly.
        assert len(bills) == 1
        bill = bills[0]
        assert bill.bill_id == "registration"
        assert bill.recurring is False
        assert bill.start_date == datetime.date(2024, 3, 15)
        assert bill.end_date == datetime.date(2024, 3, 15)
        assert bill.occurrences == 1


########################################################################
## INSTANCE GENERATION
########################################################################

class TestBillManagerActiveInstances:
    """
    Test active_instances_in_range behavior and edge cases.
    """

    def test_active_instances_with_no_bills_returns_empty(self) -> None:
        """
        Test that no bills result in an empty instance list.
        """

        manager = BillManager()

        instances = manager.active_instances_in_range(
            start_reference=datetime.date(2024, 1, 1),
            end_reference=datetime.date(2024, 12, 31),
        )

        assert instances == []

    def test_active_instances_includes_range_and_next_instance(
        self,
        monthly_bill: Bill,
    ) -> None:
        """
        Test that instances in range plus a next instance are included.
        """

        manager = BillManager()
        manager.add_bills(monthly_bill)

        instances = manager.active_instances_in_range(
            start_reference=datetime.date(2024, 1, 1),
            end_reference=datetime.date(2024, 12, 31),
        )

        # Expect 12 in-range instances plus one next instance.
        assert len(instances) == 13

        # The last instance should be one interval after the last in-range
        # occurrence.
        assert instances[-1].due_date == datetime.date(2025, 1, 15)

    def test_active_instances_for_bill_outside_range(
        self,
        one_time_bill: Bill,
    ) -> None:
        """
        Test behavior when bill has no instances in range.
        """

        manager = BillManager()
        manager.add_bills(one_time_bill)

        # Range ends before the one-time bill due date, so there are no
        # in-range instances but next_instance should still be included.
        instances = manager.active_instances_in_range(
            start_reference=datetime.date(2024, 1, 1),
            end_reference=datetime.date(2024, 2, 1),
        )

        assert len(instances) == 1
        assert instances[0].due_date == datetime.date(2024, 3, 15)

    def test_active_instances_for_expired_bill_has_no_next_instance(
        self,
        one_time_bill: Bill,
    ) -> None:
        """
        Test behavior when bill is already past its due date.
        """

        manager = BillManager()
        manager.add_bills(one_time_bill)

        # Range starts after the one-time bill due date. There should be
        # no in-range instances and next_instance should be None.
        instances = manager.active_instances_in_range(
            start_reference=datetime.date(2024, 4, 1),
            end_reference=datetime.date(2024, 12, 31),
        )

        assert instances == []


