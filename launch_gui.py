#!/usr/bin/env python3
"""
GUI Launcher for MB-Sim Modbus Simulator

This script provides an easy way to launch the GUI without needing to set PYTHONPATH.
Run this script from the project root directory.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Launch the MB-Sim GUI application."""
    # Get the current directory (project root)
    project_root = Path(__file__).parent.absolute()

    # Set up the environment
    env = os.environ.copy()
    env['PYTHONPATH'] = str(project_root / 'src')

    # Path to the GUI module
    gui_module = 'mb_sim.gui'

    try:
        # Launch the GUI
        print(f"🚀 Launching MB-Sim GUI from {project_root}")
        print("📁 Using PYTHONPATH:", env['PYTHONPATH'])
        print("🎯 Running:", f"python -m {gui_module}")
        print("\n" + "="*50)
        print("💡 Tips:")
        print("   • Press Ctrl+C to exit the GUI")
        print("   • The GUI will show device and register management")
        print("   • Make sure no other Modbus server is running on port 1502")
        print("="*50 + "\n")

        # Run the GUI module
        result = subprocess.run([
            sys.executable, '-m', gui_module
        ], env=env, cwd=project_root)

        return result.returncode

    except KeyboardInterrupt:
        print("\n👋 GUI launcher interrupted by user")
        return 0
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure you're in the project root directory")
        print("   2. Check that Python 3.11+ is installed")
        print("   3. Install dependencies: pip install -r requirements.txt")
        print("   4. Try running: python -m mb_sim.gui")
        return 1

if __name__ == "__main__":
    sys.exit(main())