#!/usr/bin/env python3
"""
Automatic installation script for Nexora Logger
"""

import sys
import subprocess
import importlib
import os
import venv

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("Python 3.8 or higher is required")
        sys.exit(1)
    print(f"Python {sys.version_info.major}.{sys.version_info.minor} detected")

def create_virtual_env():
    """Create and activate virtual environment"""
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        venv.create("venv", with_pip=True)
    
    # Determine the pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = os.path.join("venv", "Scripts", "pip")
        python_path = os.path.join("venv", "Scripts", "python")
    else:  # Linux/Mac
        pip_path = os.path.join("venv", "bin", "pip")
        python_path = os.path.join("venv", "bin", "python")
    
    return pip_path, python_path

def install_dependencies(pip_path):
    """Install missing dependencies in virtual environment"""
    dependencies = [
        "requests",
        "pillow", 
        "psutil",
        "pyautogui",
        "colorama"
    ]
    
    print("Installing dependencies in virtual environment...")
    
    for package in dependencies:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([pip_path, "install", package])
            print(f"{package} successfully installed")
        except subprocess.CalledProcessError:
            print(f"Installation failed for {package}")
            return False
    return True

def create_launcher_scripts():
    """Create launcher scripts for easy use"""
    # Create Linux/Mac launcher
    with open("run_nexora.sh", "w") as f:
        f.write("""#!/bin/bash
source venv/bin/activate
python nexora.py
""")
    os.chmod("run_nexora.sh", 0o755)
    
    # Create Windows launcher
    with open("run_nexora.bat", "w") as f:
        f.write("""@echo off
venv\\Scripts\\activate
python nexora.py
""")

def main():
    print("Nexora Logger - Installation")
    print("=" * 40)
    
    check_python_version()
    
    pip_path, python_path = create_virtual_env()
    
    if install_dependencies(pip_path):
        create_launcher_scripts()
        print("\nInstallation completed successfully!")
        print("\nNow you can run:")
        print("  On Linux/Mac: ./run_nexora.sh")
        print("  On Windows: run_nexora.bat")
        print("  Or manually: source venv/bin/activate && python nexora.py")
    else:
        print("\nInstallation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()