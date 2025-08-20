"""
Bill Manager
============

The BillManager provides comprehensive bill lifecycle management within
a sinking fund system. It orchestrates bill creation, validation, and
instance generation while abstracting the complexity of multiple data
sources and formats from the core sinking fund operations.

Core Abstractions
-----------------

**Bill Management**: Centralized storage and validation of bill
definitions with support for both one-time and recurring payment
obligations.

**Source Abstraction**: Unified interface for loading bills from
diverse sources including files (CSV, Excel, JSON), dictionaries,
and structured data lists.

**Instance Generation**: Intelligent creation of bill instances within
specified time ranges, including next-instance prediction for
forward-looking planning.

**Validation Framework**: Comprehensive duplicate detection and input
validation to maintain bill registry integrity.

Key Features
------------

- **Multi-source bill loading** with automatic format detection and
  standardized processing pipeline
- **Flexible bill addition** supporting both individual bills and
  batch operations with atomic validation
- **Bill removal** with existence validation and clean state management
- **Instance timeline generation** for specified date ranges with
  automatic next-instance calculation
- **Robust duplicate prevention** with detailed validation and clear
  error reporting

Examples
--------

.. code-block:: python

   from datetime import date
   from sinkingfund.managers import BillManager

   # Create manager and load bills from file
   manager = BillManager()
   bills = manager.create_bills("bills.csv")
   manager.add_bills(bills)

   # Add individual bill
   bill_data = {
       'bill_id': 'netflix',
       'service': 'Netflix Subscription',
       'amount_due': 15.99,
       'recurring': True,
       'start_date': date(2024, 1, 1),
       'frequency': 'monthly'
   }
   new_bills = manager.create_bills([bill_data])
   manager.add_bills(new_bills)

   # Generate bill instances for planning period
   instances = manager.active_instances_in_range(
       start_reference=date(2024, 1, 1),
       end_reference=date(2024, 12, 31)
   )
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import datetime

from typing import Any

from ..models import Bill, BillInstance
from ..utils import load_bill_data_from_file

########################################################################
## BILL MANAGER
########################################################################

class BillManager:
    """
    Coordinate bill operations for systematic sinking fund management.

    The BillManager centralizes bill lifecycle operations including
    creation, validation, storage, and instance generation. It abstracts
    the complexity of multi-source data loading and provides a unified
    interface for bill-related operations within the sinking fund system.

    Core Responsibilities
    ---------------------

    - **Bill Registry Management**: Maintain a validated collection of
      bill definitions with uniqueness constraints and clean operations.
    - **Multi-Source Loading**: Support diverse data sources with
      automatic format detection and standardized processing.
    - **Instance Generation**: Create bill instances for specified time
      ranges with intelligent next-instance prediction.
    - **Validation Coordination**: Enforce business rules for bill
      uniqueness and data integrity.

    Design Patterns
    ---------------

    - **Manager Pattern**: Centralized coordination of bill operations
      with clear separation from core sinking fund logic.
    - **Source Abstraction**: Unified interface hiding complexity of
      different data formats and loading mechanisms.
    - **Factory Pattern**: Consistent bill creation from various input
      types with standardized validation.

    Attributes
    ----------
    bills : list[Bill]
        Collection of managed bill definitions, maintained in insertion
        order for predictable iteration behavior.

    Notes
    -----
    The manager enforces bill_id uniqueness across all managed bills.
    This ensures clear identification and prevents conflicting bill
    definitions that could lead to ambiguous instance generation.

    Examples
    --------
    .. code-block:: python

       # Create manager and load from multiple sources.
       manager = BillManager()
       
       # Load from file.
       file_bills = manager.create_bills("monthly_bills.csv")
       manager.add_bills(file_bills)
       
       # Add individual bill.
       single_bill = manager.create_bills([bill_dict])
       manager.add_bills(single_bill)
       
       # Generate instances for planning.
       instances = manager.active_instances_in_range(
           start_reference=date(2024, 1, 1),
           end_reference=date(2024, 12, 31)
       )
    """
    
    def __init__(self) -> None:
        """
        Initialize an empty bill manager.

        Creates a new manager instance with no bills, ready to accept
        bill creation and management operations from various sources.

        Notes
        -----
        The manager starts with an empty bill collection. Bills must be
        explicitly created via `create_bills()` and added via
        `add_bills()` before instance generation can be performed.
        """
        self.bills: list[Bill] = []

    def add_bills(self, bills: list[Bill] | Bill) -> None:
        """
        Add one or more bills to the manager with validation.

        Accepts both individual bills and lists of bills, performing
        duplicate validation before addition to maintain bill registry
        integrity and prevent conflicting bill definitions.

        Parameters
        ----------
        bills : list[Bill] or Bill
            Single bill or list of bills to add to the manager. Each
            bill must have a unique bill_id within the manager.

        Raises
        ------
        ValueError
            If any bill has a bill_id that conflicts with existing
            bills in the manager.
        TypeError
            If the input is neither a Bill nor a list of Bills.

        Notes
        -----
        The method normalizes single bill inputs to lists internally
        for consistent validation processing. All validation occurs
        before any bills are added, ensuring atomic success or failure.

        Examples
        --------
        .. code-block:: python

           # Add single bill.
           manager.add_bills(bill)

           # Add multiple bills.
           manager.add_bills([bill1, bill2, bill3])
        """
        
        # DESIGN CHOICE: Normalize input to list for consistent
        # processing.
        if isinstance(bills, Bill):
            bill_list = [bills]
        elif isinstance(bills, list):
            bill_list = bills
        else:
            raise TypeError(
                f"Unsupported bill type: {type(bills)}. "
                f"Expected list[Bill] or Bill."
            )

        # EARLY EXIT OPTIMIZATION: Skip processing if no bills provided
        if not bill_list:
            return

        # BUSINESS GOAL: Prevent duplicate bill IDs that could lead to
        # ambiguous bill identification and instance generation
        self._validate_no_duplicate_bills(bill_list)

        # SIDE EFFECTS: Modify manager state by adding validated bills
        self.bills.extend(bill_list)
    
    def remove_bill(self, bill_id: str) -> None:
        """
        Remove a bill from the manager by bill_id.

        Removes the bill with the specified bill_id from the manager's
        collection after validating its existence. This operation
        maintains the integrity of the bill registry.

        Parameters
        ----------
        bill_id : str
            Unique identifier of the bill to remove. Must exist in the
            current manager collection.

        Raises
        ------
        ValueError
            If no bill exists with the specified bill_id.

        Notes
        -----
        After removal, the bill is no longer available for instance
        generation or other operations. This operation cannot be undone
        without re-adding the bill.

        Examples
        --------
        .. code-block:: python

           # Remove specific bill
           manager.remove_bill("netflix")
           
           # Verify removal
           assert manager.get_bill_count() == previous_count - 1
        """
        
        # BUSINESS GOAL: Validate bill existence before removal to
        # provide clear error feedback.
        if not self._bill_exists(bill_id):
            raise ValueError(
                f"Bill with ID '{bill_id}' does not exist. "
                f"Cannot remove non-existent bill."
            )

        # SIDE EFFECTS: Modify manager state by removing specified bill
        self.bills = [
            bill for bill in self.bills if bill.bill_id != bill_id
        ]
    
    def create_bills(self, source: str | list[dict], **kwargs) -> list[Bill]:
        """
        Create bills from diverse data sources with unified processing.

        Provides a flexible interface for bill creation from multiple
        source types including files, dictionaries, and structured data.
        Handles format detection, data loading, and standardized Bill
        object creation.

        Parameters
        ----------
        source : str or list[dict]
            Data source for bill creation:
            
            - **str**: File path to data file (CSV, Excel, JSON)
            - **list[dict]**: Collection of bill data dictionaries
            
        **kwargs
            Additional arguments passed to file loading functions.
            Common examples:
            
            - ``sheet_name`` : str, for Excel files
            - ``encoding`` : str, for text files
            
        Returns
        -------
        list[Bill]
            Newly created Bill objects from the source data, ready for
            addition to the manager.
            
        Raises
        ------
        ValueError
            If the source type is not supported or if bill data is
            malformed.
        FileNotFoundError
            If a file path is provided but the file doesn't exist.
        KeyError
            If required bill data fields are missing from dictionaries.
            
        Notes
        -----
        This method creates bills but does not add them to the manager.
        Use `add_bills()` to incorporate created bills into the managed
        collection.
        
        File sources are processed through the utility loading pipeline
        which handles format detection and data standardization.
            
        Examples
        --------
        Create bills from file:
        
        .. code-block:: python
        
           bills = manager.create_bills("data/bills.csv")
           manager.add_bills(bills)
           
        Create bills from dictionary data:
        
        .. code-block:: python
        
           bill_data = [{
               'bill_id': 'netflix',
               'service': 'Netflix Subscription',
               'amount_due': 15.99,
               'recurring': True,
               'start_date': date(2025, 1, 1),
               'frequency': 'monthly'
           }]
           bills = manager.create_bills(bill_data)
           manager.add_bills(bills)
        """

        # DESIGN CHOICE: Route to appropriate processing based on source
        # type.
        if isinstance(source, str):
            
            # BUSINESS GOAL: Support file-based bill data loading with
            # flexible format handling.
            bill_data = load_bill_data_from_file(source, **kwargs)
            
            bills = self.create_bills_from_data(bill_data)
            
            return bills
        
        elif (
            isinstance(source, list)
            and all(isinstance(item, dict) for item in source)
        ):
            # DESIGN CHOICE: Direct processing for pre-structured data.
            bills = self.create_bills_from_data(source)
            
            return bills
            
        else:
            raise ValueError(
                f"Unsupported source type: {type(source)}. "
                f"Expected str (file path) or list[dict] (bill data)."
            )
    
    def get_bill_count(self) -> int:
        """
        Get the number of bills currently managed.

        Provides a simple count of bills in the manager's collection,
        useful for validation, reporting, and capacity planning.
        
        Returns
        -------
        int
            The number of bills in the manager. Returns 0 if no bills
            are currently managed.

        Examples
        --------
        .. code-block:: python

           # Check manager state.
           if manager.get_bill_count() == 0:
               print("No bills loaded.")
           else:
               print(f"Managing {manager.get_bill_count()} bills.")
        """
        return len(self.bills)
    
    def active_instances_in_range(
        self, start_reference: datetime.date, end_reference: datetime.date
    ) -> list[BillInstance]:
        """
        Generate bill instances for a specified time range with
        lookahead.

        Creates a comprehensive timeline of bill instances covering the
        specified period, including one additional "next" instance beyond
        the range for forward-looking planning and envelope preparation.

        Parameters
        ----------
        start_reference : datetime.date
            Start date of the range for instance generation (inclusive).
        end_reference : datetime.date
            End date of the range for instance generation (inclusive).

        Returns
        -------
        list[BillInstance]
            All bill instances with due dates in [start_reference,
            end_reference], plus one next instance per bill for planning.
            Returns empty list if no bills are managed.

        Notes
        -----
        **Generation Strategy**:
        
        1. Generate instances within the specified range for each bill
        2. Calculate one "next" instance beyond the range per bill
        3. Combine all instances into a unified timeline
        
        The next instance inclusion supports sinking fund planning by
        providing visibility into upcoming obligations that may require
        envelope preparation during the current planning period.
        
        **Edge Cases**:
        
        - For non-recurring bills, next_instance may return None
        - Empty bill collection returns empty instance list
        - Invalid date ranges are handled by individual bill logic

        Examples
        --------
        .. code-block:: python

           # Generate instances for quarterly planning
           instances = manager.active_instances_in_range(
               start_reference=date(2024, 1, 1),
               end_reference=date(2024, 3, 31)
           )
           
           # Each bill contributes instances in Q1 plus one next instance
           for instance in instances:
               if instance:  # Check for None from non-recurring bills
                   print(f"{instance.bill_id}: {instance.due_date}")
        """
        
        # EARLY EXIT OPTIMIZATION: Handle empty bill collection.
        if not self.bills:
            return []

        # BUSINESS GOAL: Create comprehensive timeline of bill
        # obligations for systematic sinking fund planning.
        active_instances = []

        # PERFORMANCE: Process each bill independently to minimize
        # coupling between bill instance generation.
        for bill in self.bills:
            
            # DESIGN CHOICE: Generate instances within range first.
            bill_instances = bill.instances_in_range(
                start_reference=start_reference, end_reference=end_reference
            )

            # BUSINESS GOAL: Include next instance for forward planning
            # to support envelope preparation for upcoming obligations.
            if bill_instances:
                # Use last instance in range as reference for next
                # calculation.
                next_instance = bill.next_instance(
                    reference_date=bill_instances[-1].due_date
                )
            else:
                # Use start reference if no instances in range.
                next_instance = bill.next_instance(
                    reference_date=start_reference
                )

            # EDGE CASE: Handle None next_instance from non-recurring
            # bills.
            if next_instance is not None:
                bill_instances.append(next_instance)

            # SIDE EFFECTS: Accumulate instances from all bills.
            active_instances.extend(bill_instances)

        return active_instances
        
    def _bill_exists(self, bill_id: str) -> bool:
        """
        Check if a bill exists with the specified bill_id.

        Performs efficient lookup to determine whether a bill with the
        given bill_id is currently managed by this instance.
        
        Parameters
        ----------
        bill_id : str
            Unique identifier of the bill to check for existence.
            
        Returns
        -------
        bool
            True if a bill exists with the specified bill_id,
            False otherwise.

        Notes
        -----
        This method performs case-sensitive string comparison on bill_id
        values. Empty or None bill_id values will return False.
        """
        # PERFORMANCE: Generator expression avoids materializing full
        # list when early match is found.
        return any(bill.bill_id == bill_id for bill in self.bills)

    def _validate_no_duplicate_bills(
        self, bills_to_add: list[Bill]
    ) -> None:
        """
        Validate that bills to add do not conflict with existing ones.

        Performs comprehensive duplicate checking to ensure bill_id
        uniqueness constraints are maintained. Checks both against
        existing manager bills and within the candidate list itself.

        Parameters
        ----------
        bills_to_add : list[Bill]
            Candidate bills for addition to the manager. Must not
            conflict with existing bills or each other.
            
        Raises
        ------
        ValueError
            If any bill has a bill_id that conflicts with existing
            bills or if the candidate list contains internal duplicates.

        Notes
        -----
        The validation performs two checks:
        1. Against existing manager bills (external conflicts)
        2. Within the candidate list itself (internal conflicts)
        
        This ensures atomic addition where either all bills are added
        successfully or none are added.
        """
        
        # BUSINESS GOAL: Prevent duplicate bill_id values that could
        # lead to ambiguous bill identification.
        for bill in bills_to_add:
            
            if self._bill_exists(bill.bill_id):
                
                raise ValueError(
                    f"Bill with ID '{bill.bill_id}' already exists. "
                    f"Cannot add duplicate bill."
                )

    def create_bills_from_data(
        self, data: list[dict[str, Any]]
    ) -> list[Bill]:
        """
        Convert standardized dictionary data into Bill objects.

        Transforms structured bill data dictionaries into properly
        configured Bill instances using standardized field mapping.
        This method is format-agnostic and focuses solely on the
        business logic of Bill object construction.
        
        Parameters
        ----------
        data : list[dict[str, Any]]
            List of dictionaries containing bill data with standardized
            field names. Each dictionary must contain required fields:
            
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
            
        Returns
        -------
        list[Bill]
            Properly configured Bill objects ready for manager addition.
            Returns empty list if input data is empty.
            
        Raises
        ------
        KeyError
            If required fields are missing from any dictionary.
        TypeError
            If field values have incorrect types.
            
        Notes
        -----
        This method uses Bill constructor validation to ensure proper
        object creation. Invalid data will raise exceptions during Bill
        instantiation, providing clear error feedback.
        
        The method handles optional fields gracefully using dict.get()
        to provide None defaults for missing values.

        Examples
        --------
        .. code-block:: python

           bill_data = [{
               'bill_id': 'electric',
               'service': 'Electric Utility',
               'amount_due': 150.00,
               'recurring': True,
               'start_date': date(2024, 1, 1),
               'frequency': 'monthly'
           }]
           bills = manager.create_bills_from_data(bill_data)
        """
        
        # EARLY EXIT OPTIMIZATION: Handle empty input efficiently.
        if not data:
            return []

        # BUSINESS GOAL: Convert structured data into validated Bill
        # objects for systematic management. Use Bill constructor for
        # validation and consistent object creation across all data
        # sources.
        bills = [
            Bill(
                bill_id=record['bill_id'],
                service=record['service'],
                amount_due=record['amount_due'],
                recurring=record['recurring'],
                due_date=record.get('due_date'),
                start_date=record.get('start_date'),
                end_date=record.get('end_date'),
                frequency=record.get('frequency'),
                interval=record.get('interval'),
                occurrences=record.get('occurrences')
            )
            for record in data
        ]
        
        return bills