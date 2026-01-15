"""
Template Management Module

This module handles loading and managing prompt templates for common tasks.
"""

import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class TaskTemplate:
    """Represents a task template."""
    id: str
    name: str
    description: str
    prompt: str
    category: str


class TemplateManager:
    """Manager for task templates."""
    
    def __init__(self, templates_file: Optional[str] = None):
        """
        Initialize template manager.
        
        Args:
            templates_file: Path to templates JSON file (default: resources/templates.json)
        """
        if templates_file is None:
            # Get path relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            templates_file = os.path.join(
                os.path.dirname(current_dir),
                "resources",
                "templates.json"
            )
        
        self.templates_file = templates_file
        self.templates: List[TaskTemplate] = []
        self._load_templates()
    
    def _load_templates(self):
        """Load templates from JSON file."""
        try:
            if os.path.exists(self.templates_file):
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for template_data in data.get('templates', []):
                        template = TaskTemplate(
                            id=template_data['id'],
                            name=template_data['name'],
                            description=template_data['description'],
                            prompt=template_data['prompt'],
                            category=template_data['category']
                        )
                        self.templates.append(template)
        except Exception as e:
            print(f"Error loading templates: {e}")
    
    def get_all_templates(self) -> List[TaskTemplate]:
        """
        Get all templates.
        
        Returns:
            List of all TaskTemplate objects
        """
        return self.templates
    
    def get_template_by_id(self, template_id: str) -> Optional[TaskTemplate]:
        """
        Get template by ID.
        
        Args:
            template_id: Template ID to search for
        
        Returns:
            TaskTemplate if found, None otherwise
        """
        for template in self.templates:
            if template.id == template_id:
                return template
        return None
    
    def get_templates_by_category(self, category: str) -> List[TaskTemplate]:
        """
        Get templates by category.
        
        Args:
            category: Category name to filter by
        
        Returns:
            List of TaskTemplate objects in the specified category
        """
        return [t for t in self.templates if t.category == category]
    
    def get_categories(self) -> List[str]:
        """
        Get all unique categories.
        
        Returns:
            List of unique category names
        """
        categories = set(t.category for t in self.templates)
        return sorted(list(categories))
    
    def add_custom_template(
        self,
        name: str,
        description: str,
        prompt: str,
        category: str = "Custom"
    ) -> TaskTemplate:
        """
        Add a custom template.
        
        Args:
            name: Template name
            description: Template description
            prompt: Prompt text
            category: Category (default: "Custom")
        
        Returns:
            The created TaskTemplate
        """
        # Generate ID from name
        template_id = name.lower().replace(' ', '_')
        
        # Ensure unique ID
        counter = 1
        original_id = template_id
        while self.get_template_by_id(template_id) is not None:
            template_id = f"{original_id}_{counter}"
            counter += 1
        
        template = TaskTemplate(
            id=template_id,
            name=name,
            description=description,
            prompt=prompt,
            category=category
        )
        
        self.templates.append(template)
        return template
    
    def save_templates(self):
        """Save templates back to JSON file."""
        try:
            data = {
                'templates': [
                    {
                        'id': t.id,
                        'name': t.name,
                        'description': t.description,
                        'prompt': t.prompt,
                        'category': t.category
                    }
                    for t in self.templates
                ]
            }
            
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving templates: {e}")


# Module-level convenience functions
_template_manager = None


def get_template_manager() -> TemplateManager:
    """
    Get the global template manager instance.
    
    Returns:
        TemplateManager instance
    """
    global _template_manager
    if _template_manager is None:
        _template_manager = TemplateManager()
    return _template_manager


def get_all_templates() -> List[TaskTemplate]:
    """Get all templates."""
    return get_template_manager().get_all_templates()


def get_template_by_id(template_id: str) -> Optional[TaskTemplate]:
    """Get template by ID."""
    return get_template_manager().get_template_by_id(template_id)
