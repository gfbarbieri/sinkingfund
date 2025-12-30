# Scripts

This directory contains utility scripts for development and maintenance tasks.

## Notebook Testing

### `run_notebooks.py`

Execute all example notebooks to verify they run without errors.

**Usage:**
```bash
poetry run python scripts/run_notebooks.py
```

**Features:**
- Executes all `.ipynb` files in the `examples/` directory
- Provides progress output and detailed error reporting
- Shows a summary of passed/failed notebooks
- Returns exit code 0 if all pass, 1 if any fail (useful for CI/CD)

### `run_notebooks.sh`

Alternative shell script version using `jupyter nbconvert` directly.

**Usage:**
```bash
./scripts/run_notebooks.sh
```

**Features:**
- Same functionality as the Python script
- Simpler implementation using jupyter command-line tools
- Less detailed error reporting than the Python version

