#!/bin/bash
# Compile Qt resource files
echo "Compiling icons.qrc to icons_rc.py..."
/Volumes/MYPART/hoangduytran/Dev/pyenv_3110/bin/python /Volumes/MYPART/hoangduytran/Dev/pyenv_3110/bin/pyside6-rcc icons.qrc -o icons_rc.py
echo "Done! Resource file compiled successfully."
