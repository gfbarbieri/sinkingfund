"""
Sinking Fund Model
==================

The SinkingFund class is the main class for the sinking fund model. It
orchestrates the entire planning workflow from bill loading to cash
flow projection.
"""

########################################################################
## IMPORTS
########################################################################

import datetime

from .bills import BillInstance
from .envelope import Envelope

from ..managers import (
    BillManager, EnvelopeManager, AllocationManager, ScheduleManager
)

########################################################################
## SINKING FUND MODEL
########################################################################

class SinkingFund:
    """
    A comprehensive sinking fund management system that orchestrates the
    entire planning workflow from bill loading to cash flow projection.
    """
    
    def __init__(
        self, start_date: datetime.date, end_date: datetime.date,
        balance: float=0.0
    ) -> None:
        """
        Initialize the SinkingFund object.

        Parameters
        ----------
        start_date : datetime.date
            The start date of the planning period.
        end_date : datetime.date
            The end date of the planning period.
        balance : float, optional
            The balance of the sinking fund. Defaults to 0.
        """

        self.start_date = start_date
        self.end_date = end_date
        self.balance = balance

        self.bill_manager = BillManager()
        self.envelope_manager = EnvelopeManager()
        self.allocation_manager = AllocationManager()
        self.schedule_manager = ScheduleManager()
    
    ####################################################################
    ## BILLS MANAGEMENTs
    ####################################################################

    def create_bills(self, source: str | list[dict]) -> None:
        """
        Load the bills from the source.
        """

        # Create the bills. The bill manager handles how to creatre the
        # bill instance based on the source data type.
        bills = self.bill_manager.create_bills(source=source)

        # Add the bills to the bill manager.
        self.bill_manager.add_bills(bills)

    def delete_bills(self, bill_ids: list[str]) -> None:
        """
        Remove the bills from the bill manager.
        """

        for bill_id in bill_ids:
            self.bill_manager.remove_bill(bill_id)

    def get_bills_in_range(self) -> list[BillInstance]:
        """
        Get the bills from the bill manager.
        """
        
        # Get the bills in the range.
        bills = self.bill_manager.active_instances_in_range(
            start_reference=self.start_date, end_reference=self.end_date
        )

        return bills

    ####################################################################
    ## ENVELOPE MANAGEMENT
    ####################################################################

    def create_envelopes(self, bill_instances: list[BillInstance]) -> None:
        """
        Create the envelopes from the bill instances.
        """

        # Create the envelopes.
        envelopes = self.envelope_manager.create_envelopes(
            bill_instances=bill_instances
        )

        # Add the envelopes to the envelope manager.
        self.envelope_manager.add_envelopes(envelopes)

    def delete_envelopes(
        self, envelope_ids: list[tuple[str, datetime.date]]
    ) -> None:
        """
        Remove the envelopes from the envelope manager.
        """

        for bill_id, due_date in envelope_ids:
            self.envelope_manager.remove_envelope(
                bill_id=bill_id,
                due_date=due_date
            )

    def update_contribution_dates(self, contribution_interval: int) -> None:
        """
        Update the contribution dates for the envelopes.
        """

        self.envelope_manager.set_contrib_dates(
            start_contrib_date=self.start_date,
            contrib_interval=contribution_interval
        )

    ####################################################################
    ## ALLOCATION MANAGEMENT
    ####################################################################

    def set_allocation_strategy(self, strategy: str, **kwargs) -> None:
        """
        Set the allocation strategy.
        """

        # Set the allocation strategy.
        self.allocation_manager.set_allocator(
            strategy=strategy, **kwargs
        )

    def allocate_balance(self, **kwargs) -> None:
        """
        Allocate the balance to the envelopes.
        """

        # Allocate the balance to the envelopes.
        allocations = self.allocation_manager.allocate(
            envelopes=self.envelope_manager.envelopes,
            balance=self.balance,
            **kwargs
        )

        # Set the allocations to the envelopes.
        self.envelope_manager.set_allocations(allocations)

    ####################################################################
    ## SCHEDULE MANAGEMENT
    ####################################################################

    def set_scheduler(self, strategy: str, **kwargs) -> None:
        """
        Set the scheduler strategy.
        """

        self.schedule_manager.set_scheduler(strategy=strategy, **kwargs)

    def create_schedules(self, **kwargs) -> None:
        """
        Create the schedules for the envelopes.
        """

        # Create cash flow schedules for the envelopes.
        schedules = self.schedule_manager.create_schedules(
            envelopes=self.envelope_manager.envelopes, **kwargs
        )

        # Use the envelope manager to assign the schedules to the
        # envelopes.
        self.envelope_manager.set_schedules(schedules)