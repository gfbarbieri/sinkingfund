Testing
=======

The Sinking Fund library includes a comprehensive testing suite to ensure
reliability and correctness of all financial calculations.

Running Tests
-------------

Quick Test Run
~~~~~~~~~~~~~~

Run the complete test suite:

.. code-block:: bash

   poetry run pytest

With coverage reporting:

.. code-block:: bash

   poetry run pytest --cov=sinkingfund --cov-report=html

Run specific test categories:

.. code-block:: bash

   # Unit tests only
   poetry run pytest tests/unit/
   
   # Integration tests only  
   poetry run pytest tests/integration/
   
   # Specific module tests
   poetry run pytest tests/unit/models/
   poetry run pytest tests/unit/utils/

Verbose Output
~~~~~~~~~~~~~~

For detailed test information:

.. code-block:: bash

   poetry run pytest -v
   poetry run pytest tests/unit/models/test_bills.py -v

Test Structure
--------------

The testing suite is organized into several categories:

Unit Tests
~~~~~~~~~~

Located in ``tests/unit/``, these test individual components in isolation:

- **Models** (``tests/unit/models/``): Core domain objects
  
  - ``test_bills.py``: Bill and BillInstance functionality
  - ``test_cash_flow.py``: CashFlow and CashFlowSchedule operations
  - ``test_envelope.py``: Envelope calculations and state management
  - ``test_sinkingfund.py``: Main orchestrator class

- **Managers** (``tests/unit/managers/``): Collection management classes

- **Allocation** (``tests/unit/allocation/``): Allocation strategies

- **Schedules** (``tests/unit/schedules/``): Contribution scheduling

- **Utils** (``tests/unit/utils/``): Utility functions
  
  - ``test_date_utils.py``: Calendar arithmetic and date handling
  - ``test_loaders.py``: File loading and data conversion
  - ``test_readers.py``: Low-level file format readers
  - ``test_format_registry.py``: Format detection and configuration
  - ``test_file_utils.py``: File system utilities

Integration Tests
~~~~~~~~~~~~~~~~~

Located in ``tests/integration/``, these test complete workflows:

- End-to-end scenarios combining multiple components
- Real-world usage patterns
- Cross-component interaction validation

Test Fixtures
~~~~~~~~~~~~~

Common test data is defined in ``tests/conftest.py``:

.. code-block:: python

   # Example fixtures available in all tests
   
   @pytest.fixture
   def fixed_date():
       """Deterministic date for consistent test results."""
       return date(2024, 1, 15)
   
   @pytest.fixture  
   def small_amount():
       """Small monetary amount for testing."""
       return Decimal("50.00")
   
   @pytest.fixture
   def sample_bill():
       """Standard test bill."""
       return Bill(
           bill_id="test_bill",
           service="Test Service", 
           amount_due=Decimal("100.00"),
           recurring=True,
           start_date=date(2024, 1, 15),
           frequency="monthly"
       )

Test Coverage
-------------

The test suite maintains high coverage across all modules:

Coverage Goals
~~~~~~~~~~~~~~

- **Unit Tests**: >95% line coverage for all core modules
- **Integration Tests**: All major workflows covered
- **Edge Cases**: Boundary conditions and error scenarios
- **Financial Accuracy**: Precise decimal arithmetic validation

Key Testing Areas
~~~~~~~~~~~~~~~~~

**Date Arithmetic**
  Calendar-aware date calculations, leap years, month-end handling

**Monetary Precision**
  Decimal arithmetic for financial calculations, rounding behavior

**Bill Scheduling** 
  Recurring bill instances, frequency calculations, edge dates

**Envelope Logic**
  Balance calculations, funding status, contribution tracking

**Allocation Strategies**
  Fund distribution algorithms, priority handling, edge cases

**Data Loading**
  File format support, error handling, data validation

Testing Philosophy
------------------

Deterministic Tests
~~~~~~~~~~~~~~~~~~~

All tests use fixed dates and amounts to ensure reproducible results:

.. code-block:: python

   # ✓ Good: Fixed, deterministic date
   test_date = date(2024, 1, 15)
   
   # ✗ Bad: Non-deterministic, changes daily
   test_date = date.today()

This ensures tests pass consistently regardless of when they're run.

Financial Precision
~~~~~~~~~~~~~~~~~~~

All monetary calculations use ``Decimal`` types for exact precision:

.. code-block:: python

   # ✓ Good: Precise decimal arithmetic
   amount = Decimal("123.45")
   
   # ✗ Bad: Floating point precision issues
   amount = 123.45

Comprehensive Validation
~~~~~~~~~~~~~~~~~~~~~~~~

Tests validate both expected behavior and edge cases:

.. code-block:: python

   def test_monthly_increment_edge_cases():
       """Test month increments for edge cases like leap years."""
       # Test leap year February 29
       leap_date = date(2024, 2, 29)
       result = increment_date(leap_date, frequency="monthly", interval=1)
       # Should handle month-end normalization correctly
       assert result == date(2024, 3, 29)

Running Specific Test Categories
--------------------------------

Property-Based Testing
~~~~~~~~~~~~~~~~~~~~~~

Some tests use Hypothesis for property-based testing:

.. code-block:: bash

   # Run property-based tests with more examples
   poetry run pytest tests/ -v --hypothesis-show-statistics

Performance Testing
~~~~~~~~~~~~~~~~~~~

For performance-critical components:

.. code-block:: bash

   # Run with performance profiling
   poetry run pytest tests/unit/utils/ --profile

Test Development Guidelines
---------------------------

Writing New Tests
~~~~~~~~~~~~~~~~~

When adding new functionality:

1. **Start with unit tests** for individual components
2. **Use fixtures** from ``conftest.py`` for common test data
3. **Follow naming conventions**: ``test_<functionality>_<scenario>``
4. **Test edge cases** as well as happy paths
5. **Use descriptive assertions** with clear error messages

Example Test Structure
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def test_envelope_funding_calculation_with_partial_contributions():
       """Test envelope remaining amount with partial contributions."""
       # Arrange
       bill_instance = BillInstance(
           bill=sample_bill,
           due_date=date(2024, 3, 15),
           amount_due=Decimal("300.00")
       )
       envelope = Envelope(
           bill_instance=bill_instance,
           initial_allocation=Decimal("100.00"),
           start_contrib_date=date(2024, 1, 1),
           end_contrib_date=date(2024, 3, 10)
       )
       
       # Act  
       remaining = envelope.remaining()
       
       # Assert
       expected = Decimal("200.00")  # 300 - 100
       assert remaining == expected, (
           f"Expected remaining {expected}, got {remaining}"
       )

Continuous Integration
----------------------

The test suite runs automatically on all pull requests and commits:

- **GitHub Actions**: Automated testing on multiple Python versions
- **Coverage Reports**: Automatic coverage tracking and reporting  
- **Quality Gates**: Tests must pass before merging

Local Development
~~~~~~~~~~~~~~~~~

Before committing changes:

.. code-block:: bash

   # Run full test suite
   poetry run pytest
   
   # Check test coverage
   poetry run pytest --cov=sinkingfund --cov-report=term-missing
   
   # Run linting (if available)
   poetry run ruff check .
   poetry run mypy sinkingfund/

This ensures code quality and prevents regressions in the financial
calculation logic.
