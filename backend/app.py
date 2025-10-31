"""
Flask backend for server control panel
Automatically discovers and loads modules from the modules directory
"""

from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from dotenv import load_dotenv
import importlib
import inspect
import os
import sys
from pathlib import Path
from typing import Dict, List
from module_base import ModuleBase

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / '.env')

app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')

# Session configuration
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

CORS(app)

# Authentication credentials (from environment variables)
AUTH_USERNAME = os.environ.get('AUTH_USERNAME', 'admin')
AUTH_PASSWORD_HASH = os.environ.get('AUTH_PASSWORD_HASH', generate_password_hash('admin'))

# Store loaded modules
modules: Dict[str, ModuleBase] = {}


def login_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'authenticated' not in session:
            if request.path.startswith('/api/'):
                return jsonify({"success": False, "error": "Authentication required"}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def discover_modules():
    """Discover and load all modules from the modules directory"""
    global modules
    modules = {}

    # Add modules directory to Python path
    modules_dir = Path(__file__).parent.parent / "modules"
    if str(modules_dir) not in sys.path:
        sys.path.insert(0, str(modules_dir))

    if not modules_dir.exists():
        print(f"Warning: modules directory not found at {modules_dir}")
        return

    # Find all Python files in modules directory
    for file_path in modules_dir.glob("*.py"):
        if file_path.name.startswith("_"):
            continue

        module_name = file_path.stem

        try:
            # Import the module
            module = importlib.import_module(module_name)

            # Find all classes that inherit from ModuleBase
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, ModuleBase) and obj != ModuleBase:
                    # Instantiate the module
                    module_instance = obj()
                    module_id = obj.__name__.lower()
                    modules[module_id] = module_instance
                    print(f"✓ Loaded module: {module_instance.name} ({module_id})")

        except Exception as e:
            print(f"✗ Error loading module {module_name}: {e}")

    print(f"\nTotal modules loaded: {len(modules)}")


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login page and authentication"""
    if request.method == 'GET':
        # If already authenticated, redirect to main page
        if 'authenticated' in session:
            return redirect(url_for('index'))
        return render_template('login.html')

    # POST request - process login
    username = request.form.get('username')
    password = request.form.get('password')

    if username == AUTH_USERNAME and check_password_hash(AUTH_PASSWORD_HASH, password):
        session['authenticated'] = True
        session['username'] = username
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login', error='invalid'))


@app.route('/logout')
def logout():
    """Log out the current user"""
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    """Serve the main control panel page"""
    return render_template('index.html')


@app.route('/api/modules')
@login_required
def get_modules():
    """Get all available modules and their current state"""
    return jsonify({
        "success": True,
        "modules": [module.get_module_data() for module in modules.values()]
    })


@app.route('/api/modules/<module_id>/status')
@login_required
def get_module_status(module_id):
    """Get status for a specific module"""
    if module_id not in modules:
        return jsonify({"success": False, "error": "Module not found"}), 404

    try:
        status = modules[module_id].get_status()
        return jsonify({"success": True, "status": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/modules/<module_id>/action', methods=['POST'])
@login_required
def execute_module_action(module_id):
    """Execute an action on a specific module"""
    if module_id not in modules:
        return jsonify({"success": False, "error": "Module not found"}), 404

    data = request.get_json() or {}
    action_id = data.get('action_id')
    params = data.get('params', {})

    if not action_id:
        return jsonify({"success": False, "error": "action_id is required"}), 400

    try:
        result = modules[module_id].execute_action(action_id, params)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/reload')
@login_required
def reload_modules():
    """Reload all modules (useful for development)"""
    try:
        discover_modules()
        return jsonify({
            "success": True,
            "message": f"Reloaded {len(modules)} modules",
            "modules": list(modules.keys())
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    print("=" * 50)
    print("Server Control Panel - Starting")
    print("=" * 50)
    discover_modules()
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5001)
