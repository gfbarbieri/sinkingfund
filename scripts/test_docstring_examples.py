#!/usr/bin/env python3
"""
Docstring Example Test Runner
==============================

Extract and execute all code-block examples from docstrings to verify
they run without errors. This script parses Python files, extracts
code blocks from docstrings, and executes them to ensure examples are
accurate and executable.

The script processes each Python file in the sinkingfund/ directory,
extracting code blocks marked with `.. code-block:: python` from
docstrings, and provides detailed reporting on which examples pass or
fail.

Features:
- Extracts code blocks from docstring Examples sections
- Executes examples in isolated context
- Detailed error reporting with file and method context
- Summary statistics and failure reports
- Exit code suitable for CI/CD integration (0 on success, 1 on failure)

Examples
--------
.. code-block:: bash

   # Run all docstring examples and report results
   poetry run python scripts/test_docstring_examples.py

   # Use in CI/CD pipeline
   poetry run python scripts/test_docstring_examples.py || exit 1
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import ast
import importlib.util
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    pass

########################################################################
## CONSTANTS
########################################################################

DEFAULT_TIMEOUT = 60
CODE_BLOCK_PATTERN = re.compile(
    r'\.\.\s+code-block::\s+python\s*\n\s*\n((?:   .*\n?)+)',
    re.MULTILINE
)

########################################################################
## CODE BLOCK EXTRACTION
########################################################################


def extract_code_blocks(docstring: str) -> List[str]:
    """
    Extract Python code blocks from docstring.

    Parameters
    ----------
    docstring : str
        The docstring to parse.

    Returns
    -------
    List[str]
        List of code block strings, one per code block found.
    """
    if not docstring:
        return []

    code_blocks = []
    matches = CODE_BLOCK_PATTERN.findall(docstring)

    for match in matches:
        # Remove leading indentation (assuming 3 spaces per indent level).
        lines = match.split('\n')
        dedented_lines = []
        for line in lines:
            if line.startswith('   '):
                dedented_lines.append(line[3:])
            elif line.strip() == '':
                dedented_lines.append('')
            else:
                dedented_lines.append(line)

        code_block = '\n'.join(dedented_lines).strip()
        if code_block:
            code_blocks.append(code_block)

    return code_blocks


def find_docstrings_in_file(file_path: Path) -> List[Tuple[str, str, int]]:
    """
    Find all docstrings in a Python file.

    Parameters
    ----------
    file_path : Path
        Path to the Python file.

    Returns
    -------
    List[Tuple[str, str, int]]
        List of tuples containing (docstring, context, line_number).
        Context is the name of the function/class/module containing the
        docstring.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content, filename=str(file_path))

        docstrings = []

        # Module-level docstring.
        if (tree.body and isinstance(tree.body[0], ast.Expr) and
                isinstance(tree.body[0].value, ast.Constant) and
                isinstance(tree.body[0].value.value, str)):
            docstring = tree.body[0].value.value
            docstrings.append(
                (docstring, f"{file_path.name} (module)", 1)
            )

        # Function and class docstrings.
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
                docstring = ast.get_docstring(node)
                if docstring:
                    context = (
                        f"{file_path.name}::{node.name}"
                        if isinstance(node, (ast.FunctionDef,
                                             ast.AsyncFunctionDef))
                        else f"{file_path.name}::{node.name} (class)"
                    )
                    docstrings.append((docstring, context, node.lineno))

        return docstrings

    except SyntaxError as e:
        print(f"Warning: Syntax error in {file_path}: {e}")
        return []
    except Exception as e:
        print(f"Warning: Error parsing {file_path}: {e}")
        return []


########################################################################
## CODE BLOCK EXECUTION
########################################################################


def execute_code_block(
        code_block: str, context: str, setup_code: str = ""
    ) -> Tuple[bool, str]:
    """
    Execute a code block and return success status and error message.

    Parameters
    ----------
    code_block : str
        The Python code to execute.
    context : str
        Context description for error reporting.
    setup_code : str, optional
        Setup code to run before the example (e.g., imports).

    Returns
    -------
    Tuple[bool, str]
        Tuple containing:
        - success: True if code executed without errors, False otherwise.
        - error_message: Empty string on success, formatted error on
          failure.
    """
    try:
        # Combine setup and example code.
        full_code = setup_code + '\n' + code_block if setup_code else code_block

        # Create execution namespace with safe imports.
        namespace = {
            '__name__': '__main__',
            '__file__': '<docstring_example>',
        }

        # Execute the code.
        exec(compile(full_code, '<string>', 'exec'), namespace)

        return True, ""

    except SyntaxError as e:
        error_msg = (
            f"SyntaxError in {context}:\n"
            f"  {e.msg} at line {e.lineno}\n"
            f"  {e.text.strip() if e.text else ''}"
        )
        return False, error_msg

    except Exception as e:
        error_msg = (
            f"Error in {context}:\n"
            f"  {type(e).__name__}: {str(e)}"
        )
        return False, error_msg


