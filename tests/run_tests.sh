#!/bin/bash

# Script to run all UI tests for the PySide6 POEditor plugin

echo "Running PySide6 POEditor Plugin Tests"
echo "===================================="

# Set the PYTHONPATH to include the project root directory
export PYTHONPATH=$(pwd):$PYTHONPATH

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Create a log directory if it doesn't exist
mkdir -p tests/logs

# Get current date and time for log files
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="tests/logs/tests_${TIMESTAMP}.log"

echo "Logging test results to: ${LOG_FILE}"

run_test() {
    TEST_FILE=$1
    TEST_NAME=$(basename $TEST_FILE .py)
    
    echo -n "Running $TEST_NAME... "
    python -m unittest $TEST_FILE > /tmp/test_output.log 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}PASSED${NC}"
        echo "✓ $TEST_NAME: PASSED" >> $LOG_FILE
    else
        echo -e "${RED}FAILED${NC}"
        echo "✗ $TEST_NAME: FAILED" >> $LOG_FILE
        cat /tmp/test_output.log >> $LOG_FILE
        echo "" >> $LOG_FILE
    fi
}

# Run Explorer Context Menu tests
run_test tests/ui/test_cases/test_explorer_context_menu.py

# Add more tests here as they are developed
# run_test tests/ui/test_cases/test_another_component.py

echo ""
echo "Test Summary"
echo "==========="
PASSED=$(grep -c "PASSED" $LOG_FILE)
FAILED=$(grep -c "FAILED" $LOG_FILE)

echo -e "${GREEN}PASSED: $PASSED${NC}"
echo -e "${RED}FAILED: $FAILED${NC}"
echo ""
echo "See $LOG_FILE for details"
