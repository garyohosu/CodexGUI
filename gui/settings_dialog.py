"""
Settings Dialog

This module provides a settings dialog for configuring the application.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QGroupBox,
    QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import Qt
import json
import os


class SettingsDialog(QDialog):
    """Dialog for application settings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self._init_ui()
        self._load_settings()
    
    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Codex CLI settings group
        codex_group = QGroupBox("Codex CLI Configuration")
        codex_layout = QVBoxLayout(codex_group)
        
        # Path input
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Codex CLI Path:"))
        
        self.codex_path_input = QLineEdit()
        self.codex_path_input.setPlaceholderText("e.g., codex.exe or /path/to/codex")
        path_layout.addWidget(self.codex_path_input, 1)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._on_browse_clicked)
        path_layout.addWidget(self.browse_button)
        
        codex_layout.addLayout(path_layout)
        
        # Help text
        help_label = QLabel(
            "Leave empty for auto-detection. "
            "On Windows, use 'codex.exe' or full path to the executable."
        )
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: gray; font-size: 10px;")
        codex_layout.addWidget(help_label)
        
        layout.addWidget(codex_group)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._on_accepted)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _on_browse_clicked(self):
        """Handle browse button click."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Codex CLI Executable",
            "",
            "Executable Files (*.exe *.cmd);;All Files (*.*)"
        )
        
        if file_path:
            self.codex_path_input.setText(file_path)
    
    def _load_settings(self):
        """Load settings from file."""
        settings_file = self._get_settings_file()
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.codex_path_input.setText(
                        settings.get('codex_path', '')
                    )
            except Exception as e:
                print(f"Error loading settings: {e}")
    
    def _save_settings(self):
        """Save settings to file."""
        settings = {
            'codex_path': self.codex_path_input.text()
        }
        
        settings_file = self._get_settings_file()
        try:
            os.makedirs(os.path.dirname(settings_file), exist_ok=True)
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Save Error",
                f"Failed to save settings: {e}"
            )
    
    def _get_settings_file(self) -> str:
        """Get path to settings file."""
        # Use user's home directory
        home = os.path.expanduser("~")
        settings_dir = os.path.join(home, ".codexgui")
        return os.path.join(settings_dir, "settings.json")
    
    def _on_accepted(self):
        """Handle OK button click."""
        self._save_settings()
        self.accept()
    
    def get_codex_path(self) -> str:
        """Get configured Codex CLI path."""
        return self.codex_path_input.text()
    
    @staticmethod
    def load_codex_path() -> str:
        """Load Codex CLI path from settings."""
        home = os.path.expanduser("~")
        settings_file = os.path.join(home, ".codexgui", "settings.json")
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get('codex_path', '')
            except Exception:
                pass
        
        return ''
