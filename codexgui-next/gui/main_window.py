"""
Main Window

Integrates Explorer, Chat, and Detail panels.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTabWidget, QMessageBox, QStatusBar, QMenuBar
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QAction

from gui.explorer_panel import ExplorerPanel
from gui.chat_panel import ChatPanel
from gui.detail_panel import DetailPanel
from core.runner import LocalRunner, RunnerEvent, RunnerState


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize runner
        self.runner = LocalRunner()
        
        # State
        self.current_folder = None
        self.selected_files = []
        self.current_task = None
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components."""
        self.setWindowTitle("CodexGUI Next - Chat-driven Codex CLI")
        self.setMinimumSize(1200, 800)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Top splitter (Explorer + Chat)
        top_splitter = QSplitter(Qt.Horizontal)
        
        # Explorer panel (left)
        self.explorer = ExplorerPanel()
        self.explorer.folder_changed.connect(self._on_folder_changed)
        self.explorer.selection_changed.connect(self._on_selection_changed)
        top_splitter.addWidget(self.explorer)
        
        # Chat panel (right)
        self.chat = ChatPanel()
        self.chat.task_selected.connect(self._on_task_selected)
        self.chat.message_sent.connect(self._on_message_sent)
        top_splitter.addWidget(self.chat)
        
        # Set initial sizes (30% - 70%)
        top_splitter.setSizes([360, 840])
        
        main_layout.addWidget(top_splitter, 2)
        
        # Bottom tabs (Detail panel)
        bottom_tabs = QTabWidget()
        bottom_tabs.setMaximumHeight(300)
        
        # Detail panel
        self.detail = DetailPanel()
        bottom_tabs.addTab(self.detail, "詳細")
        
        # Initially hide details (can be shown when execution starts)
        bottom_tabs.setVisible(False)
        self.bottom_tabs = bottom_tabs
        
        main_layout.addWidget(bottom_tabs, 1)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("準備完了 - フォルダを選択してください")
    
    def _create_menu_bar(self):
        """Create menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # Toggle details action
        self.toggle_details_action = QAction("Show Details", self)
        self.toggle_details_action.setCheckable(True)
        self.toggle_details_action.triggered.connect(self._on_toggle_details)
        file_menu.addAction(self.toggle_details_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self._on_about_clicked)
        help_menu.addAction(about_action)
    
    def _on_folder_changed(self, folder_path: str):
        """Handle folder selection change."""
        self.current_folder = folder_path
        self.status_bar.showMessage(f"対象フォルダ: {folder_path}")
        self.chat.append_message(f"フォルダを選択しました: {folder_path}", "system")
    
    def _on_selection_changed(self, selected_paths: list):
        """Handle file selection change."""
        self.selected_files = selected_paths
        
        if selected_paths:
            count = len(selected_paths)
            self.status_bar.showMessage(f"{count} 個のファイルを選択中")
    
    def _on_task_selected(self, task_data: dict):
        """Handle task card click."""
        self.current_task = task_data
        
        # Check if folder is selected
        if not self.current_folder:
            QMessageBox.warning(
                self,
                "フォルダ未選択",
                "対象フォルダを選択してください。"
            )
            return
        
        # Show task confirmation
        task_title = task_data.get('title', 'Unknown Task')
        self.chat.append_message(
            f"タスク「{task_title}」を実行します。対象: {self.current_folder}",
            "assistant"
        )
        
        # For M1, just execute a simple listing command
        self._execute_task(task_data)
    
    def _on_message_sent(self, message: str):
        """Handle user message."""
        # For M1, just echo back
        self.chat.append_message(
            f"メッセージを受信しました: {message}",
            "assistant"
        )
        
        # TODO: In M2, send to OpenAI API for planning
    
    def _execute_task(self, task_data: dict):
        """
        Execute task using Runner.
        
        Args:
            task_data: Task definition
        """
        if self.runner.is_running():
            QMessageBox.warning(
                self,
                "実行中",
                "既にタスクが実行中です。完了するまでお待ちください。"
            )
            return
        
        # Show details panel
        self.bottom_tabs.setVisible(True)
        self.toggle_details_action.setChecked(True)
        
        # Clear previous logs
        self.detail.clear_logs()
        
        # Build simple prompt for M1 testing
        task_id = task_data.get('id', '')
        
        # Simple prompts for testing
        prompt_map = {
            'organize_folder': 'List all files in this folder with their sizes',
            'create_file_list': 'Create a file listing with tree structure',
            'find_large_files': 'Find files larger than 10MB',
            'find_duplicates': 'Find duplicate files',
            'create_readme': 'Analyze project and suggest README content',
            'review_changes': 'List recently modified files'
        }
        
        prompt = prompt_map.get(task_id, 'List all files')
        
        # Update UI
        self.chat.append_message("実行を開始します...", "system")
        self.chat.set_input_enabled(False)
        self.status_bar.showMessage("実行中...")
        
        # Execute with Runner
        self.runner.execute(
            prompt=prompt,
            working_dir=self.current_folder,
            callback=self._on_runner_event
        )
    
    @Slot(object)
    def _on_runner_event(self, event: RunnerEvent):
        """Handle runner event."""
        # Log to detail panel
        if event.type == "command":
            self.detail.append_command(event.data)
        elif event.type == "stdout":
            self.detail.append_stdout(event.data)
        elif event.type == "stderr":
            self.detail.append_stderr(event.data)
        elif event.type == "status":
            self.detail.append_status(event.data)
        elif event.type == "error":
            self.detail.append_error(event.data)
        
        # Log to events
        self.detail.append_event(event.type, event.data, event.timestamp)
        
        # Check if execution finished
        if event.type in ["status", "error"]:
            state = self.runner.get_state()
            
            if state in [RunnerState.COMPLETED, RunnerState.FAILED, RunnerState.CANCELLED]:
                self._on_execution_finished(state)
    
    def _on_execution_finished(self, state: RunnerState):
        """Handle execution completion."""
        # Re-enable UI
        self.chat.set_input_enabled(True)
        
        # Update status
        if state == RunnerState.COMPLETED:
            self.status_bar.showMessage("実行完了")
            self.chat.append_message("✓ 実行が完了しました", "assistant")
        elif state == RunnerState.FAILED:
            self.status_bar.showMessage("実行失敗")
            self.chat.append_message("✗ 実行に失敗しました", "assistant")
        elif state == RunnerState.CANCELLED:
            self.status_bar.showMessage("実行中止")
            self.chat.append_message("実行を中止しました", "system")
    
    def _on_toggle_details(self, checked: bool):
        """Toggle details panel visibility."""
        self.bottom_tabs.setVisible(checked)
    
    def _on_about_clicked(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About CodexGUI Next",
            "<h3>CodexGUI Next v0.1.0-M1</h3>"
            "<p>Chat-driven GUI for ChatGPT API × Codex CLI integration</p>"
            "<p><b>Milestone 1:</b> Basic UI structure with streaming execution</p>"
            "<p><b>Author:</b> garyohosu</p>"
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.runner.is_running():
            reply = QMessageBox.question(
                self,
                "実行中",
                "タスクが実行中です。本当に終了しますか？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.runner.cancel()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
