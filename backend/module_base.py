"""
Base class for all server control modules.
Each module should inherit from this class and implement the required methods.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class ModuleBase(ABC):
    """Base class for all control modules"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Module display name"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Module description"""
        pass

    @property
    def icon(self) -> str:
        """Module icon (emoji or icon class)"""
        return "⚙️"

    @property
    def color(self) -> str:
        """Module color theme (hex color)"""
        return "#6366f1"

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Get current module status/state
        Returns: Dict with status information
        """
        pass

    @abstractmethod
    def get_actions(self) -> List[Dict[str, Any]]:
        """
        Get available actions for this module
        Returns: List of action definitions with:
            - id: unique action identifier
            - label: button label
            - type: 'button', 'input', 'toggle', etc.
            - variant: 'primary', 'danger', 'success', etc.
        """
        pass

    @abstractmethod
    def execute_action(self, action_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a module action
        Args:
            action_id: The action identifier
            params: Optional parameters for the action
        Returns: Dict with:
            - success: bool
            - message: str
            - data: optional additional data
        """
        pass

    def get_module_data(self) -> Dict[str, Any]:
        """Get complete module data for frontend"""
        return {
            "id": self.__class__.__name__.lower(),
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "color": self.color,
            "status": self.get_status(),
            "actions": self.get_actions()
        }
