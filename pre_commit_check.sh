#!/bin/bash
# Pre-commit validation script for PySide POEditor Plugin
# Run this script before committing to ensure code quality and functionality

set -e  # Exit on first error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}PySide POEditor Plugin - Pre-Commit Validation${NC}"
echo "=============================================="

# Get timestamp for logs
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_DIR="logs"
mkdir -p $LOG_DIR

# Function to run command with logging
run_check() {
    local check_name=$1
    local command=$2
    local log_file="$LOG_DIR/precommit_${check_name}_${TIMESTAMP}.log"
    
    echo -n -e "${YELLOW}Running $check_name...${NC} "
    
    if eval $command > "$log_file" 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo -e "${RED}Error details in: $log_file${NC}"
        cat "$log_file"
        return 1
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo ""
echo -e "${BLUE}1. Code Quality Checks${NC}"
echo "====================="

# Check if Python files exist to validate
if find . -name "*.py" -not -path "./docs/*" -not -path "./__pycache__/*" | head -1 | read; then
    
    # Pylint check
    if command_exists pylint; then
        run_check "pylint" "pylint core/ panels/ plugins/ services/ managers/ models/ widgets/ --exit-zero"
    else
        echo -e "${YELLOW}Warning: pylint not found, skipping pylint check${NC}"
    fi
    
    # Pyflakes check  
    if command_exists pyflakes; then
        run_check "pyflakes" "pyflakes core/ panels/ plugins/ services/ managers/ models/ widgets/"
    else
        echo -e "${YELLOW}Warning: pyflakes not found, skipping pyflakes check${NC}"
    fi
    
    # Python compile check
    run_check "py_compile" "python -c \"import py_compile, os; [py_compile.compile(os.path.join(root, file), doraise=True) for root, dirs, files in os.walk('.') for file in files if file.endswith('.py') and not any(skip in root for skip in ['__pycache__', 'docs/build', '.git'])]\""
    
else
    echo -e "${YELLOW}No Python files found to check${NC}"
fi

echo ""
echo -e "${BLUE}2. Resource Compilation${NC}"
echo "======================"

# Check if resources need compilation
if [ -f "resources.qrc" ]; then
    if [ ! -f "resources_rc.py" ] || [ "resources.qrc" -nt "resources_rc.py" ]; then
        echo -e "${YELLOW}Resources need compilation...${NC}"
        run_check "resources" "./compile_resources.sh"
    else
        echo -e "${GREEN}✓ Resources up to date${NC}"
    fi
else
    echo -e "${YELLOW}No resources.qrc found${NC}"
fi

echo ""
echo -e "${BLUE}3. Test Execution${NC}"
echo "================"

# Run tests if test runner exists
if [ -f "tests/run_tests.sh" ]; then
    run_check "tests" "./tests/run_tests.sh"
else
    echo -e "${YELLOW}No test runner found at tests/run_tests.sh${NC}"
fi

echo ""
echo -e "${BLUE}4. Documentation Build${NC}"
echo "===================="

# Build documentation if Sphinx docs exist
if [ -f "docs/build_docs.sh" ]; then
    run_check "documentation" "./docs/build_docs.sh"
elif [ -f "docs/source/conf.py" ]; then
    run_check "documentation" "cd docs && sphinx-build -b html source build"
else
    echo -e "${YELLOW}No Sphinx documentation found${NC}"
fi

echo ""
echo -e "${BLUE}5. Application Startup Check${NC}"
echo "=========================="

# Quick application startup test
if [ -f "main.py" ]; then
    run_check "startup" "timeout 10s python -c \"import main; print('Import successful')\""
else
    echo -e "${YELLOW}No main.py found for startup test${NC}"
fi

echo ""
echo -e "${BLUE}6. Git Status Check${NC}"
echo "================="

# Show git status
echo -e "${YELLOW}Current git status:${NC}"
git status --short

echo ""
echo -e "${BLUE}Pre-Commit Validation Complete${NC}"
echo "============================="

# Check if any critical checks failed
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Ready to commit.${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Review changes: git diff --cached"
    echo "2. Commit: git commit -m \"your commit message\""
    echo "3. Push: git push origin <branch-name>"
else
    echo -e "${RED}✗ Some checks failed. Please fix issues before committing.${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}Log files created in: $LOG_DIR/${NC}"
ls -la $LOG_DIR/precommit_*_${TIMESTAMP}.log 2>/dev/null || echo "No log files created"
