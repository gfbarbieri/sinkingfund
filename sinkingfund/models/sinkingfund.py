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

from decimal import Decimal

from .bills import BillInstance

from ..managers import (
    BillManager, EnvelopeManager, AllocationManager, ScheduleManager
)
from ..utils.date_utils import get_date_range

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
        self.balance = Decimal(str(balance))

        self.bill_manager = BillManager()
        self.envelope_manager = EnvelopeManager()
        self.allocation_manager = AllocationManager()
        self.schedule_manager = ScheduleManager()

    ####################################################################
    ## QUICK START
    ####################################################################

    def quick_start(
        self, bill_source: str | list[dict], contribution_interval: int=14,
        allocation_config=None, scheduler_config=None
    ) -> dict[datetime.date, dict[str, Decimal]]:
        
        # DESIGN CHOICE: (1) Set default allocation and scheduler
        # configurations. (2) Allow for custom allocation and scheduler
        # configurations.
        if allocation_config is None:
            allocation_config = {
                'strategy': 'sorted',
                'strategy_kwargs': {'sort_key': 'cascade', 'reverse': False},
                'allocator_kwargs': {}
            }

        if scheduler_config is None:
            scheduler_config = {
                'strategy': 'independent_scheduler',
                'strategy_kwargs': {},
                'scheduler_kwargs': {}
            }
    
        # Create envelopes from bills.
        self.create_bills(source=bill_source)
        instances = self.get_bills_in_range()
        self.create_envelopes(bill_instances=instances)

        # Use allocation configuration to set the allocation strategy
        # and allocate the balance.
        self.set_allocation_strategy(
            strategy=allocation_config['strategy'],
            **allocation_config['strategy_kwargs']
        )
        self.allocate_balance(**allocation_config['allocator_kwargs'])

        # Use the contribution interval to update contribution start and
        # end dates for envelopes.
        self.update_contribution_dates(
            contribution_interval=contribution_interval
        )

        # Use scheduler configuration to set the scheduler strategy and
        # create cash flow schedules for envelopes.
        self.set_scheduler(
            strategy=scheduler_config['strategy'],
            **scheduler_config['strategy_kwargs']
        )
        self.create_schedules(**scheduler_config['scheduler_kwargs'])

        # Create report.
        report = self.build_daily_account_report(active_only=True)

        return report

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

    ####################################################################
    ## ACCOUNT REPORTING
    ####################################################################

    def build_daily_account_report(
        self, active_only: bool=False
    ) -> dict[datetime.date, dict[str, Decimal]]:
        """
        Build the daily account report.

        Parameters
        ----------
        active_only : bool, optional
            Whether to only include active bills in the report.

        Returns
        -------
        dict[datetime.date, dict[str, Decimal]]
            The daily account report.

        Examples
        --------
        Build the daily account report for a specific date:

        .. code-block:: python

            from datetime import date

            report = sinkingfund.build_daily_account_report(date=date(2025, 1, 1))

        The report is a dictionary with the following structure:

        .. code-block:: python

            {date: {bill_id: Decimal}}

        The report contains the balance for each bill on the specified
        date.
        """

        # Get all dates between the start and end dates.
        dates = get_date_range(
            start_date=self.start_date, end_date=self.end_date
        )

        # BUSINESS GOAL: Build the account balance report.
        acct_report = {}

        for date in dates:

            # Get the information for the account balances,
            # contributions, and payouts.
            acct = self.envelope_manager.get_balance_as_of_date(
                as_of_date=date
            )

            contrib = self.envelope_manager.total_cash_flow_on_date(
                date=date, exclude='payouts'
            )

            payout = self.envelope_manager.total_cash_flow_on_date(
                date=date, exclude='contributions'
            )

            # Add the information to the report.
            acct_report[date] = {
                'account_balance': self._build_report_section(
                    data_dict=acct, date=date
                ),
                'contributions': self._build_report_section(
                    data_dict=contrib, date=date
                ),
                'payouts': self._build_report_section(
                    data_dict=payout, date=date
                )
            }

            # Subset if active only.
            if active_only:
                acct_report = {
                    date: data
                    for date, data in acct_report.items()
                    if data['contributions']['count'] > 0
                    or data['payouts']['count'] > 0
                }

        return acct_report

    def _build_report_section(
        self, data_dict: dict, date: datetime.date
    ) -> dict[str, int | Decimal]:
        """
        Helper to build a report section with consistent structure.

        Parameters
        ----------
        data_dict : dict
            The data dictionary.
        date : datetime.date
            The date to build the report for.

        Returns
        -------
        dict[str, int | Decimal]
            The report section.
        """

        # Get the data for the date.
        data = data_dict.get(date, {})

        # Build the report section.
        section = {
            'total': sum(data.values()),
            'count': len([x for x in data.values() if x != 0]),
            'bills': data
        }

        return section