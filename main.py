#!/usr/bin/env python3
"""
CodexGUI - Main Entry Point

A Qt/PySide6 GUI wrapper for OpenAI Codex CLI.
"""

import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """Main application entry point."""
    # Create application
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("CodexGUI")
    app.setOrganizationName("garyohosu")
    app.setApplicationVersion("0.0.1")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
