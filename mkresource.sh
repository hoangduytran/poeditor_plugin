#!/bin/bash
# Compile Qt resource files

# Check if resources.qrc exists
if [ ! -f "resources.qrc" ]; then
    echo "Error: resources.qrc file not found!"
    exit 1
fi

echo "Compiling resources.qrc to resources_rc.py..."

# Try to find pyside6-rcc in various locations
if command -v pyside6-rcc >/dev/null 2>&1; then
    RCC_CMD="pyside6-rcc"
elif [ -f "/Volumes/MYPART/hoangduytran/Dev/pyenv_3110/bin/pyside6-rcc" ]; then
    RCC_CMD="/Volumes/MYPART/hoangduytran/Dev/pyenv_3110/bin/pyside6-rcc"
else
    echo "Error: pyside6-rcc not found! Please install PySide6 or check your PATH."
    exit 1
fi

# Compile the resource file to resources/resources_rc.py (where it belongs)
if $RCC_CMD resources.qrc -o resources/resources_rc.py; then
    echo "✅ Resource file compiled successfully to resources/resources_rc.py"
else
    echo "❌ Failed to compile resource file"
    exit 1
fi
