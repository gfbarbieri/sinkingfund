Allocation Package
==================

.. _allocation-strategies:

Allocation strategies implement different algorithms for distributing
available funds across multiple envelopes based on priorities and constraints.

Base Allocator
--------------

Abstract base class defining the allocation strategy interface.

.. automodule:: sinkingfund.allocation.base
   :members:
   :show-inheritance:

Proportional Allocator
----------------------

Distributes funds proportionally based on envelope requirements.

.. automodule:: sinkingfund.allocation.proportional
   :members:
   :show-inheritance:

.. autoclass:: sinkingfund.allocation.proportional.ProportionalAllocator
   :no-index:

Sorted Allocator
----------------

Allocates funds using priority-based sorting strategies.

.. automodule:: sinkingfund.allocation.sorted
   :members:
   :show-inheritance:

.. autoclass:: sinkingfund.allocation.sorted.SortedAllocator
   :no-index:
