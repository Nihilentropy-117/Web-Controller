"""
Quick Commands Module
Execute predefined server commands quickly
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from module_base import ModuleBase
import subprocess
from datetime import datetime


class QuickCommandsModule(ModuleBase):
    """Module for executing quick commands"""

    def __init__(self):
        self.last_command = None
        self.last_execution = None
        self.execution_count = 0

    @property
    def name(self) -> str:
        return "Quick Commands"

    @property
    def description(self) -> str:
        return "Execute common server commands with a single click"

    @property
    def icon(self) -> str:
        return "⚙️"

    @property
    def color(self) -> str:
        return "#f59e0b"

    def get_status(self):
        """Get current status"""
        status = {
            "total_executions": self.execution_count
        }

        if self.last_command:
            status["last_command"] = self.last_command

        if self.last_execution:
            status["last_run"] = self.last_execution.strftime("%Y-%m-%d %H:%M:%S")

        return status

    def get_actions(self):
        """Get available actions"""
        return [
            {
                "id": "check_disk",
                "label": "💾 Check Disk Space",
                "variant": "primary"
            },
            {
                "id": "list_processes",
                "label": "📋 List Top Processes",
                "variant": "primary"
            },
            {
                "id": "network_info",
                "label": "🌐 Network Info",
                "variant": "primary"
            },
            {
                "id": "date_time",
                "label": "🕐 Show Date/Time",
                "variant": "secondary"
            }
        ]

    def execute_action(self, action_id: str, params=None):
        """Execute action"""
        commands = {
            "check_disk": ("df -h /", "Disk space"),
            "list_processes": ("ps aux | head -10", "Top processes"),
            "network_info": ("ifconfig 2>/dev/null || ip addr 2>/dev/null || echo 'Network info unavailable'", "Network info"),
            "date_time": ("date", "Current date/time")
        }

        if action_id not in commands:
            return {
                "success": False,
                "error": f"Unknown action: {action_id}"
            }

        command, description = commands[action_id]

        try:
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            self.last_command = description
            self.last_execution = datetime.now()
            self.execution_count += 1

            output = result.stdout.strip() if result.stdout else result.stderr.strip()
            output_preview = output[:200] + "..." if len(output) > 200 else output

            return {
                "success": True,
                "message": f"{description} executed successfully",
                "data": {
                    "output": output_preview,
                    "return_code": result.returncode
                }
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 10 seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to execute command: {str(e)}"
            }
