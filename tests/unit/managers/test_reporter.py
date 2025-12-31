"""
Reporter Tests
==============

Focused tests for `Reporter` covering report generation, report section
building, static balance handling, and filtering options.
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import datetime
from decimal import Decimal

import pytest

from sinkingfund.managers import Reporter, EnvelopeManager
from sinkingfund.models import BillInstance, Envelope, CashFlow, CashFlowSchedule

########################################################################
## FIXTURES
########################################################################

@pytest.fixture
def envelope_manager() -> EnvelopeManager:
    """
    Create an empty envelope manager for testing.
    """
    return EnvelopeManager()


@pytest.fixture
def bill_instance() -> BillInstance:
    """
    Create a bill instance for envelope creation.
    """
    return BillInstance(
        bill_id="electric",
        service="Monthly Electric Bill",
        due_date=datetime.date(2024, 2, 15),
        amount_due=Decimal("150.00")
    )


@pytest.fixture
def envelope_with_allocation(
    envelope_manager: EnvelopeManager,
    bill_instance: BillInstance
) -> Envelope:
    """
    Create an envelope with initial allocation.
    """
    envelope = Envelope(
        bill_instance=bill_instance,
        initial_allocation=Decimal("75.00"),
        start_contrib_date=datetime.date(2024, 1, 1),
        end_contrib_date=datetime.date(2024, 2, 14),
        contrib_interval=14
    )
    envelope_manager.add_envelopes(envelope)
    return envelope


@pytest.fixture
def envelope_with_schedule(
    envelope_manager: EnvelopeManager,
    bill_instance: BillInstance
) -> Envelope:
    """
    Create an envelope with cash flow schedule.
    """
    envelope = Envelope(
        bill_instance=bill_instance,
        initial_allocation=Decimal("50.00"),
        start_contrib_date=datetime.date(2024, 1, 1),
        end_contrib_date=datetime.date(2024, 2, 14),
        contrib_interval=14
    )
    
    # Add cash flows to schedule.
    schedule = CashFlowSchedule()
    schedule.add_cash_flows([
        CashFlow(
            bill_id="electric",
            date=datetime.date(2024, 1, 15),
            amount=Decimal("25.00")
        ),
        CashFlow(
            bill_id="electric",
            date=datetime.date(2024, 2, 1),
            amount=Decimal("25.00")
        ),
        CashFlow(
            bill_id="electric",
            date=datetime.date(2024, 2, 15),
            amount=Decimal("-150.00")
        )
    ])
    envelope.schedule = schedule
    envelope_manager.add_envelopes(envelope)
    return envelope


@pytest.fixture
def reporter_with_envelopes(
    envelope_with_schedule: Envelope
) -> Reporter:
    """
    Create a reporter with envelopes containing schedules.
    """
    manager = EnvelopeManager()
    manager.add_envelopes(envelope_with_schedule)
    
    return Reporter(
        envelope_manager=manager,
        start_date=datetime.date(2024, 1, 1),
        end_date=datetime.date(2024, 2, 28),
        balance=Decimal("200.00")
    )


@pytest.fixture
def reporter_empty(
    envelope_manager: EnvelopeManager
) -> Reporter:
    """
    Create a reporter with no envelopes.
    """
    return Reporter(
        envelope_manager=envelope_manager,
        start_date=datetime.date(2024, 1, 1),
        end_date=datetime.date(2024, 1, 31),
        balance=Decimal("1000.00")
    )


########################################################################
## INITIALIZATION TESTS
########################################################################

class TestReporterInitialization:
    """
    Test Reporter initialization.
    """

    def test_initialization_sets_attributes(
        self,
        envelope_manager: EnvelopeManager
    ) -> None:
        """
        Test that Reporter initializes with correct attributes.
        """
        reporter = Reporter(
            envelope_manager=envelope_manager,
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 12, 31),
            balance=Decimal("5000.00")
        )
        
        assert reporter.envelope_manager == envelope_manager
        assert reporter.start_date == datetime.date(2024, 1, 1)
        assert reporter.end_date == datetime.date(2024, 12, 31)
        assert reporter.balance == Decimal("5000.00")


########################################################################
## GENERATE DAILY REPORT TESTS
########################################################################

class TestGenerateDailyReport:
    """
    Test generate_daily_report method.
    """

    def test_generate_daily_report_full_range(
        self,
        reporter_with_envelopes: Reporter
    ) -> None:
        """
        Test generating full daily report with all dates.
        """
        report = reporter_with_envelopes.generate_daily_report(
            active_only=False
        )
        
        assert isinstance(report, dict)
        assert len(report) > 0
        
        # Check report structure.
        first_date = min(report.keys())
        first_entry = report[first_date]
        
        assert 'account_balance' in first_entry
        assert 'contributions' in first_entry
        assert 'payouts' in first_entry
        
        assert 'total' in first_entry['account_balance']
        assert 'count' in first_entry['account_balance']
        assert 'bills' in first_entry['account_balance']

    def test_generate_daily_report_active_only(
        self,
        reporter_with_envelopes: Reporter
    ) -> None:
        """
        Test generating report with only active dates.
        """
        report = reporter_with_envelopes.generate_daily_report(
            active_only=True
        )
        
        assert isinstance(report, dict)
        
        # All dates should have contributions or payouts.
        for date, data in report.items():
            assert (
                data['contributions']['count'] > 0
                or data['payouts']['count'] > 0
            )

    def test_generate_daily_report_empty_envelopes(
        self,
        reporter_empty: Reporter
    ) -> None:
        """
        Test generating report with no envelopes.
        """
        report = reporter_empty.generate_daily_report(active_only=False)
        
        assert isinstance(report, dict)
        assert len(report) > 0
        
        # All entries should have zero counts.
        for date, data in report.items():
            assert data['account_balance']['count'] == 0
            assert data['contributions']['count'] == 0
            assert data['payouts']['count'] == 0

    def test_generate_daily_report_static_balance(
        self,
        envelope_manager: EnvelopeManager
    ) -> None:
        """
        Test that static unallocated balance is included in report.
        """
        # Create envelope with allocation less than balance.
        envelope = Envelope(
            bill_instance=BillInstance(
                bill_id="test",
                service="Test",
                due_date=datetime.date(2024, 2, 15),
                amount_due=Decimal("100.00")
            ),
            initial_allocation=Decimal("50.00"),
            start_contrib_date=datetime.date(2024, 1, 1),
            end_contrib_date=datetime.date(2024, 2, 14)
        )
        envelope_manager.add_envelopes(envelope)
        
        reporter = Reporter(
            envelope_manager=envelope_manager,
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 1, 31),
            balance=Decimal("200.00")  # More than allocation.
        )
        
        report = reporter.generate_daily_report(active_only=False)
        
        # Static balance should be 200 - 50 = 150.
        first_date = min(report.keys())
        account_balance = report[first_date]['account_balance']
        
        # Total should include static balance.
        assert account_balance['total'] >= Decimal("150.00")

    def test_generate_daily_report_no_static_balance(
        self,
        envelope_manager: EnvelopeManager
    ) -> None:
        """
        Test report when balance equals total allocations.
        """
        envelope = Envelope(
            bill_instance=BillInstance(
                bill_id="test",
                service="Test",
                due_date=datetime.date(2024, 2, 15),
                amount_due=Decimal("100.00")
            ),
            initial_allocation=Decimal("100.00"),
            start_contrib_date=datetime.date(2024, 1, 1),
            end_contrib_date=datetime.date(2024, 2, 14)
        )
        envelope_manager.add_envelopes(envelope)
        
        reporter = Reporter(
            envelope_manager=envelope_manager,
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 1, 31),
            balance=Decimal("100.00")  # Equals allocation.
        )
        
        report = reporter.generate_daily_report(active_only=False)
        
        # Static balance should be 0.
        first_date = min(report.keys())
        account_balance = report[first_date]['account_balance']
        
        # Total should equal envelope balance.
        assert account_balance['total'] == Decimal("100.00")

    def test_generate_daily_report_multiple_envelopes(
        self,
        envelope_manager: EnvelopeManager
    ) -> None:
        """
        Test report with multiple envelopes.
        """
        instances = [
            BillInstance(
                bill_id="electric",
                service="Electric",
                due_date=datetime.date(2024, 2, 15),
                amount_due=Decimal("150.00")
            ),
            BillInstance(
                bill_id="water",
                service="Water",
                due_date=datetime.date(2024, 3, 1),
                amount_due=Decimal("75.00")
            )
        ]
        
        for inst in instances:
            envelope = Envelope(
                bill_instance=inst,
                initial_allocation=inst.amount_due / 2,
                start_contrib_date=datetime.date(2024, 1, 1),
                end_contrib_date=inst.due_date - datetime.timedelta(days=1)
            )
            envelope_manager.add_envelopes(envelope)
        
        reporter = Reporter(
            envelope_manager=envelope_manager,
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 1, 31),
            balance=Decimal("500.00")
        )
        
        report = reporter.generate_daily_report(active_only=False)
        
        assert isinstance(report, dict)
        first_date = min(report.keys())
        account_balance = report[first_date]['account_balance']
        
        # Should have entries for both bills.
        assert len(account_balance['bills']) == 2


########################################################################
## BUILD REPORT SECTION TESTS
########################################################################

class TestBuildReportSection:
    """
    Test _build_report_section helper method.
    """

    def test_build_report_section_with_data(
        self,
        reporter_with_envelopes: Reporter
    ) -> None:
        """
        Test building report section with actual data.
        """
        data_dict = {
            datetime.date(2024, 1, 15): {
                "electric": Decimal("25.00")
            }
        }
        
        section = reporter_with_envelopes._build_report_section(
            data_dict=data_dict,
            date=datetime.date(2024, 1, 15)
        )
        
        assert section['total'] == Decimal("25.00")
        assert section['count'] == 1
        assert section['bills'] == {"electric": Decimal("25.00")}

    def test_build_report_section_empty_data(
        self,
        reporter_with_envelopes: Reporter
    ) -> None:
        """
        Test building report section with no data for date.
        """
        data_dict = {}
        
        section = reporter_with_envelopes._build_report_section(
            data_dict=data_dict,
            date=datetime.date(2024, 1, 20)
        )
        
        assert section['total'] == Decimal("0")
        assert section['count'] == 0
        assert section['bills'] == {}

    def test_build_report_section_multiple_bills(
        self,
        reporter_with_envelopes: Reporter
    ) -> None:
        """
        Test building report section with multiple bills.
        """
        data_dict = {
            datetime.date(2024, 1, 15): {
                "electric": Decimal("25.00"),
                "water": Decimal("15.00")
            }
        }
        
        section = reporter_with_envelopes._build_report_section(
            data_dict=data_dict,
            date=datetime.date(2024, 1, 15)
        )
        
        assert section['total'] == Decimal("40.00")
        assert section['count'] == 2
        assert len(section['bills']) == 2

    def test_build_report_section_zero_values(
        self,
        reporter_with_envelopes: Reporter
    ) -> None:
        """
        Test building report section with zero values.
        """
        data_dict = {
            datetime.date(2024, 1, 15): {
                "electric": Decimal("0.00"),
                "water": Decimal("0.00")
            }
        }
        
        section = reporter_with_envelopes._build_report_section(
            data_dict=data_dict,
            date=datetime.date(2024, 1, 15)
        )
        
        assert section['total'] == Decimal("0")
        assert section['count'] == 0  # Zero values don't count.
        assert len(section['bills']) == 2

    def test_build_report_section_mixed_values(
        self,
        reporter_with_envelopes: Reporter
    ) -> None:
        """
        Test building report section with mixed zero and non-zero values.
        """
        data_dict = {
            datetime.date(2024, 1, 15): {
                "electric": Decimal("25.00"),
                "water": Decimal("0.00")
            }
        }
        
        section = reporter_with_envelopes._build_report_section(
            data_dict=data_dict,
            date=datetime.date(2024, 1, 15)
        )
        
        assert section['total'] == Decimal("25.00")
        assert section['count'] == 1  # Only non-zero counts.
        assert len(section['bills']) == 2


########################################################################
## EDGE CASE TESTS
########################################################################

class TestReporterEdgeCases:
    """
    Test Reporter edge cases and error scenarios.
    """

    def test_single_day_range(
        self,
        envelope_manager: EnvelopeManager
    ) -> None:
        """
        Test report generation for single day range.
        """
        reporter = Reporter(
            envelope_manager=envelope_manager,
            start_date=datetime.date(2024, 1, 15),
            end_date=datetime.date(2024, 1, 15),
            balance=Decimal("100.00")
        )
        
        report = reporter.generate_daily_report(active_only=False)
        
        assert len(report) == 1
        assert datetime.date(2024, 1, 15) in report

    def test_leap_year_range(
        self,
        envelope_manager: EnvelopeManager
    ) -> None:
        """
        Test report generation spanning leap year.
        """
        reporter = Reporter(
            envelope_manager=envelope_manager,
            start_date=datetime.date(2024, 2, 28),
            end_date=datetime.date(2024, 3, 1),
            balance=Decimal("100.00")
        )
        
        report = reporter.generate_daily_report(active_only=False)
        
        # Should include Feb 29 (leap day).
        assert datetime.date(2024, 2, 29) in report
        assert len(report) == 3

    def test_year_boundary_range(
        self,
        envelope_manager: EnvelopeManager
    ) -> None:
        """
        Test report generation spanning year boundary.
        """
        reporter = Reporter(
            envelope_manager=envelope_manager,
            start_date=datetime.date(2024, 12, 30),
            end_date=datetime.date(2025, 1, 2),
            balance=Decimal("100.00")
        )
        
        report = reporter.generate_daily_report(active_only=False)
        
        assert datetime.date(2024, 12, 30) in report
        assert datetime.date(2024, 12, 31) in report
        assert datetime.date(2025, 1, 1) in report
        assert datetime.date(2025, 1, 2) in report
        assert len(report) == 4

    def test_negative_static_balance(
        self,
        envelope_manager: EnvelopeManager
    ) -> None:
        """
        Test report when allocations exceed balance.
        """
        envelope = Envelope(
            bill_instance=BillInstance(
                bill_id="test",
                service="Test",
                due_date=datetime.date(2024, 2, 15),
                amount_due=Decimal("100.00")
            ),
            initial_allocation=Decimal("200.00"),  # More than balance.
            start_contrib_date=datetime.date(2024, 1, 1),
            end_contrib_date=datetime.date(2024, 2, 14)
        )
        envelope_manager.add_envelopes(envelope)
        
        reporter = Reporter(
            envelope_manager=envelope_manager,
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 1, 31),
            balance=Decimal("100.00")  # Less than allocation.
        )
        
        report = reporter.generate_daily_report(active_only=False)
        
        # Static balance should be negative (100 - 200 = -100).
        # But it should still generate report.
        assert isinstance(report, dict)
        first_date = min(report.keys())
        account_balance = report[first_date]['account_balance']
        
        # Total should reflect envelope balance.
        assert account_balance['total'] == Decimal("200.00")

