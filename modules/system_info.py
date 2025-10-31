"""
System Information Module
Displays server system information like CPU, memory, disk usage, etc.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from module_base import ModuleBase
import platform
import psutil
from datetime import datetime


class SystemInfoModule(ModuleBase):
    """Module to display system information"""

    @property
    def name(self) -> str:
        return "System Information"

    @property
    def description(self) -> str:
        return "View server system information, resource usage, and uptime"

    @property
    def icon(self) -> str:
        return "💻"

    @property
    def color(self) -> str:
        return "#3b82f6"

    def get_status(self):
        """Get current system information"""
        # CPU Information
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()

        # Memory Information
        memory = psutil.virtual_memory()
        memory_total = self._bytes_to_gb(memory.total)
        memory_used = self._bytes_to_gb(memory.used)
        memory_percent = memory.percent

        # Disk Information
        disk = psutil.disk_usage('/')
        disk_total = self._bytes_to_gb(disk.total)
        disk_used = self._bytes_to_gb(disk.used)
        disk_percent = disk.percent

        # Uptime
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        uptime_str = self._format_uptime(uptime)

        return {
            "hostname": platform.node(),
            "os": f"{platform.system()} {platform.release()}",
            "cpu_usage": f"{cpu_percent}%",
            "cpu_cores": cpu_count,
            "memory_usage": f"{memory_used:.1f}GB / {memory_total:.1f}GB ({memory_percent}%)",
            "disk_usage": f"{disk_used:.1f}GB / {disk_total:.1f}GB ({disk_percent}%)",
            "uptime": uptime_str,
            "python_version": platform.python_version()
        }

    def get_actions(self):
        """Get available actions"""
        return [
            {
                "id": "refresh",
                "label": "🔄 Refresh Info",
                "variant": "primary"
            }
        ]

    def execute_action(self, action_id: str, params=None):
        """Execute action"""
        if action_id == "refresh":
            # Just return success, the frontend will reload the status
            return {
                "success": True,
                "message": "System information refreshed"
            }

        return {
            "success": False,
            "error": f"Unknown action: {action_id}"
        }

    @staticmethod
    def _bytes_to_gb(bytes_value):
        """Convert bytes to gigabytes"""
        return bytes_value / (1024 ** 3)

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

        return " ".join(parts) if parts else "< 1m"
