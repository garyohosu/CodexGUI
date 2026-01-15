"""
Storage Module

Manages settings, API keys, and execution history.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class Storage:
    """Persistent storage for application settings and history."""
    
    def __init__(self):
        """Initialize storage."""
        self.settings_dir = self._get_settings_dir()
        self.settings_file = self.settings_dir / "settings.json"
        self.history_file = self.settings_dir / "history.json"
        
        # Ensure directory exists
        self.settings_dir.mkdir(parents=True, exist_ok=True)
        
        # Load settings
        self.settings = self._load_settings()
    
    def _get_settings_dir(self) -> Path:
        """Get settings directory path."""
        home = Path.home()
        return home / ".codexgui-next"
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
        
        # Default settings
        return {
            "openai_api_key": "",
            "codex_path": "",
            "language": "ja",
            "transmission_policy": {
                "send_file_content": False,
                "max_files_to_send": 10,
                "max_file_size": 1024 * 100,  # 100KB
                "send_diff_summary": True,
                "send_error_messages": True
            }
        }
    
    def _save_settings(self):
        """Save settings to file."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get setting value.
        
        Args:
            key: Setting key (dot notation supported, e.g., 'transmission_policy.send_file_content')
            default: Default value if not found
        
        Returns:
            Setting value
        """
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set setting value.
        
        Args:
            key: Setting key (dot notation supported)
            value: Value to set
        """
        keys = key.split('.')
        target = self.settings
        
        # Navigate to the parent
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        # Set value
        target[keys[-1]] = value
        self._save_settings()
    
    def get_api_key(self) -> str:
        """Get OpenAI API key."""
        return self.get("openai_api_key", "")
    
    def set_api_key(self, api_key: str):
        """Set OpenAI API key."""
        self.set("openai_api_key", api_key)
    
    def get_transmission_policy(self) -> Dict[str, Any]:
        """Get transmission policy settings."""
        return self.get("transmission_policy", {})
    
    def set_transmission_policy(self, policy: Dict[str, Any]):
        """Set transmission policy settings."""
        self.set("transmission_policy", policy)
    
    def add_history_entry(self, entry: Dict[str, Any]):
        """
        Add execution history entry.
        
        Args:
            entry: History entry with task info and results
        """
        try:
            # Load existing history
            history = []
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # Add timestamp
            entry['timestamp'] = datetime.now().isoformat()
            
            # Add new entry
            history.append(entry)
            
            # Keep only last 100 entries
            history = history[-100:]
            
            # Save
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def get_history(self, limit: int = 50) -> list:
        """
        Get execution history.
        
        Args:
            limit: Maximum number of entries to return
        
        Returns:
            List of history entries
        """
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    return history[-limit:]
        except Exception as e:
            print(f"Error loading history: {e}")
        
        return []
    
    def clear_history(self):
        """Clear execution history."""
        try:
            if self.history_file.exists():
                self.history_file.unlink()
        except Exception as e:
            print(f"Error clearing history: {e}")


# Global storage instance
_storage: Optional[Storage] = None


def get_storage() -> Storage:
    """
    Get global storage instance.
    
    Returns:
        Storage instance
    """
    global _storage
    if _storage is None:
        _storage = Storage()
    return _storage
