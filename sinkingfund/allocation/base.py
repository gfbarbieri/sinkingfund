"""
Allocation Base Module
======================

This module establishes the foundation for all envelope allocation
strategies in the sinking fund system through a consistent abstract
interface.

Allocation is the process of distributing available funds across
different financial obligations (envelopes). This module provides the
framework for implementing various allocation strategies through:

1. Abstract Interface Definition: The BaseAllocator abstract class
defines the contract that all allocation strategies must follow.
2. Strategy Pattern Implementation: Enables multiple interchangeable
allocation algorithms that can be selected at runtime.
3. Consistent API: Ensures all allocation strategies support the same
core operations with consistent parameters.

The allocation process determines:
- How much money goes to each envelope.
- Which bills get fully funded when there's not enough for everything.
- The priority order for distributing limited funds.

By implementing the BaseAllocator interface, specialized allocation
strategies can implement approaches like:
- Cascading (waterfall) allocation based on due dates.
- Equal distribution across all envelopes.
- Proportional allocation based on bill amounts.
- Priority-based allocation using custom rules.
- Debt snowball/avalanche methods.

This abstract foundation enables the flexibility to choose the right
allocation strategy based on your financial goals while maintaining a
consistent interface throughout the system.

"""

########################################################################
## IMPORTS
########################################################################

import datetime

from abc import ABC, abstractmethod

from ..models.envelope import Envelope

########################################################################
## ABSTRACT BASE CLASS
########################################################################

class BaseAllocator(ABC):
    """Abstract base class for allocation strategies."""
    
    @abstractmethod
    def allocate(
            self, envelopes: list[Envelope], balance: float,
            curr_date: datetime.date
        ) -> None:
        """
        Allocate the balance to envelopes according to the strategy.

        Parameters
        ----------
        envelopes: list[Envelope]
            The envelopes to allocate the balance to.
        balance: float
            The current balance to allocate.
        curr_date: datetime.date
            The current date to allocate the balance to.
        """
        pass