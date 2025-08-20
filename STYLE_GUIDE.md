# Python Style Guide — Sinking Fund & Analytics Codebase

## 1. Philosophy

* **Clarity over cleverness**: optimize for future readers. Comment intent and tradeoffs.
* **Explain *why***: comments should add design context, not narrate syntax.
* **Deterministic behavior**: predictable APIs, explicit boundaries (inclusive/exclusive), and validated inputs.
* **Single-source-of-truth utilities**: calendar math, money arithmetic, and parsing live in well-tested helpers.

## 2. File layout & spacing conventions

* Start each module with a **narrative, Sphinx-friendly top-level docstring**:

  * Title, overview, abstractions, features, examples (`.. code-block:: python`).

* Use **section banners** like:

  ```python
  ########################################################################
  ## IMPORTS
  ########################################################################
  ```

* Import groups: (1) stdlib, (2) third-party, (3) local. One blank line between groups.
* Vertical whitespace:

  * Two blank lines between **top-level** declarations.
  * One blank line between **methods** inside classes.
  * Keep generous spacing around comment blocks for readability.

## 2.1 Writing style (prose & punctuation)

* **Complete sentences** in narrative comments and docstrings, with a **period at the end**.
* **No em dashes**. Prefer commas, parentheses, or splitting into two sentences.
* **No semicolons**. Use separate sentences or new lines instead.
* **Plain English** over jargon. Define acronyms on first use in a docstring or comment block.
* **US English** spelling.
* **Inline comments policy**:

  * Do **not** use end-of-line comments. Place block comments **above** the code they describe.
  * Each line starts with `# ` (hash and a space) and aligns with the code's indentation level.
  * Insert a blank line **before** a multi-line comment block when it separates logical steps.

## 2.2 Whitespace & PEP 8 spacing

* Indentation is **4 spaces**, never tabs.
* Spaces around binary operators (`a + b`, not `a+b`), after commas, and after colons in dict literals. No extra spaces **inside** parentheses/brackets/braces.
* One import per line. Keep import groups separated by one blank line.
* Two blank lines between top-level declarations. One blank line between class methods (already in §2).
* Prefer implicit line joining inside parentheses for line wraps. Avoid backslashes.

## 2.3 Line length & wrapping

**Profiles**

* **PEP 8 classic**: code <= 79, comments/docstrings <= 72.

**Wrapping rules**

* **Comments/docstrings**: hard-wrap at the chosen comment limit.
* **Code**: wrap at the code limit using hanging indents within parentheses. Keep operators at line breaks consistent and readable.

**Tooling snippet for the PEP 8 classic profile**

```toml
[tool.black]
line-length = 79

[tool.ruff]
line-length = 79

[tool.docformatter]
wrap-summaries = 72
wrap-descriptions = 72
```

**Optional `.editorconfig` to help editors wrap comments**

```ini
root = true

[*]
indent_style = space
indent_size = 4
insert_final_newline = true
trim_trailing_whitespace = true
max_line_length = 79
```

## 3. Naming, APIs, and data modeling

* Names are descriptive and literal, e.g., `next_instance`, `instances_in_range`, `iter_instances_in_range`.
* Avoid boolean ambiguity. Prefer `include_reference_date` over `inclusive`.
* Types everywhere. Add `from __future__ import annotations` in packages that support it.
* Prefer `Enum` for controlled vocabularies (e.g., `Frequency`) over string literals.
* Value objects (`BillInstance`, etc.) use `@dataclass(frozen=True, order=True)`.

## 4. Money & dates (production rules)

* Use `Decimal` (quantize to cents) rather than `float`.
* No mutable defaults: function signatures use `reference_date: date | None = None` and set inside.
  * Document and test **inclusive/exclusive** boundaries.
  * Delegate calendar arithmetic to a single helper (`increment_date`). Cover month-end and leap-year cases.

## 5. Comments: your signature style

Use uppercase intent tags that carry unique information.

