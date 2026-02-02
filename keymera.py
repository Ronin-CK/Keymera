import asyncio
import re
import os
import subprocess
import sys
import signal
import json
import time
import atexit
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import shutil
import warnings

# Suppress Gemini API deprecation warning
warnings.filterwarnings("ignore", category=FutureWarning, message=".*All support for the `google.generativeai`.*")
os.environ["GRPC_VERBOSITY"] = "ERROR"  # Silence gRPC noise too

__version__ = "2.1.0"
__author__ = "Chandra Kant"

# ═══════════════════════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).parent.absolute()
USER_DATA_DIR = Path.home() / ".local" / "share" / "keymera"

# Use centralized data dir if it exists (so CLI commands update the live service)
# Otherwise fall back to local script dir (dev mode / portable)
if USER_DATA_DIR.exists():
    BASE_DIR = USER_DATA_DIR
else:
    BASE_DIR = SCRIPT_DIR

CONFIG_FILE = BASE_DIR / "config.json"
STYLES_FILE = BASE_DIR / "styles.json"
API_KEY_FILE = BASE_DIR / "api_key.txt"
PID_FILE = Path("/tmp/keymera.pid")
HISTORY_FILE = Path.home() / ".cache" / "keymera" / "history.json"

# ═══════════════════════════════════════════════════════════════════════════════
# DEPENDENCY CHECK
# ═══════════════════════════════════════════════════════════════════════════════


def check_dependencies() -> bool:
    """Verify all required packages are installed"""
    missing = []
    
    try:
        from evdev import InputDevice, UInput, ecodes
    except ImportError:
        missing.append("evdev")
        
    try:
        import google.generativeai
    except ImportError:
        missing.append("google-generativeai")

    try:
        import aiohttp
    except ImportError:
        missing.append("aiohttp")
    
    if missing:
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                    MISSING DEPENDENCIES                      ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        for dep in missing:
            print(f"  ✗ {dep}")
        print(f"\nInstall with:\n  pip install {' '.join(missing)} --break-system-packages")
        return False
    
    # Check for clipboard tools
    wl_copy = subprocess.run(['which', 'wl-copy'], capture_output=True)
    wl_paste = subprocess.run(['which', 'wl-paste'], capture_output=True)
