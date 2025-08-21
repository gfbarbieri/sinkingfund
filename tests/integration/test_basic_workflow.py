"""
Basic Workflow Integration Tests
================================

Integration tests for basic sinking fund workflows from bill creation
through envelope funding and cash flow analysis.
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import datetime
from decimal import Decimal

import pytest

from sinkingfund.models import Bill, BillInstance, Envelope

########################################################################
## BASIC WORKFLOW TESTS
########################################################################

class TestBasicWorkflow:
    """
    Test basic sinking fund workflow integration.
    """

    def test_simple_bill_to_envelope_workflow(self) -> None:
        """
        Test creating a bill, generating instances, and creating
        envelopes.
        """

        # Create a monthly bill.
        bill = Bill(
            bill_id="electric",
            service="Monthly Electric Bill",
            amount_due=Decimal("150.00"),
            recurring=True,
            start_date=datetime.date(2024, 1, 15),
            frequency="monthly"
        )
        
        # Generate bill instances for first quarter.
        instances = bill.instances_in_range(
            start_reference=datetime.date(2024, 1, 1),
            end_reference=datetime.date(2024, 3, 31)
        )
        
        assert len(instances) == 3
        assert instances[0].due_date == datetime.date(2024, 1, 15)
        assert instances[1].due_date == datetime.date(2024, 2, 15)
        assert instances[2].due_date == datetime.date(2024, 3, 15)
        
        # Create envelope for first instance.
        envelope = Envelope(
            bill_instance=instances[0],
            initial_allocation=Decimal("75.00"),
            start_contrib_date=datetime.date(2024, 1, 1),
            end_contrib_date=datetime.date(2024, 1, 14),
            contrib_interval=7
        )
        
        # Verify envelope setup.
        assert envelope.bill_instance == instances[0]
        assert envelope.get_balance_as_of_date() == Decimal("75.00")
        assert envelope.remaining() == Decimal("75.00")
        assert not envelope.is_fully_funded()

########################################################################
## SIMPLE INTEGRATION TESTS
########################################################################

class TestSimpleIntegration:
    """
    Test simple integration scenarios.
    """

    def test_bill_instance_to_envelope_compatibility(self) -> None:
        """
        Test that BillInstance works correctly with Envelope.
        """

        # Create a bill instance directly.
        bill_instance = BillInstance(
            bill_id="car_insurance",
            service="Quarterly Car Insurance",
            due_date=datetime.date(2024, 6, 15),
            amount_due=Decimal("450.00")
        )
        
        # Create envelope for 3-month saving period.
        envelope = Envelope(
            bill_instance=bill_instance,
            start_contrib_date=datetime.date(2024, 3, 15),
            end_contrib_date=datetime.date(2024, 6, 14),
            contrib_interval=30  # Monthly contributions.
        )
        
        # Test: Verify envelope properties.
        assert envelope.bill_instance.bill_id == "car_insurance"
        assert envelope.bill_instance.amount_due == Decimal("450.00")
        assert envelope.remaining() == Decimal("450.00")
        
        # Test: Verify funding calculation.
        monthly_contribution_needed = envelope.remaining() / 3
        assert monthly_contribution_needed == Decimal("150.00")

    def test_multiple_bills_scenario(self) -> None:
        """
        Test scenario with multiple bills of different types.
        """

        # Create a one-time bill.
        registration = Bill(
            bill_id="car_registration",
            service="Annual Car Registration",
            amount_due=Decimal("125.00"),
            recurring=False,
            due_date=datetime.date(2024, 7, 1)
        )
        
        # Monthly bill.
        electric = Bill(
            bill_id="electric",
            service="Monthly Electric",
            amount_due=Decimal("150.00"),
            recurring=True,
            start_date=datetime.date(2024, 1, 15),
            frequency="monthly",
            interval=1
        )
        
        # Get instances for planning period.
        reg_instances = registration.instances_in_range(
            datetime.date(2024, 1, 1),
            datetime.date(2024, 12, 31)
        )

        electric_instances = electric.instances_in_range(
            datetime.date(2024, 1, 1),
            datetime.date(2024, 3, 31)
        )
        
        # Test: Verify that the instances are created correctly.
        assert len(reg_instances) == 1
        assert len(electric_instances) == 3
        
        # Create envelopes for different bill types.
        reg_envelope = Envelope(
            bill_instance=reg_instances[0],
            start_contrib_date=datetime.date(2024, 1, 1),
            end_contrib_date=datetime.date(2024, 6, 30)
        )
        
        electric_envelope = Envelope(
            bill_instance=electric_instances[0],
            start_contrib_date=datetime.date(2024, 1, 1),
            end_contrib_date=datetime.date(2024, 1, 14)
        )
        
        # Test: Verify different funding requirements.
        assert reg_envelope.remaining() == Decimal("125.00")
        assert electric_envelope.remaining() == Decimal("150.00")
        
        # Test: Verify total funding needed.
        total_needed = reg_envelope.remaining() + electric_envelope.remaining()
        assert total_needed == Decimal("275.00")
