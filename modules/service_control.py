"""
Service Control Module
Example module for controlling services (simulated for demonstration)
In a real implementation, this could control actual system services
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from module_base import ModuleBase
from datetime import datetime


class ServiceControlModule(ModuleBase):
    """Module to control a service (simulated)"""

    def __init__(self):
        self.is_running = False
        self.start_time = None
        self.restart_count = 0

    @property
    def name(self) -> str:
        return "Service Control"

    @property
    def description(self) -> str:
        return "Start, stop, and restart the demo service"

    @property
    def icon(self) -> str:
        return "⚡"

    @property
    def color(self) -> str:
        return "#10b981"

    def get_status(self):
        """Get current service status"""
        status = {
            "status": "Running" if self.is_running else "Stopped",
            "restart_count": self.restart_count
        }

        if self.is_running and self.start_time:
            uptime = datetime.now() - self.start_time
            status["uptime"] = self._format_uptime(uptime)

        return status

    def get_actions(self):
        """Get available actions"""
        if self.is_running:
            return [
                {
                    "id": "stop",
                    "label": "⏹️ Stop Service",
                    "variant": "danger"
                },
                {
                    "id": "restart",
                    "label": "🔄 Restart Service",
                    "variant": "warning"
                }
            ]
        else:
            return [
                {
                    "id": "start",
                    "label": "▶️ Start Service",
                    "variant": "success"
                }
            ]

    def execute_action(self, action_id: str, params=None):
        """Execute action"""
        if action_id == "start":
            if self.is_running:
                return {
                    "success": False,
                    "error": "Service is already running"
                }
            self.is_running = True
            self.start_time = datetime.now()
            return {
                "success": True,
                "message": "Service started successfully"
            }

        elif action_id == "stop":
            if not self.is_running:
                return {
                    "success": False,
                    "error": "Service is already stopped"
                }
            self.is_running = False
            self.start_time = None
            return {
                "success": True,
                "message": "Service stopped successfully"
            }

        elif action_id == "restart":
            if not self.is_running:
                return {
                    "success": False,
                    "error": "Service is not running"
                }
            self.start_time = datetime.now()
            self.restart_count += 1
            return {
                "success": True,
                "message": "Service restarted successfully"
            }

        return {
            "success": False,
            "error": f"Unknown action: {action_id}"
        }

    @staticmethod
    def _format_uptime(uptime):
        """Format uptime timedelta to readable string"""
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 and not parts:
            parts.append(f"{seconds}s")

        return " ".join(parts) if parts else "< 1s"
