"""
Linear Programming Scheduler
============================

This module implements a contribution scheduler that uses linear
programming techniques to create optimally smoothed payment schedules
across multiple envelopes.

Mathematical Formulation
-----------------------

The scheduler solves the following constrained optimization problem:

.. math::

   \\text{Minimize} z - w

   \\text{Subject to:}
    
   \\sum_{t=0}^{d_i-1} x_{i,t} = A_i \\forall i \\in \\{0,...,n-1\\} \\text{(Full funding constraint.)}
    
   x_{i,t} = 0 \\forall i \\in \\{0,...,n-1\\}, \\forall t \\geq d_i \\text{(No contributions after due date.)}
    
   y_t = \\sum_{i=0}^{n-1} x_{i,t} \\forall t \\in \\{0,...,T-1\\} \\text{(Total contribution per period.)}
    
   z \\geq y_t \\forall t \\in \\{0,...,T-1\\} \\text{(Maximum contribution bound).}
   
   w \\leq y_t \\forall t \\in \\{0,...,T-1\\} \\text{(Minimum contribution bound.)}
    
   x_{i,t} \\geq 0 \\forall i,t \\text{(Non-negative contributions.)}

Where:

* :math:`x_{i,t}` = Contribution to bill :math:`i` at time period :math:`t`.
* :math:`y_t` = Total contribution across all bills at time period :math:`t`.
* :math:`z` = Maximum total daily contribution.
* :math:`w` = Minimum total daily contribution.
* :math:`n` = Number of bills.
* :math:`T` = Planning horizon (days).
* :math:`d_i` = Days until bill :math:`i` is due.
* :math:`A_i` = Amount due for bill :math:`i`.

Key Insights
-----------

This optimization minimizes the difference between the highest and
lowest daily total contributions, effectively "smoothing" the payment
schedule. The approach leverages the Min-Max optimization technique
to create a schedule where the total contributions across all envelopes
are as uniform as possible over time.

Implementation Details
--------------------

The scheduler operates in two main phases:

#. **Optimization phase**: Creates a daily contribution schedule that
minimizes variance in total daily contributions across all bills
using linear programming.

#. **Aggregation phase**: Combines the optimized daily contributions
into interval-appropriate cash flows (e.g., weekly, bi-weekly) based
on each envelope's contribution interval.

Assumptions and Limitations
--------------------------

* **Daily Granularity**: The optimizer works at a daily level even if
contributions are made less frequently.
* **No Interest Optimization**: The current implementation doesn't
account for opportunity cost or interest rates.
* **Bill Independence**: Bills are treated as independent entities
without considering their interrelationships.
* **Mathematically vs. Behaviorally Optimal**: The solution prioritizes
mathematical smoothness of total outflows, which may lead to uneven
contributions to individual bills.
* **Computation Complexity**: For very large problems (many bills over
long time horizons), the linear programming approach may become
computationally intensive.

Advantages
---------

* **Optimal Smoothing**: Achieves the mathematically optimal solution
for payment smoothing.
* **Global Optimization**: Considers all bills simultaneously rather
than in isolation.
* **Precise Control**: Ensures exactly the right amount is contributed
to each bill by its due date.
* **Flexibility**: Can handle bills with different amounts and due dates.
* **Automatic Prioritization**: Implicitly prioritizes urgent
obligations while maintaining smoothness.

Trade-offs
---------

* **Individual Bill Variability**: While total contributions are smooth,
individual bill contributions may vary.
* **Computational Overhead**: More complex than simpler allocation
strategies like cascade or proportional.
* **Interpretability**: The resulting schedule may be less intuitive
than simpler approaches.

Usage Examples
-------------

.. code-block:: python

   from sinkingfund.schedules.lp_scheduler import LPScheduler
    
   # Initialize the scheduler
   scheduler = LPScheduler()
    
   # Schedule contributions for multiple envelopes
   scheduler.schedule(
       envelopes=my_envelopes, start_date=datetime.date.today()
   )

Notes
-----

The implementation uses the PuLP library to solve the linear programming
problem. The solution approach transforms the variance minimization
(which would be a quadratic problem) into a linear problem by
minimizing the difference between maximum and minimum contributions.

"""

