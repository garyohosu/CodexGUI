"""
Output Display Panel

This module provides the UI for displaying Codex CLI execution output.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QPushButton,
    QHBoxLayout, QLabel, QGroupBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QTextCursor, QFont


class OutputPanel(QWidget):
    """Panel for displaying execution output."""
    
    # Signals
    clear_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Output group
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 5px;
                background-color: #f0f0f0;
                border-radius: 3px;
            }
        """)
        output_layout.addWidget(self.status_label)
        
        # Output text area
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Courier New", 10))
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                border-radius: 3px;
                padding: 10px;
            }
        """)
        output_layout.addWidget(self.output_text)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.clear_button = QPushButton("Clear Output")
        self.clear_button.clicked.connect(self._on_clear_clicked)
        button_layout.addWidget(self.clear_button)
        
        self.save_button = QPushButton("Save to File")
        self.save_button.setEnabled(False)
        button_layout.addWidget(self.save_button)
        
        button_layout.addStretch()
        output_layout.addLayout(button_layout)
        
        layout.addWidget(output_group)
    
    def _on_clear_clicked(self):
        """Handle clear button click."""
        self.output_text.clear()
        self.status_label.setText("Ready")
        self.clear_requested.emit()
    
    @Slot(str)
    def append_output(self, text: str):
        """
        Append text to output display.
        
        Args:
            text: Text to append
        """
        self.output_text.moveCursor(QTextCursor.End)
        self.output_text.insertPlainText(text + "\n")
        self.output_text.moveCursor(QTextCursor.End)
        self.save_button.setEnabled(True)
    
    @Slot(str)
    def append_error(self, text: str):
        """
        Append error text to output display.
        
        Args:
            text: Error text to append
        """
        self.output_text.moveCursor(QTextCursor.End)
        
        # Insert with red color
        cursor = self.output_text.textCursor()
        format = cursor.charFormat()
        format.setForeground(Qt.red)
        cursor.setCharFormat(format)
        
        self.output_text.insertPlainText(f"ERROR: {text}\n")
        self.output_text.moveCursor(QTextCursor.End)
        
        # Reset format
        format.setForeground(Qt.white)
        cursor.setCharFormat(format)
        
        self.save_button.setEnabled(True)
    
    @Slot(str)
    def set_status(self, status: str):
        """
        Set status label text.
        
        Args:
            status: Status text
        """
        self.status_label.setText(status)
    
    @Slot()
    def clear(self):
        """Clear output display."""
        self.output_text.clear()
        self.status_label.setText("Ready")
        self.save_button.setEnabled(False)
    
    def get_output_text(self) -> str:
        """
        Get current output text.
        
        Returns:
            Output text content
        """
        return self.output_text.toPlainText()
