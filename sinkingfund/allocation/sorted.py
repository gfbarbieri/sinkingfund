"""
Sorted Allocation Strategies
============================

Cascading (Waterfall) Allocation (Due Date Priority)
----------------------------------------------------

* How it works: Sort bills by due date and allocate funds to the
earliest due bills first.
* Pros: Prioritizes urgent obligations, minimizes late payments.
* Cons: Later bills might get zero allocation.
* Best for: When avoiding late payments is the primary concern.

Debt Snowball (Smallest First)
------------------------------

* How it works: Allocate to the smallest bills first, regardless of due
date.
* Pros: Psychological win of paying off bills completely, reduces number
of bills faster.
* Cons: Ignores due dates, may lead to late payments.
* Best for: Motivational approach, when late fees are minimal.

Custom Allocation
-----------------

* How it works: Pass a custom sort key to the allocator. The sort key
must be a callable that returns bill instances. For example, priority
allocation could be a function that sorts bill instances explicitly by
priority levels (e.g., 1-5), allocating to higher priority bills first.
* Pros: Allows manual prioritization beyond just due dates.
* Cons: Requires manual priority assignment.
* Best for: When some bills are critically important regardless of their
due date.

"""

########################################################################
## IMPORTS
########################################################################

import datetime

from typing import Optional, Protocol, Any

from .base import BaseAllocator
from ..models.bills import BillInstance
from ..models.envelope import Envelope

########################################################################
## TYPES
########################################################################

class SortKey(Protocol):
    """
    Protocol defining the interface for sort key functions.
    
    A sort key function is used by SortedAllocator to determine the
    order in which envelopes are allocated funds. The function receives
    a single envelope instance and must return a comparable value used
    for sorting.
    
    The return value can be:
    - A single comparable value (int, float, string, date, etc.).
    - A tuple of comparables for multi-level sorting.
    
    Examples
    --------

    .. code-block:: python

       # Sort by due date (earliest first)
       def due_date_sort(bill):
           return bill.due_date
    
       # Sort by amount (smallest first)
       def amount_sort(bill):
           return bill.amount_due
    
       # Sort by custom urgency calculation
       def urgency_sort(bill):
            days_until_due = (bill.due_date-datetime.date.today()).days
            if days_until_due <= 7:
                return (1, days_until_due)  # Highest priority tier
            elif days_until_due <= 30:
                return (2, days_until_due)  # Medium priority tier
            else:
                return (3, days_until_due)  # Lowest priority tier
    
       # Sort by service type priority
       def service_priority(bill):
           priorities = {"rent": 1, "utilities": 2, "subscription": 3}
        
           for service, priority in priorities.items():
               if service.lower() in bill.service.lower():
                   return priority
           return 99  # Default low priority

    """
    
    def __call__(self, bill: BillInstance, **kwargs: Any) -> Any:
        """
        Extract a sort key from a bill instance.
        
        Parameters
        ----------
        bill: BillInstance
            A bill instance from which to extract a sort key.
        **kwargs: Any
            Additional keyword arguments needed by the function.

        Returns
        -------
        Any
            A comparable value or tuple of values used for sorting.
            Lower values will be allocated funds first (unless
            reverse=True).

        Notes
        -----
        The sort key function should be able to handle the bill instance
        and any additional keyword arguments. The function must return a
        comparable value or tuple of values used for sorting
        (multi-level sorting). For example, the function should return
        a value or tuple of values that are comparable in that they
        support the <, <=, >, >=, ==, != operators. This includes
        numbers (int, float), strings, dates, and other comparable
        types.
        """
        ...

########################################################################
## SORT KEYS
########################################################################

# Map of method names to their sort functions. The sort key
# is a function that takes an bill instance and returns a value
# that will be used to sort the envelopes.
SORT_KEYS = {
    "cascade": lambda e: e.due_date,
    "debt_snowball": lambda e: e.amount_due
}

########################################################################
## SORTED ALLOCATOR
########################################################################

