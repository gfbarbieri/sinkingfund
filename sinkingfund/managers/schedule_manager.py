"""
Schedule Manager
================

The ScheduleManager coordinates the creation and application of
contribution schedules for sinking fund envelopes using various
scheduling algorithms.

Core Responsibilities
--------------------

The ScheduleManager serves as the orchestration layer between envelope
management and scheduling algorithms. It:

#. **Strategy Selection**: Dynamically selects the appropriate
   scheduling algorithm based on user preferences or optimization
   criteria.

#. **Schedule Creation**: Delegates the actual cash flow generation
   to specialized scheduler implementations.

#. **Envelope Integration**: Ensures generated schedules are properly
   applied to the corresponding envelopes.

Supported Scheduling Strategies
------------------------------

* **Independent Scheduler**: Creates even contribution schedules for
  each bill independently, optimizing for predictable per-bill
  contributions.

* **LP Scheduler**: Uses linear programming to create globally
  optimized schedules that minimize variance in total daily
  contributions across all bills.

Architectural Design
-------------------

The ScheduleManager follows the Strategy pattern, allowing different
scheduling algorithms to be plugged in without changing the core
management logic. This design supports:

* Easy addition of new scheduling strategies
* Runtime algorithm selection based on user preferences
* Consistent interface regardless of underlying optimization approach
* Clear separation between scheduling logic and envelope management

Example Usage
------------

.. code-block:: python

   from sinkingfund.managers.schedule_manager import ScheduleManager
   
   # Initialize with independent scheduling strategy
   manager = ScheduleManager(strategy="independent_scheduler")
   
   # Create schedules for all envelopes
   manager.create_schedules(envelopes=my_envelopes)

Notes
-----

The ScheduleManager modifies envelopes in-place by setting their
schedule attributes. This design choice optimizes for memory efficiency
and maintains clear object relationships, though it requires careful
handling in concurrent scenarios.
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

from ..models import Envelope, CashFlowSchedule
from ..schedules import IndependentScheduler

########################################################################
## CONSTANTS
########################################################################

# DESIGN CHOICE: Registry pattern allows dynamic strategy selection
# and easy extension with new scheduling algorithms.
SCHEDULE_STRATEGIES = {
    "independent_scheduler": IndependentScheduler,
    # Future strategies can be added here:
    # "lp_scheduler": LPScheduler,
    # "cascade_scheduler": CascadeScheduler,
}

########################################################################
## SCHEDULE MANAGER
########################################################################

class ScheduleManager:
    """
    Coordinates scheduling strategy selection and schedule creation for
    sinking fund envelopes.
    
    The ScheduleManager acts as a facade that abstracts the complexity
    of different scheduling algorithms while providing a consistent
    interface for envelope schedule management.
    
    This class implements the Strategy pattern, delegating actual
    schedule creation to specialized scheduler implementations while
    handling strategy selection, validation, and envelope integration.
    
    Attributes
    ----------
    scheduler : BaseScheduler
        The active scheduling strategy instance responsible for
        generating cash flow schedules.
    
    Example
    -------
    
    .. code-block:: python
    
       # Create manager with independent scheduling.
       manager = ScheduleManager(strategy="independent_scheduler")
       
       # Generate schedules for all envelopes.
       manager.create_schedules(envelopes)
    
    Notes
    -----
    
    The manager modifies envelopes in-place by setting their schedule
    attributes. This approach maintains object relationships and
    optimizes memory usage, but requires careful handling in
    multi-threaded environments.
    """

    def __init__(self) -> None:
        """
        Initialize the ScheduleManager with a specific scheduling
        strategy.
        
        Parameters
        ----------
        strategy : str
            The name of the scheduling strategy to use. Must be a key
            in SCHEDULE_STRATEGIES. Currently supported strategies:
            
            * "independent_scheduler": Even contributions per bill
            * Additional strategies can be added to the registry
            
        **kwargs
            Additional keyword arguments passed to the scheduler
            constructor. These vary by strategy type.
            
        Raises
        ------
        KeyError
            If the specified strategy is not found in the registry.
        
        Notes
        -----
        
        The strategy pattern allows runtime selection of scheduling
        algorithms without changing client code. New strategies can
        be added by registering them in SCHEDULE_STRATEGIES.
        """
        self.scheduler = None

    def set_scheduler(
        self, strategy: str="independent_scheduler", **kwargs
    ) -> None:
        """
        Set the scheduling strategy for the ScheduleManager.

        Parameters
        ----------
        strategy : str
            The name of the scheduling strategy to use. Must be a key
            in SCHEDULE_STRATEGIES.
        **kwargs
            Additional keyword arguments passed to the scheduler
            constructor. These vary by strategy type.
        """

        # BUSINESS GOAL: Enable flexible scheduling approaches to meet
        # different user preferences and optimization objectives.
        if strategy not in SCHEDULE_STRATEGIES:
            available = ", ".join(SCHEDULE_STRATEGIES.keys())
            raise KeyError(
                f"Unknown scheduling strategy '{strategy}'. "
                f"Available strategies: {available}"
            )
        
        # DESIGN CHOICE: Instantiate the strategy immediately to catch
        # configuration errors early rather than deferring to schedule
        # creation time.
        try:
            self.scheduler = SCHEDULE_STRATEGIES[strategy](**kwargs)
        except TypeError as e:
            raise TypeError(
                f"Invalid parameters for '{strategy}' strategy: {e}"
            ) from e

    def create_schedules(
        self, envelopes: list[Envelope], **kwargs
    ) -> dict[Envelope, CashFlowSchedule]:
        """
        Create contribution schedules for the provided envelopes using
        the configured scheduling strategy.
        
        This method delegates the actual schedule creation to the
        selected scheduler implementation while providing validation
        and error handling at the management layer.
        
        Parameters
        ----------
        envelopes : list[Envelope]
            The envelopes for which to create contribution schedules.
            Each envelope should have a valid bill instance and
            contribution parameters defined.
            
        **kwargs
            Additional arguments passed to the scheduler's schedule
            method. These vary by scheduler type but commonly include
            timing and optimization parameters.
            
        Returns
        -------
        dict[Envelope, CashFlowSchedule]
            A dictionary mapping each envelope to its corresponding
            schedule.
            
        Raises
        ------
        ValueError
            If envelopes are invalid or scheduling parameters are
            inconsistent.
        """

        # BUSINESS GOAL: Validate that all envelopes are of type
        # Envelope.
        if not all(isinstance(envelope, Envelope) for envelope in envelopes):
            raise ValueError(
                "All elements must be type Envelope. Got types: "
                f"{[type(envelope) for envelope in envelopes]}."
            )
        
        return self.scheduler.schedule(envelopes, **kwargs)