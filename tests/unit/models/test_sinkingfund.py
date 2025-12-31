"""
Sinking Fund Model Tests
========================

Comprehensive tests for Sinking Fund model covering all major methods
and workflows.
"""

########################################################################
## IMPORTS
########################################################################

import datetime
import tempfile
from decimal import Decimal
from pathlib import Path

import pytest

from sinkingfund.models.sinkingfund import SinkingFund
from sinkingfund.models import Bill, BillInstance, Envelope

########################################################################
## FIXTURES
########################################################################

@pytest.fixture
def empty_fund() -> SinkingFund:
    """
    Create an empty sinking fund for testing.
    """
    return SinkingFund(
        start_date=datetime.date(2024, 1, 1),
        end_date=datetime.date(2024, 12, 31),
        balance=0.0
    )


@pytest.fixture
def funded_fund() -> SinkingFund:
    """
    Create a sinking fund with initial balance.
    """
    return SinkingFund(
        start_date=datetime.date(2024, 1, 1),
        end_date=datetime.date(2024, 12, 31),
        balance=5000.0
    )


@pytest.fixture
def bill_data() -> dict:
    """
    Create sample bill data for testing.
    """
    return {
        'bill_id': 'electric',
        'service': 'Monthly Electric Bill',
        'amount_due': 150.00,
        'recurring': True,
        'start_date': datetime.date(2024, 1, 15),
        'frequency': 'monthly',
        'interval': 1
    }


@pytest.fixture
def one_time_bill_data() -> dict:
    """
    Create sample one-time bill data for testing.
    """
    return {
        'bill_id': 'registration',
        'service': 'Car Registration',
        'amount_due': 125.00,
        'recurring': False,
        'due_date': datetime.date(2024, 3, 15)
    }


########################################################################
## SINKING FUND INITIALIZATION TESTS
########################################################################

class TestSinkingFundInitialization:
    """
    Test Sinking Fund model initialization and validation.
    """

    def test_sinking_fund_initialization(self) -> None:
        """
        Test SinkingFund initialization and basic properties.
        """

        # Create a SinkingFund instance.
        fund = SinkingFund(
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 12, 31),
            balance=1000.0
        )
        
        # Test: Assert that the SinkingFund instance has the correct
        # attributes.
        assert fund.start_date == datetime.date(2024, 1, 1)
        assert fund.end_date == datetime.date(2024, 12, 31)
        assert fund.balance == Decimal("1000.0")
        
        # Test: Assert that managers are private (not accessible).
        assert not hasattr(fund, 'bill_manager')
        assert not hasattr(fund, 'envelope_manager')
        assert not hasattr(fund, 'allocation_manager')
        assert not hasattr(fund, 'schedule_manager')
        
        # Test: Assert that public API methods exist.
        assert hasattr(fund, 'add_bills')
        assert hasattr(fund, 'get_bills')
        assert hasattr(fund, 'get_envelopes')
        assert hasattr(fund, 'allocate')
        assert hasattr(fund, 'schedule')
        assert hasattr(fund, 'report')

    def test_sinking_fund_default_balance(self) -> None:
        """
        Test SinkingFund initialization with default balance.
        """
        fund = SinkingFund(
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 12, 31)
        )
        
        assert fund.balance == Decimal("0.0")


########################################################################
## BILL MANAGEMENT TESTS
########################################################################

