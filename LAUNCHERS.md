# MB-Sim GUI Launchers

This document describes the various launcher scripts available for easily running the MB-Sim GUI application.

## Available Launchers

### 1. Universal Python Launcher (`launch.py`)

**Cross-platform launcher that automatically detects your OS and uses the best method.**

```bash
python launch.py
```

**Features:**
- ✅ Auto-detects operating system (Linux, macOS, Windows)
- ✅ Sets up PYTHONPATH automatically
- ✅ Provides helpful tips and troubleshooting
- ✅ Handles different Python installations
- ✅ Shows progress and status information

### 2. Shell Script Launcher (`launch_gui.sh`)

**For Linux and macOS users who prefer shell scripts.**

```bash
./launch_gui.sh
```

**Features:**
- ✅ Optimized for Unix-like systems
- ✅ Uses system Python detection
- ✅ Colorized output
- ✅ Clean error handling

### 3. Batch File Launcher (`launch_gui.bat`)

**For Windows users.**

```bash
launch_gui.bat
```

**Features:**
- ✅ Windows-specific batch commands
- ✅ Proper error handling
- ✅ Pause on completion

### 4. Direct Module Launch

**Standard Python module execution (fallback method).**

```bash
python -m mb_sim.gui
```

## How to Use

### Quick Start

1. **Navigate to the project root directory**
   ```bash
   cd /path/to/mb-sim
   ```

2. **Run the launcher**
   ```bash
   python launch.py
   ```

### Troubleshooting

If the launcher doesn't work, try:

1. **Check Python installation**
   ```bash
   python --version  # Should show Python 3.11+
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Try direct module execution**
   ```bash
   PYTHONPATH=/path/to/mb-sim/src python -m mb_sim.gui
   ```

4. **Check for GUI dependencies**
   ```bash
   python -c "import PyQt6; print('PyQt6 available')"
   ```

## Launcher Behavior

### OS Detection

The universal launcher automatically detects your operating system:

- **Linux**: Uses shell script if available, otherwise direct execution
- **macOS**: Uses shell script if available, otherwise direct execution
- **Windows**: Uses batch file if available, otherwise direct execution

### Environment Setup

All launchers automatically:

1. Set `PYTHONPATH` to include the `src` directory
2. Change to the project root directory
3. Detect and use the appropriate Python interpreter
4. Provide helpful output and error messages

### Exit Behavior

- **Normal exit**: Clean shutdown with proper exit codes
- **Keyboard interrupt** (Ctrl+C): Graceful termination
- **Error conditions**: Detailed error messages and troubleshooting tips

## Customization

You can modify the launcher behavior by editing the launcher scripts:

- Change Python command detection
- Modify environment variables
- Add custom startup messages
- Customize error handling

## Requirements

- Python 3.11+
- PyQt6 (for GUI functionality)
- pymodbus (for Modbus protocol)
- Other dependencies listed in `requirements.txt`

## Support

If you encounter issues with the launchers:

1. Check the troubleshooting section above
2. Try the direct module execution method
3. Ensure all dependencies are installed
4. Verify Python version compatibility