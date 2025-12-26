Models Package
==============

The models package contains core domain objects for sinking fund management,
including bills, envelopes, cash flows, and the main SinkingFund orchestrator.

Bills Module
------------

Bill and BillInstance classes for representing financial obligations.

.. automodule:: sinkingfund.models.bills
   :members:
   :show-inheritance:

.. autoclass:: sinkingfund.models.bills.Bill
   :no-index:

.. autoclass:: sinkingfund.models.bills.BillInstance
   :no-index:

Cash Flow Module
----------------

CashFlow and CashFlowSchedule classes for tracking monetary transactions.

.. automodule:: sinkingfund.models.cash_flow
   :members:
   :show-inheritance:

.. autoclass:: sinkingfund.models.cash_flow.CashFlow
   :no-index:

.. autoclass:: sinkingfund.models.cash_flow.CashFlowSchedule
   :no-index:

Envelope Module
---------------

Envelope class for digital envelope budgeting and targeted savings.

.. automodule:: sinkingfund.models.envelope
   :members:
   :show-inheritance:

.. autoclass:: sinkingfund.models.envelope.Envelope
   :no-index:

SinkingFund Module
------------------

Main SinkingFund class that orchestrates the entire system.

.. automodule:: sinkingfund.models.sinkingfund
   :members:
   :show-inheritance:

.. autoclass:: sinkingfund.models.sinkingfund.SinkingFund
   :no-index:
