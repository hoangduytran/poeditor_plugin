# Activity Bar Component Changes

## File Organization

The Activity Bar demo files have been reorganized according to the project's file organization rules:

1. Moved `demos/activity_bar_demo.py` to `tests/widgets/test_cases/activity_bar_demo.py`
2. Created `tests/widgets/test_cases/run_activity_bar_demo.sh` script
3. Updated the root `run_activity_bar_demo.sh` script to point to the new location
4. Removed the empty `demos` directory

## VS Code Tasks

Added VS Code tasks to make running the demos and tests easier:
- `Run Activity Bar Demo`: Launches the activity bar demo application
- `Run Activity Bar Tests`: Runs the pytest test suite for activity bar components

## Directory Structure

```
tests/
├── widgets/
│   ├── test_activity_bar.py        # Tests for ActivityBar
│   ├── test_activity_button.py     # Tests for ActivityButton
│   ├── test_cases/
│   │   ├── activity_bar_demo.py    # Demo application for ActivityBar
│   │   └── run_activity_bar_demo.sh # Script to run the demo
├── managers/
│   └── test_activity_manager.py    # Tests for ActivityManager
```

## Running the Demo

To run the activity bar demo, you can:
1. Use VS Code tasks: View > Command Palette > "Tasks: Run Task" > "Run Activity Bar Demo"
2. Run the script directly: `./tests/widgets/test_cases/run_activity_bar_demo.sh`
3. Use the root script: `./run_activity_bar_demo.sh`
