Managers Package
================

.. note::
   Manager classes are **internal implementation details** of the
   :class:`~sinkingfund.models.SinkingFund` class. Most users should interact
   with the system through the SinkingFund API, which provides a unified
   interface for all operations. These classes are documented here for
   advanced users who need to understand the internal architecture or extend
   the system.

Manager classes provide high-level orchestration and coordination between
different components of the sinking fund system. The SinkingFund class uses
these managers internally to coordinate operations.

Allocation Manager
------------------

Coordinates allocation strategy execution and envelope funding.

.. automodule:: sinkingfund.managers.allocation_manager
   :members:
   :show-inheritance:

.. autoclass:: sinkingfund.managers.allocation_manager.AllocationManager
   :no-index:

Bill Manager
------------

Manages bill collections, scheduling, and lifecycle operations.

.. automodule:: sinkingfund.managers.bill_manager
   :members:
   :show-inheritance:

.. autoclass:: sinkingfund.managers.bill_manager.BillManager
   :no-index:

Envelope Manager
----------------

Manages envelope collections and funding operations.

.. automodule:: sinkingfund.managers.envelope_manager
   :members:
   :show-inheritance:

.. autoclass:: sinkingfund.managers.envelope_manager.EnvelopeManager
   :no-index:

Schedule Manager
----------------

Coordinates scheduling operations and cash flow generation.

.. automodule:: sinkingfund.managers.schedule_manager
   :members:
   :show-inheritance:

.. autoclass:: sinkingfund.managers.schedule_manager.ScheduleManager
   :no-index:
