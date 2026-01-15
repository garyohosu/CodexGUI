"""
Detail Panel

Raw logs and execution details (hidden by default).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QTabWidget, 
    QPushButton, QHBoxLayout, QLabel
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont, QTextCursor


class DetailPanel(QWidget):
    """Panel for detailed logs and events."""
    
    # Signals
    clear_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Execution log tab
        exec_tab = QWidget()
        exec_layout = QVBoxLayout(exec_tab)
        exec_layout.setContentsMargins(8, 8, 8, 8)
        
        # Log display
        self.exec_log = QTextEdit()
        self.exec_log.setReadOnly(True)
        self.exec_log.setFont(QFont("Courier New", 10))
        self.exec_log.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
                padding: 8px;
            }
        """)
        exec_layout.addWidget(self.exec_log)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._on_clear_clicked)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        
        exec_layout.addLayout(button_layout)
        
        self.tabs.addTab(exec_tab, "Execution Log")
        
        # Events tab
        events_tab = QWidget()
        events_layout = QVBoxLayout(events_tab)
        events_layout.setContentsMargins(8, 8, 8, 8)
        
        self.events_log = QTextEdit()
        self.events_log.setReadOnly(True)
        self.events_log.setFont(QFont("Courier New", 9))
        self.events_log.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                color: #333;
                border: 1px solid #ddd;
                padding: 8px;
            }
        """)
        events_layout.addWidget(self.events_log)
        
        self.tabs.addTab(events_tab, "Events")
        
        layout.addWidget(self.tabs)
    
    def append_stdout(self, text: str):
        """Append stdout text."""
        self._append_colored(text, "#d4d4d4")
    
    def append_stderr(self, text: str):
        """Append stderr text."""
        self._append_colored(text, "#ff6b6b")
    
    def append_command(self, text: str):
        """Append command text."""
        self._append_colored(f"$ {text}", "#4CAF50")
    
    def append_status(self, text: str):
        """Append status text."""
        self._append_colored(f"[STATUS] {text}", "#64b5f6")
    
    def append_error(self, text: str):
        """Append error text."""
        self._append_colored(f"[ERROR] {text}", "#ff6b6b")
    
    def _append_colored(self, text: str, color: str):
        """Append colored text to execution log."""
        cursor = self.exec_log.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        html = f'<span style="color: {color};">{text}</span><br>'
        cursor.insertHtml(html)
        
        self.exec_log.setTextCursor(cursor)
        self.exec_log.ensureCursorVisible()
    
    def append_event(self, event_type: str, data: str, timestamp: float):
        """
        Append event to events log.
        
        Args:
            event_type: Type of event
            data: Event data
            timestamp: Event timestamp
        """
        import datetime
        dt = datetime.datetime.fromtimestamp(timestamp)
        time_str = dt.strftime("%H:%M:%S.%f")[:-3]
        
        event_text = f"[{time_str}] [{event_type.upper()}] {data}\n"
        self.events_log.append(event_text)
    
    def clear_logs(self):
        """Clear all logs."""
        self.exec_log.clear()
        self.events_log.clear()
    
    def _on_clear_clicked(self):
        """Handle clear button click."""
        self.clear_logs()
        self.clear_requested.emit()
    
    def get_log_text(self) -> str:
        """Get execution log text."""
        return self.exec_log.toPlainText()
