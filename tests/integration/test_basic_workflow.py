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

from sinkingfund.models import Bill, BillInstance, Envelope, SinkingFund

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
            frequency="monthly",
            interval=1
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


########################################################################
## SINKING FUND INTEGRATION TESTS
########################################################################

class TestSinkingFundIntegration:
    """
    Test complete SinkingFund workflow integration scenarios.
    """

    def test_quick_report_full_workflow(self) -> None:
        """
        Test complete end-to-end workflow using quick_report.
        """
        fund = SinkingFund(
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 12, 31),
            balance=5000.0
        )
        
        # Add multiple bills.
        fund.add_bills({
            'bill_id': 'electric',
            'service': 'Monthly Electric',
            'amount_due': 150.00,
            'recurring': True,
            'start_date': datetime.date(2024, 1, 15),
            'frequency': 'monthly',
            'interval': 1
        })
        
        fund.add_bills({
            'bill_id': 'water',
            'service': 'Monthly Water',
            'amount_due': 75.00,
            'recurring': True,
            'start_date': datetime.date(2024, 1, 1),
            'frequency': 'monthly',
            'interval': 1
        })
        
        # Generate quick report.
        report = fund.quick_report(
            contribution_interval=14,
            allocation_strategy="sorted",
            scheduler_strategy="independent_scheduler",
            active_only=False
        )
        
        assert isinstance(report, dict)
        assert len(report) > 0
        
        # Verify report structure.
        first_date = min(report.keys())
        first_entry = report[first_date]
        assert 'account_balance' in first_entry
        assert 'contributions' in first_entry
        assert 'payouts' in first_entry

    def test_allocation_strategy_switching(self) -> None:
        """
        Test switching between allocation strategies.
        """
        fund = SinkingFund(
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 12, 31),
            balance=3000.0
        )
        
        fund.add_bills({
            'bill_id': 'electric',
            'service': 'Monthly Electric',
            'amount_due': 150.00,
            'recurring': True,
            'start_date': datetime.date(2024, 1, 15),
            'frequency': 'monthly',
            'interval': 1
        })
        
        # Allocate with sorted strategy.
        result1 = fund.allocate(strategy="sorted")
        assert result1 is not None
        
        # Switch to proportional strategy.
        result2 = fund.allocate(strategy="proportional", method="proportional")
        assert result2 is not None
        
        # Both should succeed.
        assert hasattr(result1, 'envelopes')
        assert hasattr(result2, 'envelopes')

    def test_scheduler_strategy_switching(self) -> None:
        """
        Test switching between scheduler strategies.
        """
        fund = SinkingFund(
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 12, 31),
            balance=2000.0
        )
        
        fund.add_bills({
            'bill_id': 'electric',
            'service': 'Monthly Electric',
            'amount_due': 150.00,
            'recurring': True,
            'start_date': datetime.date(2024, 1, 15),
            'frequency': 'monthly',
            'interval': 1
        })
        
        fund.allocate(strategy="sorted")
        fund.update_contribution_dates(contribution_interval=14)
        
        # Create schedules.
        result = fund.schedule(strategy="independent_scheduler")
        assert result is not None
        assert hasattr(result, 'schedules')

    def test_build_daily_account_report_with_active_only(self) -> None:
        """
        Test report with active_only parameter.
        """
        fund = SinkingFund(
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 3, 31),
            balance=2000.0
        )
        
        fund.add_bills({
            'bill_id': 'electric',
            'service': 'Monthly Electric',
            'amount_due': 150.00,
            'recurring': True,
            'start_date': datetime.date(2024, 1, 15),
            'frequency': 'monthly',
            'interval': 1
        })
        
        fund.allocate(strategy="sorted")
        fund.update_contribution_dates(contribution_interval=14)
        fund.schedule()
        
        # Generate report with active_only=True.
        report = fund.report(active_only=True)
        
        assert isinstance(report, dict)
        
        # All dates should have activity.
        for date, data in report.items():
            assert (
                data['contributions']['count'] > 0
                or data['payouts']['count'] > 0
            )

    def test_rebuild_report(self) -> None:
        """
        Test rebuild_report method for regenerating reports.
        """
        fund = SinkingFund(
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 12, 31),
            balance=4000.0
        )
        
        fund.add_bills({
            'bill_id': 'electric',
            'service': 'Monthly Electric',
            'amount_due': 150.00,
            'recurring': True,
            'start_date': datetime.date(2024, 1, 15),
            'frequency': 'monthly',
            'interval': 1
        })
        
        # Generate report with different parameters using quick_report.
        report = fund.quick_report(
            allocation_strategy="proportional",
            scheduler_strategy="independent_scheduler",
            contribution_interval=7,
            active_only=False,
            method="equal"
        )
        
        assert isinstance(report, dict)
        assert len(report) > 0

    def test_sync_envelopes_with_bills(self) -> None:
        """
        Test syncing envelopes with bills.
        """
        fund = SinkingFund(
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 12, 31),
            balance=2000.0
        )
        
        fund.add_bills({
            'bill_id': 'electric',
            'service': 'Monthly Electric',
            'amount_due': 150.00,
            'recurring': True,
            'start_date': datetime.date(2024, 1, 15),
            'frequency': 'monthly',
            'interval': 1
        }, )
        
        # Delete bill but keep envelopes.
        # delete_bills always removes envelopes now.
        fund.delete_bills(['electric'])
        
        # Sync should be a no-op since envelopes were already removed.
        fund.sync_envelopes_with_bills()
        
        envelopes = fund.get_envelopes()
        assert len(envelopes) == 0

    def test_validate_state(self) -> None:
        """
        Test state validation.
        """
        fund = SinkingFund(
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 12, 31),
            balance=2000.0
        )
        
        fund.add_bills({
            'bill_id': 'electric',
            'service': 'Monthly Electric',
            'amount_due': 150.00,
            'recurring': True,
            'start_date': datetime.date(2024, 1, 15),
            'frequency': 'monthly',
            'interval': 1
        }, )
        
        # Validate state should be valid.
        is_valid, issues = fund.validate_state()
        assert is_valid is True
        assert len(issues) == 0
        
        # Create invalid state by deleting bill but keeping envelope.
        # delete_bills always removes envelopes now.
        fund.delete_bills(['electric'])
        
        # Validate should pass since envelopes were removed with bills.
        is_valid, issues = fund.validate_state()
        assert is_valid is True
