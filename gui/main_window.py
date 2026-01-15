"""
Main Window

This module provides the main application window.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QMessageBox, QStatusBar
)
from PySide6.QtCore import Qt, QThread, Signal, Slot

from gui.task_panel import TaskPanel
from gui.output_panel import OutputPanel
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
        self.codex_wrapper = CodexWrapper()
        self.worker = None
        self._init_ui()
        self._check_codex_availability()
    
    def _init_ui(self):
        """Initialize UI components."""
        self.setWindowTitle("CodexGUI - Codex CLI Wrapper")
        self.setMinimumSize(1000, 700)
        
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
    
    def _check_codex_availability(self):
        """Check if Codex CLI is available."""
        if not self.codex_wrapper.is_available():
            QMessageBox.warning(
                self,
                "Codex CLI Not Found",
                "Codex CLI is not available in your system.\n\n"
                "Please ensure:\n"
                "1. Codex CLI is installed\n"
                "2. It's in your system PATH\n"
                "3. You have necessary permissions\n\n"
                "The application will continue, but execution will fail."
            )
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
