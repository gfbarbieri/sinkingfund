Installation
============

Requirements
------------

- Python 3.12 or higher
- Poetry (recommended) or pip for package management

Install from Source
-------------------

Clone the repository and install using Poetry:

.. code-block:: bash

   git clone https://github.com/yourusername/sinkingfund.git
   cd sinkingfund
   poetry install

Or using pip:

.. code-block:: bash

   git clone https://github.com/yourusername/sinkingfund.git
   cd sinkingfund
   pip install -e .

Optional Dependencies
---------------------

For data analysis features:

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

This includes pytest, Sphinx, and all development tools needed to
contribute to the project.

Verification
------------

Verify your installation by importing the package:

.. code-block:: python

   import sinkingfund
   from sinkingfund import Bill, Envelope
   
   # Create a simple bill
   bill = Bill(
       bill_id="test",
       service="Test Bill",
       amount_due=100.00,
       recurring=False,
       start_date=date(2025, 1, 15)
   )
   
   print(f"Created bill: {bill.service}")
