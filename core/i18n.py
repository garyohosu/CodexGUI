"""
Language Manager Module

This module handles internationalization (i18n) for the application.
"""

import json
import os
from typing import Optional, Dict, Any
from pathlib import Path


class LanguageManager:
    """Manager for application internationalization."""
    
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'ja': 'Japanese (日本語)'
    }
    
    DEFAULT_LANGUAGE = 'en'
    
    def __init__(self):
        """Initialize language manager."""
        self.current_language = self.DEFAULT_LANGUAGE
        self.translations: Dict[str, Any] = {}
        self.i18n_dir = self._get_i18n_dir()
        self._load_language(self.current_language)
    
    def _get_i18n_dir(self) -> Path:
        """
        Get i18n directory path.
        
        Returns:
            Path to i18n directory
        """
        # Get path relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return Path(os.path.join(os.path.dirname(current_dir), "i18n"))
    
    def _load_language(self, language_code: str) -> bool:
        """
        Load language file.
        
        Args:
            language_code: Language code (e.g., 'en', 'ja')
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            lang_file = self.i18n_dir / f"{language_code}.json"
            
            if not lang_file.exists():
                print(f"Language file not found: {lang_file}")
                return False
            
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
            
            self.current_language = language_code
            return True
            
        except Exception as e:
            print(f"Error loading language file: {e}")
            return False
    
    def set_language(self, language_code: str) -> bool:
        """
        Set current language.
        
        Args:
            language_code: Language code (e.g., 'en', 'ja')
        
        Returns:
            True if language was changed successfully, False otherwise
        """
        if language_code not in self.SUPPORTED_LANGUAGES:
            print(f"Unsupported language: {language_code}")
            return False
        
        if language_code == self.current_language:
            return True
        
        return self._load_language(language_code)
    
    def get_current_language(self) -> str:
        """
        Get current language code.
        
        Returns:
            Current language code
        """
        return self.current_language
    
    def get_language_name(self, language_code: Optional[str] = None) -> str:
        """
        Get language display name.
        
        Args:
            language_code: Language code (default: current language)
        
        Returns:
            Language display name
        """
        code = language_code or self.current_language
        return self.SUPPORTED_LANGUAGES.get(code, code)
    
    def tr(self, key: str, **kwargs) -> str:
        """
        Translate a key.
        
        Args:
            key: Translation key in dot notation (e.g., 'menu.file')
            **kwargs: Optional format parameters
        
        Returns:
            Translated string
        """
        # Split key by dots and traverse dictionary
        keys = key.split('.')
        value = self.translations
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # Key not found, return the key itself
                return key
        
        # If value is not a string, return key
        if not isinstance(value, str):
            return key
        
        # Format string with kwargs if provided
        if kwargs:
            try:
                return value.format(**kwargs)
            except (KeyError, ValueError):
                return value
        
        return value
    
    def get_all_languages(self) -> Dict[str, str]:
        """
        Get all supported languages.
        
        Returns:
            Dictionary of language codes and names
        """
        return self.SUPPORTED_LANGUAGES.copy()
    
    def save_language_preference(self, language_code: str):
        """
        Save language preference to settings.
        
        Args:
            language_code: Language code to save
        """
        try:
            from gui.settings_dialog import SettingsDialog
            
            # Get settings file path
            home = os.path.expanduser("~")
            settings_dir = os.path.join(home, ".codexgui")
            settings_file = os.path.join(settings_dir, "settings.json")
            
            # Load existing settings
            settings = {}
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
            
            # Update language
            settings['language'] = language_code
            
            # Save settings
            os.makedirs(settings_dir, exist_ok=True)
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            print(f"Error saving language preference: {e}")
    
    def load_language_preference(self) -> str:
        """
        Load language preference from settings.
        
        Returns:
            Saved language code or default language
        """
        try:
            home = os.path.expanduser("~")
            settings_file = os.path.join(home, ".codexgui", "settings.json")
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get('language', self.DEFAULT_LANGUAGE)
                    
        except Exception as e:
            print(f"Error loading language preference: {e}")
        
        return self.DEFAULT_LANGUAGE


# Global language manager instance
_language_manager: Optional[LanguageManager] = None


def get_language_manager() -> LanguageManager:
    """
    Get the global language manager instance.
    
    Returns:
        LanguageManager instance
    """
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager()
        # Load saved language preference
        saved_lang = _language_manager.load_language_preference()
        _language_manager.set_language(saved_lang)
    return _language_manager


def tr(key: str, **kwargs) -> str:
    """
    Convenience function to translate a key.
    
    Args:
        key: Translation key in dot notation
        **kwargs: Optional format parameters
    
    Returns:
        Translated string
    """
    return get_language_manager().tr(key, **kwargs)
