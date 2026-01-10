# Python Style Guide

## 1. Overview

* Write for maintainability. Comments explain why, not what.
* Use deterministic behavior. Validate inputs. Document boundaries.
* Centralize utilities. Put common logic in reusable functions.

## 2. Code Formatting

### File Structure

Start each module with a Sphinx-friendly docstring:

```python
"""
Title
=====

Purpose and key features.

Examples
--------
.. code-block:: python

   # Minimal runnable example
"""
```

Use section banners:

```python
########################################################################
## IMPORTS
########################################################################
```

### Imports

* Group imports: (1) stdlib, (2) third-party, (3) local.
* One blank line between groups.
* One import per line.

### Spacing

* Indentation: 4 spaces, never tabs.
* Two blank lines between top-level declarations.
* One blank line between methods in classes.
* Spaces around binary operators (`a + b`, not `a+b`).
* No extra spaces inside parentheses, brackets, or braces.
* Place comments above code, not at end of line.
* Blank line before multi-line comment blocks.

### Line Length

* Code: 79 characters maximum.
* Comments and docstrings: 72 characters maximum.
* Wrap code using hanging indents within parentheses.
* Hard-wrap comments and docstrings at the limit.

```toml
[tool.black]
line-length = 79

[tool.ruff]
line-length = 79

[tool.docformatter]
wrap-summaries = 72
wrap-descriptions = 72
```

### Writing Style

* Complete sentences in comments and docstrings. End with period.
* No em dashes. Use commas, parentheses, or separate sentences.
* No semicolons. Use separate sentences or lines.
* Use plain English. Define acronyms on first use.
* US English spelling.
* No emojis or special symbols in comments or docstrings.

## 3. Naming Conventions

* Use descriptive names: `get_next`, `filter_range`, `iter_records`.
* Avoid boolean ambiguity. Use `include_start` instead of `inclusive`.
* Prefer `Enum` for controlled vocabularies over string literals.
* Use `@dataclass(frozen=True, order=True)` for immutable value objects.

Example:

```python
class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

@dataclass(frozen=True, order=True)
class Record:
    id: str
    value: int
```

## 4. Documentation

### Comments

Use uppercase intent tags:

* `# BUSINESS GOAL:` links behavior to requirements.
* `# DESIGN CHOICE:` records alternatives and rationale.
* `# EARLY EXIT OPTIMIZATION:` explains early returns.
* `# INVARIANT:` states required conditions.
* `# FAILURE MODE:` describes error conditions and handling.
* `# PERFORMANCE NOTE:` justifies complexity.
* `# EDGE CASE:` highlights boundary conditions.
* `# SIDE EFFECTS:` notes mutations, I/O, or persistence.

### Docstrings

Every public object has a NumPy-style docstring. Include Parameters, Returns, Raises, Notes, and Examples as applicable.

```python
def filter_by_range(
    items: list[Record],
    start: date,
    end: date,
    include_boundaries: bool = True
) -> list[Record]:
    """
    Filter records within a date range.

    Parameters
    ----------
    items : list[Record]
        Records to filter.
    start : date
        Start date of the range.
    end : date
        End date of the range.
    include_boundaries : bool, optional
        Include items on boundary dates. Defaults to True.

    Returns
    -------
    list[Record]
        Records within the specified range.

    Raises
    ------
    ValueError
        If start date is after end date.

    Examples
    --------
    .. code-block:: python

       records = [Record("1", 10), Record("2", 20)]
       filtered = filter_by_range(records, date(2025, 1, 1), date(2025, 1, 31))
       len(filtered)  # 2
    """
    if start > end:
        raise ValueError("start date must be <= end date")
    # ...
```

## 5. Type Hints

* Add type annotations to all function signatures.
* Use `from __future__ import annotations` when supported.
* Avoid mutable defaults. Use `value: int | None = None` and set inside.

```python
from __future__ import annotations

from datetime import date

def process_items(
    items: list[Record],
    threshold: int,
    reference_date: date | None = None
) -> list[Record]:
    if reference_date is None:
        reference_date = date.today()
    # ...
```

## 6. Validation and Error Handling

* Validate inputs early in constructors and functions.
* Write clear, actionable error messages.
* Document raised exceptions in docstrings.

Common validation patterns:

```python
def _validate(self) -> None:
    if self.value < 0:
        raise ValueError("value must be non-negative")
    
    if self.status is None:
        raise ValueError("status is required")
    
    if self.start_date > self.end_date:
        raise ValueError("start_date must be <= end_date")
    
    if self.count is not None and self.count < 1:
        raise ValueError("count must be >= 1 if provided")
```

