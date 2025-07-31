"""
Proportional Allocation
=======================

Proportional Weighting (Amount-Based)
-------------------------------------

* How it works: Allocate proportionally to the bill amount.
* Formula: allocation = balance * (bill_amount / total_all_bills).
* Pros: Larger bills get more funding, simple to explain.
* Cons: Ignores due dates entirely.
* Best for: When relative bill size is the main concern.

Equal Distribution
------------------

* How it works: Divide available balance equally among all bills.
* Pros: Simple, fair, every bill gets something.
* Cons: Doesn't consider urgency or bill size.
* Best for: When all bills have similar importance/urgency.

Urgency Weighting (Due Date Priority)
-------------------------------------

* How it works: Allocate based on a formula that considers both amount
  and due date.
* Formula: weight = amount_due / (due_date - current_date)
* Pros: Balances urgency and size, smoother allocations.
* Cons: Complex to explain, may underfund urgent small bills.
* Best for: Balanced approach considering both size and timing.

Zero Weighting
--------------

* How it works: Set all weights to zero.
* Pros: Simple, fair, every bill gets nothing.
* Cons: Ignores all bills.
* Best for: When all bills are unimportant, or when the user wants to
  manually allocate bills.

Custom Weighting
----------------

* How it works: Use a custom function to calculate the weights for
  each bill.
* Pros: Can be used to implement any weighting logic.
* Cons: Must be manually implemented.
* Best for: When the user wants to implement a custom weighting logic.

"""

########################################################################
## IMPORTS
########################################################################

import datetime

from typing import Protocol

from .base import BaseAllocator
from ..models.bills import BillInstance
from ..models.envelope import Envelope

########################################################################
## TYPES
########################################################################

class WeightFunction(Protocol):
    """
    Protocol defining the interface for weight calculation functions.
    
    A weight function must:
    1. Accept a list of BillInstance objects and a datetime.date.
    2. Return a list of float values (weights).
    3. Return weights in the same order as the input bill instances.
    """

    def __call__(
            self, bill_instances: list[BillInstance], curr_date: datetime.date
        ) -> list[float]:
        """
        Calculate weights for a list of bill instances.
        
        Parameters
        ----------
        bill_instances: list[BillInstance]
            List of bill instances to calculate weights for.
        curr_date: datetime.date
            Current date for calculating urgency-based weights.
            
        Returns
        -------
        list[float]
            List of weights, one per bill instance in the same order.
        """
        ...  # This is a placeholder for the actual implementation.

########################################################################
## CONCRETE IMPLEMENTATIONS
########################################################################

class ProportionalAllocator(BaseAllocator):
    """
    Allocates funds based on weighted proportions of bill instances.
    """
    
    def __init__(self, method: str | WeightFunction):
        """
        Initialize the proportional allocator.

        Parameters
        ----------
        method: str | WeightFunction
            The method to use for allocation.
        """

        # Map of method names to their weight functions.
        self.weight_funcs = {
            "urgency": self._urgency_weights,
            "equal": self._equal_weights,
            "proportional": self._proportional_weights,
            "zero": self._zero_weights
        }

        # Set the allocation function.
        if isinstance(method, str):
            self.weight_func = self.weight_funcs.get(method)
        else:
            self.weight_func = method
    
    def allocate(
            self, envelopes: list[Envelope], balance: float,
            curr_date: datetime.date
        ) -> None:
        """
        Allocate balance to envelopes based on calculated weights.

        Parameters
        ----------
        envelopes: list[Envelope]
            The envelopes to allocate to.
        balance: float
            The balance to allocate.
        curr_date: datetime.date
            The current date.
        """

        # For each envelope, get the next instance of the bill.
        bill_instances = [
            envelope.bill.next_instance(curr_date) for envelope in envelopes
        ]

        # Calculate the weights for each envelope.
        weights = self.weight_func(bill_instances, curr_date)

        # Calculate the shares of the balance for each envelope.
        shares = [weight / sum(weights) for weight in weights]

        # Allocate funds proportionally to shares.
        allocations = [balance * share for share in shares]

        # Set the allocations for each envelope.
        for envelope, allocation in zip(envelopes, allocations):
            envelope.allocated = allocation
            envelope.remaining = envelope.bill.amount_due - envelope.allocated
        
    def _urgency_weights(
            self, bill_instances: list[BillInstance], curr_date: datetime.date
        ) -> list[float]:
        """
        Weight based on amount and urgency (less days = higher weight).

        weight = amount_due / (due_date - current_date)

        Parameters
        ----------
        bill_instances: list[BillInstance]
            The bill instances for which to calculate the weights.
        curr_date: datetime.date
            The current date.
        """

        # Calculate the weights for each envelope.
        weights = []

        for bill in bill_instances:

            # Calculate the number of days between the due date and the
            # current date.
            days = (bill.due_date - curr_date).days

            # If the bill is due before the current date, then the bill
            # is in the past and we will treat it as if it has already
            # been paid, thus the weight is zero.
            if days < 0:
                weight = 0
            elif days == 0:
                weight = bill.amount_due
            else:
                weight = bill.amount_due / days

            # Append the weight to the list.
            weights.append(weight)
        
        return weights
        
    def _equal_weights(
            self, bill_instances: list[BillInstance], curr_date: datetime.date
        ) -> list[float]:
        """
        Equal weight for all bills.

        Parameters
        ----------
        bill_instances: list[BillInstance]
            The bill instances to calculate the weight for.
        """

        # Calculate the weights for each envelope as 1.0.
        weights = [1.0] * len(bill_instances)

        return weights
        
    def _proportional_weights(
            self, bill_instances: list[BillInstance], curr_date: datetime.date
        ) -> list[float]:
        """
        Weight based solely on bill amount.

        weight = bill_amount / total_all_bills

        Parameters
        ----------
        bill_instances: list[BillInstance]
            The bill instances to calculate the weight for.
        """

        # Calculate the total amount due for all envelopes.
        total_amount_due = sum(bill.amount_due for bill in bill_instances)

        # Calculate the weights for each envelope.
        weights = [
            bill.amount_due / total_amount_due for bill in bill_instances
        ]

        return weights
        
    def _zero_weights(
            self, bill_instances: list[BillInstance], curr_date: datetime.date
        ) -> list[float]:
        """
        Set all weights to zero.

        Parameters
        ----------
        bill_instances: list[BillInstance]
            The bill instances to calculate the weight for.
        """

        # Calculate the weights for each envelope as 0.0.
        weights = [0.0] * len(bill_instances)

        return weights