"""
Reporter
========

The Reporter provides comprehensive report generation for sinking fund
systems. It orchestrates the creation of daily account reports showing
balances, contributions, and payouts across the planning period.

Core Abstractions
-----------------

**Report Generation**: Centralized logic for building structured reports
that aggregate envelope data across time periods, providing clear
visibility into account balances, cash flows, and funding status.

**Data Aggregation**: Combines envelope-level data (balances, cash flows)
into comprehensive daily reports with consistent structure and formatting.

**Filtering and Subsetting**: Supports flexible report generation with
options to include only active dates or full date ranges.

Key Features
------------

- **Daily account reports** with account balances, contributions, and
  payouts for each date in the planning period.
- **Flexible date filtering** to include all dates or only dates with
  activity.
- **Static balance handling** for account balances not allocated to
  envelopes.
- **Consistent report structure** with totals, counts, and per-bill
  breakdowns.

Examples
--------

.. code-block:: python

   from datetime import date
   from decimal import Decimal
   from sinkingfund.managers import Reporter, EnvelopeManager

   # Create reporter with envelope manager and planning period.
   envelope_manager = EnvelopeManager()
   reporter = Reporter(
       envelope_manager=envelope_manager,
       start_date=date(2025, 1, 1),
       end_date=date(2025, 12, 31),
       balance=Decimal("5000.00")
   )

   # Generate full report.
   report = reporter.generate_daily_report(active_only=False)

   # Generate report with only active dates.
   active_report = reporter.generate_daily_report(active_only=True)
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import datetime

from decimal import Decimal

from ..managers.envelope_manager import EnvelopeManager
from ..utils.date_utils import get_date_range

########################################################################
## REPORTER
########################################################################

class Reporter:
    """
    Generate comprehensive reports for sinking fund operations.

    The Reporter orchestrates the creation of daily account reports that
    aggregate envelope data across the planning period. It provides
    structured output showing account balances, contributions, and payouts
    for each date, with options for filtering and subsetting.

    Core Responsibilities
    ---------------------

    - **Report Generation**: Build daily account reports with consistent
      structure and formatting.
    - **Data Aggregation**: Combine envelope-level data into
      comprehensive date-based reports.
    - **Balance Calculation**: Handle both envelope-allocated balances
      and static account balances not allocated to envelopes.
    - **Filtering Support**: Provide options to include all dates or only
      dates with activity.

    Design Patterns
    ---------------

    - **Manager Pattern**: Centralized coordination of report generation
      with clear separation from orchestration logic.
    - **Data Aggregation**: Collect and combine data from multiple
      sources (envelopes) into unified reports.
    - **Template Method**: Consistent report structure with flexible
      filtering options.

    Attributes
    ----------
    envelope_manager : EnvelopeManager
        The envelope manager providing access to envelope data and
        balance/cash flow calculations.
    start_date : datetime.date
        The start date of the planning period for report generation.
    end_date : datetime.date
        The end date of the planning period for report generation.
    balance : Decimal
        The initial account balance, used for calculating static
        unallocated balance.

    Notes
    -----
    The reporter calculates static account balance as the difference
    between the initial balance and the sum of all envelope initial
    allocations. This represents funds that were not allocated to any
    specific envelope and remain in the general account.

    Examples
    --------
    .. code-block:: python

       # Create reporter with envelope manager.
       reporter = Reporter(
           envelope_manager=envelope_manager,
           start_date=date(2025, 1, 1),
           end_date=date(2025, 12, 31),
           balance=Decimal("5000.00")
       )

       # Generate full daily report.
       report = reporter.generate_daily_report(active_only=False)

       # Generate report with only active dates.
       active_report = reporter.generate_daily_report(active_only=True)
    """

    def __init__(
        self,
        envelope_manager: EnvelopeManager,
        start_date: datetime.date,
        end_date: datetime.date,
        balance: Decimal
    ) -> None:
        """
        Initialize the Reporter with envelope manager and planning period.

        Creates a new reporter instance configured with the envelope
        manager for data access and the planning period for report
        generation.

        Parameters
        ----------
        envelope_manager : EnvelopeManager
            The envelope manager providing access to envelope data and
            balance/cash flow calculations.
        start_date : datetime.date
            The start date of the planning period for report generation.
        end_date : datetime.date
            The end date of the planning period for report generation.
        balance : Decimal
            The initial account balance, used for calculating static
            unallocated balance.

        Notes
        -----
        The reporter uses the envelope manager to access envelope data
        and perform balance/cash flow calculations. The planning period
        defines the date range for report generation.

        Examples
        --------
        .. code-block:: python

           reporter = Reporter(
               envelope_manager=envelope_manager,
               start_date=date(2025, 1, 1),
               end_date=date(2025, 12, 31),
               balance=Decimal("5000.00")
           )
        """
        self.envelope_manager = envelope_manager
        self.start_date = start_date
        self.end_date = end_date
        self.balance = balance

    def generate_daily_report(
        self, active_only: bool = False
    ) -> dict[datetime.date, dict[str, Decimal]]:
        """
        Generate daily account report for the planning period.

        Creates a comprehensive daily report showing account balances,
        contributions, and payouts for each date in the planning period.
        Supports filtering to include only dates with activity.

        Parameters
        ----------
        active_only : bool, optional
            Whether to only include dates with contributions or payouts
            in the report. Defaults to False.

        Returns
        -------
        dict[datetime.date, dict[str, Decimal]]
            The daily account report with the following structure:

            .. code-block:: python

               {date: {
                   'account_balance': {
                       'total': Decimal,
                       'count': int,
                       'bills': dict[str, Decimal]
                   },
                   'contributions': {
                       'total': Decimal,
                       'count': int,
                       'bills': dict[str, Decimal]
                   },
                   'payouts': {
                       'total': Decimal,
                       'count': int,
                       'bills': dict[str, Decimal]
                   }
               }}

        Notes
        -----
        **Report Structure**:

        - **account_balance**: Shows the balance for each envelope on
          each date, plus any static unallocated balance.
        - **contributions**: Shows contribution amounts for each envelope
          on each date.
        - **payouts**: Shows payout amounts for each envelope on each
          date.

        Each section includes:
        - **total**: Sum of all values in the section.
        - **count**: Number of non-zero values.
        - **bills**: Dictionary mapping bill_id to value.

        **Static Balance**: The report includes any account balance that
        was not allocated to envelopes. This can occur when the initial
        balance exceeds the sum of all envelope amounts due.

        **Filtering**: When `active_only=True`, the report includes only
        dates where contributions or payouts occurred.

        Examples
        --------
        Generate full report:

        .. code-block:: python

           report = reporter.generate_daily_report(active_only=False)

        Generate report with only active dates:

        .. code-block:: python

           active_report = reporter.generate_daily_report(active_only=True)
        """

        # Get all dates between the start and end dates.
        dates = get_date_range(
            start_date=self.start_date, end_date=self.end_date
        )

        # BUSINESS GOAL: Build the account balance report.
        acct_report = {}

        # It is possible that the account contains a balance that was
        # not allocated to any envelopes. This can happen if the initial
        # account balance is greater than the sum of the amounts due for
        # all envelopes.
        static_acct_balance = self.balance - sum(
            envelope.initial_allocation
            for envelope in self.envelope_manager.envelopes
        )

        for date in dates:

            # Get the information for the account balances,
            # contributions, and payouts.
            acct = self.envelope_manager.get_balance_as_of_date(
                as_of_date=date
            )

            contrib = self.envelope_manager.total_cash_flow_on_date(
                date=date, exclude='payouts'
            )

            payout = self.envelope_manager.total_cash_flow_on_date(
                date=date, exclude='contributions'
            )

            # Add the information to the report.
            acct_report[date] = {
                'account_balance': self._build_report_section(
                    data_dict=acct, date=date
                ),
                'contributions': self._build_report_section(
                    data_dict=contrib, date=date
                ),
                'payouts': self._build_report_section(
                    data_dict=payout, date=date
                )
            }

            # Adjust for any account balance that was not allocated to
            # any envelopes.
            if static_acct_balance > 0:
                acct_report[date]['account_balance']['total'] += (
                    static_acct_balance
                )

            # Subset if active only.
            if active_only:
                acct_report = {
                    date: data
                    for date, data in acct_report.items()
                    if data['contributions']['count'] > 0
                    or data['payouts']['count'] > 0
                }

        return acct_report

    def _build_report_section(
        self, data_dict: dict, date: datetime.date
    ) -> dict[str, int | Decimal]:
        """
        Helper to build a report section with consistent structure.

        Transforms raw data dictionaries into structured report sections
        with totals, counts, and per-bill breakdowns.

        Parameters
        ----------
        data_dict : dict
            The data dictionary containing date-keyed data with bill_id
            keys and Decimal values.
        date : datetime.date
            The date to build the report section for.

        Returns
        -------
        dict[str, int | Decimal]
            The report section with the following structure:

            .. code-block:: python

               {
                   'total': Decimal,
                   'count': int,
                   'bills': dict[str, Decimal]
               }

        Notes
        -----
        The method extracts data for the specified date from the data
        dictionary and builds a structured section with:
        - **total**: Sum of all values for the date.
        - **count**: Number of non-zero values.
        - **bills**: Dictionary mapping bill_id to value.

        If no data exists for the date, returns empty structure with zero
        total and count.

        Examples
        --------
        .. code-block:: python

           section = reporter._build_report_section(
               data_dict=balance_data,
               date=date(2025, 1, 15)
           )
        """

        # Get the data for the date.
        data = data_dict.get(date, {})

        # Build the report section.
        section = {
            'total': sum(data.values()),
            'count': len([x for x in data.values() if x != 0]),
            'bills': data
        }

        return section

