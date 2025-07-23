#!/bin/bash
# Compile Qt resources into Python module

# Ensure we're in the correct directory
cd "$(dirname "$0")"

echo "Compiling resources.qrc..."

# Use PySide6 pyside6-rcc command to compile resources
pyside6-rcc resources.qrc -o resources_rc.py

# Check if compilation was successful
if [ $? -eq 0 ]; then
    echo "Resources compiled successfully to resources_rc.py"
else
    echo "Error: Failed to compile resources"
    exit 1
fi

echo "Done!"
