"""
Task Selection Panel

This module provides the UI for selecting and configuring tasks.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QTextEdit, QPushButton, QFileDialog,
    QLineEdit, QGroupBox
)
from PySide6.QtCore import Signal

from core.templates import TemplateManager, TaskTemplate


class TaskPanel(QWidget):
    """Panel for task selection and configuration."""
    
    # Signals
    task_selected = Signal(TaskTemplate)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.template_manager = TemplateManager()
        self._init_ui()
        self._load_templates()
    
    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Task selection group
        task_group = QGroupBox("Task Selection")
        task_layout = QVBoxLayout(task_group)
        
        # Template selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Template:"))
        self.template_combo = QComboBox()
        self.template_combo.currentIndexChanged.connect(self._on_template_changed)
        selector_layout.addWidget(self.template_combo, 1)
        task_layout.addLayout(selector_layout)
        
        # Description
        self.description_label = QLabel("")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: gray; padding: 5px;")
        task_layout.addWidget(self.description_label)
        
        layout.addWidget(task_group)
        
        # Folder selection group
        folder_group = QGroupBox("Target Folder")
        folder_layout = QVBoxLayout(folder_group)
        
        folder_select_layout = QHBoxLayout()
        self.folder_path = QLineEdit()
        self.folder_path.setPlaceholderText("Select a folder...")
        folder_select_layout.addWidget(self.folder_path, 1)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._on_browse_clicked)
        folder_select_layout.addWidget(self.browse_button)
        
        folder_layout.addLayout(folder_select_layout)
        layout.addWidget(folder_group)
        
        # Prompt group
        prompt_group = QGroupBox("Prompt")
        prompt_layout = QVBoxLayout(prompt_group)
        
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Enter your prompt here...")
        self.prompt_edit.setMaximumHeight(150)
        prompt_layout.addWidget(self.prompt_edit)
        
        layout.addWidget(prompt_group)
        
        # Execute button
        self.execute_button = QPushButton("Execute Task")
        self.execute_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        layout.addWidget(self.execute_button)
        
        # Add stretch
        layout.addStretch()
    
    def _load_templates(self):
        """Load templates into combo box."""
        templates = self.template_manager.get_all_templates()
        
        for template in templates:
            self.template_combo.addItem(
                f"{template.category} - {template.name}",
                template
            )
        
        # Select first template
        if self.template_combo.count() > 0:
            self._on_template_changed(0)
    
    def _on_template_changed(self, index: int):
        """Handle template selection change."""
        template = self.template_combo.itemData(index)
        if template:
            self.description_label.setText(template.description)
            self.prompt_edit.setPlainText(template.prompt)
            self.task_selected.emit(template)
    
    def _on_browse_clicked(self):
        """Handle browse button click."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Target Folder",
            self.folder_path.text() or ""
        )
        
        if folder:
            self.folder_path.setText(folder)
    
    def get_current_template(self) -> TaskTemplate:
        """Get currently selected template."""
        index = self.template_combo.currentIndex()
        return self.template_combo.itemData(index)
    
    def get_folder_path(self) -> str:
        """Get selected folder path."""
        return self.folder_path.text()
    
    def get_prompt(self) -> str:
        """Get current prompt text."""
        return self.prompt_edit.toPlainText()
    
    def set_enabled(self, enabled: bool):
        """Enable or disable all controls."""
        self.template_combo.setEnabled(enabled)
        self.folder_path.setEnabled(enabled)
        self.browse_button.setEnabled(enabled)
        self.prompt_edit.setEnabled(enabled)
        self.execute_button.setEnabled(enabled)