########################################################################
## FILE PROCESSING
########################################################################


def process_file(
        file_path: Path, package_path: Path
    ) -> List[Tuple[str, str, bool, str]]:
    """
    Process a Python file and extract/execute all docstring examples.

    Parameters
    ----------
    file_path : Path
        Path to the Python file to process.
    package_path : Path
        Path to the package root for relative imports.

    Returns
    -------
    List[Tuple[str, str, bool, str]]
        List of tuples containing (context, code_block, success,
        error_message).
    """
    results = []

    # Find all docstrings in the file.
    docstrings = find_docstrings_in_file(file_path)

    # Calculate relative import path for setup.
    rel_path = file_path.relative_to(package_path.parent)
    module_parts = rel_path.with_suffix('').parts
    if module_parts[0] == 'sinkingfund':
        module_parts = module_parts[1:]

    # Build setup code for imports.
    if module_parts:
        module_name = '.'.join(module_parts)
        setup_code = f"from sinkingfund.{module_name} import *\n"
    else:
        setup_code = "from sinkingfund import *\n"

    # Add common imports that examples might need.
    setup_code += (
        "from datetime import date\n"
        "from decimal import Decimal\n"
    )

    # Extract and execute code blocks from each docstring.
    for docstring, context, line_no in docstrings:
        code_blocks = extract_code_blocks(docstring)

        for i, code_block in enumerate(code_blocks, 1):
            full_context = f"{context}:example_{i} (line {line_no})"
            success, error = execute_code_block(code_block, full_context,
                                                setup_code)
            results.append((full_context, code_block[:50] + "...",
                           success, error))

    return results


########################################################################
## MAIN EXECUTION
########################################################################


def find_python_files(package_dir: Path) -> List[Path]:
    """
    Find all Python files in the package directory.

    Parameters
    ----------
    package_dir : Path
        Path to the package directory.

    Returns
    -------
    List[Path]
        Sorted list of Python file paths, excluding __pycache__.
    """
    python_files = []
    for path in package_dir.rglob("*.py"):
        if "__pycache__" not in str(path):
            python_files.append(path)

    return sorted(python_files)


def _print_summary(
        results: List[Tuple[str, str, bool, str]]
    ) -> None:
    """
    Print execution summary with detailed results.

    Parameters
    ----------
    results : List[Tuple[str, str, bool, str]]
        List of (context, code_preview, success, error_message) tuples.
    """
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, _, success, _ in results if success)
    failed = len(results) - passed

    for context, code_preview, success, error in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{status}: {context}")
        if not success and error:
            print(f"  {error}\n")

    print(f"\nTotal: {len(results)} example(s)")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")


def main() -> int:
    """
    Execute all docstring examples and report results.

    Finds all Python files in the sinkingfund/ directory, extracts code
    blocks from docstrings, executes them, and prints a summary of
    results. Returns exit code 0 if all examples pass, 1 if any fail.

    Returns
    -------
    int
        Exit code: 0 if all examples passed, 1 if any failed.
    """
    script_dir = Path(__file__).parent
    package_dir = script_dir.parent / "sinkingfund"

    if not package_dir.exists():
        print(f"Error: Package directory not found: {package_dir}")
        return 1

    python_files = find_python_files(package_dir)

    if not python_files:
        print(f"Error: No Python files found in {package_dir}")
        return 1

    print(f"Found {len(python_files)} Python file(s) to process:\n")

    results: List[Tuple[str, str, bool, str]] = []
    for i, file_path in enumerate(python_files, 1):
        print(
            f"[{i}/{len(python_files)}] Processing {file_path.name}...",
            end=" ",
            flush=True
        )

        file_results = process_file(file_path, package_dir)
        results.extend(file_results)

        example_count = len(file_results)
        passed = sum(1 for _, _, s, _ in file_results if s)
        failed = example_count - passed

        if example_count > 0:
            print(f"{example_count} example(s), {passed} passed, "
                  f"{failed} failed")
        else:
            print("no examples found")

    _print_summary(results)

    passed_count = sum(1 for _, _, success, _ in results if success)
    failed_count = len(results) - passed_count

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
