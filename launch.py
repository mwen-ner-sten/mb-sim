#!/usr/bin/env python3
"""
Universal GUI Launcher for MB-Sim Modbus Simulator

This script automatically detects your operating system and launches the GUI
using the most appropriate method for your platform.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def detect_os():
    """Detect the operating system."""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":  # macOS
        return "macos"
    else:  # Linux and others
        return "linux"

def main():
    """Launch the GUI using the appropriate method for the OS."""
    os_type = detect_os()
    project_root = Path(__file__).parent.absolute()

    print("🚀 MB-Sim GUI Launcher")
    print(f"💻 Operating System: {platform.system()}")
    print(f"📁 Project root: {project_root}")

    # Set up environment
    env = os.environ.copy()
    env['PYTHONPATH'] = str(project_root / 'src')

    # Common options for all platforms
    gui_options = {
        'env': env,
        'cwd': project_root
    }

    try:
        if os_type == "windows":
            # On Windows, try multiple approaches
            print("🎯 Method: Direct module execution")

            # Method 1: Try running as module first
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'mb_sim.gui'
                ], **gui_options, timeout=5)
                return result.returncode
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                pass

            # Method 2: Try using the batch file
            print("🎯 Method: Using batch file launcher")
            batch_file = project_root / 'launch_gui.bat'
            if batch_file.exists():
                result = subprocess.run([str(batch_file)], shell=True, **gui_options)
                return result.returncode
            else:
                print("⚠️  Batch file not found, falling back to direct execution")

        elif os_type == "macos":
            # On macOS, use the shell script if available
            shell_script = project_root / 'launch_gui.sh'
            if shell_script.exists():
                print("🎯 Method: Using shell script launcher")
                result = subprocess.run([str(shell_script)], **gui_options)
                return result.returncode
            else:
                print("⚠️  Shell script not found, using direct execution")

        # Linux/Unix approach
        shell_script = project_root / 'launch_gui.sh'
        if shell_script.exists():
            print("🎯 Method: Using shell script launcher")
            result = subprocess.run([str(shell_script)], **gui_options)
            return result.returncode
        else:
            print("⚠️  Shell script not found, using direct execution")

        # Fallback: Direct module execution (works on all platforms)
        print("🎯 Method: Direct module execution")
        print("💡 Tips:")
        print("   • Press Ctrl+C (or Cmd+C on Mac) to exit the GUI")
        print("   • The GUI will show device and register management")
        print("   • Make sure no other Modbus server is running on port 1502")
        print("="*50)

        result = subprocess.run([
            sys.executable, '-m', 'mb_sim.gui'
        ], **gui_options)

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
        print("   5. Make sure PyQt6 is properly installed")
        return 1

if __name__ == "__main__":
    sys.exit(main())