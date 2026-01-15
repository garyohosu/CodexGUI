"""
Settings Dialog

Configuration for API key, Codex CLI path, and transmission policy.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QGroupBox,
    QDialogButtonBox, QMessageBox, QCheckBox, QSpinBox,
    QTabWidget, QWidget, QTextEdit
)
from PySide6.QtCore import Qt
from core.storage import get_storage


class SettingsDialog(QDialog):
    """Dialog for application settings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.storage = get_storage()
        self.setWindowTitle("設定 - Settings")
        self.setMinimumSize(600, 500)
        self._init_ui()
        self._load_settings()
    
    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Tab widget
        tabs = QTabWidget()
        
        # API Tab
        api_tab = self._create_api_tab()
        tabs.addTab(api_tab, "API設定")
        
        # Transmission Policy Tab
        policy_tab = self._create_policy_tab()
        tabs.addTab(policy_tab, "送信ポリシー")
        
        # Codex CLI Tab
        codex_tab = self._create_codex_tab()
        tabs.addTab(codex_tab, "Codex CLI")
        
        layout.addWidget(tabs)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._on_accepted)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _create_api_tab(self) -> QWidget:
        """Create API settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # OpenAI API Key
        api_group = QGroupBox("OpenAI API キー")
        api_layout = QVBoxLayout(api_group)
        
        help_label = QLabel(
            "ChatGPT API を使用するには OpenAI API キーが必要です。\n"
            "https://platform.openai.com/api-keys で取得できます。"
        )
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #666; font-size: 11px;")
        api_layout.addWidget(help_label)
        
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("API Key:"))
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("sk-...")
        key_layout.addWidget(self.api_key_input, 1)
        
        show_key_btn = QPushButton("👁")
        show_key_btn.setMaximumWidth(40)
        show_key_btn.setCheckable(True)
        show_key_btn.toggled.connect(
            lambda checked: self.api_key_input.setEchoMode(
                QLineEdit.Normal if checked else QLineEdit.Password
            )
        )
        key_layout.addWidget(show_key_btn)
        
        api_layout.addLayout(key_layout)
        
        # Test button
        test_btn = QPushButton("接続テスト")
        test_btn.clicked.connect(self._test_api_connection)
        api_layout.addWidget(test_btn)
        
        layout.addWidget(api_group)
        
        # Security notice
        security_label = QLabel(
            "⚠️ セキュリティ: API キーは暗号化されずに保存されます。\n"
            "このPCの他のユーザーからアクセス可能な場合はご注意ください。"
        )
        security_label.setWordWrap(True)
        security_label.setStyleSheet("""
            QLabel {
                background-color: #fff3cd;
                border: 1px solid #ffc107;
                border-radius: 4px;
                padding: 8px;
                color: #856404;
                font-size: 11px;
            }
        """)
        layout.addWidget(security_label)
        
        layout.addStretch()
        
        return tab
    
    def _create_policy_tab(self) -> QWidget:
        """Create transmission policy tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Info
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(100)
        info_text.setHtml("""
            <h4>データ送信ポリシー</h4>
            <p style="color: #666; font-size: 12px;">
            OpenAI API に送信するデータを最小限に抑えるための設定です。
            機密情報を含むファイルを扱う場合は、慎重に設定してください。
            </p>
        """)
        layout.addWidget(info_text)
        
        # Policy settings
        policy_group = QGroupBox("送信設定")
        policy_layout = QVBoxLayout(policy_group)
        
        # Send file content
        self.send_content_check = QCheckBox(
            "ファイルの内容を送信する（デフォルト: OFF）"
        )
        self.send_content_check.setStyleSheet("color: #d32f2f; font-weight: bold;")
        policy_layout.addWidget(self.send_content_check)
        
        warning = QLabel(
            "⚠️ 有効にすると、ソースコードやテキストファイルの内容が OpenAI に送信されます。"
        )
        warning.setWordWrap(True)
        warning.setStyleSheet("color: #d32f2f; font-size: 11px; margin-left: 20px;")
        policy_layout.addWidget(warning)
        
        policy_layout.addSpacing(10)
        
        # Max files
        max_files_layout = QHBoxLayout()
        max_files_layout.addWidget(QLabel("送信するファイル数の上限:"))
        self.max_files_spin = QSpinBox()
        self.max_files_spin.setRange(1, 100)
        self.max_files_spin.setValue(10)
        max_files_layout.addWidget(self.max_files_spin)
        max_files_layout.addWidget(QLabel("個"))
        max_files_layout.addStretch()
        policy_layout.addLayout(max_files_layout)
        
        # Max file size
        max_size_layout = QHBoxLayout()
        max_size_layout.addWidget(QLabel("送信するファイルサイズの上限:"))
        self.max_size_spin = QSpinBox()
        self.max_size_spin.setRange(1, 1024)
        self.max_size_spin.setValue(100)
        self.max_size_spin.setSuffix(" KB")
        max_size_layout.addWidget(self.max_size_spin)
        max_size_layout.addStretch()
        policy_layout.addLayout(max_size_layout)
        
        policy_layout.addSpacing(10)
        
        # Send diff summary
        self.send_diff_check = QCheckBox(
            "差分の要約を送信する（推奨: ON）"
        )
        self.send_diff_check.setChecked(True)
        policy_layout.addWidget(self.send_diff_check)
        
        # Send error messages
        self.send_error_check = QCheckBox(
            "エラーメッセージを送信する（推奨: ON）"
        )
        self.send_error_check.setChecked(True)
        policy_layout.addWidget(self.send_error_check)
        
        layout.addWidget(policy_group)
        
        # What is sent
        sent_group = QGroupBox("常に送信される情報")
        sent_layout = QVBoxLayout(sent_group)
        sent_layout.addWidget(QLabel("• 対象フォルダのパス"))
        sent_layout.addWidget(QLabel("• ファイル名一覧（上限数まで）"))
        sent_layout.addWidget(QLabel("• ファイルのメタ情報（サイズ、拡張子、更新日時）"))
        sent_layout.addWidget(QLabel("• タスクの説明とユーザーの指示"))
        layout.addWidget(sent_group)
        
        layout.addStretch()
        
        return tab
    
    def _create_codex_tab(self) -> QWidget:
        """Create Codex CLI settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Codex path
        codex_group = QGroupBox("Codex CLI パス")
        codex_layout = QVBoxLayout(codex_group)
        
        help_label = QLabel(
            "Codex CLI の実行ファイルのパスを指定します。\n"
            "空白の場合は自動検出されます。"
        )
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #666; font-size: 11px;")
        codex_layout.addWidget(help_label)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("パス:"))
        
        self.codex_path_input = QLineEdit()
        self.codex_path_input.setPlaceholderText("codex.exe または /path/to/codex")
        path_layout.addWidget(self.codex_path_input, 1)
        
        browse_btn = QPushButton("参照...")
        browse_btn.clicked.connect(self._browse_codex_path)
        path_layout.addWidget(browse_btn)
        
        codex_layout.addLayout(path_layout)
        
        # Test button
        test_btn = QPushButton("Codex CLI バージョン確認")
        test_btn.clicked.connect(self._test_codex_cli)
        codex_layout.addWidget(test_btn)
        
        layout.addWidget(codex_group)
        layout.addStretch()
        
        return tab
    
    def _load_settings(self):
        """Load settings from storage."""
        # API key
        self.api_key_input.setText(self.storage.get_api_key())
        
        # Transmission policy
        policy = self.storage.get_transmission_policy()
        self.send_content_check.setChecked(policy.get('send_file_content', False))
        self.max_files_spin.setValue(policy.get('max_files_to_send', 10))
        self.max_size_spin.setValue(policy.get('max_file_size', 102400) // 1024)
        self.send_diff_check.setChecked(policy.get('send_diff_summary', True))
        self.send_error_check.setChecked(policy.get('send_error_messages', True))
        
        # Codex path
        self.codex_path_input.setText(self.storage.get('codex_path', ''))
    
    def _save_settings(self):
        """Save settings to storage."""
        # API key
        self.storage.set_api_key(self.api_key_input.text().strip())
        
        # Transmission policy
        policy = {
            'send_file_content': self.send_content_check.isChecked(),
            'max_files_to_send': self.max_files_spin.value(),
            'max_file_size': self.max_size_spin.value() * 1024,
            'send_diff_summary': self.send_diff_check.isChecked(),
            'send_error_messages': self.send_error_check.isChecked()
        }
        self.storage.set_transmission_policy(policy)
        
        # Codex path
        self.storage.set('codex_path', self.codex_path_input.text().strip())
    
    def _browse_codex_path(self):
        """Browse for Codex CLI executable."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Codex CLI 実行ファイルを選択",
            "",
            "実行ファイル (*.exe *.cmd);;すべてのファイル (*.*)"
        )
        
        if file_path:
            self.codex_path_input.setText(file_path)
    
    def _test_api_connection(self):
        """Test OpenAI API connection."""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            QMessageBox.warning(
                self,
                "API キー未入力",
                "OpenAI API キーを入力してください。"
            )
            return
        
        # TODO: Actual API test in M2
        QMessageBox.information(
            self,
            "接続テスト",
            "API キーが入力されています。\n\n"
            "実際の接続テストは M2 で実装されます。"
        )
    
    def _test_codex_cli(self):
        """Test Codex CLI."""
        from core.codex_wrapper import CodexWrapper
        
        codex_path = self.codex_path_input.text().strip() or None
        wrapper = CodexWrapper(codex_path)
        
        if wrapper.is_available():
            version = wrapper.get_version()
            QMessageBox.information(
                self,
                "Codex CLI 確認",
                f"✓ Codex CLI が利用可能です\n\n{version}"
            )
        else:
            help_text = wrapper.get_installation_help()
            QMessageBox.warning(
                self,
                "Codex CLI が見つかりません",
                help_text
            )
    
    def _on_accepted(self):
        """Handle OK button click."""
        self._save_settings()
        
        QMessageBox.information(
            self,
            "設定を保存しました",
            "設定が正常に保存されました。"
        )
        
        self.accept()
