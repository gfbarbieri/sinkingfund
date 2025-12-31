Schedules Package
=================

Scheduling components generate optimized contribution schedules for envelopes
based on available funds, timing constraints, and planning objectives.

Base Scheduler
--------------

Abstract base class defining the scheduler interface.

.. automodule:: sinkingfund.schedules.base
   :members:
   :show-inheritance:
   :exclude-members: ScheduleResult

.. autoclass:: sinkingfund.schedules.base.ScheduleResult
   :no-index:
   :exclude-members: schedules, metadata

Independent Scheduler
---------------------

Generates independent contribution schedules for individual envelopes.

.. automodule:: sinkingfund.schedules.indep_scheduler
   :members:
   :show-inheritance:

.. autoclass:: sinkingfund.schedules.indep_scheduler.IndependentScheduler
   :no-index:
