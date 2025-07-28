#!/bin/bash

# Script to build API documentation for POEditor Plugin
# This script builds the Sphinx documentation from RST files

echo "Building API documentation for POEditor Plugin..."

# Navigate to docs directory
cd "$(dirname "$0")"

# Create build directory if it doesn't exist
mkdir -p build

# Run Sphinx build
sphinx-build -b html source build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "Documentation built successfully!"
    echo "Open the documentation by opening: build/index.html"
else
    echo "Error: Documentation build failed!"
    exit 1
fi
