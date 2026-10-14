#!/usr/bin/env python3
"""
Automatic installation script for Nexora Logger
"""

import sys
import subprocess
import os
import venv

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("[-] Python 3.8 or higher is required.")
        sys.exit(1)
    print(f"[+] Python {sys.version_info.major}.{sys.version_info.minor} detected.")

def create_virtual_env():
    """Create and return path to virtual environment python"""
    if os.name == 'nt':  # Windows
        python_path = os.path.join("venv", "Scripts", "python.exe")
        if not os.path.exists(python_path):
            python_path = os.path.join("venv", "Scripts", "python")
    else:  # Linux/Mac
        python_path = os.path.join("venv", "bin", "python")

    # Vérifie si le venv existe et fonctionne
    venv_functional = False
    if os.path.exists(python_path):
        try:
            subprocess.run([python_path, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            venv_functional = True
        except Exception:
            venv_functional = False

    if not venv_functional:
        print("[*] Creating fresh virtual environment 'venv'...")
        venv.create("venv", with_pip=True, clear=True)
    else:
        print("[*] Functional virtual environment detected.")

    return python_path

def install_dependencies(python_path):
    """Install dependencies in virtual environment using requirements.txt"""
    req_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    if not os.path.exists(req_file):
        print("[-] requirements.txt not found!")
        return False

    print(f"[*] Installing dependencies from {req_file}...")
    try:
        # Upgrade pip first to prevent resolver issues
        subprocess.check_call([python_path, "-m", "pip", "install", "--upgrade", "pip"], stdout=subprocess.DEVNULL)
        # Install requirements in batch
        subprocess.check_call([python_path, "-m", "pip", "install", "-r", req_file])
        print("[+] All dependencies successfully installed.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[-] Dependency installation failed with error: {e}")
        return False

def create_launcher_scripts():
    """Create launcher scripts for easy use"""
    # Create Linux/Mac launcher
    with open("run_nexora.sh", "w", encoding="utf-8") as f:
        f.write("""#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
if [ -d "$DIR/venv" ]; then
    source "$DIR/venv/bin/activate"
fi
python3 "$DIR/nexora.py" || python "$DIR/nexora.py"
""")
    os.chmod("run_nexora.sh", 0o755)

    # Create Windows launcher
    with open("run_nexora.bat", "w", encoding="utf-8") as f:
        f.write("""@echo off
cd /d "%~dp0"
if exist "venv\\Scripts\\activate.bat" (
    call venv\\Scripts\\activate.bat
)
python nexora.py
pause
""")

def main():
    print("=" * 45)
    print("   Nexora Logger - Automated Setup")
    print("=" * 45)

    check_python_version()
    python_path = create_virtual_env()

    if install_dependencies(python_path):
        create_launcher_scripts()
        print("\n[+] Installation completed successfully!")
        print("\nLaunch options:")
        print("  - Linux/macOS : ./run_nexora.sh")
        print("  - Windows     : run_nexora.bat")
        print("  - Manual      : source venv/bin/activate && python nexora.py")
    else:
        print("\n[-] Installation failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()