"""
Explorer Panel

File tree view with selection support.
"""

import os
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QFileDialog, QHBoxLayout, QLabel, QLineEdit
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon


class ExplorerPanel(QWidget):
    """Panel for browsing and selecting files/folders."""
    
    # Signals
    folder_changed = Signal(str)  # Emitted when target folder changes
    selection_changed = Signal(list)  # Emitted when file selection changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_folder = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title_label = QLabel("📁 Explorer")
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
        
        # Folder selection
        folder_layout = QHBoxLayout()
        folder_layout.setContentsMargins(8, 8, 8, 8)
        
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Select target folder...")
        self.folder_input.setReadOnly(True)
        folder_layout.addWidget(self.folder_input, 1)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._on_browse_clicked)
        folder_layout.addWidget(browse_btn)
        
        layout.addLayout(folder_layout)
        
        # File tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Size", "Type"])
        self.tree.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.tree.setColumnWidth(0, 250)
        self.tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #ddd;
                background-color: white;
            }
            QTreeWidget::item {
                padding: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #e3f2fd;
                color: black;
            }
        """)
        layout.addWidget(self.tree)
        
        # Status
        self.status_label = QLabel("No folder selected")
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 4px 8px;
                color: gray;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.status_label)
    
    def _on_browse_clicked(self):
        """Handle browse button click."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Target Folder",
            self.current_folder or ""
        )
        
        if folder:
            self.set_folder(folder)
    
    def set_folder(self, folder_path: str):
        """
        Set target folder and load file tree.
        
        Args:
            folder_path: Path to folder
        """
        self.current_folder = folder_path
        self.folder_input.setText(folder_path)
        self._load_tree()
        self.folder_changed.emit(folder_path)
    
    def _load_tree(self):
        """Load file tree for current folder."""
        self.tree.clear()
        
        if not self.current_folder or not os.path.exists(self.current_folder):
            return
        
        try:
            root_path = Path(self.current_folder)
            root_item = QTreeWidgetItem(self.tree)
            root_item.setText(0, root_path.name or str(root_path))
            root_item.setText(2, "Folder")
            root_item.setData(0, Qt.UserRole, str(root_path))
            
            # Load contents recursively (limit depth for performance)
            self._load_tree_recursive(root_path, root_item, depth=0, max_depth=3)
            
            root_item.setExpanded(True)
            
            # Update status
            file_count = self._count_files(root_path)
            self.status_label.setText(f"{file_count} files")
            
        except Exception as e:
            self.status_label.setText(f"Error loading folder: {e}")
    
    def _load_tree_recursive(self, path: Path, parent_item: QTreeWidgetItem, depth: int, max_depth: int):
        """
        Recursively load directory tree.
        
        Args:
            path: Directory path
            parent_item: Parent tree item
            depth: Current depth
            max_depth: Maximum depth to traverse
        """
        if depth >= max_depth:
            return
        
        try:
            # Get sorted entries (folders first)
            entries = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            
            for entry in entries:
                # Skip hidden files (starting with .)
                if entry.name.startswith('.'):
                    continue
                
                item = QTreeWidgetItem(parent_item)
                item.setText(0, entry.name)
                item.setData(0, Qt.UserRole, str(entry))
                
                if entry.is_dir():
                    item.setText(2, "Folder")
                    # Load subdirectory
                    self._load_tree_recursive(entry, item, depth + 1, max_depth)
                else:
                    # File
                    try:
                        size = entry.stat().st_size
                        item.setText(1, self._format_size(size))
                        item.setText(2, entry.suffix or "File")
                    except:
                        item.setText(2, "File")
                        
        except PermissionError:
            pass
        except Exception as e:
            print(f"Error loading {path}: {e}")
    
    def _format_size(self, size: int) -> str:
        """Format file size in human-readable form."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def _count_files(self, path: Path, max_count: int = 10000) -> int:
        """Count files in directory."""
        count = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    count += 1
                    if count >= max_count:
                        return max_count
        except:
            pass
        return count
    
    def _on_selection_changed(self):
        """Handle selection change."""
        selected_items = self.tree.selectedItems()
        selected_paths = [item.data(0, Qt.UserRole) for item in selected_items]
        self.selection_changed.emit(selected_paths)
    
    def get_selected_files(self) -> list:
        """Get list of selected file paths."""
        selected_items = self.tree.selectedItems()
        return [item.data(0, Qt.UserRole) for item in selected_items]
    
    def get_current_folder(self) -> str:
        """Get current target folder."""
        return self.current_folder or ""