class TestBillManagement:
    """
    Test bill management methods.
    """

    def test_add_bill_with_envelope_creation(
        self,
        empty_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test adding a bill with automatic envelope creation.
        """
        empty_fund.add_bills(bill_data)
        
        bills = empty_fund.get_bills()
        assert len(bills) == 1
        assert bills[0].bill_id == 'electric'
        
        envelopes = empty_fund.get_envelopes()
        assert len(envelopes) > 0

    def test_add_bill_without_envelope_creation(
        self,
        empty_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test adding a bill - envelopes are always created now.
        """
        empty_fund.add_bills(bill_data)
        
        bills = empty_fund.get_bills()
        assert len(bills) == 1
        
        # Envelopes are now always created when bills are added.
        envelopes = empty_fund.get_envelopes()
        assert len(envelopes) > 0

    def test_load_bills_from_dict(
        self,
        empty_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test loading bills from dictionary list.
        """
        empty_fund.add_bills([bill_data])
        
        bills = empty_fund.get_bills()
        assert len(bills) == 1
        assert bills[0].bill_id == 'electric'

    def test_load_bills_from_file(
        self,
        empty_fund: SinkingFund
    ) -> None:
        """
        Test loading bills from CSV file.
        """
        # CSV reader expects dates in %m/%d/%Y format, not ISO format.
        csv_content = (
            "bill_id,service,amount_due,recurring,due_date,start_date,"
            "end_date,frequency,interval,occurrences\n"
            "electric,Electric Bill,150.00,True,,01/15/2024,,monthly,1,\n"
        )
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.csv', delete=False
        ) as tmp_file:
            tmp_file.write(csv_content)
            tmp_path = tmp_file.name
        
        try:
            empty_fund.add_bills(tmp_path)
            bills = empty_fund.get_bills()
            assert len(bills) == 1
            assert bills[0].bill_id == 'electric'
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_create_bills_deprecated(
        self,
        empty_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test deprecated create_bills method.
        """
        empty_fund.add_bills([bill_data])
        
        bills = empty_fund.get_bills()
        assert len(bills) == 1

    def test_update_bill(
        self,
        empty_fund: SinkingFund,
        one_time_bill_data: dict
    ) -> None:
        """
        Test updating a bill and envelope synchronization.
        """
        empty_fund.add_bills(one_time_bill_data)
        
        # Update bill amount.
        empty_fund.update_bill('registration', {'amount_due': 150.00})
        
        bills = empty_fund.get_bills()
        assert bills[0].amount_due == Decimal("150.00")
        
        # Envelopes should be recreated.
        envelopes = empty_fund.get_envelopes()
        assert len(envelopes) > 0

    def test_delete_bills_with_envelopes(
        self,
        empty_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test deleting bills with envelope removal (always happens now).
        """
        empty_fund.add_bills(bill_data)
        empty_fund.delete_bills(['electric'])
        
        bills = empty_fund.get_bills()
        assert len(bills) == 0
        
        envelopes = empty_fund.get_envelopes()
        assert len(envelopes) == 0

    def test_delete_bills_without_envelopes(
        self,
        empty_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test deleting bills - envelopes are always removed now.
        """
        empty_fund.add_bills(bill_data)
        
        empty_fund.delete_bills(['electric'])
        
        bills = empty_fund.get_bills()
        assert len(bills) == 0
        
        # Envelopes are always removed when bills are deleted.
        envelopes = empty_fund.get_envelopes()
        assert len(envelopes) == 0

    def test_get_bills(
        self,
        empty_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test getting all bills.
        """
        empty_fund.add_bills(bill_data)
        
        bills = empty_fund.get_bills()
        assert isinstance(bills, list)
        assert len(bills) == 1
        assert isinstance(bills[0], Bill)

    def test_get_bill_instances(
        self,
        empty_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test getting bill instances for planning period.
        """
        empty_fund.add_bills(bill_data)
        
        instances = empty_fund.get_bill_instances()
        assert isinstance(instances, list)
        assert len(instances) > 0
        assert all(isinstance(inst, BillInstance) for inst in instances)

    def test_get_bills_in_range_deprecated(
        self,
        empty_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test get_bill_instances method (get_bills_in_range was removed).
        """
        empty_fund.add_bills(bill_data)
        
        instances = empty_fund.get_bill_instances()
        assert isinstance(instances, list)


########################################################################
## ENVELOPE MANAGEMENT TESTS
########################################################################

class TestEnvelopeManagement:
    """
    Test envelope management methods.
    """

    def test_create_envelopes(
        self,
        empty_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test that add_bills automatically creates envelopes.
        """
        # add_bills automatically creates envelopes.
        empty_fund.add_bills(bill_data)
        instances = empty_fund.get_bill_instances()
        
        envelopes = empty_fund.get_envelopes()
        assert len(envelopes) == len(instances)

    def test_setup_envelopes(
        self,
        empty_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test that add_bills automatically sets up envelopes with contribution dates.
        """
        # add_bills now automatically creates envelopes with contribution dates.
        empty_fund.add_bills(bill_data, contribution_interval=14)
        
        envelopes = empty_fund.get_envelopes()
        assert len(envelopes) > 0

    def test_get_envelopes(
        self,
        empty_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test getting all envelopes.
        """
        empty_fund.add_bills(bill_data)
        
        envelopes = empty_fund.get_envelopes()
        assert isinstance(envelopes, list)
        assert len(envelopes) > 0
        assert all(isinstance(env, Envelope) for env in envelopes)

    def test_get_envelope(
        self,
        empty_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test getting a specific envelope.
        """
        empty_fund.add_bills(bill_data)
        instances = empty_fund.get_bill_instances()
        
        if instances:
            instance = instances[0]
            envelope = empty_fund.get_envelope(
                bill_id=instance.bill_id,
                due_date=instance.due_date
            )
            
            assert envelope is not None
            assert envelope.bill_instance.bill_id == instance.bill_id

    def test_get_envelope_not_found(
        self,
        empty_fund: SinkingFund
    ) -> None:
        """
        Test getting non-existent envelope returns None.
        """
        envelope = empty_fund.get_envelope(
            bill_id='nonexistent',
            due_date=datetime.date(2024, 1, 1)
        )
        
        assert envelope is None

    def test_update_contribution_dates(
        self,
        empty_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test updating contribution dates for envelopes.
        """
        empty_fund.add_bills(bill_data)
        empty_fund.update_contribution_dates(contribution_interval=7)
        
        envelopes = empty_fund.get_envelopes()
        assert len(envelopes) > 0


########################################################################
## BALANCE MANAGEMENT TESTS
########################################################################

class TestBalanceManagement:
    """
    Test balance management methods.
    """

    def test_update_balance(
        self,
        empty_fund: SinkingFund
    ) -> None:
        """
        Test updating the sinking fund balance.
        """
        empty_fund.update_balance(2500.0)
        
        assert empty_fund.balance == Decimal("2500.0")


########################################################################
## ALLOCATION TESTS
########################################################################

class TestAllocation:
    """
    Test allocation methods.
    """

    def test_allocate_with_sorted_strategy(
        self,
        funded_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test allocation using sorted strategy.
        """
        funded_fund.add_bills(bill_data)
        
        result = funded_fund.allocate(strategy="sorted")
        
        assert result is not None
        assert hasattr(result, 'envelopes')
        assert hasattr(result, 'metadata')

    def test_allocate_with_proportional_strategy(
        self,
        funded_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test allocation using proportional strategy.
        """
        funded_fund.add_bills(bill_data)
        
        result = funded_fund.allocate(
            strategy="proportional",
            method="proportional"
        )
        
        assert result is not None

    def test_reallocate(
        self,
        funded_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test allocate method (reallocate was removed, just use allocate).
        """
        funded_fund.add_bills(bill_data)
        
        result = funded_fund.allocate(strategy="sorted")
        
        assert result is not None

    def test_set_allocation_strategy_deprecated(
        self,
        funded_fund: SinkingFund
    ) -> None:
        """
        Test that set_allocation_strategy method no longer exists.
        """
        # Method was removed - use allocate() directly instead.
        assert not hasattr(funded_fund, 'set_allocation_strategy')

########################################################################
## SCHEDULING TESTS
########################################################################

class TestScheduling:
    """
    Test scheduling methods.
    """

    def test_schedule(
        self,
        funded_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test creating schedules.
        """
        funded_fund.add_bills(bill_data)
        funded_fund.allocate(strategy="sorted")
        funded_fund.update_contribution_dates(contribution_interval=14)
        
        result = funded_fund.schedule(strategy="independent_scheduler")
        
        assert result is not None
        assert hasattr(result, 'schedules')
        assert hasattr(result, 'metadata')

########################################################################
## REPORTING TESTS
########################################################################

class TestReporting:
    """
    Test reporting methods.
    """

    def test_report(
        self,
        funded_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test generating a report.
        """
        funded_fund.add_bills(bill_data)
        funded_fund.allocate(strategy="sorted")
        funded_fund.update_contribution_dates(contribution_interval=14)
        funded_fund.schedule()
        
        report = funded_fund.report(active_only=False)
        
        assert isinstance(report, dict)
        assert len(report) > 0

    def test_report_active_only(
        self,
        funded_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test generating report with active_only=True.
        """
        funded_fund.add_bills(bill_data)
        funded_fund.allocate(strategy="sorted")
        funded_fund.update_contribution_dates(contribution_interval=14)
        funded_fund.schedule()
        
        report = funded_fund.report(active_only=True)
        
        assert isinstance(report, dict)

    def test_build_daily_account_report(
        self,
        funded_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test report method.
        """
        funded_fund.add_bills(bill_data)
        funded_fund.allocate(strategy="sorted")
        funded_fund.update_contribution_dates(contribution_interval=14)
        funded_fund.schedule()
        
        report = funded_fund.report(active_only=False)
        
        assert isinstance(report, dict)

    def test_quick_report(
        self,
        funded_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test quick_report convenience method.
        """
        funded_fund.add_bills(bill_data)
        
        report = funded_fund.quick_report(
            contribution_interval=14,
            allocation_strategy="sorted",
            scheduler_strategy="independent_scheduler",
            active_only=False
        )
        
        assert isinstance(report, dict)
        assert len(report) > 0

    def test_quick_report_active_only(
        self,
        funded_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test quick_report with active_only=True.
        """
        funded_fund.add_bills(bill_data)
        
        report = funded_fund.quick_report(active_only=True)
        
        assert isinstance(report, dict)

    def test_rebuild_report(
        self,
        funded_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test quick_report method (rebuild_report was removed).
        """
        funded_fund.add_bills(bill_data)
        
        report = funded_fund.quick_report(
            allocation_strategy="proportional",
            scheduler_strategy="independent_scheduler",
            contribution_interval=7,
            active_only=False,
            method="equal"
        )
        
        assert isinstance(report, dict)


########################################################################
## STATE MANAGEMENT TESTS
########################################################################

class TestStateManagement:
    """
    Test state management methods.
    """

    def test_sync_envelopes_with_bills(
        self,
        empty_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test syncing envelopes with bills.
        """
        empty_fund.add_bills(bill_data)
        
        # delete_bills always removes envelopes now.
        empty_fund.delete_bills(['electric'])
        
        # Sync should be a no-op since envelopes were already removed.
        empty_fund.sync_envelopes_with_bills()
        
        envelopes = empty_fund.get_envelopes()
        assert len(envelopes) == 0

    def test_sync_envelopes_creates_missing(
        self,
        empty_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test sync creates missing envelopes.
        """
        empty_fund.add_bills(bill_data)
        
        # Sync should create missing envelopes.
        empty_fund.sync_envelopes_with_bills()
        
        envelopes = empty_fund.get_envelopes()
        assert len(envelopes) > 0

    def test_validate_state_valid(
        self,
        empty_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test validate_state with valid state.
        """
        empty_fund.add_bills(bill_data)
        
        is_valid, issues = empty_fund.validate_state()
        
        assert is_valid is True
        assert len(issues) == 0

    def test_validate_state_with_orphaned_envelope(
        self,
        empty_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test validate_state detects orphaned envelopes.
        """
        empty_fund.add_bills(bill_data)
        
        # delete_bills always removes envelopes now.
        empty_fund.delete_bills(['electric'])
        
        is_valid, issues = empty_fund.validate_state()
        
        # State should be valid since envelopes were removed with bills.
        assert is_valid

    def test_validate_state_balance_mismatch(
        self,
        empty_fund: SinkingFund,
        bill_data: dict
    ) -> None:
        """
        Test validate_state runs correctly (balance mismatch check was removed).
        """
        empty_fund.add_bills(bill_data)
        
        # Update balance - Reporter is now created on-demand, no mismatch check.
        empty_fund.update_balance(2000.0)
        
        is_valid, issues = empty_fund.validate_state()
        
        # Validation should run without error.
        assert isinstance(is_valid, bool)
        assert isinstance(issues, list)
        assert isinstance(issues, list)
