#!/usr/bin/env python3
"""
Notebook Execution Test Runner
===============================

Execute all example notebooks to verify they run without errors. This
script uses nbconvert to execute notebooks in the examples/ directory
and provides detailed reporting on which notebooks pass or fail.

The script processes each notebook sequentially, capturing execution
errors and providing both summary and detailed error information. This
enables automated validation of example notebooks in CI/CD pipelines
while providing actionable feedback for developers.

Features:
- Sequential execution of all notebooks in examples/ directory
- Detailed error reporting with cell-level error information
- Progress tracking with pass/fail status for each notebook
- Summary statistics and detailed failure reports
- Exit code suitable for CI/CD integration (0 on success, 1 on failure)

Examples
--------
.. code-block:: bash

   # Run all notebooks and report results
   poetry run python scripts/run_notebooks.py

   # Use in CI/CD pipeline
   poetry run python scripts/run_notebooks.py || exit 1
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    import nbformat

try:
    import nbformat
    from nbconvert.preprocessors import ExecutePreprocessor
except ImportError:
    print(
        "Error: nbconvert is required. "
        "Install with: poetry install --with notebook"
    )
    sys.exit(1)


########################################################################
## CONSTANTS
########################################################################

DEFAULT_TIMEOUT = 600


########################################################################
## ERROR EXTRACTION HELPERS
########################################################################

def _extract_cell_errors(
        notebook: nbformat.NotebookNode
    ) -> List[str]:
    """
    Extract error messages from notebook cells after execution.

    Parameters
    ----------
    notebook : nbformat.NotebookNode
        The executed notebook containing cell outputs.

    Returns
    -------
    List[str]
        List of formatted error messages, one per error cell.
    """
    error_messages = []
    for i, cell in enumerate(notebook.cells, 1):
        if cell.cell_type != 'code':
            continue

        if 'outputs' not in cell:
            continue

        for output in cell.outputs:
            if output.output_type != 'error':
                continue

            error_name = output.get('ename', 'Error')
            error_value = output.get('evalue', 'Unknown error')
            error_info = f"Cell {i}: {error_name}: {error_value}"

            # DESIGN CHOICE: Include last traceback line for context
            # without overwhelming output with full stack traces.
            if 'traceback' in output:
                tb_lines = output['traceback']
                if tb_lines:
                    last_line = tb_lines[-1].strip()
                    error_info += f"\n  {last_line}"

            error_messages.append(error_info)

    return error_messages


def _format_exception_error(
        exception: Exception, notebook: nbformat.NotebookNode | None
    ) -> str:
    """
    Format exception message with additional context if available.

    Parameters
    ----------
    exception : Exception
        The exception that occurred during execution.
    notebook : nbformat.NotebookNode | None
        The notebook object if it was loaded before the exception.

    Returns
    -------
    str
        Formatted error message with exception details and any cell
        errors found in the notebook.
    """
    error_msg = f"{type(exception).__name__}: {str(exception)}"

    # BUSINESS GOAL: Include additional context from exception if
    # available (e.g., from ExecutePreprocessor).
    if hasattr(exception, 'output'):
        error_msg += f"\n{exception.output}"

    # BUSINESS GOAL: If notebook was loaded, include cell-level errors
    # to provide actionable debugging information.
    if notebook is not None:
        cell_errors = _extract_cell_errors(notebook)
        if cell_errors:
            error_msg += "\n" + "\n".join(cell_errors)

    return error_msg


########################################################################
## NOTEBOOK EXECUTION
########################################################################

def execute_notebook(
        notebook_path: Path, timeout: int = DEFAULT_TIMEOUT
    ) -> Tuple[bool, str]:
    """
    Execute a single notebook and return success status and error
    message.

    Loads the notebook, executes all cells using nbconvert's
    ExecutePreprocessor, and checks for execution errors. Returns
    detailed error information if execution fails.

    Parameters
    ----------
    notebook_path : Path
        Path to the notebook file to execute.
    timeout : int, optional
        Execution timeout in seconds. Default is 600 (10 minutes).

    Returns
    -------
    Tuple[bool, str]
        Tuple containing:
        - success: True if notebook executed without errors, False
          otherwise.
        - error_message: Empty string on success, formatted error
          information on failure.

    Notes
    -----
    The notebook is executed in memory and not modified on disk. The
    execution path is set to the notebook's parent directory to ensure
    relative imports and file references work correctly.
    """
    notebook = None

    try:
        # SIDE EFFECTS: Read notebook file from disk.
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)

        # DESIGN CHOICE: Use ExecutePreprocessor for consistent
        # execution environment and timeout handling.
        executor = ExecutePreprocessor(
            timeout=timeout, kernel_name='python3'
        )

        # SIDE EFFECTS: Execute notebook cells, modifying notebook
        # object in memory with outputs.
        execution_path = str(notebook_path.parent)
        executor.preprocess(notebook, {'metadata': {'path': execution_path}})

        # BUSINESS GOAL: Check for execution errors in cell outputs
        # after successful preprocessing (no exception raised).
        cell_errors = _extract_cell_errors(notebook)
        if cell_errors:
            return False, "\n".join(cell_errors)

        return True, ""

    except Exception as e:
        # FAILURE MODE: Execution failed with exception. Format error
        # message with context from notebook if available.
        error_message = _format_exception_error(e, notebook)
        return False, error_message


########################################################################
## MAIN EXECUTION
########################################################################

def _find_notebooks(examples_dir: Path) -> List[Path]:
    """
    Find all notebook files in the examples directory.

    Parameters
    ----------
    examples_dir : Path
        Path to the examples directory.

    Returns
    -------
    List[Path]
        Sorted list of notebook file paths.

    Raises
    ------
    FileNotFoundError
        If examples_dir does not exist.
    ValueError
        If no notebooks are found in the directory.
    """
    if not examples_dir.exists():
        raise FileNotFoundError(
            f"Examples directory not found: {examples_dir}"
        )

    notebooks = sorted(examples_dir.glob("*.ipynb"))

    if not notebooks:
        raise ValueError(f"No notebooks found in {examples_dir}")

    return notebooks


def _print_summary(results: List[Tuple[Path, bool, str]]) -> None:
    """
    Print execution summary with detailed results.

    Parameters
    ----------
    results : List[Tuple[Path, bool, str]]
        List of (notebook_path, success, error_message) tuples from
        execution.
    """
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, success, _ in results if success)
    failed = len(results) - passed

    for notebook, success, error in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{status}: {notebook.name}")

        # BUSINESS GOAL: Provide detailed error information for failed
        # notebooks to aid debugging.
        if not success and error:
            print(f"  Error details:\n{error}\n")

    print(f"\nTotal: {len(results)} notebook(s)")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")


def main() -> int:
    """
    Execute all notebooks in the examples directory and report results.

    Finds all notebooks in the examples/ directory, executes them
    sequentially, and prints a summary of results. Returns exit code 0
    if all notebooks pass, 1 if any fail.

    Returns
    -------
    int
        Exit code: 0 if all notebooks passed, 1 if any failed.

    Notes
    -----
    The examples directory is located relative to the script location:
    scripts/run_notebooks.py -> ../examples/
    """
    # BUSINESS GOAL: Locate examples directory relative to script
    # location to work regardless of current working directory.
    script_dir = Path(__file__).parent
    examples_dir = script_dir.parent / "examples"

    try:
        notebooks = _find_notebooks(examples_dir)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return 1

    print(f"Found {len(notebooks)} notebook(s) to execute:\n")

    # BUSINESS GOAL: Execute each notebook and collect results for
    # summary reporting.
    results: List[Tuple[Path, bool, str]] = []
    for i, notebook in enumerate(notebooks, 1):
        print(
            f"[{i}/{len(notebooks)}] Executing {notebook.name}...",
            end=" ",
            flush=True
        )

        success, error = execute_notebook(notebook)
        results.append((notebook, success, error))

        if success:
            print("✓ PASSED")
        else:
            print("✗ FAILED")
            # BUSINESS GOAL: Show first error line in progress output
            # for immediate feedback without overwhelming output.
            if error:
                first_line = error.split('\n')[0]
                print(f"    Error: {first_line}")

    _print_summary(results)

    # BUSINESS GOAL: Return appropriate exit code for CI/CD pipelines.
    passed_count = sum(1 for _, success, _ in results if success)
    failed_count = len(results) - passed_count

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
