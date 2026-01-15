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
from gui.settings_dialog import SettingsDialog
from core.runner import LocalRunner, RunnerEvent, RunnerState
from core.orchestrator import Orchestrator, OrchestratorState


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize orchestrator (replaces direct runner usage)
        self.orchestrator = Orchestrator()
        self.orchestrator.on_state_changed = self._on_orchestrator_state_changed
        self.orchestrator.on_message = self._on_orchestrator_message
        self.orchestrator.on_plan_ready = self._on_plan_ready
        self.orchestrator.on_runner_event = self._on_runner_event
        
        # State
        self.current_folder = None
        self.selected_files = []
        self.current_task = None
        self.current_plan = None
        
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
        
        # Settings action
        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self._on_settings_clicked)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
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
        
        # Check if busy
        if self.orchestrator.is_busy():
            QMessageBox.warning(
                self,
                "実行中",
                "既にタスクが実行中です。完了するまでお待ちください。"
            )
            return
        
        # Start task with orchestrator
        task_id = task_data.get('id', '')
        task_title = task_data.get('title', 'Unknown Task')
        user_request = task_data.get('description', '')
        
        self.chat.append_message(
            f"タスク「{task_title}」を開始します...",
            "system"
        )
        
        # Show details panel
        self.bottom_tabs.setVisible(True)
        self.toggle_details_action.setChecked(True)
        self.detail.clear_logs()
        
        # Start task
        self.orchestrator.start_task(
            task_id=task_id,
            task_title=task_title,
            user_request=user_request,
            folder_path=self.current_folder,
            selected_files=self.selected_files
        )
    
    def _on_message_sent(self, message: str):
        """Handle user message."""
        # Check orchestrator state
        state = self.orchestrator.get_state()
        
        if state == OrchestratorState.CLARIFYING:
            # Provide clarification answer
            self.orchestrator.provide_clarification(message)
        elif state == OrchestratorState.REVIEWING:
            # User might want to modify plan or confirm
            # For now, treat as general chat
            self.chat.append_message(
                "プランを確認してください。実行する場合は「実行」ボタンをクリックしてください。",
                "assistant"
            )
        else:
            # General conversation (future: use OpenAI chat)
            self.chat.append_message(
                f"メッセージを受信しました: {message}\n\n"
                "タスクを開始するには、上のタスクカードをクリックしてください。",
                "assistant"
            )
    
    # Orchestrator callbacks
    
    def _on_orchestrator_state_changed(self, state: OrchestratorState):
        """Handle orchestrator state change."""
        state_messages = {
            OrchestratorState.IDLE: "待機中",
            OrchestratorState.PLANNING: "計画を生成中...",
            OrchestratorState.CLARIFYING: "追加情報が必要です",
            OrchestratorState.REVIEWING: "計画を確認してください",
            OrchestratorState.RUNNING: "実行中...",
            OrchestratorState.SUMMARIZING: "結果を要約中...",
            OrchestratorState.COMPLETED: "完了",
            OrchestratorState.ERROR: "エラー"
        }
        
        message = state_messages.get(state, str(state))
        self.status_bar.showMessage(message)
        
        # Enable/disable input based on state
        if state in [OrchestratorState.RUNNING, OrchestratorState.PLANNING, OrchestratorState.SUMMARIZING]:
            self.chat.set_input_enabled(False)
        else:
            self.chat.set_input_enabled(True)
    
    def _on_orchestrator_message(self, message: str, sender: str):
        """Handle message from orchestrator."""
        self.chat.append_message(message, sender)
    
    def _on_plan_ready(self, plan: dict):
        """Handle plan ready from orchestrator."""
        self.current_plan = plan
        
        # Display plan to user
        plan_type = plan.get('type', 'unknown')
        
        if plan_type == 'plan':
            steps = plan.get('steps', [])
            warnings = plan.get('warnings', [])
            
            # Format plan message
            plan_text = "📋 **実行計画**\n\n"
            
            for i, step in enumerate(steps, 1):
                desc = step.get('description', 'ステップ')
                plan_text += f"{i}. {desc}\n"
            
            if warnings:
                plan_text += "\n⚠️ **警告**\n"
                for warning in warnings:
                    plan_text += f"• {warning}\n"
            
            plan_text += "\n実行してよろしいですか？"
            
            self.chat.append_message(plan_text, "assistant")
            
            # Show confirmation dialog
            reply = QMessageBox.question(
                self,
                "実行確認",
                "この計画を実行しますか？\n\n" + plan_text,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.orchestrator.execute_plan()
            else:
                self.chat.append_message("実行をキャンセルしました", "system")
                self.orchestrator.cancel()
    
    @Slot(object)
    def _on_runner_event(self, event: RunnerEvent):
        """Handle runner event from orchestrator."""
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
    
    def _on_toggle_details(self, checked: bool):
        """Toggle details panel visibility."""
        self.bottom_tabs.setVisible(checked)
    
    def _on_settings_clicked(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def _on_about_clicked(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About CodexGUI Next",
            "<h3>CodexGUI Next v0.1.0-M2</h3>"
            "<p>Chat-driven GUI for ChatGPT API × Codex CLI integration</p>"
            "<p><b>Milestone 2:</b> OpenAI API integration with plan generation and summarization</p>"
            "<p><b>Author:</b> garyohosu</p>"
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.orchestrator.is_busy():
            reply = QMessageBox.question(
                self,
                "実行中",
                "タスクが実行中です。本当に終了しますか？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.orchestrator.cancel()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
