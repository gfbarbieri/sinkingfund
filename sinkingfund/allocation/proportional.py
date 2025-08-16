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

from typing import Any, Protocol

from .base import BaseAllocator
from ..models.envelope import Envelope

########################################################################
## TYPES
########################################################################

class WeightFunction(Protocol):
    """
    Protocol defining the interface for weight calculation functions.
    
    A weight function must:
    1. Accept a list of Envelope objects and a datetime.date.
    2. Return a list of float values (weights).
    3. Return weights in the same order as the input envelopes.
    """

    def __call__(
            self, envelopes: list[Envelope], **kwargs: Any
        ) -> list[float]:
        """
        Calculate weights for a list of envelopes.
        
        Parameters
        ----------
        envelopes: list[Envelope]
            List of envelopes to calculate weights for.
            
        Returns
        -------
        list[float]
            List of weights, one per envelope in the same order.
        """
        ...  # This is a placeholder for the actual implementation.

########################################################################
## CONCRETE IMPLEMENTATIONS
########################################################################

class ProportionalAllocator(BaseAllocator):
    """
    Allocates funds based on weighted proportions of bill instances.
    """
    
    def __init__(self, method: str | WeightFunction) -> None:
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
            self, envelopes: list[Envelope], balance: float, **kwargs: Any
        ) -> None:
        """
        Allocate balance to envelopes based on calculated weights.

        Parameters
        ----------
        envelopes: list[Envelope]
            The envelopes to allocate to.
        balance: float
            The balance to allocate.
        """

        # Calculate the weights for each envelope.
        weights = self.weight_func(envelopes, **kwargs)

        # Calculate the shares of the balance for each envelope.
        shares = [weight / sum(weights) for weight in weights]

        # Allocate funds proportionally to shares.
        allocations = [balance * share for share in shares]

        # Set the allocations for each envelope.
        for envelope, allocation in zip(envelopes, allocations):
            envelope.initial_allocation = allocation
        
    def _urgency_weights(
            self, envelopes: list[Envelope], curr_date: datetime.date
        ) -> list[float]:
        """
        Weight based on amount and urgency (less days = higher weight).

        weight = amount_due / (due_date - current_date)

        Parameters
        ----------
        envelopes: list[Envelope]
            The envelopes for which to calculate the weights.
        curr_date: datetime.date
            The current date.
        """

        # Calculate the weights for each envelope.
        weights = []

        for envelope in envelopes:

            # Calculate the number of days between the due date and the
            # current date.
            days = (envelope.bill_instance.due_date - curr_date).days

            # If the bill is due before the current date, then the bill
            # is in the past and we will treat it as if it has already
            # been paid, thus the weight is zero.
            if days < 0:
                weight = 0
            elif days == 0:
                weight = envelope.bill_instance.amount_due
            else:
                weight = envelope.bill_instance.amount_due / days

            # Append the weight to the list.
            weights.append(weight)
        
        return weights
        
    def _equal_weights(
            self, envelopes: list[Envelope]
        ) -> list[float]:
        """
        Equal weight for all bills.

        Parameters
        ----------
        envelopes: list[Envelope]
            The envelopes to calculate the weight for.
        """

        # Calculate the weights for each envelope as 1.0.
        weights = [1.0] * len(envelopes)

        return weights
        
    def _proportional_weights(
            self, envelopes: list[Envelope]
        ) -> list[float]:
        """
        Weight based solely on bill amount.

        weight = bill_amount / total_all_bills

        Parameters
        ----------
        envelopes: list[Envelope]
            The envelopes to calculate the weight for.
        """

        # Calculate the total amount due for all envelopes.
        total_amount_due = sum(
            envelope.bill_instance.amount_due for envelope in envelopes
        )

        # Calculate the weights for each envelope.
        weights = [
            envelope.bill_instance.amount_due / total_amount_due
            for envelope in envelopes
        ]

        return weights
        
    def _zero_weights(
            self, envelopes: list[Envelope]
        ) -> list[float]:
        """
        Set all weights to zero.

        Parameters
        ----------
        envelopes: list[Envelope]
            The envelopes to calculate the weight for.
        """

        # Calculate the weights for each envelope as 0.0.
        weights = [0.0] * len(envelopes)

        return weights