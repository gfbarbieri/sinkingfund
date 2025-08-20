"""
Allocation Base Module
======================

This module establishes the foundation for all envelope allocation
strategies in the sinking fund system through a consistent abstract
interface.

Allocation is the process of distributing available funds across
different financial obligations (envelopes). This module provides the
framework for implementing various allocation strategies through:

#. Abstract Interface Definition: The BaseAllocator abstract class
   defines the contract that all allocation strategies must follow.
#. Strategy Pattern Implementation: Enables multiple interchangeable
   allocation algorithms that can be selected at runtime.
#. Consistent API: Ensures all allocation strategies support the same
   core operations with consistent parameters.

The allocation process determines:

* How much money goes to each envelope.
* Which bills get fully funded when there's not enough for everything.
* The priority order for distributing limited funds.

By implementing the BaseAllocator interface, specialized allocation
strategies can implement approaches like:

* Cascading (waterfall) allocation based on due dates.
* Equal distribution across all envelopes.
* Proportional allocation based on bill amounts.
* Priority-based allocation using custom rules.
* Debt snowball/avalanche methods.

This abstract foundation enables the flexibility to choose the right
allocation strategy based on your financial goals while maintaining a
consistent interface throughout the system.

"""

########################################################################
## IMPORTS
########################################################################

import datetime
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from abc import ABC, abstractmethod

from ..models.envelope import Envelope

########################################################################
## ALLOCATION RESULT DATA CLASS
########################################################################

@dataclass(frozen=True)
class AllocationResult:
    """
    Results of an allocation strategy execution.

    Attributes
    ----------
    envelopes: dict[Envelope, Decimal]
        The allocations for each envelope.
    strategy: dict[str, Any]
        Additional metadata about the allocation strategy.
    """
    
    envelopes: dict[Envelope, Decimal]
    metadata: dict[str, Any]

########################################################################
## ABSTRACT BASE ALLOCATOR CLASS
########################################################################

class BaseAllocator(ABC):
    """
    Abstract base class for allocation strategies.

    This class defines the interface that all allocation strategies must
    implement.
    """
    
    @abstractmethod
    def allocate(
            self, envelopes: list[Envelope], balance: Decimal,
            curr_date: datetime.date
        ) -> AllocationResult:
        """
        Allocate the balance to envelopes according to the strategy.

        Parameters
        ----------
        envelopes: list[Envelope]
            The envelopes to allocate the balance to.
        balance: Decimal
            The current balance to allocate.
        curr_date: datetime.date
            The current date to allocate the balance to.
        """
        pass