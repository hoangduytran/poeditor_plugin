#!/bin/zsh
# Run theme test files

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${0:A}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/../../.."

# Change to the project root directory
cd "$PROJECT_ROOT"

# Display menu
echo "===== Theme Testing Tools ====="
echo "1) Run QPushButton Theme Test"
echo "2) Run Theme Switcher Test"
echo "3) Exit"

echo -n "Choose an option (1-3): "
read choice

case $choice in
    1)
        echo "Running QPushButton Theme Test..."
        # Set PYTHONPATH to include project root to help with imports
        PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH" python "$PROJECT_ROOT/tests/ui/test_cases/test_qpushbutton_theme.py"
        ;;
    2)
        echo "Running Theme Switcher Test..."
        # Set PYTHONPATH to include project root to help with imports
        PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH" python "$PROJECT_ROOT/tests/ui/test_cases/test_theme_switcher.py"
        ;;
    3)
        echo "Exiting."
        exit 0
        ;;
    *)
        echo "Invalid option. Exiting."
        exit 1
        ;;
esac
