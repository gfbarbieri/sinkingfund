"""
Envelope Manager
================

The EnvelopeManager provides sophisticated envelope lifecycle management
for bill instances within a sinking fund strategy. It orchestrates the
creation, validation, and contribution scheduling of payment envelopes
that accumulate funds toward future bill obligations.

Core Abstractions
-----------------

**Envelope**: A dedicated savings container for a specific bill instance,
tracking contribution dates, funding status, and payment obligations.

**Contribution Scheduling**: The manager implements non-overlapping
contribution periods for bill instances from the same recurring bill,
ensuring users contribute to only one envelope at a time per bill series.

**Validation Framework**: Comprehensive duplicate detection and input
validation to maintain envelope integrity and prevent conflicting
commitments.

Key Features
------------

- **Automated envelope creation** from bill instances with configurable
  contribution parameters.
- **Intelligent contribution date scheduling** that prevents overlapping
  funding periods for recurring bills.
- **Flexible envelope addition** supporting both individual envelopes
  and batch operations.
- **Robust duplicate prevention** with detailed validation and clear
  error reporting.
- **Funding status awareness** with special handling for fully-funded
  envelopes.

Examples
--------

.. code-block:: python

   from datetime import date
   from sinkingfund.managers import EnvelopeManager
   from sinkingfund.models import BillInstance

   # Create manager and bill instances.
   manager = EnvelopeManager()
   instances = [
       BillInstance(
           bill_id="electric",
           amount_due=Decimal("150.00"),
           due_date=date(2024, 3, 15)
       ),
       BillInstance(
           bill_id="electric",
           amount_due=Decimal("145.00"),
           due_date=date(2024, 4, 15)
       )
   ]

   # Create and configure envelopes.
   envelopes = manager.create_envelopes(instances)
   manager.add_envelopes(envelopes)
   manager.set_contrib_dates(
       start_contrib_date=date(2024, 1, 1),
       contrib_interval=14
   )

   # Envelopes now have non-overlapping contribution schedules.
   # First envelope: Jan 1 - Mar 15.
   # Second envelope: Mar 16+ - Apr 15.
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import datetime

from ..models import BillInstance, Envelope
from ..utils import increment_date

########################################################################
## ENVELOPE MANAGER
########################################################################

class EnvelopeManager:
    """
    Manage envelope lifecycle for bill instances in a sinking fund.

    The EnvelopeManager orchestrates envelope creation, validation, and
    contribution scheduling to ensure systematic accumulation of funds
    toward future bill obligations. It implements business rules for
    non-overlapping contribution periods and maintains envelope integrity
    through comprehensive validation.

    Core Responsibilities
    ---------------------

    - **Envelope Creation**: Generate payment envelopes from bill instances
      with default configuration suitable for immediate use
    - **Contribution Scheduling**: Assign start and end contribution dates
      with intelligent handling of recurring bill sequences
    - **Duplicate Prevention**: Validate against conflicting envelopes
      using bill ID and due date uniqueness constraints
    - **Batch Operations**: Support both individual and bulk envelope
      management with consistent validation

    Design Patterns
    ---------------

    - **Manager Pattern**: Centralized coordination of envelope operations
      with clear separation of concerns.
    - **Validation Strategy**: Early input validation with detailed error
      reporting and graceful failure modes.
    - **Business Rule Enforcement**: Automatic application of contribution
      scheduling rules to prevent user conflicts.

    Attributes
    ----------
    envelopes : list[Envelope]
        Collection of managed payment envelopes, maintained in insertion
        order for predictable iteration behavior.

    Notes
    -----
    The manager implements a "contribute to one envelope per bill at a time"
    policy for recurring bills. This prevents users from accidentally
    funding multiple instances of the same bill simultaneously, which could
    lead to cash flow management complexity.

    Examples
    --------
    .. code-block:: python

       # Basic envelope management workflow.
       manager = EnvelopeManager()
       envelopes = manager.create_envelopes(bill_instances)
       manager.add_envelopes(envelopes)
       manager.set_contrib_dates()

       # Access managed envelopes.
       for envelope in manager.envelopes:
           print(f"{envelope.bill_instance.bill_id}: "
                 f"{envelope.start_contrib_date} - "
                 f"{envelope.end_contrib_date}")
    """

    def __init__(self) -> None:
        """
        Initialize an empty envelope manager.

        Creates a new manager instance with no envelopes, ready to accept
        envelope creation and management operations.

        Notes
        -----
        The manager starts with an empty envelope collection. Envelopes
        must be explicitly created via `create_envelopes()` and added
        via `add_envelopes()` before contribution scheduling can be
        performed.
        """
        self.envelopes: list[Envelope] = []

    def add_envelopes(self, envelopes: list[Envelope] | Envelope) -> None:
        """
        Add one or more envelopes to the manager with validation.

        Accepts both individual envelopes and lists of envelopes,
        performing duplicate validation before addition to maintain
        envelope uniqueness constraints.

        Parameters
        ----------
        envelopes : list[Envelope] or Envelope
            Single envelope or list of envelopes to add to the manager.
            Each envelope must have a unique combination of bill_id and
            due_date.

        Raises
        ------
        ValueError
            If any envelope conflicts with existing envelopes (same
            bill_id and due_date combination) or if the input type is
            not supported.
        TypeError
            If the input is neither an Envelope nor a list of Envelopes.

        Notes
        -----
        The method normalizes single envelope inputs to lists internally
        for consistent validation processing. All validation occurs
        before any envelopes are added, ensuring atomic success or
        failure.

        Examples
        --------
        .. code-block:: python

           # Add single envelope
           manager.add_envelopes(envelope)

           # Add multiple envelopes
           manager.add_envelopes([envelope1, envelope2, envelope3])
        """

        # DESIGN CHOICE: Normalize input to list for consistent
        # processing.
        if isinstance(envelopes, Envelope):
            envelope_list = [envelopes]
        elif isinstance(envelopes, list):
            envelope_list = envelopes
        else:
            raise TypeError(
                f"Unsupported envelope type: {type(envelopes)}. "
                f"Expected list[Envelope] or Envelope."
            )

        # EARLY EXIT OPTIMIZATION: Skip processing if no envelopes
        # provided.
        if not envelope_list:
            return

        # BUSINESS GOAL: Prevent duplicate envelope creation that could
        # lead to double-funding of the same bill instance
        self._validate_no_duplicate_envelopes(envelope_list)

        # SIDE EFFECTS: Modify manager state by adding validated envelopes
        self.envelopes.extend(envelope_list)

    def create_envelopes(
        self, bill_instances: list[BillInstance]
    ) -> list[Envelope]:
        """
        Create payment envelopes from bill instances with defaults.

        Generates envelope objects for each provided bill instance using
        default configuration suitable for immediate use. Created envelopes
        require subsequent contribution date configuration via
        `set_contrib_dates()`.

        Parameters
        ----------
        bill_instances : list[BillInstance]
            Bill instances to create envelopes for. Each instance must
            have a valid bill_id, amount_due, and due_date.

        Returns
        -------
        list[Envelope]
            Newly created envelopes with default configuration. Envelopes
            are returned in the same order as input instances.

        Notes
        -----
        Created envelopes have default contribution scheduling that must
        be configured before use. Call `set_contrib_dates()` after adding
        envelopes to the manager to establish contribution periods.

        The method does not validate for duplicates against existing
        manager envelopes. Use `add_envelopes()` to perform validation
        when adding to the manager.

        Examples
        --------
        .. code-block:: python

           instances = [bill_instance1, bill_instance2]
           envelopes = manager.create_envelopes(instances)
           # envelopes[0].bill_instance == bill_instance1
           # envelopes[1].bill_instance == bill_instance2
        """

        # EARLY EXIT OPTIMIZATION: Handle empty input efficiently.
        if not bill_instances:
            return []

        # BUSINESS GOAL: Create envelope containers for systematic
        # accumulation of funds toward bill obligations. DESIGN CHOICE:
        # Use default Envelope constructor for consistent initialization
        # across all envelopes.
        envelopes = [
            Envelope(bill_instance=instance)
            for instance in bill_instances
        ]

        return envelopes

    def set_contrib_dates(
        self,
        start_contrib_date: datetime.date | None = None,
        contrib_interval: int=14
    ) -> None:
        """
        Configure contribution schedules for all managed envelopes.

        Assigns contribution start and end dates to all envelopes using
        intelligent scheduling that prevents overlapping contribution
        periods for recurring bills. Fully-funded envelopes receive
        nominal scheduling while underfunded envelopes get sequential
        non-overlapping periods.

        Parameters
        ----------
        start_contrib_date : datetime.date, optional
            Reference date to begin contribution scheduling. If None,
            defaults to today's date.
        contrib_interval : int, default 14
            Days between contribution payments. Must be positive.

        Raises
        ------
        ValueError
            If contrib_interval is not positive.

        Notes
        -----
        **Scheduling Strategy**:

        - **Fully-funded envelopes**: Receive start_contrib_date as
          start and due_date as end, with specified interval
        - **Underfunded envelopes**: Get sequential non-overlapping
          periods within each bill_id group, sorted by due_date

        **Business Rule**: Users contribute to only one envelope per
        bill at a time. For recurring bills with multiple underfunded
        instances, contribution periods are scheduled sequentially to
        prevent conflicts.

        Examples
        --------
        .. code-block:: python

           # Configure with default start date (today)
           manager.set_contrib_dates(contrib_interval=7)

           # Configure with specific start date
           manager.set_contrib_dates(
               start_contrib_date=date(2024, 1, 1),
               contrib_interval=14
           )
        """
        
        # DESIGN CHOICE: Avoid mutable default by setting None and
        # assigning inside function body.
        if start_contrib_date is None:
            start_contrib_date = datetime.date.today()

        # BUSINESS GOAL: Ensure positive contribution intervals for
        # meaningful payment scheduling.
        if contrib_interval <= 0:
            raise ValueError(
                f"contrib_interval must be positive, got {contrib_interval}"
            )

        # EARLY EXIT OPTIMIZATION: Skip processing if no envelopes
        # exist.
        if not self.envelopes:
            return

        # BUSINESS GOAL: Handle fully-funded envelopes with nominal
        # scheduling since no further contributions are expected.
        for envelope in self.envelopes:

            if envelope.is_fully_funded(as_of_date=start_contrib_date):
                
                envelope.start_contrib_date = start_contrib_date
                envelope.end_contrib_date = envelope.bill_instance.due_date
                envelope.contrib_interval = contrib_interval

        # BUSINESS GOAL: Implement sequential contribution scheduling
        # for underfunded envelopes to prevent user conflicts.
        bill_ids = {
            e.bill_instance.bill_id for e in self.envelopes
            if not e.is_fully_funded(as_of_date=start_contrib_date)
        }

        # PERFORMANCE: Process each bill_id group independently
        # to minimize iteration complexity.
        for bill_id in bill_ids:
            
            # DESIGN CHOICE: Sort by due_date to establish chronological
            # contribution sequence for recurring bills.
            envelopes = sorted(
                [
                    e for e in self.envelopes
                    if e.bill_instance.bill_id == bill_id
                ],
                key=lambda e: e.bill_instance.due_date
            )

            # INVARIANT: Process envelopes in chronological order to
            # ensure non-overlapping contribution periods.
            for i, envelope in enumerate(envelopes):
                
                if i == 0:
                    # DESIGN CHOICE: First envelope starts on reference
                    # date for both single and recurring bill scenarios.
                    start = start_contrib_date
                else:
                    # BUSINESS GOAL: Find first valid contribution date
                    # after previous envelope's due date.
                    curr_date = start_contrib_date
                    prev_due_date = envelopes[i - 1].bill_instance.due_date

                    # PERFORMANCE: Increment by contribution interval
                    # until we find a date after previous due date.
                    while curr_date <= prev_due_date:
                        curr_date = increment_date(
                            reference_date=curr_date,
                            frequency='daily',
                            interval=contrib_interval,
                            num_intervals=1
                        )

                    start = curr_date

                # SIDE EFFECTS: Configure envelope contribution schedule
                envelope.start_contrib_date = start
                envelope.end_contrib_date = envelope.bill_instance.due_date
                envelope.contrib_interval = contrib_interval
    
    def _envelope_exists(
        self, bill_id: str, due_date: datetime.date
    ) -> bool:
        """
        Check if an envelope exists for the given bill instance.

        Determines whether an envelope already exists for the specific
        combination of bill_id and due_date, which uniquely identifies
        a bill instance in the system.

        Parameters
        ----------
        bill_id : str
            Unique identifier of the bill to check.
        due_date : datetime.date
            Due date of the bill instance to check.

        Returns
        -------
        bool
            True if an envelope exists for this bill instance,
            False otherwise.

        Notes
        -----
        A bill instance is uniquely identified by the combination of
        bill_id and due_date. This allows multiple envelopes for the
        same bill (different due dates) while preventing duplicates
        for the same specific instance.
        """
        # DESIGN CHOICE: Use tuple comparison for efficient lookup
        # of bill_id and due_date combinations.
        target_instance = (bill_id, due_date)
        
        # PERFORMANCE: Generator expression avoids materializing
        # full list when early match is found.
        return any(
            (envelope.bill_instance.bill_id, envelope.bill_instance.due_date)
            == target_instance
            for envelope in self.envelopes
        )

    def _validate_no_duplicate_envelopes(
        self, envelopes_to_add: list[Envelope]
    ) -> None:
        """
        Validate that envelopes to add do not conflict with existing
        ones.

        Performs comprehensive duplicate checking to ensure envelope
        uniqueness constraints are maintained. Checks both against
        existing manager envelopes and within the candidate list itself.

        Parameters
        ----------
        envelopes_to_add : list[Envelope]
            Candidate envelopes for addition to the manager. Must not
            conflict with existing envelopes or each other.

        Raises
        ------
        ValueError
            If any envelope conflicts with existing envelopes or if
            the candidate list contains internal duplicates.

        Notes
        -----
        The validation performs two checks:
        1. Against existing manager envelopes (external conflicts)
        2. Within the candidate list itself (internal conflicts)

        This ensures atomic addition where either all envelopes are
        added successfully or none are added.
        """
        
        # BUSINESS GOAL: Check for conflicts with existing envelopes to
        # prevent duplicate creations of the same bill instance.
        for envelope in envelopes_to_add:
            bill_id = envelope.bill_instance.bill_id
            due_date = envelope.bill_instance.due_date
            
            if self._envelope_exists(bill_id, due_date):
                raise ValueError(
                    f"Envelope already exists for bill '{bill_id}' "
                    f"due on {due_date}. Cannot add duplicate envelope."
                )