## 7. Performance Patterns

* Provide iterator forms to avoid materializing sequences.
* Use early returns for non-overlapping ranges.
* Prefer efficient algorithms over naive iteration when appropriate.

Pattern:

```python
def iter_records(
    self,
    start: date,
    end: date
) -> Iterator[Record]:
    """
    Yield records in range [start, end].
    """
    # EARLY EXIT OPTIMIZATION: skip if no overlap
    if end < self.min_date or start > self.max_date:
        return
    
    # DESIGN CHOICE: fast-forward to first >= start
    current = self._find_first_after(start)
    while current is not None and current.created_date <= end:
        yield current
        current = self._get_next(current)

def get_records(
    self,
    start: date,
    end: date
) -> list[Record]:
    """
    Return list of records in range.
    """
    return list(self.iter_records(start, end))
```

## 8. Testing

* Use doctests from examples. Run in CI.
* Write unit tests with pytest for validation and core paths.
* Use property-based tests (Hypothesis) for sequences and boundaries.
* Add regression tests for known edge cases.

## 9. Tooling Configuration

### pyproject.toml

```toml
[tool.black]
line-length = 79

[tool.ruff]
line-length = 79
select = [
  "E",   # pycodestyle
  "F",   # pyflakes
  "B",   # bugbear
  "I",   # isort
  "UP",  # pyupgrade
  "ANN", # type hints
  "SIM", # complexity reductions
  "PL",  # pylint rules
]
ignore = ["D100", "D101", "D102", "D103"]

[tool.pydocstyle]
convention = "numpy"
add-ignore = "D401,D205"

[tool.mypy]
python_version = "3.11"
strict = true
warn_unused_ignores = true
warn_redundant_casts = true
warn_return_any = true
disallow_untyped_defs = true
no_implicit_optional = true

[tool.docformatter]
wrap-summaries = 72
wrap-descriptions = 72

[tool.pytest.ini_options]
addopts = "-q --doctest-glob='*.py' --doctest-modules"
```

### Pre-commit Hooks

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.8.0
    hooks:
      - id: black
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
      - id: ruff-format
  - repo: https://github.com/myint/docformatter
    rev: v1.7.5
    hooks:
      - id: docformatter
        args: ["--in-place", "--wrap-summaries", "72", "--wrap-descriptions", "72"]
  - repo: https://github.com/pycqa/pydocstyle
    rev: 6.3.0
    hooks:
      - id: pydocstyle
        additional_dependencies: [pydocstyle[toml]]
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.2
    hooks:
      - id: mypy
```

### CI (GitHub Actions)

```yaml
name: ci
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -U pip
      - run: pip install -e .[dev]
      - run: pre-commit run --all-files
      - run: pytest
```

### Sphinx Configuration

```python
# docs/conf.py
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.doctest",
]
napoleon_google_docstring = False
napoleon_numpy_docstring = True
autosummary_generate = True
```

## 10. Templates

### Module Header

```python
"""
Module Name
===========

Brief description of purpose and key functionality.

Examples
--------
.. code-block:: python

   from module import Record
   record = Record("id", 42)
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Iterator

########################################################################
## MODELS
########################################################################
```

### Class Docstring

```python
@dataclass(frozen=True, order=True)
class Record:
    """
    Immutable data record.

    Attributes
    ----------
    id : str
        Unique identifier.
    value : int
        Numeric value.
    created_date : date
        Creation date.

    Notes
    -----
    Immutability ensures data integrity. Ordering enables sorting.
    """
    id: str
    value: int
    created_date: date
```

### Iterator Pattern

```python
def iter_records(
    self,
    start: date,
    end: date
) -> Iterator[Record]:
    """
    Yield records in range [start, end].
    """
    # EARLY EXIT OPTIMIZATION: check for overlap
    if end < self.min_date or start > self.max_date:
        return
    
    # DESIGN CHOICE: use efficient lookup
    current = self._find_first_after(start)
    while current is not None and current.created_date <= end:
        yield current
        current = self._get_next(current)

def get_records(
    self,
    start: date,
    end: date
) -> list[Record]:
    """
    Return list of records in range.
    """
    return list(self.iter_records(start, end))
```

### Validation Pattern

```python
def _validate(self) -> None:
    """
    Validate record attributes.
    """
    if not self.id or not self.id.strip():
        raise ValueError("id cannot be empty")
    
    if self.value < 0:
        raise ValueError("value must be non-negative")
    
    if self.created_date > date.today():
        raise ValueError("created_date cannot be in the future")
```