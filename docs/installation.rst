Installation
============

Requirements
------------

- Python 3.12 or higher
- Poetry (for dependency management)

Install from Source
-------------------

Clone the repository and install using Poetry:

.. code-block:: bash

   git clone https://github.com/gfbarbieri/sinkingfund.git
   cd sinkingfund
   poetry install

Optional Dependencies
---------------------

For data analysis features (pandas, matplotlib):

.. code-block:: bash

   poetry install --extras analysis

For Jupyter notebook support:

.. code-block:: bash

   poetry install --extras notebooks

For all optional features:

.. code-block:: bash

   poetry install --extras all

Development Installation
------------------------

For development with testing and documentation tools:

.. code-block:: bash

   poetry install --with dev

This includes:

- pytest (testing framework)
- pytest-cov (coverage reporting)
- hypothesis (property-based testing)
- sphinx (documentation generation)
- sphinx-rtd-theme (documentation theme)

Running Tests
-------------

After installation, verify everything works by running the test suite:

.. code-block:: bash

   poetry run pytest

Verification
------------

Verify your installation by importing the package:

.. code-block:: python

   from sinkingfund import Bill
   from datetime import date
   
   # Create a simple bill
   bill = Bill(
       bill_id="test",
       service="Test Bill",
       amount_due=100.00,
       recurring=False,
       start_date=date(2025, 1, 15)
   )
   
   print(f"Created bill: {bill.service}")
