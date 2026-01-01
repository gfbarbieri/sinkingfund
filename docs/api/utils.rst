Utils Package
=============

Utility functions provide foundational support for date arithmetic,
file operations, data loading, and format handling.

Date Utils
----------

Calendar-aware date arithmetic for financial calculations and centralized
date parsing utilities for consistent date handling across all data input
sources.

Date Parsing
~~~~~~~~~~~~

The library provides a centralized date parsing system that supports
multiple date string formats for user convenience and data source
compatibility.

Supported Date Formats
^^^^^^^^^^^^^^^^^^^^^^

The following date string formats are supported (tried in order):

* ``%m/%d/%Y`` - US format (e.g., ``01/15/2025``)
* ``%Y-%m-%d`` - ISO format (e.g., ``2025-01-15``)
* ``%m-%d-%Y`` - US with dashes (e.g., ``01-15-2025``)
* ``%d/%m/%Y`` - European format (e.g., ``15/01/2025``)
* ``%d-%m-%Y`` - European with dashes (e.g., ``15-01-2025``)
* ``%Y/%m/%d`` - ISO with slashes (e.g., ``2025/01/15``)

The ``parse_date()`` function automatically tries all formats and returns
a ``datetime.date`` object if successful, or ``None`` if the string cannot
be parsed.

.. automodule:: sinkingfund.utils.date_utils
   :members:
   :show-inheritance:

File Utils
----------

File format detection and path handling utilities.

.. automodule:: sinkingfund.utils.file_utils
   :members:
   :show-inheritance:

Format Registry
---------------

Centralized format configuration and reader function mapping.

.. automodule:: sinkingfund.utils.format_registry
   :members:
   :show-inheritance:

Loaders
-------

High-level data loading interface with automatic format detection.

.. automodule:: sinkingfund.utils.loaders
   :members:
   :show-inheritance:

Readers
-------

Low-level file readers for CSV, Excel, and JSON data sources.

.. automodule:: sinkingfund.utils.readers
   :members:
   :show-inheritance:
