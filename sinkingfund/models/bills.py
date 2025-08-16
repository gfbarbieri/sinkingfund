"""
Bill Models
===========

This module defines the core models for representing financial
obligations in a sinking fund system. The models capture both one-time
and recurring expenses with sophisticated date calculation capabilities.

The bill models serve as the foundation of the sinking fund system.
They represent the financial obligations that require planning and
saving. This module provides two key abstractions:

Classes
-------
Bill
    Represents the complete definition of a financial obligation. Bills
    can be one-time expenses (such as an annual insurance payment) or
    recurring obligations (such as a monthly subscription). For
    recurring bills, the system supports various frequencies including
    daily, weekly, monthly, quarterly, and annual with customizable
    intervals.

BillInstance  
    Represents a specific occurrence of a bill with a concrete due date
    and amount. A recurring bill generates multiple bill instances over
    time.

Features
--------
The Bill class provides sophisticated date calculation methods that
handle calendar complexities such as varying month lengths and leap
years. For example, a monthly bill due on the 31st will correctly
adjust to the last day of shorter months.

Key capabilities include:

* Determining when the next payment is due relative to any reference
  date.
* Generating sequences of all future payments within specified date
  ranges.
* Calculating the number of occurrences within time boundaries.
* Managing bill lifecycle through start dates, end dates, and
  occurrence limits.
* Controlling whether bills due on a reference date are considered
  "current" or "next" through the inclusive parameter.

By modeling bills with this level of detail, the sinking fund system
can project future cash flow needs with precision, calculate required
savings rates to meet obligations, track progress toward fully funded
financial goals, visualize the timing of upcoming expenses, and group
expenses for allocation strategies.

The bill models work in concert with the Envelope and CashFlow models
to provide a complete picture of your sinking fund strategy and
execution.

Examples
--------

Creating a recurring monthly bill:

.. code-block:: python

   bill = Bill(
       bill_id="insurance",
       service="Car Insurance", 
       amount_due=150.00,
       recurring=True,
       start_date=date(2025, 1, 15),
       frequency="monthly",
       interval=1,
       occurrences=12
   )

Getting the next instance with inclusive control:

.. code-block:: python

   # Get next instance including today if due.
   next_payment = bill.next_instance(
       date(2025, 3, 15), inclusive=True
   )
   print(next_payment.due_date)  # 2025-03-15

   # Get next instance after today.
   next_payment = bill.next_instance(
       date(2025, 3, 15), inclusive=False
   )
   print(next_payment.due_date)  # 2025-04-15

"""

########################################################################
## IMPORTS
########################################################################

import datetime

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Union

from ..utils import increment_date

########################################################################
## BILLS
########################################################################

@dataclass(frozen=True, order=True)
class BillInstance:
    """
    Immutable record of a specific bill occurrence with concrete due
    date and amount.
    
    BillInstance represents a single, concrete occurrence of a financial
    obligation that is due on a particular date. While Bill represents
    the general definition and schedule of an obligation, BillInstance
    represents one specific payment event in that schedule.
    
    Parameters
    ----------
    due_date : datetime.date
        The date when this instance payment is due. Used as primary
        sort key for chronological ordering.
    bill_id : str
        Unique identifier linking this instance to its parent bill
        definition. Must be non-empty.
    service : str
        Human-readable name of the service or obligation this instance
        represents. Used for reporting and identification.
    amount_due : Decimal
        Monetary amount required for this specific instance. Must be
        positive for valid financial obligations.
        
    Raises
    ------
    ValueError
        If bill_id is empty, service is empty, or amount_due is not
        positive.
        
    Notes
    -----
    DESIGN CHOICE: Using frozen dataclass ensures instances remain
    immutable after creation, preventing accidental modifications that
    could compromise financial calculations and audit trails.
    
    BUSINESS GOAL: Chronological ordering via due_date enables efficient
    timeline analysis and cash flow projections without manual sorting.
    
    BillInstance objects are typically created by Bill methods such as 
    next_instance() and instances_in_range(). They represent the
    concrete scheduling information needed for cash flow planning and
    allocation calculations.
    
    For recurring bills, multiple BillInstance objects represent the
    sequence of payments over time. For non-recurring bills, there is
    exactly one BillInstance.
    
    Examples
    --------
    Create a bill instance manually:
    
    .. code-block:: python
    
       from decimal import Decimal
       from datetime import date
       
       instance = BillInstance(
           due_date=date(2025, 1, 1),
           bill_id="rent_jan",
           service="Monthly Rent",
           amount_due=Decimal("1200.00")
       )
    
    Get instances from a bill:
    
    .. code-block:: python
    
       bill = Bill(
           "insurance", "Car Insurance", Decimal("150.00"), True,
           start_date=date(2025, 1, 15), frequency="monthly", 
           occurrences=3
       )
        
       instances = bill.instances_in_range(
           date(2025, 1, 1), date(2025, 3, 31)
       )
        
       for instance in instances:
           print(
               f"{instance.service}: ${instance.amount_due} due "
               f"{instance.due_date}"
           )

    """
    
    # INVARIANT: Primary sorting key for chronological ordering.
    # Secondary keys provide deterministic ordering when multiple
    # instances occur on the same date.
    due_date: datetime.date
    bill_id: str
    service: str
    amount_due: Decimal
    
    def __post_init__(self) -> None:
        """
        Validate bill instance data immediately after construction.
        
        Raises
        ------
        ValueError
            If bill_id is empty, service is empty, or amount_due is not
            positive.
            
        Notes
        -----
        Validation runs once at construction time rather than on every
        property access, ensuring data integrity with minimal
        performance overhead.
        """
    
        # BUSINESS GOAL: Prevent silent failures from empty identifiers
        # that could cause incorrect bill associations or reporting.
        if not self.bill_id or not self.bill_id.strip():
            raise ValueError("bill_id cannot be empty or whitespace")
            
        if not self.service or not self.service.strip():
            raise ValueError("service cannot be empty or whitespace")
        
        # BUSINESS GOAL: Ensure all financial obligations have positive
        # amounts to prevent accounting errors and negative cash flows.
        if self.amount_due <= 0:
            raise ValueError("amount_due must be positive")
        
        # DESIGN CHOICE: Explicit Decimal validation catches conversion
        # errors early rather than allowing invalid monetary values.
        try:
            if not isinstance(self.amount_due, Decimal):
                object.__setattr__(
                    self, 'amount_due', Decimal(str(self.amount_due))
                )
        except (ValueError, TypeError) as e:
            raise ValueError(f"amount_due must be a valid monetary value: {e}")

class Bill:
    """
    A financial obligation with due dates and amounts.
    
    The Bill class represents both one-time and recurring financial 
    obligations. It provides sophisticated date calculation methods to 
    determine payment schedules, handle calendar complexities, and
    manage bill lifecycles through configurable parameters.
    
    Parameters
    ----------
    bill_id : str
        The unique identifier for the bill.
    service : str  
        The name of the service or obligation that the bill represents.
    amount_due : float
        The amount due for each instance of the bill.
    recurring : bool
        Whether the bill repeats according to a schedule. Non-recurring 
        bills have exactly one due date.
    due_date : datetime.date, optional
        The due date for non-recurring bills. Required when
        recurring=False.
    start_date : datetime.date, optional  
        The date of the first occurrence for recurring bills. Required
        when recurring=True.
    end_date : datetime.date, optional
        The final due date for recurring bills. Cannot be used with
        occurrences.
    frequency : str, optional
        The frequency of recurrence. Valid values are 'daily', 'weekly', 
        'monthly', 'quarterly', 'annual'. Required when recurring=True.
    interval : int, optional
        The interval between occurrences. For example, interval=2 with 
        frequency='weekly' creates a bi-weekly bill. Defaults to 1.
    occurrences : int, optional
        The total number of occurrences for recurring bills. Cannot be
        used with end_date. The system will calculate end_date
        automatically.
    
    Attributes  
    ----------
    bill_id : str
        The unique identifier for the bill.
    service : str
        The name of the service that the bill represents.
    amount_due : float  
        The amount due for each instance of the bill.
    recurring : bool
        Whether the bill repeats according to a schedule.
    start_date : datetime.date
        The date of the first occurrence. For non-recurring bills, this 
        equals due_date.
    end_date : datetime.date  
        The date of the final occurrence. For non-recurring bills, this 
        equals due_date.
    frequency : str or None
        The frequency of recurrence. None for non-recurring bills.
    interval : int or None
        The interval between occurrences. None for non-recurring bills.
    occurrences : int
        The total number of occurrences. Always 1 for non-recurring
        bills.
    
    Notes
    -----
    The constructor automatically standardizes bill configurations.
    Bills marked as recurring with occurrences=1 are converted to
    non-recurring bills. When occurrences is provided, end_date is
    calculated automatically. When end_date is provided without
    occurrences, the number of occurrences is calculated automatically.
    
    Examples
    --------
    Create a non-recurring bill:
    
    .. code-block:: python
    
       bill = Bill(
           bill_id="annual_fee",
           service="Credit Card Annual Fee",
           amount_due=95.00, 
           recurring=False,
           due_date=date(2025, 12, 1)
       )
    
    Create a recurring bill with a fixed number of occurrences:
    
    .. code-block:: python
    
       bill = Bill(
           bill_id="rent", 
           service="Monthly Rent",
           amount_due=1200.00,
           recurring=True,
           start_date=date(2025, 1, 1),
           frequency="monthly", 
           interval=1,
           occurrences=12
       )

    """

    def __init__(
        self,
        bill_id: str,
        service: str,
        amount_due: Union[Decimal, float],
        recurring: bool,
        due_date: Optional[datetime.date] = None,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
        frequency: Optional[str] = None,
        interval: Optional[int] = None,
        occurrences: Optional[int] = None
    ):
        """
        Initialize a Bill with automatic configuration standardization.
        
        The constructor automatically standardizes bill configurations
        to ensure consistency. Bills marked as recurring with
        occurrences=1 are converted to non-recurring bills. When
        occurrences is provided, end_date is calculated automatically.
        When end_date is provided without occurrences, the number of
        occurrences is calculated automatically.
        
        Parameters
        ----------
        bill_id : str
            The unique identifier for the bill.
        service : str  
            The name of the service or obligation that the bill
            represents.
        amount_due : float
            The amount due for each instance of the bill.
        recurring : bool
            Whether the bill repeats according to a schedule.
            Non-recurring bills have exactly one due date.
        due_date : datetime.date, optional
            The due date for non-recurring bills. Required when
            recurring=False.
        start_date : datetime.date, optional  
            The date of the first occurrence for recurring bills.
            Required when recurring=True.
        end_date : datetime.date, optional
            The final due date for recurring bills. Cannot be used with
            occurrences. The system will calculate occurrences
            automatically.
        frequency : str, optional
            The frequency of recurrence. Valid values are 'daily',
            'weekly', 'monthly', 'quarterly', 'annual'. Required when
            recurring=True.
        interval : int, optional
            The interval between occurrences. For example, interval=2
            with frequency='weekly' creates a bi-weekly bill. Defaults
            to 1.
        occurrences : int, optional
            The total number of occurrences for recurring bills. Cannot
            be used with end_date. The system will calculate end_date
            automatically.
        
        Notes
        -----
        The constructor performs several standardization operations:
        
        1. **Non-recurring bills**: Sets start_date and end_date to
        due_date, and occurrences to 1.
        2. **Pseudo-recurring bills**: Bills marked as recurring with
        occurrences=1 are converted to non-recurring for consistency.
        3. **End date calculation**: When occurrences > 1 is provided,
        the end_date is calculated as start_date + (occurrences-1)
        intervals.
        4. **Occurrence calculation**: When end_date is provided without
        occurrences, the number of occurrences is calculated by counting
        how many instances fit between start_date and end_date.
        
        The occurrences-1 pattern is used because start_date represents
        the first occurrence, so only (occurrences-1) additional
        intervals are needed to reach the final occurrence.
        
        Raises
        ------
        The constructor does not currently validate input parameters,
        but invalid combinations may cause errors in subsequent method
        calls.
        
        Examples
        --------
        Create a non-recurring bill:
        
        .. code-block:: python
        
        bill = Bill(
            bill_id="annual_fee",
            service="Credit Card Annual Fee",
            amount_due=95.00, 
            recurring=False,
            due_date=date(2025, 12, 1)
        )
        
        Create a recurring bill with automatic end_date calculation:
        
        .. code-block:: python
        
        bill = Bill(
            bill_id="rent", 
            service="Monthly Rent",
            amount_due=1200.00,
            recurring=True,
            start_date=date(2025, 1, 1),
            frequency="monthly", 
            interval=1,
            occurrences=12  # end_date calculated automatically
        )
        
        Create a recurring bill with automatic occurrence calculation:
        
        .. code-block:: python
        
        bill = Bill(
            bill_id="quarterly_tax", 
            service="Quarterly Tax Payment",
            amount_due=2500.00,
            recurring=True,
            start_date=date(2025, 1, 15),
            end_date=date(2025, 12, 15),
            frequency="quarterly", 
            interval=1  # occurrences calculated automatically
        )
        """
        
        # Convert amount_due to Decimal for financial precision.
        if not isinstance(amount_due, Decimal):
            amount_due = Decimal(str(amount_due))
        
        # BUSINESS GOAL: Validate core bill properties to prevent
        # downstream errors in financial calculations.
        if not bill_id or not bill_id.strip():
            raise ValueError("bill_id cannot be empty or whitespace")
            
        if not service or not service.strip():
            raise ValueError("service cannot be empty or whitespace")
            
        if amount_due <= 0:
            raise ValueError("amount_due must be positive")
        
        self.bill_id = bill_id
        self.service = service
        self.amount_due = amount_due
        self.recurring = recurring
        self.start_date = start_date
        self.end_date = end_date
        self.frequency = frequency
        self.interval = interval
        self.occurrences = occurrences

        # BUSINESS GOAL: Ensure all bills have consistent, predictable
        # behavior regardless of how users specify them. This
        # standardization prevents edge cases in downstream planning
        # and allocation calculations.

        # 1. Non-recurring bills need consistent date handling. We set
        # start_date = end_date = due_date so that all bill types can
        # use the same date-based methods (instances_in_range, etc.)
        # without special-casing non-recurring logic throughout the
        # system.    
        if recurring == False:
            self.start_date = due_date
            self.end_date = due_date
            self.occurrences = 1
    
        # 2. "Recurring" bills with only 1 occurrence are actually
        # non-recurring bills. Users might mistakenly set this
        # configuration, so we normalize it to prevent confusion in
        # planning calculations. This ensures occurrences=1 always
        # means non-recurring behavior.
        elif (
            recurring == True and end_date is None
            and occurrences is not None and occurrences == 1
        ):
            self.recurring = False
            self.end_date = start_date
            self.frequency = None
            self.interval = None

        # 3. Calculate end_date from occurrences for finite recurring
        # bills.
        # DESIGN CHOICE: We use (occurrences - 1) because start_date
        # represents the first occurrence. To reach the Nth occurrence,
        # we need (N-1) additional intervals from the start. This
        # ensures the bill has exactly the requested number of
        # instances, which is critical for accurate savings
        # calculations and envelope funding.
        elif recurring == True and occurrences is not None and occurrences > 1:
            self.end_date = increment_date(
                reference_date=start_date,
                frequency=frequency,
                interval=interval,
                num_intervals=(occurrences - 1)
            )

        # 4. Calculate occurrences from end_date for user convenience.
        # DESIGN CHOICE: Users often know when a bill series should end
        # (e.g., "lease ends December 31st") but don't want to manually
        # count occurrences. This auto-calculation supports intuitive
        # bill setup while maintaining internal consistency for
        # allocation algorithms.
        elif (
            recurring == True and end_date is not None
            and occurrences is None
        ):
            self.occurrences = self._calculate_occurrences_in_range(
                start_date=start_date,
                end_date=end_date,
                frequency=frequency,
                interval=interval
            )

    def next_instance(
        self,
        reference_date: Optional[datetime.date] = None,
        inclusive: bool = False
    ) -> Optional[BillInstance]:
        """
        Get the next upcoming instance of the bill relative to a
        reference date.
        
        This method finds the first bill instance that is due on or
        after the reference date. It handles the complexities of
        recurring bill schedules including start dates, end dates, and
        frequency calculations.
        
        Parameters
        ----------
        reference_date : datetime.date, optional
            The reference date from which to search for the next bill
            instance. If None, uses today's date. This can be any date,
            not necessarily a due date.
        inclusive : bool, default=False
            Controls whether bills due exactly on the reference date
            are included. If True, includes bills due on the reference
            date as the "next" instance. If False, only returns bills
            due after the reference date.
        
        Returns
        -------
        BillInstance or None
            The next bill instance due on or after the reference date
            (if inclusive=True), or after the reference date (if
            inclusive=False). Returns None if no future instances exist.
        
        Notes
        -----
        The method handles three main scenarios:
        
        1. **Past end date**: Returns None if the reference date exceeds
        the bill's end date.
        2. **Before start date**: Returns the first instance if the
        reference date is before the bill's start date.
        3. **Within active period**: Iterates through the recurring
        schedule to find the first due date based on the inclusive
        parameter.
        
        For recurring bills, the method efficiently steps through due
        dates without generating the entire schedule. It stops at the
        first valid instance that meets the criteria.
        
        Examples
        --------
        Get the next instance including today:
        
        .. code-block:: python
        
           bill = Bill(
               "rent", "Monthly Rent", 1200.00, True, 
               start_date=date(2025, 1, 1), frequency="monthly"
           )
           next_bill = bill.next_instance(
               date(2025, 3, 1), inclusive=True
           )
           print(next_bill.due_date) # 2025-03-01
        
        Get the next instance after today:
        
        .. code-block:: python
        
           next_bill = bill.next_instance(
               date(2025, 3, 1), inclusive=False
           )
           print(next_bill.due_date) # 2025-04-01

        """
        
        # Set default to today's date.
        if reference_date is None:
            reference_date = datetime.date.today()

        # 1. Reference date is beyond the bill's active period.
        # If an end date is set and we're past it, no future instances
        # exist.
        if self.end_date is not None and reference_date > self.end_date:
            return None
        
        # 2. If the reference date is before the bill's first due date,
        # then the next instance is the first occurrence (start_date).
        elif reference_date < self.start_date:
            return BillInstance(
                due_date=self.start_date,
                bill_id=self.bill_id,
                service=self.service,
                amount_due=self.amount_due
            )
        
        # 3. Reference date falls within the bill's active period.
        # Need to find the first due date that occurs on or after
        # reference_date.
        else:

            # Start iterating from the bill's first due date.
            current_date = self.start_date
            
            # Step through the recurring schedule until we find a due
            # date that is on or after our reference date. This gives
            # us the "upcoming" instance relative to the reference
            # date.
            if inclusive == True:
                # Find the first due date >= reference_date.
                while current_date < reference_date:
                    current_date = self._next_due_date(current_date)
            else:
                # Find the first due date > reference_date.
                while current_date <= reference_date:
                    current_date = self._next_due_date(current_date)

            # Verify the found due date doesn't exceed the bill's end
            # date. If it does, no valid future instances exist within
            # the bill's lifetime.
            if self.end_date is not None and current_date > self.end_date:
                return None
            
            # Return the first valid due date on or after the reference
            # date.
            return BillInstance(
                due_date=current_date,
                bill_id=self.bill_id,
                service=self.service,
                amount_due=self.amount_due
            )
        
    def instances_in_range(
        self, start_reference: datetime.date, end_reference: datetime.date
    ) -> list[BillInstance]:
        """
        Generate all bill instances for this bill within a specified
        date range.
        
        This method generates the complete sequence of bill instances
        starting from the bill's start_date, then filters to return
        only those within the specified range. This handles cases
        where start_reference is not itself a due date.
        
        Parameters
        ----------
        start_reference : datetime.date
            The start of the date range (inclusive). Can be any date.
        end_reference : datetime.date
            The end of the date range (inclusive). Can be any date.
            
        Returns
        -------
        list[BillInstance]
            A list of all bill instances within the specified range,
            sorted by due date. Returns an empty list if no bill
            instances fall within the range.
        
        Notes
        -----
        For non-recurring bills, this method returns at most one
        instance if the bill's due date falls within the specified
        range.
        
        For recurring bills, the method generates all instances from the
        bill's start_date until the effective end date (which is the
        minimum of the bill's end_date and the requested end_reference).
        The method respects the bill's occurrence limits and end_date
        constraints.
        
        Examples
        --------
        Get all instances in the first quarter:
        
        .. code-block:: python
        
           bill = Bill(
               "insurance", "Monthly Insurance", 200.00, True,
               start_date=date(2025, 1, 15), frequency="monthly"
           )
           
           instances = bill.instances_in_range(
               date(2025, 1, 1), date(2025, 3, 31)
           )
           
           # Prints: 2025-01-15, 2025-02-15, 2025-03-15.
           for instance in instances:
                print(instance.due_date)
        
        Get instances for a non-recurring bill:
        
        .. code-block:: python
        
           bill = Bill(
               "tax", "Annual Tax Payment", 5000.00, False,
               due_date=date(2025, 4, 15)
           )

           instances = bill.instances_in_range(
               date(2025, 1, 1), date(2025, 12, 31)
           )
           
           print(len(instances)) # 1

        """

        # EARLY EXIT OPTIMIZATION: Non-recurring bills have at most
        # one instance to check against the range.
        if not self.recurring:
            if start_reference <= self.start_date <= end_reference:
                return [
                    BillInstance(
                        due_date=self.start_date,
                        bill_id=self.bill_id,
                        service=self.service,
                        amount_due=self.amount_due
                    )
                ]
            else:
                return []
        
        # If the bill is recurring, then we need to generate all bill
        # instances in the range.

        # EARLY EXIT OPTIMIZATIONS: Avoid unnecessary computation when
        # ranges don't overlap with the bill's active period. These
        # checks prevent wasted iteration and provide clear, predictable
        # behavior.

        # Check 1: Range ends before bill starts - no possible overlap.
        if end_reference < self.start_date:
            return []
        
        # Check 2: Range starts after bill ends - no possible overlap.
        # BUSINESS LOGIC: Respects finite bill series (limited
        # occurrences) and supports accurate cash flow projections by
        # not showing bills that have already concluded.
        if self.end_date is not None and start_reference > self.end_date:
            return []

        # CORE GENERATION LOOP: Build all instances within the effective
        # range.
        # DESIGN PRINCIPLE: Generate from start_date and filter, rather
        # than trying to calculate the first valid date mathematically.
        # This approach handles arbitrary start_reference dates that
        # might not align with actual due dates (e.g., "show me bills
        # from mid-month").

        # Initialize the list of bill instances.
        instances = []

        # Determine the effective start and end dates to begin
        # generating bill instances. We cannot exceed the end date.
        current_due_date = self.start_date

        if self.end_date is not None:
            end_reference = min(end_reference, self.end_date)

        while current_due_date <= end_reference:

            # FILTERING LOGIC: Only include dates within the requested
            # range. This two-step process (generate all, then filter)
            # ensures we handle edge cases where start_reference falls
            # between due dates. BUSINESS VALUE: Supports flexible
            # planning windows that don't need to align with bill
            # cycles.
            if start_reference <= current_due_date <= end_reference:
                instances.append(
                    BillInstance(
                        due_date=current_due_date,
                        bill_id=self.bill_id,
                        service=self.service,
                        amount_due=self.amount_due
                    )
                )
            
            # SEQUENCE ADVANCEMENT: Move to the next due date in the
            # series. We rely on _next_due_date() to handle all
            # calendar complexities (month lengths, leap years, etc.)
            # consistently across the system.
            current_due_date = self._next_due_date(current_due_date)
        
        return instances

    def _next_due_date(self, curr_due_date: datetime.date) -> datetime.date:
        """
        Calculate the next due date after the current due date.
        
        This method follows the bill's frequency and interval to
        determine the subsequent due date in the recurring sequence. The
        method handles calendar complexities such as varying month
        lengths and leap years.
        
        Parameters
        ----------
        curr_due_date : datetime.date
            The current due date. This must be a valid due date for the
            bill.
            
        Returns
        -------
        datetime.date
            The next due date in the sequence.
        
        Notes
        -----
        This is a private method that assumes the input date is a valid
        due date for the bill. The method delegates to the
        increment_date utility function from the date_utils module,
        using the bill's frequency and interval settings.
        
        The method does not validate that curr_due_date is actually a
        valid due date for this bill. Callers are responsible for
        ensuring the input date is correct.
        
        Examples
        --------
        Calculate the next monthly due date:
        
        .. code-block:: python
        
           bill = Bill(
               "rent", "Monthly Rent", 1200.00, True,
               start_date=date(2025, 1, 31), frequency="monthly"
           )

           next_date = bill._next_due_date(date(2025, 1, 31))
           
           print(next_date) # 2025-02-28
        """

        # This function needs code to validate the current due date,
        # otherwise, it's just a function that increments the date by
        # the interval.

        next_due_date = increment_date(
            reference_date=curr_due_date,
            frequency=self.frequency,
            interval=self.interval
        )
        
        return next_due_date

    def _calculate_occurrences_in_range(
        self, start_date: datetime.date, end_date: datetime.date, 
        frequency: str, interval: int
    ) -> int:
        """
        Calculate the number of occurrences between start_date and
        end_date.
        
        This method counts how many bill instances would occur within
        the specified date range, given the frequency and interval
        parameters. The range is inclusive of both start_date and
        end_date.
        
        Parameters
        ----------
        start_date : datetime.date
            The first due date in the sequence.
        end_date : datetime.date  
            The last possible due date in the range.
        frequency : str
            The frequency of recurrence. Valid values are 'daily',
            'weekly', 'monthly', 'quarterly', 'annual'.
        interval : int
            The interval between occurrences.
            
        Returns
        -------
        int
            The number of occurrences that fit within the range.
        
        Notes
        -----
        This is a private method used during bill initialization to
        calculate the number of occurrences when an end_date is provided
        but occurrences is None. The method steps through the recurring
        sequence from start_date, counting each occurrence until it
        exceeds end_date.
        
        The method uses the increment_date utility function to generate
        the sequence, ensuring consistency with other date calculations
        in the system.
        
        Examples
        --------
        Calculate monthly occurrences in a year:
        
        .. code-block:: python
        
           bill = Bill(
               "rent", "Monthly Rent", 1200.00, True,
               start_date=date(2025, 1, 1), frequency="monthly"
           )

           count = bill._calculate_occurrences_in_range(
               date(2025, 1, 1), date(2025, 12, 31), "monthly", 1
           )
           print(count) # 12
        """
        
        # Initialize the number of occurrences.
        occurrences = 0

        # Initialize the current date.
        current_date = start_date
        
        # Count occurrences by stepping through the sequence.
        while current_date <= end_date:

            # Increment the number of occurrences.
            occurrences += 1

            # Get the next due date using existing logic.
            current_date = increment_date(
                reference_date=current_date, frequency=frequency,
                interval=interval, num_intervals=1
            )
        
        return occurrences