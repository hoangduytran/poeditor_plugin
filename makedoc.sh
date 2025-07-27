#!/bin/bash
# makedoc.sh - Documentation helper script for POEditor Plugin
# Usage: ./makedoc.sh [command]
#   where command is one of: clear, update, generate, all, help

set -e  # Exit on error

# Directory variables
DOCS_DIR="docs"
BUILD_DIR="$DOCS_DIR/build"
SOURCE_DIR="$DOCS_DIR/source"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display help
show_help() {
    echo -e "${YELLOW}POEditor Plugin Documentation Helper${NC}"
    echo "Usage: ./makedoc.sh [command]"
    echo ""
    echo "Commands:"
    echo "  clear     - Remove all generated documentation files"
    echo "  update    - Update API reference documentation (module autodocs)"
    echo "  generate  - Generate HTML documentation (may overwrite RST files)"
    echo "  build     - Build HTML documentation without overwriting RST files"
    echo "  open      - Open the generated documentation in the default browser"
    echo "  all       - Run clear, update, and generate in sequence"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./makedoc.sh clear     # Clear all generated documentation"
    echo "  ./makedoc.sh update    # Update API docs only"
    echo "  ./makedoc.sh generate  # Generate HTML from current source (may overwrite RST)"
    echo "  ./makedoc.sh build     # Build HTML without overwriting RST files"
    echo "  ./makedoc.sh all       # Full rebuild of documentation"
}

# Function to clear the build directory
clear_docs() {
    echo -e "${YELLOW}Clearing documentation build files...${NC}"
    
    # Remove the build directory
    if [ -d "$BUILD_DIR" ]; then
        rm -rf "$BUILD_DIR"
        echo -e "${GREEN}Removed $BUILD_DIR${NC}"
    else
        echo -e "${YELLOW}$BUILD_DIR does not exist, nothing to clear${NC}"
    fi
    
    # Optionally clear any auto-generated source files
    # Uncomment the following if you have auto-generated files that should be cleared
    # find "$SOURCE_DIR" -name "*.auto.rst" -type f -delete
    
    echo -e "${GREEN}Documentation cleared successfully${NC}"
}

# Function to update API documentation
update_docs() {
    echo -e "${YELLOW}Updating API documentation...${NC}"
    
    # This typically involves running autodoc tools, sphinx-apidoc, etc.
    # Adjust this command based on your specific setup
    if [ -f "./generate_docs.py" ]; then
        python ./generate_docs.py --update-only
        echo -e "${GREEN}API documentation updated successfully${NC}"
    else
        # If you don't have a Python script, you can use sphinx-apidoc directly
        echo -e "${YELLOW}Using sphinx-apidoc to update API docs...${NC}"
        sphinx-apidoc -f -o "$SOURCE_DIR" . -e -M -d 2 --no-toc
        echo -e "${GREEN}API documentation updated successfully${NC}"
    fi
}

# Function to generate HTML documentation
generate_docs() {
    echo -e "${YELLOW}Generating HTML documentation...${NC}"
    
    # Ensure build directory exists
    mkdir -p "$BUILD_DIR"
    
    # Use generate_docs.py if available, otherwise use sphinx-build directly
    if [ -f "./generate_docs.py" ]; then
        python ./generate_docs.py
    else
        sphinx-build -b html "$SOURCE_DIR" "$BUILD_DIR/html"
    fi
    
    echo -e "${GREEN}Documentation generated successfully${NC}"
    echo -e "Open ${YELLOW}$BUILD_DIR/html/index.html${NC} in your browser to view it"
}

# Function to build HTML without regenerating RST files
build_html() {
    echo -e "${YELLOW}Building HTML documentation from existing RST files...${NC}"
    
    # Ensure build directory exists
    mkdir -p "$BUILD_DIR"
    
    # Use sphinx-build directly to avoid regenerating RST files
    sphinx-build -b html "$SOURCE_DIR" "$BUILD_DIR/html"
    
    echo -e "${GREEN}HTML documentation built successfully${NC}"
    echo -e "Open ${YELLOW}$BUILD_DIR/html/index.html${NC} in your browser to view it"
}

# Function to open documentation in browser
open_docs() {
    echo -e "${YELLOW}Opening documentation in browser...${NC}"
    
    HTML_INDEX="$BUILD_DIR/html/index.html"
    if [ -f "$HTML_INDEX" ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            open "$HTML_INDEX"
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            xdg-open "$HTML_INDEX" &> /dev/null
        else
            # Fallback for other systems
            echo -e "${YELLOW}Cannot automatically open browser on this OS.${NC}"
            echo -e "Please open ${GREEN}$HTML_INDEX${NC} manually."
        fi
    else
        echo -e "${RED}Documentation not found. Please generate it first with:${NC}"
        echo -e "  ./makedoc.sh generate"
    fi
}

# Parse command
case "$1" in
    "clear")
        clear_docs
        ;;
    "update")
        update_docs
        ;;
    "generate")
        generate_docs
        ;;
    "build")
        build_html
        ;;
    "open")
        open_docs
        ;;
    "all")
        clear_docs
        update_docs
        build_html
        open_docs
        ;;
    "help" | "--help" | "-h" | "")
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        show_help
        exit 1
        ;;
esac

exit 0
