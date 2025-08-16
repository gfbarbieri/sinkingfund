"""
Allocation Manager
==================

The AllocationManager provides sophisticated fund allocation
orchestration for envelope-based sinking fund systems. It implements
the strategy pattern to enable flexible allocation algorithms while
maintaining a consistent interface for fund distribution across
payment envelopes.

Core Abstractions
-----------------

**Strategy Pattern**: The manager delegates allocation logic to
pluggable strategy implementations, enabling different allocation
approaches (sorted priority, proportional distribution, custom
algorithms) without modifying core allocation coordination logic.

**Allocation Coordination**: Centralized management of fund distribution
processes with validation, error handling, and consistent state
management across different allocation strategies.

**Envelope Integration**: Seamless integration with envelope collections
to modify funding levels while maintaining envelope integrity and
business rule compliance.

Key Features
------------

- **Pluggable allocation strategies** with automatic strategy selection
  and initialization based on configuration.
- **Unified allocation interface** that abstracts strategy-specific
  implementation details from client code.
- **Flexible parameter passing** supporting strategy-specific options
  and configuration through keyword arguments.
- **Envelope-aware processing** with proper handling of envelope
  collections and funding state modifications.
- **Strategy registry** with extensible design for adding custom
  allocation algorithms.

Available Strategies
--------------------

- **sorted**: Priority-based allocation using envelope sorting criteria.
- **proportional**: Distribution based on proportional funding needs.

Examples
--------

.. code-block:: python

   from decimal import Decimal
   from sinkingfund.managers import AllocationManager
   from sinkingfund.models import Envelope

   # Create manager with sorted allocation strategy.
   manager = AllocationManager(strategy="sorted")
   
   # Allocate funds to envelope collection.
   available_funds = Decimal("1000.00")
   manager.allocate(
       envelopes=envelope_list,
       balance=available_funds
   )
   
   # Create manager with proportional strategy and options.
   prop_manager = AllocationManager(
       strategy="proportional",
       min_allocation=Decimal("10.00")
   )
   prop_manager.allocate(
       envelopes=envelope_list,
       balance=available_funds,
       target_months=3
   )
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

from decimal import Decimal
from typing import Any

from ..models import Envelope
from ..allocation.sorted import SortedAllocator
from ..allocation.proportional import ProportionalAllocator

########################################################################
## CONSTANTS
########################################################################

# DESIGN CHOICE: Strategy registry enables extensible allocation
# algorithms without modifying core manager implementation
ALLOCATION_STRATEGIES: dict[str, type] = {
    "sorted": SortedAllocator,
    "proportional": ProportionalAllocator
}

########################################################################
## ALLOCATION MANAGER
########################################################################

class AllocationManager:
    """
    Orchestrate fund allocation using pluggable strategy
    implementations.

    The AllocationManager implements the strategy pattern to provide
    flexible fund distribution across envelope collections. It maintains
    a clean separation between allocation coordination and strategy-
    specific logic, enabling diverse allocation approaches through a
    unified interface.

    Core Responsibilities
    ---------------------

    - **Strategy Management**: Initialize and maintain allocation
    strategy instances with proper configuration and parameter handling.
    - **Allocation Coordination**: Provide unified interface for fund
    distribution while delegating algorithm specifics to strategies.
    - **Parameter Routing**: Pass strategy-specific options and
    configuration through to underlying allocation implementations.
    - **Error Handling**: Validate inputs and provide clear feedback
    for invalid strategies or allocation parameters.

    Design Patterns
    ---------------

    - **Strategy Pattern**: Encapsulate allocation algorithms in
    interchangeable strategy objects with consistent interfaces.
    - **Delegation Pattern**: Forward allocation operations to strategy
    implementations while maintaining management responsibilities.
    - **Registry Pattern**: Use strategy lookup table for flexible
    algorithm selection and extensibility.

    Attributes
    ----------
    allocator : BaseAllocator
        The strategy instance responsible for actual fund allocation
        logic, initialized based on strategy name and configuration.

    Notes
    -----
    The manager validates strategy names at initialization and provides
    clear error messages for unsupported strategies. Strategy-specific
    parameters are passed through to the underlying allocator during
    both initialization and allocation operations.

    Examples
    --------
    .. code-block:: python

       # Create manager with strategy and configuration.
       manager = AllocationManager(
           strategy="sorted",
           reverse=True
       )
       
       # Perform allocation with runtime parameters.
       manager.allocate(
           envelopes=envelope_collection,
           balance=Decimal("1000.00"),
           max_allocation=Decimal("500.00")
       )
    """

    def __init__(self, strategy: str, **kwargs: Any) -> None:
        """
        Initialize allocation manager with specified strategy.

        Creates a new manager instance configured with the specified
        allocation strategy and any strategy-specific parameters.
        Validates strategy availability and initializes the underlying
        allocator implementation.

        Parameters
        ----------
        strategy : str
            Name of the allocation strategy to use. Must be a key in
            the ALLOCATION_STRATEGIES registry. Currently supported:
            
            - **"sorted"**: Priority-based allocation.
            - **"proportional"**: Proportional distribution.
            
        **kwargs : Any
            Strategy-specific initialization parameters passed through
            to the underlying allocator constructor. Refer to individual
            strategy documentation for supported parameters.

        Raises
        ------
        KeyError
            If the specified strategy is not available in the registry.
        TypeError
            If strategy-specific parameters are invalid for the chosen
            allocator implementation.

        Notes
        -----
        The manager validates strategy availability immediately at
        initialization rather than deferring to allocation time. This
        provides early feedback for configuration errors.

        Strategy-specific parameters are validated by the underlying
        allocator constructor, ensuring proper parameter handling
        without duplicating validation logic.

        Examples
        --------
        .. code-block:: python

           # Initialize with basic strategy
           manager = AllocationManager(strategy="sorted")
           
           # Initialize with strategy configuration
           manager = AllocationManager(
               strategy="proportional",
               min_allocation=Decimal("10.00")
           )
        """

        # BUSINESS GOAL: Validate strategy availability early to provide
        # clear feedback on configuration errors.
        if strategy not in ALLOCATION_STRATEGIES:
            
            available_strategies = list(ALLOCATION_STRATEGIES.keys())

            raise KeyError(
                f"Unknown allocation strategy '{strategy}'. "
                f"Available strategies: {available_strategies}"
            )

        # DESIGN CHOICE: Delegate strategy initialization to enable
        # strategy-specific parameter validation and configuration.
        try:
            self.allocator = ALLOCATION_STRATEGIES[strategy](**kwargs)
        except TypeError as e:
            raise TypeError(
                f"Invalid parameters for '{strategy}' strategy: {e}"
            ) from e

    def allocate(
        self, envelopes: list[Envelope], balance: int, **kwargs
    ) -> None:
        """
        Distribute available funds across envelope collection using
        strategy.

        Delegates fund allocation to the configured strategy
        implementation while providing validation, error handling, and
        consistent interface for all allocation operations. Modifies
        envelope funding levels in-place based on strategy-specific
        allocation logic.

        Parameters
        ----------
        envelopes : list[Envelope]
            Collection of envelopes to receive fund allocations.
            Envelopes are modified in-place with updated funding levels
            based on allocation strategy results.
        balance : int
            Total amount of funds available for allocation across all
            envelopes. Must be non-negative.
        **kwargs : Any
            Strategy-specific allocation parameters passed through to
            the underlying allocator. Supported parameters vary by
            strategy:
            
            - **sorted**: ``reverse``, ``max_allocation``.
            - **proportional**: ``target_months``, ``min_allocation``.
            
            Refer to individual strategy documentation for complete
            parameter specifications.

        Raises
        ------
        ValueError
            If balance is negative or if envelope collection contains
            invalid envelope states.
        TypeError
            If strategy-specific parameters are invalid or incompatible
            with the chosen allocation algorithm.

        Notes
        -----
        **Side Effects**: This method modifies envelope funding levels
        in-place. The original envelope collection is altered by the
        allocation process.
        
        **Strategy Delegation**: The manager performs minimal validation
        and delegates core allocation logic to the strategy
        implementation. This enables strategy-specific optimizations
        while maintaining consistent error handling.

        **Parameter Routing**: Runtime parameters are passed directly to
        the strategy, enabling flexible allocation behavior without
        requiring manager modifications for new strategy features.

        Examples
        --------
        .. code-block:: python

           # Basic allocation with default strategy behavior.
           manager.allocate(
               envelopes=envelope_list,
               balance=Decimal("1000.00")
           )
        """

        # BUSINESS GOAL: Validate input parameters to provide clear
        # error feedback before delegation to strategy.
        if balance < 0:
            raise ValueError(
                f"Balance must be non-negative, got {balance}"
            )
        
        # EARLY EXIT OPTIMIZATION: Skip allocation if no funds
        # available.
        if balance == 0:
            return
        
        # EARLY EXIT OPTIMIZATION: Skip allocation if no envelopes
        # provided.
        if not envelopes:
            return

        # SIDE EFFECTS: Delegate to strategy implementation which will
        # modify envelope funding levels in-place.
        try:
            self.allocator.allocate(envelopes, balance, **kwargs)
        except Exception as e:
            raise type(e)(
                f"Allocation failed with '{type(self.allocator).__name__}' "
                f"strategy: {e}"
            ) from e