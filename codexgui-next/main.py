"""
CodexGUI Next - Main Entry Point

Chat-driven GUI for ChatGPT API × Codex CLI integration.
"""

import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """Main application entry point."""
    # Create application
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("CodexGUI Next")
    app.setOrganizationName("garyohosu")
    app.setApplicationVersion("0.1.0-M2")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
