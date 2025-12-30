#!/bin/bash
# Execute all example notebooks to verify they run without errors.
#
# This script uses jupyter nbconvert to execute all notebooks in the
# examples/ directory and reports which ones pass or fail.

set -e

# Get script directory and project root.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

EXAMPLES_DIR="$PROJECT_ROOT/examples"
TEMP_OUTPUT_DIR="$PROJECT_ROOT/.notebook_outputs"

# Change to project root for relative paths to work correctly.
cd "$PROJECT_ROOT"

echo "Executing all notebooks in $EXAMPLES_DIR/"
echo ""

PASSED=0
FAILED=0
FAILED_NOTEBOOKS=()

# Find and execute each notebook.
for notebook in "$EXAMPLES_DIR"/*.ipynb; do
    if [ ! -f "$notebook" ]; then
        continue
    fi

    notebook_name=$(basename "$notebook")
    echo "Executing $notebook_name..."
    
    # Execute notebook with nbconvert.
    # --to notebook keeps the output format the same.
    # --execute runs all cells.
    # --stdout suppresses the output file path.
    # --inplace would modify the original, so we don't use it.
    if jupyter nbconvert --to notebook --execute --stdout "$notebook" > /dev/null 2>&1; then
        echo "  ✓ PASSED"
        ((PASSED++))
    else
        echo "  ✗ FAILED"
        ((FAILED++))
        FAILED_NOTEBOOKS+=("$notebook_name")
    fi
done

echo ""
echo "============================================================"
echo "SUMMARY"
echo "============================================================"
echo "Total: $((PASSED + FAILED)) notebook(s)"
echo "Passed: $PASSED"
echo "Failed: $FAILED"

if [ $FAILED -gt 0 ]; then
    echo ""
    echo "Failed notebooks:"
    for nb in "${FAILED_NOTEBOOKS[@]}"; do
        echo "  - $nb"
    done
    echo ""
    echo "To see detailed errors, run:"
    echo "  jupyter nbconvert --to notebook --execute $EXAMPLES_DIR/<notebook_name>"
    exit 1
fi

# Clean up.
rm -rf "$TEMP_OUTPUT_DIR"

exit 0

