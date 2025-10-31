# Server Control Panel

A beautiful, modular web-based control panel for managing server operations. Built with Flask (Python backend) and modern HTML/CSS/JS (frontend).

## Features

- 🎨 **Modern, Beautiful UI** - Dark theme with smooth animations and responsive design
- 🔌 **Modular Architecture** - Easily add new control modules by creating Python files
- 🔄 **Hot Reload** - Add new modules without restarting the server
- ⚡ **Real-time Updates** - Automatic status refresh every 30 seconds
- 📱 **Responsive** - Works great on desktop and mobile devices

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Server

```bash
cd backend
python app.py
```

### 3. Open in Browser

Navigate to `http://localhost:5000`

## Project Structure

```
control_site/
├── backend/
│   ├── app.py              # Flask application and API routes
│   └── module_base.py      # Base class for all modules
├── modules/
│   ├── system_info.py      # System information module
│   ├── service_control.py  # Service control module
│   └── quick_commands.py   # Quick commands module
├── static/
│   ├── style.css           # Frontend styles
│   └── app.js              # Frontend JavaScript
├── templates/
│   └── index.html          # Main HTML page
└── requirements.txt        # Python dependencies
```

## Creating a New Module

Modules are incredibly easy to create! Just follow these steps:

### 1. Create a New Python File

Create a new file in the `modules/` directory, e.g., `modules/my_module.py`

### 2. Implement the Module Class

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from module_base import ModuleBase

class MyModule(ModuleBase):
    """Your custom module"""

    @property
    def name(self) -> str:
        return "My Custom Module"

    @property
    def description(self) -> str:
        return "Description of what this module does"

    @property
    def icon(self) -> str:
        return "🎯"  # Any emoji

    @property
    def color(self) -> str:
        return "#10b981"  # Hex color for the module card

    def get_status(self):
        """Return a dict of status information to display"""
        return {
            "status": "Active",
            "items_count": 42,
            "last_update": "2025-10-30"
        }

    def get_actions(self):
        """Return a list of available actions/buttons"""
        return [
            {
                "id": "do_something",
                "label": "🚀 Do Something",
                "variant": "primary"  # primary, success, danger, warning, secondary
            },
            {
                "id": "do_something_else",
                "label": "⭐ Do Something Else",
                "variant": "success"
            }
        ]

    def execute_action(self, action_id: str, params=None):
        """Handle action execution"""
        if action_id == "do_something":
            # Your logic here
            return {
                "success": True,
                "message": "Action completed successfully!"
            }

        elif action_id == "do_something_else":
            # Your logic here
            return {
                "success": True,
                "message": "Something else was done!"
            }

        return {
            "success": False,
            "error": f"Unknown action: {action_id}"
        }
```

### 3. Reload Modules

Click the "🔄 Reload Modules" button in the UI, or restart the server. Your new module will automatically appear!

## Module API Reference

### Required Properties

- `name` - Display name for the module
- `description` - Short description of what the module does
- `icon` - Emoji or icon to display (default: ⚙️)
- `color` - Hex color for the module card theme (default: #6366f1)

### Required Methods

#### `get_status() -> Dict[str, Any]`

Returns a dictionary of status information to display. The keys become labels, and values are displayed.

**Special handling:**
- Boolean values are shown as Yes/No badges
- Keys containing "status" are shown as colored badges
- All other values are displayed as text

**Example:**
```python
def get_status(self):
    return {
        "status": "Running",        # Shows as colored badge
        "cpu_usage": "45%",         # Shows as text
        "is_enabled": True,         # Shows as green "Yes" badge
        "uptime": "3d 5h 22m"       # Shows as text
    }
```

#### `get_actions() -> List[Dict[str, Any]]`

Returns a list of action buttons to display. Each action should have:
- `id` - Unique identifier for the action
- `label` - Button text (can include emojis)
- `variant` - Button style: `primary`, `success`, `danger`, `warning`, or `secondary`

**Example:**
```python
def get_actions(self):
    return [
        {
            "id": "start",
            "label": "▶️ Start",
            "variant": "success"
        },
        {
            "id": "stop",
            "label": "⏹️ Stop",
            "variant": "danger"
        }
    ]
```

#### `execute_action(action_id: str, params: Dict = None) -> Dict[str, Any]`

Handles action execution. Should return a dictionary with:
- `success` - Boolean indicating if the action succeeded
- `message` - Success message (shown in toast notification)
- `error` - Error message if success is False
- `data` - Optional additional data

**Example:**
```python
def execute_action(self, action_id: str, params=None):
    if action_id == "start":
        # Your logic here
        return {
            "success": True,
            "message": "Service started successfully"
        }

    return {
        "success": False,
        "error": f"Unknown action: {action_id}"
    }
```

## Action Button Variants

- `primary` - Blue, for main actions
- `success` - Green, for positive actions (start, enable, etc.)
- `danger` - Red, for destructive actions (stop, delete, etc.)
- `warning` - Orange, for caution actions (restart, reset, etc.)
- `secondary` - Gray, for secondary actions

## Tips

1. **Keep modules focused** - Each module should handle one specific area of functionality
2. **Use descriptive names** - Make action labels clear and use emojis for visual appeal
3. **Handle errors gracefully** - Always return proper error messages
4. **Update status frequently** - The frontend auto-refreshes every 30 seconds
5. **Test thoroughly** - Use the reload button to quickly test changes without restarting

## Example Modules Included

1. **System Information** - Displays CPU, memory, disk usage, and uptime
2. **Service Control** - Start, stop, and restart a demo service
3. **Quick Commands** - Execute common server commands

## Customization

### Frontend Styling

Edit `static/style.css` to customize colors, fonts, spacing, etc.

### Backend Configuration

Edit `backend/app.py` to change the port, host, or add custom API endpoints.

## API Endpoints

- `GET /` - Serve the main page
- `GET /api/modules` - Get all modules and their current state
- `GET /api/modules/<id>/status` - Get status for a specific module
- `POST /api/modules/<id>/action` - Execute an action on a module
- `GET /api/reload` - Reload all modules

## Requirements

- Python 3.7+
- Flask 3.0.0
- flask-cors 4.0.0
- psutil 5.9.6

## License

Feel free to use and modify as needed for your server management needs!
