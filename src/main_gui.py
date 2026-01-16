#!/usr/bin/env python3
"""
MediaBench - Native GUI Entry Point
"""
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

try:
    from PyQt6.QtWidgets import QApplication
except ImportError:
    print("❌ Error: PyQt6 is not installed.")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

from src.gui.window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MediaBench")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