class SortedAllocator(BaseAllocator):
    """
    A sorted allocator is an allocator that sorts the envelopes by a
    given key and then allocates the balance to the envelopes in the
    sorted order.

    Parameters
    ----------
    sort_key: Optional[Callable]
        Function to extract sort key from envelope.
        Default: Sort by due date (lambda e: e.bill.due_date)
    reverse: bool
        Whether to reverse the sort order.
        Default: False

    Attributes
    ----------
    sort_key: SortKey
        Function to extract sort key from envelope.
        Default: Sort by due date (lambda e: e.due_date)
    reverse: bool
        Whether to reverse the sort order.
        Default: False
    """

    def __init__(
            self, sort_key: str | Optional[SortKey] = None,
            reverse: bool = False
        ) -> None:
        """
        Initialize the sorted allocator.

        Parameters
        ----------
        sort_key: Optional[SortKey]
            Function to extract sort key from envelope.
            Default: Sort by due date (lambda e: e.bill.due_date)
        reverse: bool
            Whether to reverse the sort order.
            Default: False
        """

        # Set the sort key. If the sort key is a string, then it is a
        # method name and we will use the corresponding sort function.
        # Otherwise, the sort key is a function and we will use it
        # directly.
        if isinstance(sort_key, str):
            self.sort_func = SORT_KEYS.get(sort_key)
        else:
            self.sort_func = sort_key

        # Set the reverse flag.
        self.reverse = reverse

    def allocate(
            self, envelopes: list[Envelope], balance: float,
            curr_date: datetime.date, return_last: bool = False,
            **kwargs: Any
        ) -> list[Envelope]:
        """
        Allocate the balance to the envelopes. Updates the envelopes
        directly with the allocated amount and the remaining amount
        needed.

        Parameters
        ----------
        envelopes: list[Envelope]
            The envelopes to allocate the balance to.
        balance: float
            The current balance to allocate.
        curr_date: datetime.date
            The current date to allocate the balance to.
        return_last: bool
            Whether to return the last instance of the bill.
            Default: False
        **kwargs: Any
            Additional keyword arguments needed by the sort key
            function.
        """

        # For each envelope, get the next instance of the bill. If the
        # return last flag is True, then we will get the last instance
        # of the bill. Otherwise, we will get the next instance of the
        # bill. If the return true is False, then past-due bills return
        # None.
        bill_instances = []

        for envelope in envelopes:
            bill = envelope.bill.next_instance(
                curr_date, return_last=return_last
            )

            if bill is not None:
                bill_instances.append(bill)

        # Sort the envelopes by the sort key. This cannot have None
        # values or it will fail.
        sorted_bills = sorted(
            bill_instances,
            key=lambda x: self.sort_func(x, **kwargs),
            reverse=self.reverse
        )

        # Allocate the balance to the envelopes.
        # If the current date is past the bill's due date, then we are
        # not going to allocate existing balance to the bill. Instead,
        # we are going to assume the bill is already paid and the
        # balance reflects the paid bills. The balance is the balance
        # at the start date, or the expected balance at the start date.
        # If this is not true, then it is up to the user to adjust the
        # balance to reflect the expected balance at the start date.
        #
        # Otherwise, allocate the balance to the bill and calculate
        # the remaining amount needed. The amount allocated is the
        # minimum of the balance and the amount due, which is equal to
        # the amount due if the balance is greater than the amount due.
        # The remaining amount needed is the amount due minus the
        # amount allocated.
        for bill in sorted_bills:

            if curr_date > bill.due_date:
                allocate = 0
                remaining = 0
            else:
                allocate = min(balance, bill.amount_due)
                remaining = bill.amount_due - allocate

            # Since the bills have been sorted, we will use the bill ID
            # to find the envelope.
            envelope = next(
                e for e in envelopes if e.bill.bill_id == bill.bill_id
            )

            # Assign the allocations and remaining needed.
            envelope.allocated = allocate
            envelope.remaining = remaining

            # Update the balance for the next bill.
            balance -= allocate