########################################################################
## IMPORTS
########################################################################

import datetime
import pulp

from .base import BaseScheduler

from ..models.envelope import Envelope
from ..models.cash_flow import CashFlow
from ..models.bills import BillInstance

########################################################################
## INDEPENDENT SCHEDULER
########################################################################

class LPScheduler(BaseScheduler):
    """
    A scheduler that uses linear programming to optimize contribution
    schedules across multiple envelopes, creating smooth payment
    patterns.
    
    This scheduler implements two key algorithms:
    
    #. **Optimization**: Uses linear programming to find the
    mathematically optimal daily contribution schedule that minimizes
    variance in total outflows across all bills.
       
    #. **Aggregation**: Combines daily optimized contributions into
    interval-based cash flows (weekly, bi-weekly, etc.) according to
    each envelope's specified contribution interval.
    
    The LP scheduler differs from simpler schedulers by considering all
    bills holistically, rather than in isolation. This creates more
    uniform total outflows over time, though individual bill
    contributions may vary more.
    
    The mathematical approach transforms what would naturally be a
    quadratic variance-minimization problem into a linear programming
    problem by using the min-max formulation (minimizing the difference
    between maximum and minimum daily contribution).
    
    Example
    -------

    .. code-block:: python
    
       scheduler = LPScheduler()
       scheduler.schedule(
           envelopes=my_envelopes, start_date=datetime.date.today()
       )
    
    Notes
    -----
    This scheduler requires the PuLP library for linear programming
    optimization. The solution quality depends on the solver's
    capability, with the default being the open-source CBC solver.
    """
    
    def __init__(self):
        """
        Initialize the scheduler.
        """
        pass

    def schedule(
        self, envelopes: list[Envelope], start_date: datetime.date
    ):
        """
        Create optimally smoothed contribution schedules for multiple
        envelopes.
    
        This method performs two key operations:
        
        #. Optimizes daily contributions across all bills to minimize
        variance in total outflows using linear programming.
        
        #. Aggregates the optimized daily contributions into interval-
        appropriate cash flows based on each envelope's contribution
        interval.
        
        The optimization creates a schedule where the total
        contributions across all envelopes are as uniform as possible
        over time. This mathematical smoothing may result in varying
        contribution patterns for individual bills while maintaining an
        optimal total contribution schedule.
        
        Parameters
        ----------
        envelopes : list[Envelope]
            The collection of envelopes for which to schedule
            contributions. Each envelope should have a valid bill and
            contribution interval defined.
            
        start_date : datetime.date
            The date from which to begin scheduling contributions. This
            serves as the reference point for all timing calculations.
        
        Returns
        -------
        None
            The method modifies the provided envelopes in-place by
            setting their schedule attribute with the optimized cash
            flows.
        
        Notes
        -----
        
        * Envelopes without a valid next bill instance (e.g., past-due
        bills with no future recurrence) will be skipped.
        * The optimization is performed at a daily granularity even when
        contribution intervals are longer.
        * Contribution intervals are respected during the aggregation
        phase, with daily contributions summed into the appropriate
        interval periods.
        * The solution is optimal in the sense that it minimizes the
        difference between the maximum and minimum daily contributions,
        which is a measure of the smoothness of the contribution
        schedule.
        """

        # Get all the bills that need to be scheduled. Bills without
        # next instances at the current date are not included.
        bills = []

        for envelope in envelopes:

            # For each envelope, get the next instance of the bill.
            bill = envelope.bill.next_instance(reference_date=start_date)

            # Skip over envelopes that do not have a next instance of
            # the bill. This occurs if bills are listed in envelopes
            # that do not have a next instance at the current date.
            if bill is None:
                continue

            bills.append(bill)

        # Optimize the contributions. This optimizes the cash flows by
        # minimizing the variance of *total* contributions across all
        # bills, not individual bills. This means that the total
        # contributions will be very similar per period, but
        # contributions to individual bills can have higher variance
        # than expected. This will return a dictionary with the bill ID
        # as the key and a list of cash flows objects as the value.
        opt_contrib = self.optimize_contributions(
            bills=bills, start_date=start_date
        )

        # Aggregate the cash flows. If the contribution interval is
        # not daily, then the optimized cash flow objects need to be
        # aggregated into a single cash flow per interval period.
        for envelope in envelopes:

            # Get the optimized daily cash flows for the envelope.
            envelope_cash_flows = opt_contrib[envelope.bill.bill_id]

            # Aggregate the cash flows.
            aggregated_flows = self.aggregate_cash_flows(
                envelopes=envelope_cash_flows,
                start_date=start_date,
                interval=envelope.interval
            )

            # Add the aggregated cash flows to the envelope.
            envelope.schedule = aggregated_flows

    def optimize_contributions(
        self, bills: list[BillInstance], start_date: datetime.date
    ) -> list[tuple[str, float, datetime.date]]:
        """
        Minimize the difference between the maximum and minimum daily
        contributions to the bills.

        Parameters
        ----------
        bills: list[BillInstance]
            The bills to schedule contributions for
        start_date: datetime.date
            The start date.

        Returns
        -------
        list[str, float, datetime.date]
            The scheduled contributions.
        """

        # Calculate T and n. T is the number of days between the start
        # date and the due date of the last bill. n is the number of
        # bills.
        bills = sorted(bills, key=lambda x: x.due_date)
        T = (bills[-1].due_date - start_date).days
        n = len(bills)

        # Create the model. This is a linear programming problem that
        # minimizes the difference between the maximum and minimum daily
        # contributions.
        model = pulp.LpProblem(name="schedule", sense=pulp.LpMinimize)

        ################################################################
        ## Define the Variables
        ################################################################

        # 1. Create contribution to bill i at time t. Contributions
        # cannot be negative, and are only defined for the period that
        # the bill is due.
        x = {}

        for i in range(n):
            for t in range(T):
                x[i, t] = pulp.LpVariable(f"x_{i}_{t}", lowBound=0)

        # 2. Similarly, create a variable the will represent the total
        # contribution at time t to all bills.
        y = {}

        for t in range(T):
            y[t] = pulp.LpVariable(f"y_{t}", lowBound=0)
        
        # 3. Create variables for the maximum and minimum contributions,
        # respectively. We will use this to calculate the objective
        # function.
        z = pulp.LpVariable("z", lowBound=0)
        w = pulp.LpVariable("w", lowBound=0)

        ################################################################
        ## Add Constraints
        ################################################################

        for i, bill in enumerate(bills):

            # Calculate the number of days until the due date.
            days_until_due = (bill.due_date - start_date).days

            # 1. Full Funding: add the constraint that the sum of the
            # contributions for the bill must be equal to the amount.
            model += pulp.lpSum([
                x[i, t] for t in range(days_until_due)
            ]) == bill.amount_due

            # 2. No Contribution After Due Date: add the constraint that
            # no contributions are allowed after the due date.
            # Literally, for every day after this bill is due, make sure
            # no money is allocated to it.
            for t in range(days_until_due, T):
                model += x[i, t] == 0

        # 3. Total Contributions: add the constraint that the total
        # contributions at time t is the sum of the contributions to all
        # bills at time t.
        for t in range(T):
            model += y[t] == pulp.lpSum([x[i, t] for i in range(n)])

        # 4. Set maximum and minimum contribution bounds. z must be at
        # least as large as the largest daily contribution for each
        # period; and w must be at most as small as the smallest daily
        # contribution in each period.
        for t in range(T):
            model += z >= y[t]
            model += w <= y[t]

        # 5. Set the objective function. Minimize the difference between
        # the maximum and minimum contributions. This is considered the
        # objective function because it is not an equality or inequality
        # creating relationships between expressions, but an expression
        # on its own.
        model += z - w

        ################################################################
        ## Solve the Model
        ################################################################

        # Solve the model.
        model.solve(pulp.PULP_CBC_CMD(msg=False))
        
        # Check if the solution is optimal
        if pulp.LpStatus[model.status] != 'Optimal':
            raise ValueError(
                "Could not find optimal solution. Status: "
                f"{pulp.LpStatus[model.status]}"
            )

        ################################################################
        ## Return the Results
        ################################################################

        # Get the results and regroup them by bill.
        result = {}

        for i, bill in enumerate(bills):

            # Create a list to store the cash flows for the bill.
            result[bill.bill_id] = []

            for t in range(T):

                # Get the value of the contribution from the model.
                value = x[i, t].value()

                # Create the date from the start date and the number of
                # days since the start date.
                date = start_date + datetime.timedelta(days=t)
                
                # Create the cash flow.
                cash_flow = CashFlow(
                    bill_id=bill.bill_id, date=date, amount=value
                )

                # Add the cash flow to the list.
                result[bill.bill_id].append(cash_flow)
    
        return result

    def aggregate_cash_flows(
        self, cash_flows: list[CashFlow], start_date: datetime.date,
        interval: int
    ) -> list[CashFlow]:
        """
        Aggregate cash flows into a single cash flow per interval
        period. This is done by summing up all contributions for each
        interval period and creating a single cash flow for the total
        amount in that interval.

        Parameters
        ----------
        cash_flows : list
            List of CashFlow objects.
        start_date : datetime.date
            Start date.
        interval : int
            Contribution interval in days.

        Returns
        -------
        list
            List of CashFlow objects.
        """

        # Initialize dictionary to track total contributions per
        # interval period.
        int_contribs = {}
        bill_id = cash_flows[0].bill_id

        # Step 1: Sum up all contributions by interval period.
        #
        # The first interval has index 0, the second has index 1, etc.
        # They represent the number of days since the start date. If
        # the interval is 14 days, interval index 0 is the first 14 day
        # period, interval index 1 is the second 14 day period, etc.
        # When the loop is done, interval_contributions will have a key
        # for each interval index, and the value will be the total
        # contribution for that interval. The interval index tells us
        # that it belongs to the interval index-th interval, regardless
        # of the exact date of the contribution.
        for cf in cash_flows:

            # Calculate days since start date.
            days_since_start = (cf.date - start_date).days
            
            # Determine to which interval period this contribution
            # belongs. The integer division by the interval length
            # gives the index of the interval, which is enough to
            # determine which interval the contribution belongs to.
            int_idx = days_since_start // interval
            
            # Add this contribution to the interval sum. Initialize to 0
            # if this is the first contribution to this interval.
            if int_idx not in int_contribs:
                int_contribs[int_idx] = 0

            # Add the contribution to the interval's total.
            int_contribs[int_idx] += cf.amount

        # Step 2: Create one aggregated cash flow per interval period.
        agg_flows = []

        for int_idx, total_amount in sorted(int_contribs.items()):

            # Calculate the date for this interval. This approach puts
            # all contributions on the first day of the interval. This
            # avoids complications with partial intervals, but comes
            # at the cost of paying off the bill earlier than the due
            # date by the contribution interval size.
            int_date = (
                start_date + datetime.timedelta(days=int_idx * interval)
            )

            # Create a single cash flow for the total amount in this
            # interval. If the total amount is negative, we do not add
            # a cash flow because it means that the bill is paid off.
            if total_amount > 0:

                # Create the cash flow object. We round the amount to 2
                # decimal places to avoid floating point precision
                # issues. However, this is not a perfect solution, and
                # can lead to errors in the sum of the contributions.
                agg_flows.append(
                    CashFlow(
                        bill_id=bill_id,
                        date=int_date,
                        amount=round(total_amount, 2)
                    )
                )

        return agg_flows