* `# BUSINESS GOAL:` link behavior to user/business need.
* `# DESIGN CHOICE:` record alternatives and why this won.
* `# EARLY EXIT OPTIMIZATION:` explain pruning paths.
* `# INVARIANT:` state what must hold.
* `# FAILURE MODE:` describe what can go wrong and mitigation.
* `# PERFORMANCE NOTE:` justify complexity or iteration.
* `# EDGE CASE:` call out month-end, leap, DST, etc.
* `# SIDE EFFECTS:` persistence, I/O, mutation.

## 6. Docstrings (Sphinx/NumPy + doctest)

* Every public object has a NumPy-style docstring with these sections where applicable: Parameters, Returns, Raises, Notes, Examples.
* Examples must be realistic and doctestable (runnable in CI).
* Prefer small, focused code blocks with expected output shown as comments.

**Function template**

```python
def foo(bar: int, when: date | None=None) -> Baz:
    """
    Compute X from Y.

    Parameters
    ----------
    bar : int
        Meaningful description.
    when : datetime.date, optional
        Reference date. If None, defaults to today.

    Returns
    -------
    Baz
        Description of the result.

    Raises
    ------
    ValueError
        If input constraints are violated.

    Notes
    -----
    Brief rationale or algorithmic remark.

    Examples
    --------
    .. code-block:: python

       result = foo(3, date(2025, 1, 31))
       result.ok # True.
    """
```

## 7. Validation & error handling

* Validate early in constructors/factories. Keep error messages actionable.
* Typical checks:

  * `amount_due >= 0`
  * For recurring schedules: require `start_date` + `frequency`; allow either `occurrences` XOR `end_date` (or neither for open-ended); `interval >= 1`.
  * Ensure `start_date <= end_date` if both given.
* Document `Raises` in docstrings.

## 8. Performance patterns

* Provide iterator forms to avoid materializing long sequences.
  * `iter_instances_in_range(...)` is the primitive. `instances_in_range(...)` wraps `list(...)`.
* Add fast-forward math to jump near `start_reference` instead of stepping from `start_date` when possible.
* Add early-return checks for non-overlapping ranges.

## 9. Testing strategy

* **Doctests** from examples run in CI.
* **Unit tests** (pytest) cover validation errors and core paths.
* **Property-based tests** (Hypothesis) for calendar math: monotonic sequences, month-end behavior, leap years.
* Golden tests around known tricky anchors (e.g., Jan 31 → Feb 28/29 → Mar 31).

## 10. Tooling & enforcement

Use these settings via `pyproject.toml` (copy/paste and adjust):

```toml
[tool.black]
line-length = 100

[tool.ruff]
line-length = 100
select = [
  "E",  # pycodestyle
  "F",  # pyflakes
  "B",  # bugbear
  "I",  # isort
  "UP", # pyupgrade
  "ANN",# type hints
  "SIM",# complexity reductions
  "PL", # pylint rules (subset)
]
ignore = ["D100","D101","D102","D103"] # pydocstyle handled separately

[tool.pydocstyle]
convention = "numpy"
add-ignore = "D401,D205" # sentence case; allow blank line flexibility

[tool.mypy]
python_version = "3.11"
strict = true
warn_unused_ignores = true
warn_redundant_casts = true
warn_return_any = true
disallow_untyped_defs = true
no_implicit_optional = true

[tool.docformatter]
wrap-summaries = 100
wrap-descriptions = 100

[tool.pytest.ini_options]
addopts = "-q --doctest-glob='*.py' --doctest-modules"
```

**Pre-commit hooks (`.pre-commit-config.yaml`)**

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.6
    hooks:
      - id: ruff
      - id: ruff-format
  - repo: https://github.com/myint/docformatter
    rev: v1.7.5
    hooks:
      - id: docformatter
        args: ["--in-place", "--wrap-summaries", "100", "--wrap-descriptions", "100"]
  - repo: https://github.com/pycqa/pydocstyle
    rev: 6.3.0
    hooks:
      - id: pydocstyle
        additional_dependencies: [pydocstyle[toml]]
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
```

**CI (GitHub Actions)**

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

**Sphinx** (enable napoleon + doctest)

```python
# docs/conf.py (snippets)
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

