"""
FastAPI backend for server control panel
Automatically discovers and loads modules from the modules directory
"""

from fastapi import FastAPI, Request, Depends, HTTPException, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext
from dotenv import load_dotenv
import importlib
import inspect
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from module_base import ModuleBase

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / '.env')

app = FastAPI(title="Server Control Panel")

# Session configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="session",
    max_age=3600,
    same_site="lax",
    https_only=False
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates - use absolute paths
base_dir = Path(__file__).parent.parent
app.mount("/static", StaticFiles(directory=str(base_dir / "static")), name="static")
templates = Jinja2Templates(directory=str(base_dir / "templates"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Authentication credentials (from environment variables)
AUTH_USERNAME = os.environ.get('AUTH_USERNAME', 'admin')
AUTH_PASSWORD_HASH = os.environ.get('AUTH_PASSWORD_HASH', pwd_context.hash('admin'))

# Store loaded modules
modules: Dict[str, ModuleBase] = {}


async def get_session(request: Request):
    """Get session from request"""
    return request.session


async def require_authentication(request: Request):
    """Dependency to require authentication"""
    if 'authenticated' not in request.session:
        if request.url.path.startswith('/api/'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/login"}
        )
    return request.session


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


@app.get('/login', response_class=HTMLResponse)
async def login_page(request: Request):
    """Display login page"""
    # If already authenticated, redirect to main page
    if 'authenticated' in request.session:
        return RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse('login.html', {'request': request})


@app.post('/login')
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """Handle login authentication"""
    if username == AUTH_USERNAME and pwd_context.verify(password, AUTH_PASSWORD_HASH):
        request.session['authenticated'] = True
        request.session['username'] = username
        return RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)
    else:
        return RedirectResponse(url='/login?error=invalid', status_code=status.HTTP_303_SEE_OTHER)


@app.get('/logout')
async def logout(request: Request):
    """Log out the current user"""
    request.session.clear()
    return RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)


@app.get('/', response_class=HTMLResponse)
async def index(request: Request, session=Depends(require_authentication)):
    """Serve the main control panel page"""
    return templates.TemplateResponse('index.html', {'request': request})


@app.get('/api/modules')
async def get_modules_api(session=Depends(require_authentication)):
    """Get all available modules and their current state"""
    return {
        "success": True,
        "modules": [module.get_module_data() for module in modules.values()]
    }


@app.get('/api/modules/{module_id}/status')
async def get_module_status_api(module_id: str, session=Depends(require_authentication)):
    """Get status for a specific module"""
    if module_id not in modules:
        raise HTTPException(status_code=404, detail="Module not found")

    try:
        module_status = modules[module_id].get_status()
        return {"success": True, "status": module_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/modules/{module_id}/action')
async def execute_module_action_api(
    module_id: str,
    request: Request,
    session=Depends(require_authentication)
):
    """Execute an action on a specific module"""
    if module_id not in modules:
        raise HTTPException(status_code=404, detail="Module not found")

    data = await request.json()
    action_id = data.get('action_id')
    params = data.get('params', {})

    if not action_id:
        raise HTTPException(status_code=400, detail="action_id is required")

    try:
        result = modules[module_id].execute_action(action_id, params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/reload')
async def reload_modules_api(session=Depends(require_authentication)):
    """Reload all modules (useful for development)"""
    try:
        discover_modules()
        return {
            "success": True,
            "message": f"Reloaded {len(modules)} modules",
            "modules": list(modules.keys())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("=" * 50)
    print("Server Control Panel - Starting")
    print("=" * 50)
    discover_modules()
    print("=" * 50)
