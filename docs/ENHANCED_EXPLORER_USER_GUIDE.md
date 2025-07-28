# Enhanced Explorer User Guide

**Date:** July 28, 2025  
**Component:** Enhanced Explorer Panel  
**Version:** 2.0.0  
**Status:** Production

## Introduction

The Enhanced Explorer panel provides an intuitive interface for managing files and directories within the POEditor application. This guide covers the key features and how to use them effectively.

## Table of Contents

1. [Basic Navigation](#basic-navigation)
2. [File Operations](#file-operations)
3. [Context Menu](#context-menu)
4. [Drag and Drop](#drag-and-drop)
5. [Keyboard Shortcuts](#keyboard-shortcuts)
6. [Search and Filtering](#search-and-filtering)
7. [Tips and Tricks](#tips-and-tricks)

## Basic Navigation

### Directory Navigation

- **Up Button**: Click the "↑ Up" button to navigate to the parent directory
- **Double-Click**: Double-click a folder to navigate into it
- **Path Display**: The current path is shown above the file list

### View Options

- **Icon View**: View files as icons with names
- **List View**: View files as a detailed list with additional information
- **Column Sorting**: Click column headers to sort files by name, size, type, or date

## File Operations

### Selection

- **Single Item**: Click on a file or folder to select it
- **Multiple Items**: 
  - Hold Ctrl (Cmd on macOS) and click to select multiple individual items
  - Hold Shift and click to select a range of items
- **Select All**: Ctrl+A (Cmd+A on macOS) to select all visible items

### Basic Operations

- **Open**: Double-click a file to open it in the appropriate editor
- **Rename**: Select a file, press F2 (or select "Rename" from the context menu)
- **Delete**: Select file(s), press Delete (or select "Delete" from the context menu)
- **Copy/Cut/Paste**: Use the context menu or standard keyboard shortcuts

## Context Menu

Right-click on files or folders to access a context menu with the following options:

### File Context Menu

- **Open**: Open the file in the default editor
- **Open With**: Choose an application to open the file with
- **Copy**: Copy the selected file(s)
- **Cut**: Cut the selected file(s)
- **Paste**: Paste previously copied/cut files (only visible when applicable)
- **Delete**: Move the file to the trash/recycle bin
- **Rename**: Rename the file
- **Duplicate**: Create a copy of the file in the same location
- **Properties**: View file properties

### Directory Context Menu

- **Open**: Open the folder
- **Copy**: Copy the selected folder(s)
- **Cut**: Cut the selected folder(s)
- **Paste**: Paste previously copied/cut files into this folder
- **Delete**: Move the folder to the trash/recycle bin
- **Rename**: Rename the folder
- **New File**: Create a new file in this folder
- **New Folder**: Create a new subfolder in this folder
- **Properties**: View folder properties

### Multiple Selection Context Menu

When multiple items are selected, the context menu shows operations that can be performed on all selected items:
- **Copy**: Copy all selected items
- **Cut**: Cut all selected items
- **Delete**: Move all selected items to the trash/recycle bin

## Drag and Drop

### Within the Application

- **Move**: Drag files/folders to another folder to move them
- **Copy**: Hold Ctrl (Option on macOS) while dragging to copy instead of move

### With External Applications

- **Drag Out**: Drag files from the explorer to other applications
- **Drag In**: Drag files from other applications to import them

### Visual Feedback

- **Highlighted Drop Target**: The potential drop location is highlighted
- **Operation Indicator**: The cursor changes to indicate whether the operation will be a copy or move

## Keyboard Shortcuts

| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Copy | Ctrl+C | Cmd+C |
| Cut | Ctrl+X | Cmd+X |
| Paste | Ctrl+V | Cmd+V |
| Delete | Delete | Delete |
| Permanent Delete | Shift+Delete | Shift+Delete |
| Rename | F2 | Enter |
| Select All | Ctrl+A | Cmd+A |
| Refresh | F5 | Cmd+R |
| New Folder | Ctrl+Shift+N | Cmd+Shift+N |
| Undo | Ctrl+Z | Cmd+Z |
| Redo | Ctrl+Y | Cmd+Shift+Z |
| Navigate Up | Backspace | Cmd+↑ |
| Search | Ctrl+F | Cmd+F |

## Search and Filtering

### Basic Search

- Type in the search bar to filter files by name
- Results update as you type
- Press Enter to search for file contents (where applicable)

### Advanced Filtering

- **File Type Filters**: Use wildcards like `*.txt` to filter by file extension
- **Name Filters**: Enter text to filter by filename
- **Search Options**: Right-click the search field for advanced options:
  - Case sensitivity
  - Whole word matching
  - Regular expression search

## Tips and Tricks

### Efficient Navigation

- **Breadcrumb Navigation**: Click on segments of the path to jump to specific parent directories
- **History Navigation**: Use the back/forward buttons (if available) to navigate through your history

### File Management

- **Duplicate and Rename**: Quickly create a modified version of a file by duplicating and immediately renaming
- **Drag with Right Mouse Button**: Drag with the right mouse button to get a context menu on drop that lets you choose between Copy, Move, or Link

### Selection Techniques

- **Inverse Selection**: Ctrl+Click (Cmd+Click on macOS) on a selected item to deselect it
- **Keyboard Navigation**: Use arrow keys to navigate, spacebar to select/deselect

### Customization

- **Column Visibility**: Right-click on column headers to show/hide specific columns
- **Sort Order**: Click a column header once to sort ascending, twice for descending

## Troubleshooting

### Common Issues

- **Item Not Visible**: Check the search/filter field and clear it
- **Cannot Paste**: Ensure you have copied files to the clipboard first
- **Drag and Drop Not Working**: Verify you have the necessary permissions in the target location

### Error Recovery

- **Undo**: Most operations can be undone with Ctrl+Z (Cmd+Z on macOS)
- **Recover from Trash**: Deleted items can be recovered from the system trash/recycle bin

## Need Help?

For additional assistance:
- Check the in-app help documentation
- Visit the support portal at support.poeditor.com
- Contact technical support at support@poeditor.com