## 11. Required templates

**Module header template**

```python
"""
Title
=====

Short narrative describing purpose, abstractions, features, and examples.

Examples
--------
.. code-block:: python

   # concise, runnable example(s)
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Iterator, Optional

########################################################################
## MODELS
########################################################################
```

**Class docstring template**

```python
@dataclass(frozen=True, order=True)
class BillInstance:
    """
    A specific occurrence of a bill with a concrete due date and amount.

    Attributes
    ----------
    bill_id : str
        Unique identifier of the parent bill.
    amount_due : Decimal
        Monetary amount (quantized to cents).
    due_date : date
        When this instance is due.

    Notes
    -----
    Explain design choices (immutability, ordering) and typical usage.
    """
```

**Iterator + list wrapper**

```python
def iter_instances_in_range(self, start_reference: date, end_reference: date) -> Iterator[BillInstance]:
    """Yield instances in [start_reference, end_reference]."""
    # EARLY EXIT OPTIMIZATION: skip if no overlap
    # DESIGN CHOICE: fast-forward to first >= start_reference
    ...

def instances_in_range(self, start_reference: date, end_reference: date) -> list[BillInstance]:
    """Return a list of instances in the range; wraps iterator."""
    return list(self.iter_instances_in_range(start_reference, end_reference))
```

**Validation pattern**

```python
def _validate(self) -> None:
    if self.amount_due < Decimal("0"):
        raise ValueError("amount_due must be non-negative")
    if self.recurring:
        if self.start_date is None:
            raise ValueError("start_date required for recurring bills")
        if self.frequency is None:
            raise ValueError("frequency required for recurring bills")
        if self.interval is not None and self.interval < 1:
            raise ValueError("interval must be >= 1")
        if self.end_date and self.occurrences and self.occurrences > 0:
            raise ValueError("Provide either occurrences or end_date, not both")
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValueError("end_date must be >= start_date")
```

## 12. Review checklist (humans & agents)

* [ ] Module has narrative Sphinx docstring with runnable examples.
* [ ] Section banners present; import groups ordered.
* [ ] Types everywhere; `Enum` for token domains; `Decimal` for money.
* [ ] No mutable defaults; inclusive/exclusive boundaries documented.
* [ ] Validation performed; `Raises` documented.
* [ ] Iterator provided where sequences can be long.
* [ ] Uppercase intent-tag comments used **only** where they add design context.
* [ ] Doctests + unit tests added; edge cases covered.

## 13. AI agent compliance block

Paste this into an AI system/developer prompt to enforce style:

```text
Follow this exact style:
- Start files with a narrative Sphinx docstring (title, overview, abstractions, features, examples).
- Use section banners with `########################################################################`.
- Use NumPy/Sphinx docstrings (Parameters/Returns/Raises/Notes/Examples) with runnable examples.
- Comment with uppercase intent tags: BUSINESS GOAL, DESIGN CHOICE, EARLY EXIT OPTIMIZATION, INVARIANT, FAILURE MODE, PERFORMANCE NOTE, EDGE CASE, SIDE EFFECTS.
- **Writing style**: Always end sentences with periods, even if in bulleted lists, even in in-line comments in Examples in doc-strings. Do not use em dashes or semicolons. Write in plain English and use US spelling.
- **Comments**: never end-of-line; always above the code; start lines with `# ` aligned to code; wrap 72 if using PEP classic.
- **Line lengths**: wrap code at 79 if using PEP classic. Prefer implicit line joining in parentheses.
- Use Decimal for money. Use Enum for frequency. Use @dataclass(frozen=True, order=True) for instances. Use type hints everywhere.
- No mutable datetime defaults. Set None in signature and assign inside.
- Provide iterator APIs and fast-forward logic. Add early exits for non-overlapping ranges.
- Validate inputs early and raise clear errors. Document Raises.
- Keep comments verbose but *non-repetitive* (explain rationale and tradeoffs, not syntax).
```