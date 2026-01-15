"""
Main Window

This module provides the main application window.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QMessageBox, QStatusBar, QMenuBar, QMenu
)
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QAction

from gui.task_panel import TaskPanel
from gui.output_panel import OutputPanel
from gui.settings_dialog import SettingsDialog
from core.codex_wrapper import CodexWrapper, CodexResult


class CodexWorker(QThread):
    """Worker thread for executing Codex commands."""
    
    # Signals
    output_received = Signal(str)
    error_received = Signal(str)
    finished = Signal(CodexResult)
    
    def __init__(self, wrapper: CodexWrapper, prompt: str, working_dir: str):
        super().__init__()
        self.wrapper = wrapper
        self.prompt = prompt
        self.working_dir = working_dir
    
    def run(self):
        """Execute Codex command in thread."""
        try:
            # Use streaming execution
            result = self.wrapper.execute_prompt_streaming(
                self.prompt,
                self.working_dir,
                callback=lambda line: self.output_received.emit(line)
            )
            
            if not result.success and result.error:
                self.error_received.emit(result.error)
            
            self.finished.emit(result)
            
        except Exception as e:
            error_msg = f"Execution error: {str(e)}"
            self.error_received.emit(error_msg)
            self.finished.emit(CodexResult(
                success=False,
                output="",
                error=error_msg,
                exit_code=-1
            ))


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Load custom codex path from settings
        custom_path = SettingsDialog.load_codex_path()
        self.codex_wrapper = CodexWrapper(custom_path if custom_path else None)
        
        self.worker = None
        self._init_ui()
        self._check_codex_availability()
    
    def _init_ui(self):
        """Initialize UI components."""
        self.setWindowTitle("CodexGUI - Codex CLI Wrapper")
        self.setMinimumSize(1000, 700)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Task panel (left)
        self.task_panel = TaskPanel()
        self.task_panel.execute_button.clicked.connect(self._on_execute_clicked)
        splitter.addWidget(self.task_panel)
        
        # Output panel (right)
        self.output_panel = OutputPanel()
        splitter.addWidget(self.output_panel)
        
        # Set initial sizes (30% - 70%)
        splitter.setSizes([300, 700])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _create_menu_bar(self):
        """Create menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        settings_action = QAction("&Settings...", self)
        settings_action.triggered.connect(self._on_settings_clicked)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._on_about_clicked)
        help_menu.addAction(about_action)
        
        codex_help_action = QAction("Codex CLI &Installation", self)
        codex_help_action.triggered.connect(self._on_codex_help_clicked)
        help_menu.addAction(codex_help_action)
    
    def _check_codex_availability(self):
        """Check if Codex CLI is available."""
        if not self.codex_wrapper.is_available():
            help_text = self.codex_wrapper.get_installation_help()
            
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Codex CLI Not Found")
            msg_box.setText("Codex CLI is not available in your system.")
            msg_box.setInformativeText(
                "The application will continue, but execution will fail."
            )
            msg_box.setDetailedText(help_text)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
            
            self.status_bar.showMessage("Warning: Codex CLI not available")
    
    def _on_execute_clicked(self):
        """Handle execute button click."""
        # Validate inputs
        folder_path = self.task_panel.get_folder_path()
        if not folder_path:
            QMessageBox.warning(
                self,
                "Missing Folder",
                "Please select a target folder."
            )
            return
        
        prompt = self.task_panel.get_prompt()
        if not prompt.strip():
            QMessageBox.warning(
                self,
                "Missing Prompt",
                "Please enter a prompt."
            )
            return
        
        # Disable controls
        self.task_panel.set_enabled(False)
        self.output_panel.clear()
        
        # Update status
        template = self.task_panel.get_current_template()
        self.status_bar.showMessage(f"Executing: {template.name}...")
        self.output_panel.set_status(f"Executing: {template.name}")
        
        # Log execution start
        self.output_panel.append_output("=" * 60)
        self.output_panel.append_output(f"Task: {template.name}")
        self.output_panel.append_output(f"Folder: {folder_path}")
        self.output_panel.append_output("=" * 60)
        self.output_panel.append_output("")
        
        # Create and start worker thread
        self.worker = CodexWorker(
            self.codex_wrapper,
            prompt,
            folder_path
        )
        self.worker.output_received.connect(self.output_panel.append_output)
        self.worker.error_received.connect(self.output_panel.append_error)
        self.worker.finished.connect(self._on_execution_finished)
        self.worker.start()
    
    @Slot(CodexResult)
    def _on_execution_finished(self, result: CodexResult):
        """Handle execution completion."""
        # Re-enable controls
        self.task_panel.set_enabled(True)
        
        # Update status
        if result.success:
            self.status_bar.showMessage("Execution completed successfully")
            self.output_panel.set_status("✓ Completed successfully")
            self.output_panel.append_output("")
            self.output_panel.append_output("=" * 60)
            self.output_panel.append_output("Execution completed successfully")
            self.output_panel.append_output("=" * 60)
        else:
            self.status_bar.showMessage("Execution failed")
            self.output_panel.set_status("✗ Execution failed")
            self.output_panel.append_output("")
            self.output_panel.append_output("=" * 60)
            self.output_panel.append_output("Execution failed")
            if result.error:
                self.output_panel.append_error(result.error)
            self.output_panel.append_output("=" * 60)
        
        # Clean up worker
        self.worker = None
    
    def _on_settings_clicked(self):
        """Handle settings menu click."""
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Reload Codex wrapper with new settings
            custom_path = dialog.get_codex_path()
            self.codex_wrapper = CodexWrapper(custom_path if custom_path else None)
            
            # Update status
            if self.codex_wrapper.is_available():
                self.status_bar.showMessage("Codex CLI path updated and verified")
                QMessageBox.information(
                    self,
                    "Settings Updated",
                    "Codex CLI configuration has been updated successfully."
                )
            else:
                self.status_bar.showMessage("Warning: Codex CLI not available")
                QMessageBox.warning(
                    self,
                    "Codex CLI Not Found",
                    "The specified Codex CLI path is not valid.\n"
                    "Please check the path and try again."
                )
    
    def _on_about_clicked(self):
        """Handle about menu click."""
        QMessageBox.about(
            self,
            "About CodexGUI",
            "<h3>CodexGUI v0.0.1</h3>"
            "<p>A Qt/PySide6 GUI wrapper for OpenAI Codex CLI</p>"
            "<p>Enables easy access to AI-powered code analysis, "
            "file organization, and task automation through an "
            "intuitive desktop interface.</p>"
            "<p><b>Author:</b> garyohosu</p>"
            "<p><b>GitHub:</b> <a href='https://github.com/garyohosu/CodexGUI'>"
            "https://github.com/garyohosu/CodexGUI</a></p>"
        )
    
    def _on_codex_help_clicked(self):
        """Handle Codex CLI help menu click."""
        help_text = self.codex_wrapper.get_installation_help()
        
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Codex CLI Installation Help")
        msg_box.setText("How to install Codex CLI")
        msg_box.setInformativeText(help_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Execution in Progress",
                "A task is currently running. Are you sure you want to quit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.worker.terminate()
                self.worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
