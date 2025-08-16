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

from typing import Any, Protocol

from .base import BaseAllocator

from ..models import BillInstance
from ..models import Envelope

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
    "cascade": lambda e: e.bill_instance.due_date,
    "debt_snowball": lambda e: e.bill_instance.amount_due
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

    def __init__(self, sort_key: str | SortKey, reverse: bool=False) -> None:
        """
        Initialize the sorted allocator.

        Parameters
        ----------
        sort_key: str | SortKey
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
            self, envelopes: list[Envelope], balance: float, **kwargs: Any
        ) -> None:
        """
        Allocate the balance to the envelopes. Updates the envelopes
        in place with the allocated amount and the remaining amount
        needed.

        Parameters
        ----------
        envelopes: list[Envelope]
            The envelopes to allocate the balance to.
        balance: float
            The current balance to allocate.
        **kwargs: Any
            Additional keyword arguments needed by the sort key
            function.
        """

        # Sort the envelopes by the sort key. This cannot have None
        # values or it will fail. The envelopes in the new sorted list
        # are references to the original envelopes.
        sorted_envelopes = sorted(
            envelopes,
            key=lambda x: self.sort_func(x, **kwargs),
            reverse=self.reverse
        )

        # Allocate the balance to the envelopes in the sorted order.
        # This will allocate the balance to the envelopes in the order
        # they are sorted. Envelopes are edited in place.
        for envelope in sorted_envelopes:

            # Calculate the amount to allocate.
            allocation = min(balance, envelope.bill_instance.amount_due)

            # Assign the allocations.
            envelope.initial_allocation = allocation

            # Update the balance for the next envelope.
            balance -= allocation