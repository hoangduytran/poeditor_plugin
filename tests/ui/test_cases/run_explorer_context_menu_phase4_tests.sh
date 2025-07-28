#!/bin/bash

# Explorer Context Menu Phase 4 Tests Runner
# Tests accessibility, keyboard navigation, and theme integration

echo "========================================"
echo "Explorer Context Menu Phase 4 Tests"
echo "========================================"

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT"

# Set PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test and track results
run_test() {
    local test_name="$1"
    local test_file="$2"
    
    echo "----------------------------------------"
    echo "Running: $test_name"
    echo "----------------------------------------"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if python3 "$test_file"; then
        echo "✅ $test_name - PASSED"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo "❌ $test_name - FAILED"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    echo ""
}

# Run accessibility tests
run_test "Context Menu Accessibility" "tests/ui/test_cases/test_explorer_context_menu_accessibility.py"

# Run keyboard navigation tests
run_test "Context Menu Keyboard Navigation" "tests/ui/test_cases/test_explorer_context_menu_keyboard_navigation.py"

# Run theme integration tests
run_test "Context Menu Theme Integration" "tests/ui/test_cases/test_explorer_context_menu_theme_integration.py"

# Run existing context menu tests for regression
if [ -f "tests/ui/test_cases/test_explorer_context_menu.py" ]; then
    run_test "Context Menu Base Functionality" "tests/ui/test_cases/test_explorer_context_menu.py"
fi

# Summary
echo "========================================"
echo "Test Results Summary"
echo "========================================"
echo "Total Tests: $TOTAL_TESTS"
echo "Passed: $PASSED_TESTS"
echo "Failed: $FAILED_TESTS"

if [ $FAILED_TESTS -eq 0 ]; then
    echo "🎉 All tests passed!"
    exit 0
else
    echo "⚠️  Some tests failed."
    exit 1
fi
