#!/bin/bash
set -e

# DORA Metrics Pipeline - Full Orchestration
# INPUT → COLLECTION → CALCULATION → VALIDATION → PRESENTATION

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "========================================================================"
echo "DORA METRICS PIPELINE"
echo "========================================================================"
echo ""

# Step 1: Parse Input
echo "Step 1: INPUT Layer"
echo "  Parsing ReposInput.md..."
if [ ! -f "ReposInput.md" ]; then
    echo "  ✗ ReposInput.md not found"
    exit 1
fi
echo "  ✓ Repository definitions loaded"
echo ""

# Step 2: Collection
echo "Step 2: COLLECTION Layer"
echo "  Collecting git artifacts..."
python3 src/collection/collect_git.py
echo ""

echo "  Collecting CI artifacts..."
python3 src/collection/collect_ci.py
echo ""

# Step 3: Calculation
echo "Step 3: CALCULATION Layer"
python3 src/calculations/calculate.py
echo ""

# Step 4: Validation
echo "Step 4: VALIDATION Layer"
if python3 src/validation/validate.py; then
    echo "  ✓ Quality gates passed"
else
    echo "  ✗ Quality gates failed"
    exit 1
fi
echo ""

# Step 5: Summary
echo "========================================================================"
echo "PIPELINE COMPLETE ✓"
echo "========================================================================"
echo ""
echo "Dashboard: Open public/index.html in a browser"
echo "Data location: calculations/"
echo "Raw artifacts: git_artifacts/, ci_artifacts/"
echo ""
echo "Next: Review metrics or add new repositories to ReposInput.md"
echo ""
