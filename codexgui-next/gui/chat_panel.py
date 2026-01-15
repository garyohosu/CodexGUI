"""
Chat Panel

Task cards and conversation interface.
"""

import json
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QLabel, QScrollArea, QFrame, QGridLayout
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QTextCursor


class TaskCard(QFrame):
    """Individual task card widget."""
    
    clicked = Signal(dict)  # Emits task data when clicked
    
    def __init__(self, task_data: dict, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self._init_ui()
    
    def _init_ui(self):
        """Initialize card UI."""
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(1)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            TaskCard {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 12px;
            }
            TaskCard:hover {
                border-color: #4CAF50;
                background-color: #f8fff8;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Icon (emoji for now)
        icon_map = {
            "folder": "📁",
            "list": "📋",
            "search": "🔍",
            "duplicate": "📑",
            "document": "📄",
            "review": "✅"
        }
        icon = icon_map.get(self.task_data.get("icon", ""), "📦")
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 32px;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(self.task_data.get("title", "Task"))
        title_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #333;
            }
        """)
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(self.task_data.get("description", ""))
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #666;
            }
        """)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
    
    def mousePressEvent(self, event):
        """Handle mouse click."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.task_data)
        super().mousePressEvent(event)


class ChatPanel(QWidget):
    """Panel for task cards and conversation."""
    
    # Signals
    task_selected = Signal(dict)  # Emitted when task card is clicked
    message_sent = Signal(str)  # Emitted when user sends message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks = []
        self._init_ui()
        self._load_tasks()
    
    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title_label = QLabel("💬 Chat & Tasks")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
                background-color: #f0f0f0;
                border-bottom: 1px solid #ddd;
            }
        """)
        layout.addWidget(title_label)
        
        # Task cards section
        cards_container = QWidget()
        cards_layout = QVBoxLayout(cards_container)
        cards_layout.setContentsMargins(12, 12, 12, 12)
        
        # Greeting
        greeting_label = QLabel("こんにちは！何をお手伝いしましょうか？")
        greeting_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #333;
                padding: 8px;
            }
        """)
        cards_layout.addWidget(greeting_label)
        
        # Task cards grid
        self.cards_grid = QGridLayout()
        self.cards_grid.setSpacing(12)
        cards_layout.addLayout(self.cards_grid)
        
        cards_layout.addStretch()
        
        # Scroll area for cards
        scroll = QScrollArea()
        scroll.setWidget(cards_container)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        layout.addWidget(scroll, 1)
        
        # Chat log
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(12, 8, 12, 8)
        
        chat_title = QLabel("会話")
        chat_title.setStyleSheet("font-weight: bold; color: #666;")
        chat_layout.addWidget(chat_title)
        
        self.chat_log = QTextEdit()
        self.chat_log.setReadOnly(True)
        self.chat_log.setMaximumHeight(200)
        self.chat_log.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        chat_layout.addWidget(self.chat_log)
        
        layout.addWidget(chat_container)
        
        # Input area
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(12, 0, 12, 12)
        
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("例: 古いログファイルを削除して...")
        self.input_field.setMaximumHeight(80)
        self.input_field.setStyleSheet("""
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            QTextEdit:focus {
                border-color: #4CAF50;
            }
        """)
        input_layout.addWidget(self.input_field)
        
        # Send button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.send_button = QPushButton("送信 ▶")
        self.send_button.clicked.connect(self._on_send_clicked)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 24px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        button_layout.addWidget(self.send_button)
        
        input_layout.addLayout(button_layout)
        layout.addWidget(input_container)
    
    def _load_tasks(self):
        """Load task templates from JSON file."""
        try:
            # Get resources path
            current_dir = Path(__file__).parent.parent
            tasks_file = current_dir / "resources" / "task_templates.json"
            
            if tasks_file.exists():
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = data.get('tasks', [])
                    self._create_task_cards()
        except Exception as e:
            print(f"Error loading tasks: {e}")
    
    def _create_task_cards(self):
        """Create task card widgets."""
        # Clear existing cards
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Create cards in 2x3 grid
        for i, task in enumerate(self.tasks):
            card = TaskCard(task)
            card.clicked.connect(self._on_task_clicked)
            
            row = i // 2
            col = i % 2
            self.cards_grid.addWidget(card, row, col)
    
    def _on_task_clicked(self, task_data: dict):
        """Handle task card click."""
        self.append_message(f"タスク選択: {task_data.get('title', 'Unknown')}", "system")
        self.task_selected.emit(task_data)
    
    def _on_send_clicked(self):
        """Handle send button click."""
        message = self.input_field.toPlainText().strip()
        
        if message:
            self.append_message(message, "user")
            self.message_sent.emit(message)
            self.input_field.clear()
    
    def append_message(self, message: str, sender: str = "system"):
        """
        Append message to chat log.
        
        Args:
            message: Message text
            sender: 'user', 'assistant', or 'system'
        """
        # Format message with color based on sender
        color_map = {
            "user": "#0066cc",
            "assistant": "#2e7d32",
            "system": "#666"
        }
        
        prefix_map = {
            "user": "あなた",
            "assistant": "AI",
            "system": "システム"
        }
        
        color = color_map.get(sender, "#333")
        prefix = prefix_map.get(sender, "")
        
        html = f'<p style="margin: 8px 0;"><b style="color: {color};">{prefix}:</b> {message}</p>'
        self.chat_log.append(html)
        
        # Scroll to bottom
        cursor = self.chat_log.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_log.setTextCursor(cursor)
    
    def clear_chat(self):
        """Clear chat log."""
        self.chat_log.clear()
    
    def set_input_enabled(self, enabled: bool):
        """Enable or disable input."""
        self.input_field.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
