"""
Sinking Fund Model Tests
========================

Initialization tests for Sinking Fund model. Since sinking fund model
includes a number of sub-models, we will test only the initialization
here and test the workflow in the integration tests.
"""

########################################################################
## IMPORTS
########################################################################

import datetime
from decimal import Decimal

import pytest

from sinkingfund.models.sinkingfund import SinkingFund

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
        
        # Test: Assert that the SinkingFund instance has the correct
        # managers.
        assert fund.bill_manager is not None
        assert fund.envelope_manager is not None
        assert fund.allocation_manager is not None
        assert fund.schedule_manager is not None
