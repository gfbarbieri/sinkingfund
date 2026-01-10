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

from __future__ import annotations

import datetime

from decimal import Decimal

from .bills import Bill, BillInstance
from .envelope import Envelope

from ..allocation.base import AllocationResult
from ..managers import (
    BillManager, EnvelopeManager, AllocationManager, Reporter,
    ScheduleManager
)
from ..schedules.base import ScheduleResult

########################################################################
## SINKING FUND MODEL
########################################################################

class SinkingFund:
    """
    A comprehensive sinking fund management system that orchestrates the
    entire planning workflow from bill loading to cash flow projection.
    """
    
    def __init__(
        self,
        start_date: datetime.date,
        end_date: datetime.date,
        balance: float = 0.0
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

        Notes
        -----
        Managers are created internally and are not exposed as public
        attributes. All operations should be performed through the
        SinkingFund public API methods.
        """

        self.start_date = start_date
        self.end_date = end_date
        self.balance = Decimal(str(balance))

        # DESIGN CHOICE: Managers are private implementation details.
        # All operations go through SinkingFund's public API.
        self._bill_manager = BillManager()
        self._envelope_manager = EnvelopeManager()
        self._allocation_manager = AllocationManager()
        self._schedule_manager = ScheduleManager()

    ####################################################################
    ## BILLS MANAGEMENT
    ####################################################################

    def add_bills(
        self, source: str | dict | list[dict], contribution_interval: int = 14
    ) -> None:
        """
        Add bills from file, single dictionary, or list of dictionaries.

        Adds bills to the bill manager and automatically creates envelopes
        for bill instances in the planning period with contribution dates
        configured. This method orchestrates both BillManager and
        EnvelopeManager operations.

        Parameters
        ----------
        source : str or dict or list[dict]
            Data source for bills:
            
            - **str**: File path to bill data (CSV, Excel, JSON)
            - **dict**: Single bill dictionary with required fields:
                - **bill_id** : str, unique identifier
                - **service** : str, service description
                - **amount_due** : Decimal or float, payment amount
                - **recurring** : bool, recurrence flag
                
                Optional fields:
                - **due_date** : date, for one-time bills
                - **start_date** : date, for recurring bills
                - **end_date** : date, recurrence end
                - **frequency** : str, recurrence frequency
                - **interval** : int, recurrence interval
                - **occurrences** : int, occurrence limit
            - **list[dict]**: List of bill dictionaries with same structure
              as dict parameter
        contribution_interval : int, optional
            Days between contribution payments. Defaults to 14 (bi-weekly).
            Used to set contribution dates for created envelopes.

        Notes
        -----
        Envelopes are automatically created for all bill instances in the
        planning period with contribution dates configured. This ensures
        envelopes are ready for allocation and scheduling immediately after
        bills are added.

        Examples
        --------
        Add bills from a CSV file:

        .. code-block:: python

           from datetime import date
           from sinkingfund import SinkingFund
           
           fund = SinkingFund(
               start_date=date(2025, 1, 1),
               end_date=date(2025, 12, 31),
               balance=1000.00
           )
           fund.add_bills("bills.csv")

        Add a single bill from a dictionary:

        .. code-block:: python

           from datetime import date
           from decimal import Decimal
           from sinkingfund import SinkingFund
           
           fund = SinkingFund(
               start_date=date(2025, 1, 1),
               end_date=date(2025, 12, 31),
               balance=1000.00
           )
           fund.add_bills({
               'bill_id': 'electric',
               'service': 'Electric Bill',
               'amount_due': Decimal("150.00"),
               'recurring': True,
               'start_date': date(2025, 1, 1),
               'frequency': 'monthly'
           })

        Add multiple bills from a list with custom contribution interval:

        .. code-block:: python

           from datetime import date
           from decimal import Decimal
           from sinkingfund import SinkingFund
           
           fund = SinkingFund(
               start_date=date(2025, 1, 1),
               end_date=date(2025, 12, 31),
               balance=1000.00
           )
           bills = [
               {
                   'bill_id': 'electric',
                   'service': 'Electric Bill',
                   'amount_due': Decimal("150.00"),
                   'recurring': True,
                   'start_date': date(2025, 1, 1),
                   'frequency': 'monthly'
               },
               {
                   'bill_id': 'water',
                   'service': 'Water Bill',
                   'amount_due': Decimal("75.00"),
                   'recurring': True,
                   'start_date': date(2025, 1, 1),
                   'frequency': 'monthly'
               }
           ]
           fund.add_bills(bills, contribution_interval=7)
        """
        
        # BUSINESS GOAL: Normalize input to list[dict] format for processing.
        # If single dict provided, wrap it in a list.
        if isinstance(source, dict):
            bill_data_list = [source]
        else:
            bill_data_list = source
        
        # BUSINESS GOAL: Create bills using BillManager to ensure proper
        # validation and standardization.
        bills = self._bill_manager.create_bills(bill_data_list)
        
        # BUSINESS GOAL: Add bills to manager with validation.
        self._bill_manager.add_bills(bills)
        
        # BUSINESS GOAL: Always create envelopes for new bills to maintain
        # consistent workflow.
        # Get all bill instances including the new bills.
        instances = self.get_bill_instances()
        
        # Filter to instances for the new bill_ids.
        new_bill_ids = {bill.bill_id for bill in bills}
        new_instances = [
            instance for instance in instances
            if instance.bill_id in new_bill_ids
        ]
        
        # Create envelopes for new instances and set contribution dates
        # so envelopes are ready for allocation and scheduling.
        if new_instances:
            self.create_envelopes(new_instances)
            self.update_contribution_dates(
                contribution_interval=contribution_interval
            )

    def update_bill(self, bill_id: str, updates: dict) -> None:
        """
        Update a bill and sync associated envelopes.

        Updates bill properties and recreates associated envelopes to
        ensure consistency. This method orchestrates BillManager and
        EnvelopeManager operations.

        Parameters
        ----------
        bill_id : str
            Unique identifier of the bill to update.
        updates : dict
            Dictionary of properties to update. Supported keys:
            
            - **service** : str, service description
            - **amount_due** : Decimal or float, payment amount
            - **recurring** : bool, recurrence flag
            - **due_date** : date, for one-time bills
            - **start_date** : date, for recurring bills
            - **end_date** : date, recurrence end
            - **frequency** : str, recurrence frequency
            - **interval** : int, recurrence interval
            - **occurrences** : int, occurrence limit

        Notes
        -----
        When a bill is updated, its instances may change, so associated
        envelopes are deleted and recreated if the bill still has
        instances in the planning period.

        Examples
        --------
        Update bill amount:

        .. code-block:: python

           from datetime import date
           from decimal import Decimal
           from sinkingfund import SinkingFund
           
           fund = SinkingFund(
               start_date=date(2025, 1, 1),
               end_date=date(2025, 12, 31),
               balance=1000.00
           )
           fund.add_bills({
               'bill_id': 'electric',
               'service': 'Electric Bill',
               'amount_due': Decimal("150.00"),
               'recurring': True,
               'start_date': date(2025, 1, 1),
               'frequency': 'monthly'
           })
           fund.update_bill("electric", {"amount_due": Decimal("175.00")})

        Update multiple properties:

        .. code-block:: python

           from datetime import date
           from decimal import Decimal
           from sinkingfund import SinkingFund
           
           fund = SinkingFund(
               start_date=date(2025, 1, 1),
               end_date=date(2025, 12, 31),
               balance=1000.00
           )
           fund.add_bills({
               'bill_id': 'rent',
               'service': 'Monthly Rent',
               'amount_due': Decimal("1200.00"),
               'recurring': True,
               'start_date': date(2025, 1, 1),
               'frequency': 'monthly'
           })
           fund.update_bill(
               "rent",
               {
                   "amount_due": Decimal("1250.00"),
                   "frequency": "monthly"
               }
           )
        """
        
        # BUSINESS GOAL: Update bill using BillManager to ensure proper
        # validation and standardization.
        self._bill_manager.update_bill(bill_id, updates)
        
        # DESIGN CHOICE: Find and delete old envelopes since bill
        # instances may have changed.
        old_envelopes = self._envelope_manager.get_envelopes_for_bill(
            bill_id
        )
        
        if old_envelopes:
            envelope_ids = [
                (
                    envelope.bill_instance.bill_id,
                    envelope.bill_instance.due_date
                )
                for envelope in old_envelopes
            ]
            self._delete_envelopes(envelope_ids)
        
        # BUSINESS GOAL: Recreate envelopes if bill still has instances
        # in the planning period.
        instances = self.get_bill_instances()
        new_instances = [
            instance for instance in instances
            if instance.bill_id == bill_id
        ]
        
        if new_instances:
            self.create_envelopes(new_instances)

    def delete_bills(self, bill_ids: list[str]) -> None:
        """
        Remove bills and their associated envelopes.

        Removes bills from the bill manager and automatically removes
        associated envelopes. This method orchestrates both BillManager
        and EnvelopeManager operations to maintain state consistency.

        Parameters
        ----------
        bill_ids : list[str]
            List of bill IDs to remove.

        Notes
        -----
        At the SinkingFund level, bills and envelopes are managed together.
        Deleting a bill automatically deletes its associated envelopes to
        maintain consistency.

        Examples
        --------
        Delete bills and their envelopes:

        .. code-block:: python

           from datetime import date
           from sinkingfund import SinkingFund
           
           fund = SinkingFund(
               start_date=date(2025, 1, 1),
               end_date=date(2025, 12, 31),
               balance=1000.00
           )
           fund.add_bills([
               {'bill_id': 'electric', 'service': 'Electric',
                'amount_due': 150.00, 'recurring': True,
                'start_date': date(2025, 1, 1), 'frequency': 'monthly'},
               {'bill_id': 'water', 'service': 'Water',
                'amount_due': 75.00, 'recurring': True,
                'start_date': date(2025, 1, 1), 'frequency': 'monthly'}
           ])
           fund.delete_bills(['electric', 'water'])
        """
        
        # BUSINESS GOAL: Always remove associated envelopes before deleting
        # bills to maintain state consistency.
        envelope_ids = []
        
        for bill_id in bill_ids:
            # Find envelopes for this bill.
            envelopes = self._envelope_manager.get_envelopes_for_bill(
                bill_id
            )
            
            # Build envelope_ids list.
            for envelope in envelopes:
                envelope_ids.append((
                    envelope.bill_instance.bill_id,
                    envelope.bill_instance.due_date
                ))
        
        # Delete all associated envelopes.
        if envelope_ids:
            self._delete_envelopes(envelope_ids)
        
        # BUSINESS GOAL: Remove bills from BillManager.
        for bill_id in bill_ids:
            self._bill_manager.remove_bill(bill_id)

    def get_bills(self) -> list[Bill]:
        """
        Get all loaded bills.

        Returns
        -------
        list[Bill]
            A copy of all bills currently loaded in the sinking fund.

        Examples
        --------
        Get all bills:

        .. code-block:: python

           from datetime import date
           from sinkingfund import SinkingFund
           
           fund = SinkingFund(
               start_date=date(2025, 1, 1),
               end_date=date(2025, 12, 31),
               balance=1000.00
           )
           fund.add_bills({
               'bill_id': 'electric',
               'service': 'Electric Bill',
               'amount_due': 150.00,
               'recurring': True,
               'start_date': date(2025, 1, 1),
               'frequency': 'monthly'
           })
           bills = fund.get_bills()
           for bill in bills:
               print(f"{bill.bill_id}: {bill.service}")
        """
        return self._bill_manager.bills.copy()

    def get_bill_instances(self) -> list[BillInstance]:
        """
        Get bill instances for the planning period.

        Returns
        -------
        list[BillInstance]
            All bill instances with due dates within the planning period,
            plus one next instance per bill for forward planning.

        Examples
        --------
        Get bill instances:

        .. code-block:: python

           from datetime import date
           from sinkingfund import SinkingFund
           
           fund = SinkingFund(
               start_date=date(2025, 1, 1),
               end_date=date(2025, 12, 31),
               balance=1000.00
           )
           fund.add_bills({
               'bill_id': 'electric',
               'service': 'Electric Bill',
               'amount_due': 150.00,
               'recurring': True,
               'start_date': date(2025, 1, 1),
               'frequency': 'monthly'
           })
           instances = fund.get_bill_instances()
           for instance in instances:
               print(f"{instance.bill_id} due {instance.due_date}")
        """
        return self._bill_manager.active_instances_in_range(
            start_reference=self.start_date, end_reference=self.end_date
        )

    ####################################################################
    ## ENVELOPE MANAGEMENT
    ####################################################################

    def create_envelopes(self, bill_instances: list[BillInstance]) -> None:
        """
        Create the envelopes from the bill instances.
        """

        # Create the envelopes.
        envelopes = self._envelope_manager.create_envelopes(
            bill_instances=bill_instances
        )

        # Add the envelopes to the envelope manager.
        self._envelope_manager.add_envelopes(envelopes)

    def _delete_envelopes(
        self, envelope_ids: list[tuple[str, datetime.date]]
    ) -> None:
        """
        Remove envelopes from the envelope manager.

        Internal method for envelope deletion. At the SinkingFund level,
        envelopes should be managed through bill operations, not directly.
        """

        for bill_id, due_date in envelope_ids:
            self._envelope_manager.remove_envelope(
                bill_id=bill_id,
                due_date=due_date
            )

    def get_envelopes(self) -> list[Envelope]:
        """
        Get all envelopes.

        Returns
        -------
        list[Envelope]
            A copy of all envelopes currently in the sinking fund.

        Examples
        --------
        Get all envelopes:

        .. code-block:: python

           from datetime import date
           from sinkingfund import SinkingFund
           
           fund = SinkingFund(
               start_date=date(2025, 1, 1),
               end_date=date(2025, 12, 31),
               balance=1000.00
           )
           fund.add_bills({
               'bill_id': 'electric',
               'service': 'Electric Bill',
               'amount_due': 150.00,
               'recurring': True,
               'start_date': date(2025, 1, 1),
               'frequency': 'monthly'
           })
           envelopes = fund.get_envelopes()
           for envelope in envelopes:
               print(f"{envelope.bill_instance.bill_id}: "
                     f"${envelope.initial_allocation}")
        """
        return self._envelope_manager.envelopes.copy()

    def get_envelope(
        self, bill_id: str, due_date: datetime.date
    ) -> Envelope | None:
        """
        Get a specific envelope by bill ID and due date.

        Parameters
        ----------
        bill_id : str
            The bill ID of the envelope.
        due_date : datetime.date
            The due date of the envelope.

        Returns
        -------
        Envelope or None
            The envelope if found, None otherwise.

        Examples
        --------
        Get a specific envelope:

        .. code-block:: python

           from datetime import date
           from sinkingfund import SinkingFund
           
           fund = SinkingFund(
               start_date=date(2025, 1, 1),
               end_date=date(2025, 12, 31),
               balance=1000.00
           )
           fund.add_bills({
               'bill_id': 'electric',
               'service': 'Electric Bill',
               'amount_due': 150.00,
               'recurring': True,
               'start_date': date(2025, 3, 1),
               'frequency': 'monthly'
           })
           envelope = fund.get_envelope(
               bill_id="electric",
               due_date=date(2025, 3, 15)
           )
        """

        # Search through envelopes to find matching one.
        for envelope in self._envelope_manager.envelopes:
            if (
                envelope.bill_instance.bill_id == bill_id
                and envelope.bill_instance.due_date == due_date
            ):
                return envelope
    
        return None

    def update_contribution_dates(self, contribution_interval: int) -> None:
        """
        Update the contribution dates for the envelopes.

        Parameters
        ----------
        contribution_interval : int
            Days between contribution payments.
        """

        self._envelope_manager.set_contrib_dates(
            start_contrib_date=self.start_date,
            contrib_interval=contribution_interval
        )

    ####################################################################
    ## BALANCE MANAGEMENT
    ####################################################################

    def update_balance(self, new_balance: float) -> None:
        """
        Update account balance.

        Updates the sinking fund balance. The Reporter is created
        on-demand when reports are generated, so no synchronization
        is needed.

        Parameters
        ----------
        new_balance : float
            The new account balance.

        Examples
        --------
        Update balance after receiving funds:

        .. code-block:: python

           from datetime import date
           from sinkingfund import SinkingFund
           
           fund = SinkingFund(
               start_date=date(2025, 1, 1),
               end_date=date(2025, 12, 31),
               balance=1000.00
           )
           fund.update_balance(6000.00)
        """
        
        # BUSINESS GOAL: Update balance to reflect current account state.
        self.balance = Decimal(str(new_balance))

    ####################################################################
    ## ALLOCATION MANAGEMENT
    ####################################################################

    def allocate(
        self, strategy: str = "sorted", **strategy_kwargs
    ) -> AllocationResult:
        """
        Allocate funds to envelopes using specified strategy.

        This method sets the allocation strategy and performs the
        allocation in one call.

        Parameters
        ----------
        strategy : str, optional
            Allocation strategy to use. Options: "sorted", "proportional".
            Defaults to "sorted".
        **strategy_kwargs
            Additional keyword arguments passed to the allocation
            strategy. See strategy documentation for available options.

        Returns
        -------
        AllocationResult
            A result object containing the allocation assignments and
            metadata about the allocation operation.

        Examples
        --------
        Allocate with default sorted strategy:

        .. code-block:: python

           from datetime import date
           from sinkingfund import SinkingFund
           
           fund = SinkingFund(
               start_date=date(2025, 1, 1),
               end_date=date(2025, 12, 31),
               balance=1000.00
           )
           fund.add_bills({
               'bill_id': 'electric',
               'service': 'Electric Bill',
               'amount_due': 150.00,
               'recurring': True,
               'start_date': date(2025, 1, 1),
               'frequency': 'monthly'
           })
           result = fund.allocate()

        Allocate with proportional strategy:

        .. code-block:: python

           from datetime import date
           from sinkingfund import SinkingFund
           
           fund = SinkingFund(
               start_date=date(2025, 1, 1),
               end_date=date(2025, 12, 31),
               balance=1000.00
           )
           fund.add_bills({
               'bill_id': 'electric',
               'service': 'Electric Bill',
               'amount_due': 150.00,
               'recurring': True,
               'start_date': date(2025, 1, 1),
               'frequency': 'monthly'
           })
           result = fund.allocate(strategy="proportional", method="equal")
        """
        # DESIGN CHOICE: Provide default sort_key for sorted strategy.
        if strategy == "sorted" and "sort_key" not in strategy_kwargs:
            strategy_kwargs["sort_key"] = "cascade"
        
        # Set the allocation strategy.
        self._allocation_manager.set_allocator(
            strategy=strategy, **strategy_kwargs
        )

        # Allocate the balance to the envelopes.
        result = self._allocation_manager.allocate(
            envelopes=self._envelope_manager.envelopes,
            balance=self.balance
        )

        # Set the allocations to the envelopes.
        self._envelope_manager.set_allocations(result.envelopes)

        return result

    ####################################################################
    ## SCHEDULER MANAGEMENT
    ####################################################################

    def schedule(
        self, strategy: str = "independent_scheduler", **strategy_kwargs
    ) -> ScheduleResult:
        """
        Create contribution schedules for envelopes using specified
        strategy.

        This method sets the scheduling strategy and creates schedules
        in one call.

        Parameters
        ----------
        strategy : str, optional
            Scheduling strategy to use. Options: "independent_scheduler".
            Defaults to "independent_scheduler".
        **strategy_kwargs
            Additional keyword arguments passed to the scheduling
            strategy. See strategy documentation for available options.

        Returns
        -------
        ScheduleResult
            A result object containing the generated schedules and
            metadata about the scheduling operation.

        Examples
        --------
        Create schedules with default strategy:

        .. code-block:: python

           from datetime import date
           from sinkingfund import SinkingFund
           
           fund = SinkingFund(
               start_date=date(2025, 1, 1),
               end_date=date(2025, 12, 31),
               balance=1000.00
           )
           fund.add_bills({
               'bill_id': 'electric',
               'service': 'Electric Bill',
               'amount_due': 150.00,
               'recurring': True,
               'start_date': date(2025, 1, 1),
               'frequency': 'monthly'
           })
           fund.allocate()
           fund.update_contribution_dates(contribution_interval=14)
           result = fund.schedule()
        """
        # Set the scheduler strategy.
        self._schedule_manager.set_scheduler(
            strategy=strategy, **strategy_kwargs
        )

        # Create cash flow schedules for the envelopes.
        result = self._schedule_manager.create_schedules(
            envelopes=self._envelope_manager.envelopes, **strategy_kwargs
        )

        # Use the envelope manager to assign the schedules to the
        # envelopes.
        self._envelope_manager.set_schedules(result.schedules)

        return result

    ####################################################################
    ## STATE MANAGEMENT
    ####################################################################

    def sync_envelopes_with_bills(self) -> None:
        """
        Ensure envelopes match current bills.

        Synchronizes envelopes with the current bill collection by
        removing orphaned envelopes (envelopes for deleted bills) and
        creating missing envelopes (bills with instances but no envelopes).

        Notes
        -----
        This method ensures state consistency between BillManager and
        EnvelopeManager. It is useful after manual bill deletions or
        when envelopes may have become out of sync.

        Examples
        --------
        Sync envelopes after deleting bills:

        .. code-block:: python

           from datetime import date
           from sinkingfund import SinkingFund
           
           fund = SinkingFund(
               start_date=date(2025, 1, 1),
               end_date=date(2025, 12, 31),
               balance=1000.00
           )
           fund.add_bills({
               'bill_id': 'old_bill',
               'service': 'Old Bill',
               'amount_due': 100.00,
               'recurring': True,
               'start_date': date(2025, 1, 1),
               'frequency': 'monthly'
           })
           fund.delete_bills(['old_bill'])
           fund.sync_envelopes_with_bills()  # Clean up orphaned envelopes
        """
        
        # Get all bill_ids from bills.
        bill_ids = {bill.bill_id for bill in self._bill_manager.bills}
        
        # Find orphaned envelopes (envelope bill_id not in bills).
        orphaned_envelopes = [
            envelope for envelope in self._envelope_manager.envelopes
            if envelope.bill_instance.bill_id not in bill_ids
        ]
        
        # Delete orphaned envelopes.
        if orphaned_envelopes:
            envelope_ids = [
                (
                    envelope.bill_instance.bill_id,
                    envelope.bill_instance.due_date
                )
                for envelope in orphaned_envelopes
            ]
            self._delete_envelopes(envelope_ids)
        
        # Get current bill instances.
        instances = self.get_bill_instances()
        
        # Find missing envelopes (bill has instances but no envelope).
        existing_envelope_keys = {
            (e.bill_instance.bill_id, e.bill_instance.due_date)
            for e in self._envelope_manager.envelopes
        }
        
        missing_instances = [
            instance for instance in instances
            if (instance.bill_id, instance.due_date) not in existing_envelope_keys
        ]
        
        # Create missing envelopes.
        if missing_instances:
            self.create_envelopes(missing_instances)

    def validate_state(self) -> tuple[bool, list[str]]:
        """
        Check if state is consistent across managers.

        Validates that the state is consistent between BillManager and
        EnvelopeManager. Returns a boolean indicating validity and a list
        of any issues found.

        Returns
        -------
        tuple[bool, list[str]]
            A tuple containing:

            - **is_valid** : bool, True if state is consistent, False
              otherwise
            - **issues** : list[str], List of descriptive issue messages

        Examples
        --------
        Validate state and check for issues:

        .. code-block:: python

           from datetime import date
           from sinkingfund import SinkingFund
           
           fund = SinkingFund(
               start_date=date(2025, 1, 1),
               end_date=date(2025, 12, 31),
               balance=1000.00
           )
           fund.add_bills({
               'bill_id': 'electric',
               'service': 'Electric Bill',
               'amount_due': 150.00,
               'recurring': True,
               'start_date': date(2025, 1, 1),
               'frequency': 'monthly'
           })
           is_valid, issues = fund.validate_state()
           if not is_valid:
               for issue in issues:
                   print(f"Issue: {issue}")
        """
        
        issues = []
        
        # Check: All envelopes have corresponding bills.
        bill_ids = {bill.bill_id for bill in self._bill_manager.bills}
        for envelope in self._envelope_manager.envelopes:
            if envelope.bill_instance.bill_id not in bill_ids:
                issues.append(
                    f"Envelope for bill '{envelope.bill_instance.bill_id}' "
                    f"has no corresponding bill."
                )
        
        # Check: No duplicate envelopes.
        envelope_keys = {}
        for envelope in self._envelope_manager.envelopes:
            key = (
                envelope.bill_instance.bill_id,
                envelope.bill_instance.due_date
            )
            if key in envelope_keys:
                issues.append(
                    f"Duplicate envelope for bill '{envelope.bill_instance.bill_id}' "
                    f"due on {envelope.bill_instance.due_date}."
                )
            else:
                envelope_keys[key] = envelope
        
        is_valid = len(issues) == 0
        
        return (is_valid, issues)

    ####################################################################
    ## ACCOUNT REPORTING
    ####################################################################

    def report(
        self, active_only: bool = False
    ) -> dict[datetime.date, dict[str, Decimal]]:
        """
        Generate daily account report.

        Parameters
        ----------
        active_only : bool, optional
            Whether to only include dates with contributions or payouts.
            Defaults to False.

        Returns
        -------
        dict[datetime.date, dict[str, Decimal]]
            The daily account report with account balances, contributions,
            and payouts for each date.

        Examples
        --------
        Generate full report:

        .. code-block:: python

           from datetime import date
           from sinkingfund import SinkingFund
           
           fund = SinkingFund(
               start_date=date(2025, 1, 1),
               end_date=date(2025, 12, 31),
               balance=1000.00
           )
           fund.add_bills({
               'bill_id': 'electric',
               'service': 'Electric Bill',
               'amount_due': 150.00,
               'recurring': True,
               'start_date': date(2025, 1, 1),
               'frequency': 'monthly'
           })
           fund.allocate()
           fund.update_contribution_dates(contribution_interval=14)
           fund.schedule()
           report = fund.report()

        Generate report with only active dates:

        .. code-block:: python

           from datetime import date
           from sinkingfund import SinkingFund
           
           fund = SinkingFund(
               start_date=date(2025, 1, 1),
               end_date=date(2025, 12, 31),
               balance=1000.00
           )
           fund.add_bills({
               'bill_id': 'electric',
               'service': 'Electric Bill',
               'amount_due': 150.00,
               'recurring': True,
               'start_date': date(2025, 1, 1),
               'frequency': 'monthly'
           })
           fund.allocate()
           fund.update_contribution_dates(contribution_interval=14)
           fund.schedule()
           report = fund.report(active_only=True)
        """

        # DESIGN CHOICE: Create Reporter on-demand with current state to
        # avoid state synchronization issues. Delegate report generation
        # to Reporter class to maintain separation of concerns.
        reporter = Reporter(
            envelope_manager=self._envelope_manager,
            start_date=self.start_date,
            end_date=self.end_date,
            balance=self.balance
        )
        
        return reporter.generate_daily_report(active_only=active_only)

    def quick_report(
        self,
        contribution_interval: int = 14,
        allocation_strategy: str = "sorted",
        scheduler_strategy: str = "independent_scheduler",
        active_only: bool = True,
        **allocation_kwargs
    ) -> dict[datetime.date, dict[str, Decimal]]:
        """
        Generate a complete report in one call following the standard workflow.

        This method performs the standard sinking fund workflow:
        1. Ensures envelopes exist (creates from bill instances if needed)
        2. Allocates existing balance to envelopes
        3. Updates contribution dates for scheduling
        4. Creates contribution schedules
        5. Generates daily account report

        This is a convenience method that encodes the standard workflow. For
        more control, use the individual methods: `allocate()`, 
        `update_contribution_dates()`, `schedule()`, and `report()`.

        Parameters
        ----------
        contribution_interval : int, optional
            Days between contribution payments. Defaults to 14 (bi-weekly).
            Updates contribution dates on all envelopes. Note: if you called
            `add_bills()` with a different interval, this will override it.
        allocation_strategy : str, optional
            Allocation strategy to use. Options: "sorted", "proportional".
            Defaults to "sorted".
        scheduler_strategy : str, optional
            Scheduling strategy to use. Options: "independent_scheduler".
            Defaults to "independent_scheduler".
        active_only : bool, optional
            Whether to only include dates with contributions or payouts
            in the report. Defaults to True.
        **allocation_kwargs
            Additional keyword arguments passed to the allocation strategy.

        Returns
        -------
        dict[datetime.date, dict[str, Decimal]]
            The daily account report with the following structure:

            .. code-block:: python

               {date: {
                   'account_balance': {
                       'total': Decimal,
                       'count': int,
                       'bills': dict[str, Decimal]
                   },
                    'contributions': {
                        'total': Decimal,
                        'count': int,
                        'bills': dict[str, Decimal]
                   },
                    'payouts': {
                        'total': Decimal,
                        'count': int,
                        'bills': dict[str, Decimal]
                   }
               }}

        Notes
        -----
        This method assumes bills have been added via `add_bills()`, which
        automatically creates envelopes. If envelopes don't exist (e.g., bills
        were added manually), envelopes will be created automatically.

        The workflow encoded by this method:
        
        1. **Get bill instances**: `get_bill_instances()` - get all bill
        occurrences in planning period
        2. **Create envelopes** (if needed): `create_envelopes()` - wrap bill
        instances in envelope containers
        3. **Allocate balance**: `allocate()` - distribute existing balance to
        envelopes (independent of contribution dates)
        4. **Update contribution dates**: `update_contribution_dates()` - set
        contribution intervals needed for scheduling
        5. **Create schedules**: `schedule()` - generate contribution schedules
        (separate from payment schedule which comes from bill instances)
        6. **Generate report**: `report()` - create daily account report

        Examples
        --------
        Standard workflow (envelopes already exist from add_bills):

        .. code-block:: python

           from decimal import Decimal
           
           fund = SinkingFund(
               start_date=date(2025, 1, 1), 
               end_date=date(2025, 12, 31),
               balance=Decimal("5000.00")
           )
        
           # Creates envelopes automatically.
           fund.add_bills("bills.csv")

           # Allocates, schedules, reports.
           report = fund.quick_report()

        Complete workflow from scratch:

        .. code-block:: python

           fund = SinkingFund(
               start_date=date(2025, 1, 1),
               end_date=date(2025, 12, 31),
               balance=5000.00
            )
        
           # quick_report will create envelopes if needed.
           report = fund.quick_report(contribution_interval=7)
        """

        # BUSINESS GOAL: Ensure envelopes exist. If add_bills() was called,
        # envelopes already exist. If not, create them from bill instances.
        if not self._envelope_manager.envelopes:
            instances = self.get_bill_instances()
            if instances:
                self.create_envelopes(bill_instances=instances)

        # BUSINESS GOAL: Update contribution dates with specified interval.
        # This allows changing the interval from what was set in add_bills(),
        # or sets it if envelopes were just created above.
        self.update_contribution_dates(
            contribution_interval=contribution_interval
        )

        # BUSINESS GOAL: Allocate existing balance to envelopes using
        # specified strategy. This is independent of contribution dates.
        self.allocate(strategy=allocation_strategy, **allocation_kwargs)

        # BUSINESS GOAL: Create contribution schedules using specified
        # strategy. Requires contribution dates to be set (done above).
        self.schedule(strategy=scheduler_strategy)

        # BUSINESS GOAL: Generate daily account report showing balances,
        # contributions, and payouts over time.
        report = self.report(active_only=active_only)

        return report