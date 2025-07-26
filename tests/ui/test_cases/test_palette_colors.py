#!/usr/bin/env python3
"""
Test to compare palette colors and find where #094771 is coming from.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QListWidget, QListWidgetItem, QLabel
from PySide6.QtGui import QPalette, QColor

class PaletteTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Palette Color Test")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Show current palette colors
        app = QApplication.instance()
        palette = app.palette()
        
        title = QLabel("Current Application Palette Colors:")
        title.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px;")
        layout.addWidget(title)
        
        # Display key palette colors
        colors_to_check = [
            ("Window", palette.color(QPalette.ColorRole.Window)),
            ("WindowText", palette.color(QPalette.ColorRole.WindowText)),
            ("Base", palette.color(QPalette.ColorRole.Base)),
            ("Text", palette.color(QPalette.ColorRole.Text)),
            ("Button", palette.color(QPalette.ColorRole.Button)),
            ("ButtonText", palette.color(QPalette.ColorRole.ButtonText)),
            ("Highlight", palette.color(QPalette.ColorRole.Highlight)),
            ("HighlightedText", palette.color(QPalette.ColorRole.HighlightedText)),
        ]
        
        for name, color in colors_to_check:
            label = QLabel(f"{name}: {color.name()}")
            # Set background to show the actual color
            label.setStyleSheet(f"background-color: {color.name()}; padding: 5px; margin: 2px; color: {'white' if color.lightness() < 128 else 'black'};")
            layout.addWidget(label)
        
        # Check if #094771 is in the palette
        target_color = QColor("#094771")
        found_094771 = False
        
        for name, color in colors_to_check:
            if color.name().lower() == "#094771":
                label = QLabel(f"🎯 FOUND #094771 in {name}!")
                label.setStyleSheet("background-color: #094771; color: white; font-weight: bold; padding: 5px;")
                layout.addWidget(label)
                found_094771 = True
        
        if not found_094771:
            label = QLabel("❌ #094771 NOT found in current palette")
            label.setStyleSheet("background-color: #ffeeee; color: red; font-weight: bold; padding: 5px;")
            layout.addWidget(label)
        
        # Add a test list widget
        layout.addWidget(QLabel("Test List Widget (check selection color):"))
        list_widget = QListWidget()
        list_widget.addItem("Item 1 - Select me!")
        list_widget.addItem("Item 2 - Or me!")
        list_widget.addItem("Item 3 - Check the selection color")
        layout.addWidget(list_widget)
        
        # Test with manual #094771 color
        layout.addWidget(QLabel("Manually set #094771 highlight:"))
        manual_list = QListWidget()
        manual_list.addItem("Item with manual #094771 highlight")
        manual_list.addItem("Select to see #094771 color")
        
        # Apply the exact color that was being set in the theme manager
        manual_palette = manual_list.palette()
        manual_palette.setColor(QPalette.ColorRole.Highlight, QColor("#094771"))
        manual_palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#cccccc"))
        manual_list.setPalette(manual_palette)
        layout.addWidget(manual_list)
        
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

def main():
    app = QApplication(sys.argv)
    
    print("=== PALETTE TEST ===")
    print("This test will show:")
    print("1. Current system palette colors")
    print("2. Whether #094771 is in the current palette")
    print("3. Comparison between system highlight and manual #094771")
    print("")
    
    window = PaletteTestWindow()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    exit_code = main()
    print(f"Palette test completed with exit code: {exit_code}")
    sys.exit(exit_code)
