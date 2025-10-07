# Shaban Logger

Advanced system monitoring and logging tool for security professionals and system administrators.

*In tribute to Shaban, a young computer engineering graduate in Gaza, whose memory reflects the strength, knowledge, and hope of a people seeking justice.*

## Features

- **System Information** - Collect detailed system specs and configuration
- **Screenshot Capture** - Automatic screenshot logging  
- **Network Monitoring** - Network interface and connection tracking
- **Process Logging** - Real-time process monitoring
- **Cross-Platform** - Works on Windows and Linux systems

## Quick Start

### Automatic Installation

# Clone the repository
git clone https://github.com/Ahlan06/shaban-logger.git
cd shaban-logger

# Install dependencies automatically
python3 install.py

Manual Installation
pip install requests pillow psutil pyautogui colorama


Usage

# Run the main logger
python3 combined_logger.py

# Run additional tools
python3 shaban.py

shaban-logger/
-install.py           # Automatic dependency installer
-combined_logger.py   # Main logging system
-shaban.py           # Additional tools
-README.md           # Documentation


# Requirements
Python: 3.8 or higher

# Dependencies:
- requests - HTTP library
-pillow - Image processing
-psutil - System utilities
-pyautogui - Screenshot capture
-colorama - Terminal colors

# Supported Systems :
-Windows 10/11
-Linux (Kali, Ubuntu, Debian)
-macOS (Untested but should work)

# In Memoriam : 

This project is named after Shaban, a young Palestinian computer scientist from Gaza with his whole life ahead of him, whose story illustrates the ongoing struggle for justice and transparency. This tool aims to bring clarity and visibility—principles embodied in Shaban's memory.

#Legal Disclaimer 
This tool is intended for:

-Educational purposes
-Security research
-System administration
-Authorized penetration testing
-Personal systems you own

# PROHIBITED:

-Unauthorized system monitoring
-Illegal surveillance
-Malicious activities
-The authors are not responsible for misuse of this software.

Security Note
This tool is designed for:

-Security professionals
-IT administrators
-Researchers
-Authorized testing environments

# Always ensure you have proper authorization before using on any system.

Troubleshooting
Installation Issues

# If pip install fails, try:
python3 -m pip install --upgrade pip

# On Linux if permission denied:
pip install --user package_name
Python Version Check
bash
python3 --version
# Should be 3.8 or higher
Support
For issues and questions:

Check the troubleshooting section above

Ensure all dependencies are installed

Verify Python version compatibility

Author
Ahlan06 - Security Researcher

License : 
This project is provided for educational and research purposes.

<div align="center">
IN MEMORY OF SHABAN 

May this tool ensure that his name is never forgotten.

USE RESPONSIBLY 

Only use on systems you own or have explicit permission to test.

</div>  
